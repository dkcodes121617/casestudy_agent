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
# `\s*` between the fields, not a space: the agent emits each pair on one line and
# the hand-built specimens are pretty-printed across four. Both are the same object,
# and a regex that only matched the agent's formatting would report "faq has 0
# questions" on every study a human wrote — which is exactly what it did first try.
_FAQ_ITEM = re.compile(
    r"\{\s*q:\s*'((?:[^'\\]|\\.)*)'\s*,\s*a:\s*'((?:[^'\\]|\\.)*)'\s*,?\s*\}")

# The prompt asks for 3-4 and nothing checked it, so a model that returned one
# question shipped a one-question FAQ. Below 3 the section is not worth the
# heading; above 5 it stops being the questions a buyer actually asks and starts
# being padding. Both ends are errors because both are cheap to regenerate.
_FAQ_MIN, _FAQ_MAX = 3, 5

# An answer that fits in a line is not an answer. This is the floor a passage
# needs to stand alone once an answer engine lifts it out of the page.
_FAQ_MIN_ANSWER = 120

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
    project_description: str = "",
) -> EntryReport:
    r = EntryReport()

    # PER-SOURCE evidence, not one pooled bucket.
    #
    # Pooling made the `source` label decorative: a value that lived only in the
    # brief satisfied a metric labelled source: 'projects.ts', so the field said
    # "verify this in projects.ts" about a number that is not in projects.ts.
    # MindMaze Junior shipped exactly that — `metrics: []` in projects.ts, and a
    # metric claiming it as the source.
    #
    # That is the same failure as the enforcement this module was written to fix:
    # a provenance claim nobody checks is worse than no claim, because it stops
    # the next person looking. So each label is now checked against ITS OWN source.
    #
    # `description` counts as projects.ts because it literally is projects.ts —
    # "Four game modes" is in that field, and metrics[] is often empty by design.
    by_source = {
        "projects.ts": (" ".join(project_metrics) + " " + project_description).lower(),
        "brief": brief_evidence.lower(),
    }

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
        elif source in by_source:
            evidence = by_source[source]
            digits = re.sub(r"[^\d.]", "", value)
            word = _WORDS.get(digits.rstrip("."))
            traced = (
                (digits and digits in evidence)
                or value.lower() in evidence
                or (word is not None and word in evidence)
            )
            if digits and not traced:
                other = next((k for k, v in by_source.items()
                              if k != source and (digits in v or (word and word in v))), None)
                fix = (f"relabel it source '{other}'" if other
                       else "cite a real figure or use source 'qualitative'")
                r.errors.append(
                    f"metric '{value}' claims source '{source}' but that value does not "
                    f"appear there — {fix}")
        else:
            r.errors.append(f"metric '{value}' has unknown source '{source}'")

    # ── The link graph must not be empty ──
    # `_related_posts` and `_related_studies` always return something, so an empty
    # array can only mean the entry was written before they existed — which is
    # exactly how mindmaze-junior published with both rails blank and nothing
    # noticed for eight studies. A study with no outbound links is a leaf node in
    # a graph whose whole purpose is that it has none.
    for field_name in ("relatedPosts", "relatedStudies"):
        m = re.search(rf"\b{field_name}:\s*\[([^\]]*)\]", entry)
        if m is None:
            r.errors.append(f"entry has no `{field_name}` field")
        elif not m.group(1).strip():
            r.errors.append(
                f"{field_name} is empty — every study links out to at least one "
                f"sibling page, or it is a dead end for readers and crawlers alike")

    # ── FAQ shape ──
    faq = _FAQ_ITEM.findall(entry)
    if not _FAQ_MIN <= len(faq) <= _FAQ_MAX:
        r.errors.append(
            f"faq has {len(faq)} question(s) — needs {_FAQ_MIN}-{_FAQ_MAX}")
    for q, a in faq:
        if not q.rstrip().endswith("?"):
            r.errors.append(f"faq question is not a question: {q!r}")
        if len(a) < _FAQ_MIN_ANSWER:
            r.errors.append(
                f"faq answer to {q!r} is {len(a)} chars — too short to be quoted "
                f"on its own, which is the only thing this section is for")
    seen = {q.strip().lower() for q, _ in faq}
    if len(seen) != len(faq):
        r.errors.append("faq repeats a question")

    # ── glance fields must stand alone ──
    for name, value in _GLANCE_FIELD.findall(entry):
        if _PRONOUN_START.match(value):
            r.errors.append(
                f"glance.{name} opens with a pronoun — each field must survive being "
                f"read with no surrounding context, so name {project_name} explicitly")
        if project_name.split()[0].lower() not in value.lower() and len(value) > 80:
            r.warnings.append(f"glance.{name} never names the project")

    return r
