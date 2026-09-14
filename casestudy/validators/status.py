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

import logging
import re
from dataclasses import dataclass, field

log = logging.getLogger("agent.status")

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

# TypeScript comments. When this scans a registry entry rather than an MDX body,
# the entry carries the comments explaining WHY a rule exists — including, with
# perfect irony, "// no shipped, launched or released claim, which is what
# hideStatus governs". A comment is not published content.
_TS_COMMENT = re.compile(r"//.*|/\*[\s\S]*?\*/")


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
    return _TS_COMMENT.sub(" ", _COMPONENT.sub(" ", _FENCE.sub(" ", mdx)))


# Words that INVERT the claim that follows them. A release-state word inside one
# of these is not a release claim — it is the opposite, and usually the thing
# that makes a web build worth choosing.
#
# Without this, the gate was unusable. Every scheduled run from 31 Jul to 13 Sep
# aborted, three publish slots missed, and all three observed failures were
# negations:
#
#   "...designed in from the start, not bolted on after launch."
#   "...updates instantly without client installations."
#   "...runs everywhere without app-store submission cycles."
#
# None of those asserts the project shipped. The loop could not recover either,
# because each rewrite regenerated all six sections and tripped a different
# innocuous word, so the rewrite budget was spent every time.
_NEGATION = re.compile(
    r"\b(?:without|no|not|never|avoids?|avoiding|skips?|skipping|eliminates?|"
    r"eliminating|instead\s+of|rather\s+than|free\s+from|independent\s+of|"
    r"regardless\s+of|prevents?|removes?|removing)\b",
    re.I,
)

#: How far back to look for a negation. Long enough to catch "without waiting on
#: a store review" (28 chars), short enough that a negation in a previous clause
#: does not excuse a genuine claim later in the same sentence.
_NEGATION_WINDOW = 44


#: Phrases that contain a negation word but do not negate anything. "Without a
#: doubt, it shipped on time" is an assertion that it shipped, and reading the
#: "without" as scope would wave the claim straight through.
_FALSE_NEGATION = re.compile(
    r"\b(?:without\s+(?:a\s+)?doubt|without\s+question|no\s+doubt|"
    r"not\s+only|no\s+less|nothing\s+short\s+of)\b",
    re.I,
)


#: Verbs that make the word after them a CAPABILITY rather than an event.
#:
#: "The modular design lets us ship core features first" describes what the
#: architecture permits; it asserts nothing about whether anything was released.
#: Same for "allows the team to ship", "possible to launch", "designed to release
#: updates" and "can download the export as CSV" — that last one is a user
#: pressing a button in the product, which has no relationship to app stores at
#: all.
#:
#: Deliberately NOT included: will, would, going to. Those read as a release
#: assertion displaced in time rather than a statement about capability, and this
#: gate is meant to be conservative.
_CAPABILITY = re.compile(
    r"\b(?:to|can|could|may|might|lets?|allows?|enables?|helps?|"
    r"able\s+to|possible\s+to|designed\s+to|built\s+to|ready\s+to)\b"
    r"[^.;:!?]{0,24}$",
    re.I,
)

#: Only the BARE form can be a capability. "shipped", "ships", "launched",
#: "downloads" are claims about something that happened or keeps happening, and
#: no preceding word makes them otherwise — which is what keeps "We shipped it to
#: the App Store" and "The team ships changes" failing exactly as before.
_BARE_FORMS = frozenset({"ship", "launch", "release", "download", "install"})


def _capability(line: str, start: int, match: str) -> bool:
    """True when the match is a bare infinitive introduced by an enabling verb."""
    if match.lower() not in _BARE_FORMS:
        return False
    window = line[max(0, start - 40): start]
    window = re.split(r"[.;:!?]", window)[-1]
    return bool(_CAPABILITY.search(window))


def _negated(line: str, start: int) -> bool:
    """True when the match at `start` sits inside a negated construction."""
    window = line[max(0, start - _NEGATION_WINDOW): start]
    # A clause boundary between the negation and the match ends its scope:
    # "no downloads. Users are on it" must still be caught.
    window = re.split(r"[.;:!?,]", window)[-1]
    if _FALSE_NEGATION.search(window):
        return False
    return bool(_NEGATION.search(window))


def scan(body_mdx: str, *, hide_status: bool) -> StatusReport:
    """Only meaningful for a hideStatus study; returns clean otherwise."""
    report = StatusReport()
    if not hide_status:
        return report

    lines = _prose_only(body_mdx).split("\n")
    for rule, pattern in ALL_RULES:
        for i, line in enumerate(lines, start=1):
            for m in pattern.finditer(line):
                if _negated(line, m.start()):
                    log.debug(
                        "status: %r on line %d is negated, not a claim", m.group(0), i
                    )
                    continue
                if _capability(line, m.start(), m.group(0)):
                    log.debug(
                        "status: %r on line %d is a capability, not an event",
                        m.group(0), i,
                    )
                    continue
                lo = max(0, m.start() - 34)
                report.findings.append(StatusFinding(
                    rule=rule, match=m.group(0), line=i,
                    context=line[lo: m.end() + 34].strip(),
                ))
    report.findings.sort(key=lambda f: f.line)
    if report.findings:
        log.error("status: %d release claim(s) on a hideStatus study:", len(report.findings))
        for f in report.findings:
            log.error("  line %d [%s] %r — %s", f.line, f.rule, f.match, f.context[:90])
    return report
