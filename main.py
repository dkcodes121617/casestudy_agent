"""Entrypoint for the WizCodes case study agent.

Deployment mirrors the blog agent: a scheduled GitHub Actions workflow on this
public repo (free minutes, no server), reading the real corpus out of the site
repo, and touching only git. Two deliberate differences:

  - MONTHLY, not hourly. Thirty known projects; no reason to rush.
  - Cadence is enforced against the site registry, not remembered, so the two
    cron slots a month cannot both publish.

Publishing mode is OPEN_PR: direct to main by default, PR on request.

Run modes:
  python main.py                    scheduled: generate one if a slot is due
  python main.py --now              force one now
  python main.py --project <id>     force a specific project
  python main.py --plan             print the ranked queue and exit
"""
from __future__ import annotations

import logging
import sys

from core.config import CONFIG


def _setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, CONFIG.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    for noisy in ("httpx", "httpcore", "urllib3", "git"):
        logging.getLogger(noisy).setLevel(logging.ERROR)


def _site_dir():
    """The site checkout to read the corpus from.

    Live runs clone the repo (so the corpus is authoritative and the publisher has
    somewhere to branch from); dry runs read the local sibling folder, so you can
    iterate without a network round trip.
    """
    if CONFIG.dry_run:
        return None
    from core.publish.pr_publisher import ensure_repo
    return ensure_repo().working_tree_dir


def main(argv: list[str]) -> int:
    _setup_logging()
    log = logging.getLogger("agent.main")

    from casestudy.corpus import load_corpus
    from casestudy.queue import rank, select_next

    forced_project = None
    if "--project" in argv:
        i = argv.index("--project")
        if i + 1 < len(argv):
            forced_project = argv[i + 1]

    # --plan reads the local corpus and never clones: it is a "what would happen"
    # command and should stay instant and offline.
    if "--plan" in argv:
        corpus = load_corpus()
        ranked = rank(corpus)
        eligible = [c for c in ranked if c.eligible]
        print(f"{len(corpus.written_slugs)} study(s) written, {len(ranked)} project(s) remaining")
        print(f"{len(eligible)} have a clean brief and could be generated now\n")
        for c in ranked[:15]:
            mark = " " if c.eligible else "x"
            print(f" {mark} {c.project.id:<26} {c.score:>5.2f}  {c.archetype:<18} "
                  f"{c.blocked_reason or '; '.join(c.reasons[:2])}")
        return 0

    problems = CONFIG.validate_for_publish()
    if problems:
        for p in problems:
            log.error("config: %s", p)
        return 1

    site_dir = _site_dir()
    corpus = load_corpus(site_dir)

    # ── Cadence guard ──
    # The cron fires on the 1st AND the 15th so a missed or failed slot has a
    # second chance in the same month. Without this check that meant two studies
    # a month regardless of STUDIES_PER_MONTH, which was declared, set in the
    # workflow, documented as the cadence control — and read by nothing.
    #
    # Counted from the site registry rather than remembered, so it is correct on
    # an ephemeral runner and cannot double-publish. A forced manual run skips it
    # deliberately: if you asked for a specific project, you meant it.
    if not forced_project:
        from casestudy.corpus import count_published_this_month
        published = count_published_this_month(site_dir)
        if published >= CONFIG.studies_per_month:
            log.info("cadence: %d study(s) already published this month "
                     "(STUDIES_PER_MONTH=%d) — nothing due, exiting",
                     published, CONFIG.studies_per_month)
            return 0
        log.info("cadence: %d/%d published this month — a study is due",
                 published, CONFIG.studies_per_month)

    if forced_project:
        candidate = next((c for c in rank(corpus) if c.project.id == forced_project), None)
        if candidate is None:
            log.error("project %r not found, or it already has a study", forced_project)
            return 1
        if not candidate.eligible:
            log.error("project %r is blocked: %s", forced_project, candidate.blocked_reason)
            return 1
        log.info("forced selection: %s", forced_project)
    else:
        candidate = select_next(corpus)
        if candidate is None:
            return 0

    # Pre-flight health check, same circuit-breaker pattern as the blog agent: if
    # the proxy is 502-ing, exit cheaply now. Nothing is marked done, so the next
    # scheduled run simply retries.
    from core.llm.client import LLMClient
    ok, detail = LLMClient().ping()
    if not ok:
        log.warning("proxy health check failed (%s) — skipping this run", detail[:120])
        return 0
    log.info("proxy healthy — generating")

    from casestudy.run import run_once
    result = run_once(candidate, corpus, site_dir=site_dir)

    status = result.get("status")
    if status in ("ready", "published"):
        log.info("run succeeded: %s (%s)", result.get("slug"), status)
        return 0

    log.warning("run did not publish: %s / %s", status, result.get("abort_reason"))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
