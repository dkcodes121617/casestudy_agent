"""Validate the published REGISTRY ENTRIES, not just the MDX bodies.

    python tools/entrycheck.py        (or: make selftest, which chains it)

── Why this exists as its own check ──

`tools/selftest.py` validated every specimen's MDX body from day one. Nothing ever
validated the typed registry entry beside it — and the entry is where the metrics,
the seven glance fields, the FAQ and hero.mockup live.

That gap published this, live, in a FAQ answer:

    "MindMaze Junior took six weeks from initial prototype to delivery…"

An invented delivery timeline for a real client. No `duration` field on the study,
no timeline in the brief — the brief explicitly flagged the question and nobody
answered it. The run reported `claims: PASS (0 numeral(s) traced)` and was telling
the truth: the body was clean, and the body was all it read.

So this runs the same gates over the entries, and it is the test that would have
caught it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from casestudy.corpus import load_brief, load_corpus  # noqa: E402
from casestudy.run import _mockup_keys  # noqa: E402
from casestudy.validators import claims, entry as entryv, status as statusv  # noqa: E402
from core.config import CONFIG  # noqa: E402

SITE = CONFIG.local_site_dir


def main() -> int:
    src = (SITE / CONFIG.studies_registry_rel).read_text(encoding="utf-8")
    region = src[src.index("export const studies"):]
    marks = [(m.group(1), m.start()) for m in re.finditer(r"\bslug:\s*'([^']+)'", region)]
    corpus = load_corpus()

    fails = 0
    for i, (slug, at) in enumerate(marks):
        chunk = region[at: marks[i + 1][1] if i + 1 < len(marks) else len(region)]
        pid_m = re.search(r"projectId:\s*'([^']+)'", chunk)
        proj = corpus.project(pid_m.group(1)) if pid_m else None
        hide = bool(re.search(r"hideStatus:\s*true", chunk))
        metrics = proj.metrics if proj else []

        # Read the REAL brief when one exists. Passing the metrics list as
        # "evidence" instead made the metric-source check invent failures: a
        # figure legitimately sourced from the brief looked untraceable simply
        # because the brief was never opened. Studies written before the brief
        # system (the seven specimens) have none, so their source check is
        # skipped rather than guessed at.
        brief = load_brief(proj.id) if proj else None
        evidence = ((brief.safe + " " + brief.metrics) if brief and brief.exists else "")
        evidence += " " + (proj.description if proj else "")
        er = entryv.validate(
            chunk,
            project_metrics=metrics,
            brief_evidence=evidence or " ".join(metrics) + " " + chunk,
            valid_mockups=_mockup_keys(None, project_id=proj.id) if proj else set(),
            project_name=proj.name if proj else slug,
        )
        ec = claims.scan(chunk, project_metrics=metrics, brief_safe=" ".join(metrics))
        es = statusv.scan(chunk, hide_status=hide)

        ok = er.ok and ec.clean and es.clean
        print(f"{'ok  ' if ok else 'FAIL'} {slug:<20} "
              f"entry={len(er.errors)}e claims={len(ec.findings)} status={len(es.findings)}")
        if not ok:
            fails += 1
            for e in er.errors:
                print(f"       entry:  {e[:104]}")
            for f in ec.findings:
                print(f"       claims: {f.value!r} — …{f.context[:76]}…")
            for f in es.findings:
                print(f"       status: [{f.rule}] {f.match!r}")

    print()
    if fails:
        print(f"{fails} of {len(marks)} registry entries have problems")
        return 1
    print(f"all {len(marks)} registry entries clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
