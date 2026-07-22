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

import re
from dataclasses import dataclass, field

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
    text = _COMPONENT.sub(" ", _FENCE.sub(" ", body_mdx))

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

    return report
