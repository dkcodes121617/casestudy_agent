"""Publish a finished case study as a PULL REQUEST.

The one place this agent deliberately differs from the blog agent's publisher.

The blog agent commits straight to `main` and lets the site's deploy workflow take
it live, unattended, 1–2 times a day. That is the right trade for a post making
industry-level claims: the blast radius of a bad one is a slightly wrong article,
and waiting for a human would mean it never runs.

A case study names a real client and describes work done under an agreement. The
blast radius of a bad one is a breached confidence, and it is not recoverable by
editing the page afterwards — it has already been read, cached, and possibly
scraped. So this opens a branch and a PR, and a human merges.

That is also where the escape hatch lives. There is deliberately no way to flag a
draft past the confidentiality or status checks; the human override is to rewrite
the sentence and re-run, which costs an affirmative edit rather than a click.

Flow:
  1. clone/pull the site repo (token in the remote URL, never logged)
  2. branch `case-study/<slug>`
  3. write src/content/case-studies/<slug>.mdx
  4. insert the typed entry into studies.ts
  5. commit, push the branch
  6. `gh pr create` with the full validation report as the body
"""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from git import Repo

from core.config import CONFIG

log = logging.getLogger("agent.publish")

_REGISTRY_ANCHOR = "export const studies: CaseStudy[] = ["


def _authed_remote() -> str:
    return f"https://x-access-token:{CONFIG.github_token}@github.com/{CONFIG.github_repo}.git"


def ensure_repo() -> Repo:
    d = CONFIG.site_repo_dir
    if (d / ".git").exists():
        repo = Repo(d)
        repo.remotes.origin.set_url(_authed_remote())
        repo.git.checkout(CONFIG.github_branch)
        repo.remotes.origin.pull(CONFIG.github_branch)
    else:
        log.info("cloning %s", CONFIG.github_repo)
        repo = Repo.clone_from(_authed_remote(), d, branch=CONFIG.github_branch)
    # CI runners have no global git identity; a commit would fail with
    # "empty ident name". Set a repo-local one.
    repo.git.config("user.email", CONFIG.git_author_email)
    repo.git.config("user.name", CONFIG.git_author_name)
    return repo


def _insert_registry(studies_ts: str, entry: str) -> str:
    idx = studies_ts.find(_REGISTRY_ANCHOR)
    if idx == -1:
        raise RuntimeError("could not find the studies[] array anchor in studies.ts")
    at = idx + len(_REGISTRY_ANCHOR)
    # Append at the END of the array, not the head. Unlike blog posts — where
    # newest-first is the reading order — studies.ts order is the queue's record of
    # what was written when, and the selector reads the tail for archetype rotation.
    close = studies_ts.rfind("\n]")
    if close == -1 or close < at:
        raise RuntimeError("could not find the closing bracket of studies[]")
    return studies_ts[:close] + "\n" + entry.rstrip() + studies_ts[close:]


def publish(state: dict, report_body: str) -> str:
    """Publish, honouring OPEN_PR.

    `OPEN_PR` was declared in config.py and set in the workflow from the first
    commit — and NOTHING READ IT. `run.py` called publish_pr() unconditionally, so
    setting OPEN_PR=0 looked like it switched to direct publishing and silently
    did nothing at all. A config flag that appears to work and doesn't is worse
    than no flag; it is now the real switch.

    OPEN_PR=1 (default) — branch + pull request, a human merges.
    OPEN_PR=0           — commit straight to main, exactly like the blog agent,
                          and the site's deploy workflow takes it live.

    Direct mode is a real choice with a real cost: every guard still runs and
    still aborts, but nobody reads the study before the world does. It is
    defensible because the confidentiality scope is owner-supplied per project —
    not because the guards are infallible.
    """
    if CONFIG.open_pr:
        return publish_pr(state, report_body)
    return publish_direct(state, report_body)


def _write_files(repo: Repo, state: dict) -> str:
    """Write the .mdx and insert the registry entry. Returns the mdx path."""
    root = Path(repo.working_tree_dir)
    slug = state["slug"]

    mdx_rel = f"{CONFIG.studies_content_rel}/{slug}.mdx"
    mdx_path = root / mdx_rel
    if mdx_path.exists():
        raise RuntimeError(f"refusing to overwrite existing study: {mdx_rel}")
    mdx_path.write_text(state["body_mdx"], encoding="utf-8")

    registry_path = root / CONFIG.studies_registry_rel
    studies_ts = registry_path.read_text(encoding="utf-8")
    if f"slug: '{slug}'" in studies_ts:
        raise RuntimeError(f"slug already in the registry: {slug}")
    new_ts = _insert_registry(studies_ts, state["registry_entry"])
    if new_ts.count(f"slug: '{slug}'") != 1:
        raise RuntimeError("registry insertion sanity check failed")
    registry_path.write_text(new_ts, encoding="utf-8")
    return mdx_rel


