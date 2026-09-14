"""Regression test for the release-claim gate's negation handling.

    python tools/test_status_negation.py

Self-contained on purpose — no corpus, no site checkout — so it runs anywhere and
in CI. `tools/selftest.py` still covers the validators against the real specimens.

WHY THIS EXISTS
Every scheduled run of this agent from 31 Jul to 13 Sep 2026 aborted on this gate,
missing three publish slots, and every observed failure was a NEGATED phrase: the
study said the project avoids app stores and the gate read that as a claim it
shipped on one. The loop could not recover, because each rewrite regenerated all
six sections and tripped a different innocuous word.

Both directions are tested. Loosening a safety gate is only correct if the thing
it exists to catch is still caught, so the MUST_FAIL block is the more important
half of this file.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from casestudy.validators import status as statusv  # noqa: E402

# Real sentences from the three runs that aborted, plus the phrasings the rules
# were originally written to catch (from the module's own docstring).
MUST_PASS = [
    # --- the three production aborts ---
    "Security was designed in from the start, not bolted on after launch.",
    "The platform updates instantly without client installations.",
    "One build runs everywhere without app-store submission cycles or device-specific builds.",
    # --- same shape, other rules ---
    "No downloads are required to use it.",
    "It avoids the App Store entirely.",
    "Updates reach people instantly rather than through a release cycle.",
    "The architecture eliminates installs for end users.",
    "Works regardless of app store approval timelines.",
    "A web build means no installations and no store submission.",
    # --- words that merely resemble the rules ---
    "The relationship with the client outlasted the engagement.",
    # --- capability, not an event: bare infinitive after an enabling verb ---
    "The modular design lets us ship core features first and add automation later.",
    "The architecture allows the team to ship changes safely.",
    "A modular build makes it possible to launch features independently.",
    "Designed to release updates without downtime.",
    "The team can download the export as CSV.",
    "The schema is built to release new field types without a migration.",
    "Staff are able to install the report template themselves.",
]

MUST_FAIL = [
    # --- genuine release claims: the gate must still catch every one ---
    "The app launched in March and has been stable since.",
    "We shipped it to the App Store in two weeks.",
    "In the weeks after launch, usage climbed steadily.",
    "Fixes reached users the same day.",
    "It is now live on the Play Store.",
    "Thousands of users have downloaded it.",
    "The build is in production use across three offices.",
    "It went live last quarter.",
    "Available for both the App Store and Google Play.",
    "Any post-release tuning is handled by their own team.",
    # --- a negation that has gone out of scope before the claim ---
    "There were no delays. The app launched in March.",
    "Without a doubt, it shipped on time.",
    # The module's own docstring lists this as a claim the phrase list MISSED,
    # so it is a true positive: it asserts an ongoing release cadence.
    "The team ships changes without waiting on a store review.",
    # --- an enabling verb must NOT excuse a conjugated form ---
    "The design lets us ship faster, and we shipped in March.",
    "It can be downloaded from the Play Store.",
    "The rewrite allowed the team to launch, and it launched on time.",
]

# KNOWN GAP, pre-existing and deliberately not papered over here: the `ship`
# stem cannot tell logistics from releases, so "Shipping containers were the
# subject of the dashboard" is still a false positive. Distinguishing the two
# needs word-sense context, which is a bigger change than this gate deserves;
# the brief for such a project should avoid the word.


def main() -> int:
    failures: list[str] = []

    for line in MUST_PASS:
        report = statusv.scan(line, hide_status=True)
        if not report.clean:
            hits = ", ".join(f"[{f.rule}] {f.match!r}" for f in report.findings)
            failures.append(f"FALSE POSITIVE  {line!r}\n                  flagged {hits}")

    for line in MUST_FAIL:
        report = statusv.scan(line, hide_status=True)
        if report.clean:
            failures.append(f"MISSED CLAIM    {line!r}")

    # A study that does not hide its status is never scanned at all.
    if not statusv.scan("The app launched in March.", hide_status=False).clean:
        failures.append("scan() flagged a study that is not hideStatus")

    total = len(MUST_PASS) + len(MUST_FAIL) + 1
    if failures:
        print(f"status negation: {len(failures)} of {total} FAILED\n")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"status negation: {total}/{total} ok "
          f"({len(MUST_PASS)} safe phrasings pass, {len(MUST_FAIL)} real claims still caught)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
