"""Validate the TYPED REGISTRY ENTRY, not just the MDX body.

── The gap this closes ──

Every gate ran against `body` only. `_render_registry_entry()` executed afterwards
and its output went straight to git. So everything that lives in the registry —
metrics, the seven glance fields, the FAQ, hero.mockup, seo — was published
completely unchecked.

That is not theoretical. It shipped this, live, in a FAQ answer:

    "MindMaze Junior took six weeks from initial prototype to delivery…"

No `duration` field on that study. No timeline in the brief — the brief explicitly
flagged "[NEEDS REVIEW] Any REAL number we may cite? … timeline" and none was
supplied. The agent invented a delivery timeline for a real client, and the run
reported `claims: PASS (0 numeral(s) traced)`, because the claims validator never
saw the FAQ.

Worse, `studies.ts` documented several of these as enforced —

    "the validator rejects a metric whose source is 'projects.ts' but whose value
     does not appear in that project's metrics[]"

— and no validator had ever read `source`. A confident comment asserting an
enforcement that does not exist is worse than no comment: it stops anyone looking.

── What this does ──

The entry is a TypeScript object literal, i.e. a string. `claims.scan` and
`statusv.scan` already take text, so they are simply run over it as well. This
module adds the checks that are specific to the entry's structure.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

log = logging.getLogger("agent.entry")

# Leading pronouns forbidden at the start of a glance field. Each value has to
# survive being lifted out of the page with zero surrounding context, which a
# sentence opening "It handles…" cannot.
_PRONOUN_START = re.compile(
    r"^\s*(it|they|this|that|these|those|we|the (app|platform|system|product|tool))\b", re.I)

_METRIC = re.compile(r"\{[^{}]*\bvalue:\s*'([^']*)'[^{}]*\bsource:\s*'([^']*)'[^{}]*\}")
_GLANCE_FIELD = re.compile(
    r"\b(businessProblem|technicalChallenges|engineeringSolution|businessValue):\s*\n?\s*'((?:[^'\\]|\\.)*)'")
_HAS_DIGIT = re.compile(r"\d")

# Evidence spells numbers as words far more often than a metric does. projects.ts
# says "Four game modes"; the metric says value: '4'. Without this the check
# rejects a perfectly traceable figure for being written in digits.
_WORDS = {
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
    "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten",
    "11": "eleven", "12": "twelve",
}


@dataclass
class EntryReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def render(self) -> str:
        if self.ok and not self.warnings:
            return "entry: PASS"
        lines = []
        if self.errors:
            lines.append(f"entry: {len(self.errors)} error(s)")
            lines += [f"  ✗ {e}" for e in self.errors]
        if self.warnings:
            lines += [f"  ! {w}" for w in self.warnings]
        return "\n".join(lines)


def validate(
    entry: str,
    *,
    project_metrics: list[str],
    brief_evidence: str,
    valid_mockups: set[str],
    project_name: str,
) -> EntryReport:
    r = EntryReport()
    evidence = (" ".join(project_metrics) + " " + brief_evidence).lower()

    # ── hero.mockup must resolve ──
    # 'REVIEW-ME' is not a registry key. MockupSlot returns null on an unknown
    # key, so this publishes a study whose hero silently renders text-only — which
    # is exactly what happened to the first study that reached production.
    m = re.search(r"mockup:\s*'([^']*)'", entry)
    if not m:
        r.errors.append("hero has no `mockup` key")
    elif m.group(1) not in valid_mockups:
        r.errors.append(
            f"hero.mockup '{m.group(1)}' is not a valid key for this project "
            f"(valid: {sorted(valid_mockups) or 'none — a mockup must be built first'})")

    # ── metric `source` traceability ──
    # The rule studies.ts claimed was enforced, finally enforced.
    for value, source in _METRIC.findall(entry):
        if source == "qualitative":
            if _HAS_DIGIT.search(value):
                r.errors.append(
                    f"metric '{value}' is marked source 'qualitative' but contains a "
                    f"numeral — qualitative means no figure at all")
        elif source in ("projects.ts", "brief"):
            digits = re.sub(r"[^\d.]", "", value)
            word = _WORDS.get(digits.rstrip("."))
            traced = (
                (digits and digits in evidence)
                or value.lower() in evidence
                or (word is not None and word in evidence)
            )
            if digits and not traced:
                r.errors.append(
                    f"metric '{value}' claims source '{source}' but that value does not "
                    f"appear there — cite a real figure or use source 'qualitative'")
        else:
            r.errors.append(f"metric '{value}' has unknown source '{source}'")

    # ── glance fields must stand alone ──
    for name, value in _GLANCE_FIELD.findall(entry):
        if _PRONOUN_START.match(value):
            r.errors.append(
                f"glance.{name} opens with a pronoun — each field must survive being "
                f"read with no surrounding context, so name {project_name} explicitly")
        if project_name.split()[0].lower() not in value.lower() and len(value) > 80:
            r.warnings.append(f"glance.{name} never names the project")

    return r