def publish_direct(state: dict, report_body: str) -> str:
    """Commit straight to main. Same shape as the blog agent's publisher.

    Pushing to `src/**` is what triggers the site's deploy workflow, so this is
    the path that actually puts a study live without a human in it.
    """
    if not CONFIG.github_token:
        raise RuntimeError("GITHUB_TOKEN not set — cannot publish")

    repo = ensure_repo()
    repo.git.checkout(CONFIG.github_branch)
    mdx_rel = _write_files(repo, state)

    repo.git.add(mdx_rel, CONFIG.studies_registry_rel)
    repo.git.commit(
        "-m", f"case study: {state['project_name']}",
        "-m", f"Automated. archetype={state.get('archetype', '')}\n\n{report_body}",
    )
    log.info("pushing to %s", CONFIG.github_branch)
    repo.remotes.origin.push(CONFIG.github_branch)
    _ping_indexnow(state["slug"])
    log.info("published %s — the site deploy workflow takes it from here", mdx_rel)
    return CONFIG.github_branch


def _ping_indexnow(slug: str) -> None:
    """Tell Bing/IndexNow the new study URL exists.

    Deliberately called from publish_direct ONLY. A PR branch is not live; pinging
    from publish_pr would announce a URL that 404s until someone merges, which is
    worse than not pinging at all — IndexNow treats a 404 as a bad submission.

    Best-effort: a failed ping must never fail a publish that already succeeded,
    so every error is swallowed with a warning. The push has happened by the time
    this runs; there is nothing left to roll back.
    """
    key = CONFIG.indexnow_key
    if not key:
        log.info("indexnow: no INDEXNOW_KEY set — skipping ping")
        return
    try:
        import requests

        resp = requests.post(
            "https://api.indexnow.org/IndexNow",
            json={
                "host": "wizcodes.site",
                "key": key,
                "keyLocation": f"https://wizcodes.site/{key}.txt",
                # /work is the index the new study appears on, so both URLs changed.
                "urlList": [
                    f"https://wizcodes.site/work/{slug}",
                    "https://wizcodes.site/work",
                ],
            },
            timeout=15,
        )
        log.info("indexnow: HTTP %s for /work/%s", resp.status_code, slug)
    except Exception as e:  # noqa: BLE001
        log.warning("indexnow ping failed (ignored): %s", e)


def publish_pr(state: dict, report_body: str) -> str:
    """Write files, branch, commit, push, open a PR. Returns the branch name."""
    if not CONFIG.github_token:
        raise RuntimeError("GITHUB_TOKEN not set — cannot publish")

    repo = ensure_repo()
    slug = state["slug"]
    branch = f"case-study/{slug}"

    # Start from a clean branch off the target, so a re-run after a failure does
    # not inherit a half-written previous attempt.
    repo.git.checkout(CONFIG.github_branch)
    if branch in repo.heads:
        repo.git.branch("-D", branch)
    repo.git.checkout("-b", branch)

    mdx_rel = _write_files(repo, state)

    repo.git.add(mdx_rel, CONFIG.studies_registry_rel)
    repo.git.commit("-m", f"case study: {state['project_name']}",
                    "-m", f"Automated draft. archetype={state.get('archetype', '')}")
    log.info("pushing branch %s", branch)
    repo.remotes.origin.push(f"{branch}:{branch}", set_upstream=True, force=True)

    _open_pr(Path(repo.working_tree_dir), branch, state, report_body)
    return branch


def _open_pr(root: Path, branch: str, state: dict, report_body: str) -> None:
    """Open the PR via `gh`, which is preinstalled on GitHub-hosted runners.

    Best-effort by design: the branch is already pushed and reviewable, so a
    failure here costs a click, not the run.
    """
    title = f"Case study: {state['project_name']}"
    body = (
        f"Automated draft for **{state['project_name']}** "
        f"(`{state.get('archetype', '')}`).\n\n"
        f"Every line below is a check that already ran — this is a summary, not a "
        f"to-do list.\n\n{report_body}\n\n"
        f"---\n"
        f"There is deliberately no way to flag a draft past the confidentiality or "
        f"status checks. If something here is wrong, rewrite it and re-run.\n"
    )
    try:
        subprocess.run(
            ["gh", "pr", "create", "--base", CONFIG.github_branch, "--head", branch,
             "--title", title, "--body", body],
            cwd=root, check=True, capture_output=True, text=True,
            env={**_gh_env()},
        )
        log.info("opened PR for %s", branch)
    except FileNotFoundError:
        log.warning("gh CLI not found — branch %s is pushed, open the PR manually", branch)
    except subprocess.CalledProcessError as e:
        log.warning("gh pr create failed (%s) — branch %s is pushed", e.stderr.strip()[:160], branch)


def _gh_env() -> dict:
    import os
    env = dict(os.environ)
    # gh authenticates from GH_TOKEN; the workflow passes the same fine-grained PAT.
    env.setdefault("GH_TOKEN", CONFIG.github_token)
    return env
