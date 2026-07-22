"""Every number must trace to something real.

STRICTER than the blog agent's factcheck node, deliberately.

That node is narrow by design — "only flag fabrications about WizCodes" — and its
router ships a draft anyway once the fix budget is spent, on the reasoning that a
remaining flag is usually a false positive on generic advice. That trade is right
for a blog post making industry-level claims.

It is wrong here. A case study's numbers are claims about a specific client's
project, they are the lines a prospect quotes back, and there is no such thing as
an acceptable invented one. So: untraceable number → abort, no budget.

Three legitimate sources, mirroring `MetricSource` in the site's studies.ts:
  - projects.ts   the value appears in that project's metrics[]
  - brief         the value appears in briefs/<id>.md under "Safe to publish"
  - qualitative   no numeral at all
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

log = logging.getLogger("agent.claims")

# Numerals that are never a claim about the client.
_ALLOWED_BARE = re.compile(
    r"^(one|two|three|four|five|six|seven|eight|nine|ten|first|second|third)$", re.I)

# Numbers appearing in these shapes are structural, not claims.
_STRUCTURAL = re.compile(
    r"\b(20\d\d|"                       # years
    r"h[1-6]|"                          # heading refs
    r"\d+\s*(px|rem|em|%\s*width))\b", re.I)

# A numeral with optional unit/suffix.
_NUMBER = re.compile(
    r"(?<![\w./-])(\d[\d,]*(?:\.\d+)?)\s*"
    r"(%|ms|s\b|k\b|m\b|x\b|kw\b|gb\b|mb\b|hours?|days?|weeks?|months?|years?)?", re.I)

# ── Word-numbers ──
#
# The gap that let the one real falsehood through. `_NUMBER` only matches digits,
# so "took six weeks from initial prototype to delivery" — an invented delivery
# timeline for a real client — was never even considered, and the run reported
# "0 numeral(s) traced".
#
# Only DURATION and TEAM-SIZE units are matched, deliberately. "six platforms" and
# "four game modes" are countable facts the surrounding prose establishes; "six
# weeks" and "three engineers" are commercial claims about an engagement that a
# prospect will quote back. The units are the discriminator, not the number.
# Vague quantifiers are deliberately ABSENT. "a few hours of reading ten reports"
# describes the problem being solved, not a commitment, and nobody quotes it back
# as one — it flagged Cyber Agent's own study. The danger is a SPECIFIC invented
# figure, so precision is a discriminator alongside the unit.
#
# Singular is excluded too: "one engineer could maintain this" is a
# capability statement in ordinary English, not a claim that one engineer
# was staffed. Invented engagement facts are plural — "six weeks",
# "three engineers".
_WORD_NUM = re.compile(
    r"\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+"
    r"(week|month|day|hour|year|sprint|engineer|developer|designer|person|people|"
    r"headcount|fte)s?\b", re.I)

# Markdown links are stripped before scanning. A link to a real post titled
# "idea to MVP in six weeks" is a citation, not a claim about this engagement —
# it flagged SolarSathi's study for linking to the blog.
_MD_LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")

# TypeScript comments — see the note in status.py. Registry entries carry the
# reasoning beside the data, and the reasoning is not a claim.
_TS_COMMENT = re.compile(r"//.*|/\*[\s\S]*?\*/")

# Structural field values in a registry entry. `testimonialId: 13` is a foreign
# key, not a claim about anything; dates are metadata. Scanning them reports the
# entry's own plumbing as invented statistics.
_ID_FIELD = re.compile(
    r"\b(testimonialId|published|updated|width|height|x|y)\s*:\s*'?[\d-]+'?", re.I)

_FENCE = re.compile(r"```.*?```", re.S)

# Self-closing JSX blocks. These MUST be stripped before scanning, and the reason
# is not obvious until you see it fail: an <Annotated> component carries pin
# coordinates as `{ x: 26, y: 30, … }`. Those are layout percentages, and a scanner
# that reads them as claims reports six untraceable "numbers" per study and blocks
# every single one. Caught by running this validator against the seven hand-written
# specimens — which is exactly what that self-test exists for.
_COMPONENT = re.compile(r"<[A-Z]\w*[\s\S]*?/>", re.S)


@dataclass
class ClaimFinding:
    value: str
    context: str


@dataclass
class ClaimReport:
    findings: list[ClaimFinding] = field(default_factory=list)
    checked: int = 0

    @property
    def clean(self) -> bool:
        return not self.findings

    def render(self) -> str:
        if self.clean:
            return f"claims: PASS ({self.checked} numeral(s) traced)"
        lines = [f"claims: {len(self.findings)} untraceable number(s) — ABORT"]
        for f in self.findings:
            lines.append(f"  {f.value!r}\n      {f.context}")
        return "\n".join(lines)


def _evidence(project_metrics: list[str], brief_safe: str, project_desc: str) -> str:
    """Everything a number is allowed to have come from, lowercased."""
    return " \n ".join([*project_metrics, brief_safe, project_desc]).lower()


def scan(
    body_mdx: str,
    *,
    project_metrics: list[str],
    brief_safe: str,
    project_description: str = "",
) -> ClaimReport:
    report = ClaimReport()
    evidence = _evidence(project_metrics, brief_safe, project_description)
    text = _ID_FIELD.sub(" ", _TS_COMMENT.sub(" ", _MD_LINK.sub(" ", _COMPONENT.sub(" ", _FENCE.sub(" ", body_mdx)))))

    for m in _NUMBER.finditer(text):
        raw, unit = m.group(1), (m.group(2) or "")
        token = f"{raw}{unit}".strip()

        if _ALLOWED_BARE.match(raw) or _STRUCTURAL.search(m.group(0)):
            continue
        # Small counts used narratively ("three AI services", "ten tools") are
        # verifiable from the prose around them and are not client metrics.
        digits = raw.replace(",", "")
        if digits.isdigit() and int(digits) <= 12 and not unit:
            continue

        report.checked += 1

        # The number, with or without its unit, must appear in the evidence.
        if digits in evidence or token.lower() in evidence or raw.lower() in evidence:
            continue

        lo = max(0, m.start() - 60)
        report.findings.append(ClaimFinding(
            value=token,
            context=text[lo: m.end() + 60].replace("\n", " ").strip(),
        ))

    # ── Word-numbers with a duration or team unit ──
    for m in _WORD_NUM.finditer(text):
        phrase = m.group(0)
        report.checked += 1
        if phrase.lower() in evidence:
            continue
        lo = max(0, m.start() - 60)
        report.findings.append(ClaimFinding(
            value=phrase,
            context=" ".join(text[lo: m.end() + 60].split()),
        ))

    if report.findings:
        # Log WHICH numbers, not just how many. A bare count leaves you unable to
        # tell an invented statistic from a false positive without downloading a
        # build artefact — exactly the position this left a CI run in.
        log.error("claims: %d untraceable number(s):", len(report.findings))
        for f in report.findings:
            log.error("  %r — …%s…", f.value, f.context[:110])

    return report
