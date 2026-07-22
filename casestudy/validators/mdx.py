"""The case study MDX + spec contract.

Mirrors the site's kit exactly. Deterministic, instant, and — following the blog
agent's ordering lesson — it runs BEFORE any LLM check, so a malformed draft never
spends an API call.

The section plan below must match SECTION_PLAN in the site's
src/content/case-studies/studies.ts. Both are the same contract; if they disagree
the study renders with headings the layout's rail cannot find.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# ── Sections owned by the MDX body (the typed ones render from the registry) ──
SECTION_PLAN: dict[str, list[str]] = {
    "product_build":     ["problem", "constraints", "build", "tour", "shipped", "decisions"],
    "ai_system":         ["problem", "constraints", "build", "tour", "shipped", "decisions"],
    "platform_frontend": ["problem", "constraints", "build", "tour", "shipped"],
    "marketplace":       ["problem", "constraints", "build", "tour", "shipped", "decisions"],
    "game":              ["problem", "constraints", "build", "tour", "shipped"],
    "design_only":       ["problem", "constraints", "tour"],
    "own_product":       ["problem", "constraints", "build", "tour", "shipped", "decisions"],
}

SECTION_HEADING = {
    "problem": "The problem",
    "constraints": "The constraints",
    "build": "How we built it",
    "tour": "Inside the product",
    "shipped": "What shipped",
    "decisions": "The decisions that mattered",
}

HIDE_STATUS_HEADING = {"shipped": "What we built"}

ARCHETYPE_HEADING = {
    "ai_system": {"tour": "Pipeline in motion"},
    "design_only": {"tour": "From flows to screens"},
    "game": {"tour": "The gameplay loop"},
    "platform_frontend": {"constraints": "Scope and boundaries"},
    "own_product": {"problem": "Why we built this"},
}

# Components the case study MDX may use. Superset of the blog kit plus the two
# case-study-only ones.
ALLOWED_COMPONENTS = {
    "KeyTakeaways", "Callout", "FlowDiagram", "CompareDiagram", "BarChart", "Figure",
    "FAQ", "BlogCTA", "StatGrid", "Timeline", "DecisionTree", "ConceptDiagram",
    "QuadrantMap", "ArchitectureDiagram", "Annotated",
}

VALID_SERVICE_SLUGS = {"web", "mobile", "ai"}
# Scaled by section count, not a flat number. A `game` study has five sections and
# a `design_only` one has three; holding all of them to a six-section floor rejects
# a complete study for being complete. ~115 words/section is the floor, against a
# 130-220 word target per section — enough headroom that a tight-but-finished study
# passes and a padded one still fails.
MIN_WORDS_PER_SECTION = 115
MAX_WORDS = 2000


def section_heading(section: str, *, archetype: str, hide_status: bool) -> str:
    """Resolve one section's heading. hideStatus beats archetype: naming is style,
    a status claim is truth."""
    if hide_status and section in HIDE_STATUS_HEADING:
        return HIDE_STATUS_HEADING[section]
    return ARCHETYPE_HEADING.get(archetype, {}).get(section, SECTION_HEADING[section])


def expected_headings(archetype: str, hide_status: bool) -> list[str]:
    return [
        section_heading(s, archetype=archetype, hide_status=hide_status)
        for s in SECTION_PLAN.get(archetype, SECTION_PLAN["product_build"])
    ]


@dataclass
class MdxReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def render(self) -> str:
        if self.ok and not self.warnings:
            return "mdx: PASS"
        lines = []
        if self.errors:
            lines.append(f"mdx: {len(self.errors)} error(s)")
            lines += [f"  ✗ {e}" for e in self.errors]
        if self.warnings:
            lines += [f"  ! {w}" for w in self.warnings]
        return "\n".join(lines)


def word_count(mdx: str) -> int:
    text = re.sub(r"```.*?```", " ", mdx, flags=re.S)
    text = re.sub(r"</?[A-Z]\w+", " ", text)
    text = re.sub(r"[<>{}\[\]/=]", " ", text)
    text = re.sub(r"\b\w+=", " ", text)
    return len(re.findall(r"[A-Za-z0-9']+", text))


def validate(
    body_mdx: str,
    *,
    archetype: str,
    hide_status: bool,
    slug: str,
    known_blog_slugs: set[str],
    known_study_slugs: set[str],
    mockup_keys: set[str],
) -> MdxReport:
    r = MdxReport()
    text = body_mdx.strip()

    if not text:
        r.errors.append("body is empty")
        return r

    if text.startswith("---"):
        r.errors.append("body must not start with YAML frontmatter")
    if re.search(r"^#\s+\S", text, re.M):
        r.errors.append("body must not contain an H1 — the layout renders the title")

    # ── Section contract, both directions ──
    actual = [m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", text, re.M)]
    expected = expected_headings(archetype, hide_status)
    for want in expected:
        if want not in actual:
            r.errors.append(f'missing required section "## {want}" for archetype {archetype}')
    for got in actual:
        if got not in expected:
            r.errors.append(
                f'unplanned section "## {got}" — archetype {archetype} defines '
                f'{len(expected)} sections and this is not one of them')
    if actual and actual != [h for h in expected if h in actual]:
        r.warnings.append("sections are out of plan order")

    # ── Components ──
    for tag in set(re.findall(r"<([A-Z]\w+)", text)):
        if tag not in ALLOWED_COMPONENTS:
            r.errors.append(f"unknown component <{tag}> — not registered in mdx-components.tsx")

    # The architecture diagram is the study's signature visual and must reference
    # THIS study, so it reads glance.architecture from the right registry entry.
    if "build" in SECTION_PLAN.get(archetype, []):
        arch = re.search(r'<ArchitectureDiagram[^>]*?study="([^"]+)"', text, re.S)
        if not arch:
            r.errors.append("missing <ArchitectureDiagram study=\"…\" /> in the build section")
        elif arch.group(1) != slug:
            r.errors.append(
                f'<ArchitectureDiagram study="{arch.group(1)}" /> points at another study '
                f'(expected "{slug}")')

    # At least one product mockup: an abstract diagram does not show a product.
    mockups = re.findall(r'<Annotated[^>]*?mockup="([^"]+)"', text, re.S)
    if not mockups:
        r.warnings.append("no <Annotated> mockup — the product tour has no visual")
    for key in mockups:
        if key not in mockup_keys:
            r.errors.append(f'unknown mockup key "{key}" — not in the mockup registry')

    # ── Length ──
    words = word_count(text)
    floor = MIN_WORDS_PER_SECTION * len(expected)
    if words < floor:
        r.errors.append(
            f"{words} words across {len(expected)} sections — thin, minimum {floor}")
    elif words > MAX_WORDS:
        r.warnings.append(f"{words} words — long, consider tightening")

    # ── Internal links ──
    links = re.findall(r"\]\((/[^)]*)\)", text)
    services = [l for l in links if l.startswith("/services/")]
    blogs = [l for l in links if l.startswith("/blog/")]
    works = [l for l in links if l.startswith("/work/")]

    if not services:
        r.errors.append("no /services/* link — a study must feed its service page")
    for l in services:
        m = re.match(r"^/services/([a-z]+)", l)
        if m and m.group(1) not in VALID_SERVICE_SLUGS:
            r.errors.append(f"invalid service link {l} (valid: web|mobile|ai)")
    if not blogs:
        r.errors.append("no /blog/* link — a study must join the topic cluster")
    for l in blogs:
        m = re.match(r"^/blog/([a-z0-9-]+)$", l)
        if m and m.group(1) not in known_blog_slugs:
            r.errors.append(f"blog link {l} points at a slug not in the registry")
    for l in works:
        m = re.match(r"^/work/([a-z0-9-]+)$", l)
        if m and m.group(1) == slug:
            r.errors.append(f"self-link {l}")
        elif m and m.group(1) not in known_study_slugs:
            r.warnings.append(f"work link {l} has no written study yet")

    # ── MDX gotchas ──
    for i, line in enumerate(text.splitlines(), start=1):
        s = line.strip()
        if s.startswith("<") or s.startswith("{") or s.startswith("|"):
            continue
        if re.match(r"^\s*\|.+\|\s*$", line):
            r.errors.append(f"line {i}: markdown table not allowed (no GFM plugin)")
        if re.search(r"<(?![A-Za-z/])", line):
            r.errors.append(f"line {i}: raw '<' in prose — MDX reads it as JSX")

    return r
