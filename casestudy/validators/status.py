"""Release-claim guard for `hideStatus` studies.

A PORT of scripts/status-check.mjs in the site repo. That script is the one that
runs in `prebuild` and blocks the deploy; this one runs inside the agent so a
violation is caught at generation time rather than at build time — same rules,
earlier failure, no wasted PR.

The rules below are not a guess. Each was added after a real miss in hand-written
content, all four of them written by someone actively trying to write none:

    written                              a phrase list had     gap
    -----------------------------------  --------------------  ------------------
    "in the weeks after launch"          "launched"            wrong conjugation
    "fixes reached users"                "users are"           wrong word order
    "for both the App Store"             "on the App Store"    wrong preposition
    "without waiting on a store review"  —                     not on the list
    "any post-release tuning that is
     not a store update"                 —                     two misses, one line

So: stems, not conjugations. Entities banned outright, not as verb phrases. And
ambiguous words matched only as phrases — bare "live" is legitimate in "live
updates" and must not fire.

KEEP IN SYNC with scripts/status-check.mjs. If you change a rule here, change it
there; the site build is the backstop and the two disagreeing is worse than either
being slightly wrong.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# Release-state stem families. Word-bounded so "relationship" never trips.
STEMS: list[tuple[str, re.Pattern[str]]] = [
    ("launch", re.compile(r"\b(launch|launches|launched|launching|relaunch(ed|ing)?|prelaunch)\b", re.I)),
    ("ship", re.compile(r"\b(ship|ships|shipped|shipping)\b", re.I)),
    ("release", re.compile(r"\b(release|releases|released|releasing|prerelease)\b", re.I)),
    ("download", re.compile(r"\b(downloads?|downloaded|installs?|installed|installations?)\b", re.I)),
]

# Release senses of ambiguous words, matched only as phrases.
PHRASES: list[tuple[str, re.Pattern[str]]] = [
    ("live", re.compile(r"\b(went live|goes live|is live|now live|live on the|currently live)\b", re.I)),
    ("production", re.compile(r"\b(in production|production use|production traffic)\b", re.I)),
    ("users", re.compile(
        r"\b((our|real|active|end|thousands of|millions of) users|users? (are|have|can now)|"
        r"reached users|user ?base)\b", re.I)),
    ("adoption", re.compile(r"\b(customers (are|use|now)|in the hands of|rolled out to)\b", re.I)),
]

# Banned outright for a hideStatus study — no verb required. There is no
# legitimate reason to discuss app-store distribution for something we are making
# no distribution claim about.
ENTITIES: list[tuple[str, re.Pattern[str]]] = [
    ("app-store", re.compile(
        r"\b(app store|appstore|play store|google play|testflight|"
        r"store (listing|review|submission|update|page))\b", re.I)),
]

ALL_RULES = STEMS + PHRASES + ENTITIES

_FENCE = re.compile(r"```.*?```", re.S)
_COMPONENT = re.compile(r"<[A-Z].*?/>", re.S)


@dataclass
class StatusFinding:
    rule: str
    match: str
    line: int
    context: str


@dataclass
class StatusReport:
    findings: list[StatusFinding] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not self.findings

    def render(self) -> str:
        if self.clean:
            return "status: PASS (no release claims)"
        lines = [f"status: {len(self.findings)} release claim(s) on a hideStatus study — ABORT"]
        for f in self.findings:
            lines.append(f"  line {f.line} [{f.rule}] {f.match!r}\n      {f.context}")
        return "\n".join(lines)


def _prose_only(mdx: str) -> str:
    return _COMPONENT.sub(" ", _FENCE.sub(" ", mdx))


def scan(body_mdx: str, *, hide_status: bool) -> StatusReport:
    """Only meaningful for a hideStatus study; returns clean otherwise."""
    report = StatusReport()
    if not hide_status:
        return report

    lines = _prose_only(body_mdx).split("\n")
    for rule, pattern in ALL_RULES:
        for i, line in enumerate(lines, start=1):
            for m in pattern.finditer(line):
                lo = max(0, m.start() - 34)
                report.findings.append(StatusFinding(
                    rule=rule, match=m.group(0), line=i,
                    context=line[lo: m.end() + 34].strip(),
                ))
    report.findings.sort(key=lambda f: f.line)
    return report
