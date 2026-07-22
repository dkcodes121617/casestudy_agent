"""Read the real corpus out of the site repo.

Same tolerant-regex approach as the blog agent's facts/snapshot.py: never execute
TS, pull durable fields, survive a formatting change rather than crashing on one.

This module answers four questions the selector and the writer both need:
  - which projects exist, and what do we know about each (projects.ts + products.ts)
  - which already have a written study (studies.ts)
  - which have a testimonial we can join (testimonials.ts)
  - which briefs exist, and are any blocked by [NEEDS REVIEW]
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from core.config import CONFIG

NEEDS_REVIEW = "[NEEDS REVIEW]"


@dataclass
class Project:
    id: str = ""
    name: str = ""
    category: str = ""
    industry: str = ""
    client: str = ""
    client_country: str = ""
    description: str = ""
    tech: list[str] = field(default_factory=list)
    slug: str = ""
    hide_status: bool = False
    featured: bool = False
    is_product: bool = False
    metrics: list[str] = field(default_factory=list)


@dataclass
class Corpus:
    projects: list[Project] = field(default_factory=list)
    written_slugs: set[str] = field(default_factory=set)
    study_archetypes: dict[str, str] = field(default_factory=dict)
    testimonial_by_client: dict[tuple[str, str], int] = field(default_factory=dict)
    blog_slugs: list[str] = field(default_factory=list)

    def project(self, pid: str) -> Project | None:
        return next((p for p in self.projects if p.id == pid), None)


def _read(site_dir: Path, rel: str) -> str:
    p = site_dir / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def _f(text: str, key: str) -> str:
    m = re.search(rf"\b{key}:\s*'([^']*)'", text)
    return m.group(1) if m else ""


def _list(text: str, key: str) -> list[str]:
    m = re.search(rf"\b{key}:\s*\[([^\]]*)\]", text)
    if not m:
        return []
    return [t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()]


def _parse_projects(src: str, *, is_product: bool) -> list[Project]:
    out: list[Project] = []
    for block in re.finditer(r"\{[^{}]*?\bid:\s*'[^']+'[^{}]*?\}", src, re.DOTALL):
        t = block.group(0)
        pid = _f(t, "id")
        name = _f(t, "name")
        if not pid or not name:
            continue
        out.append(Project(
            id=pid,
            name=name,
            category="product" if is_product else _f(t, "category"),
            industry=_f(t, "industry"),
            client=_f(t, "client"),
            client_country=_f(t, "clientCountry"),
            description=_f(t, "description"),
            tech=_list(t, "tech"),
            # projects.ts derives `slug: p.slug ?? p.id` at runtime; mirror that.
            slug=_f(t, "slug") or pid,
            hide_status="hideStatus: true" in t,
            featured="featured: true" in t,
            is_product=is_product,
            metrics=_list(t, "metrics"),
        ))
    return out


def _parse_written(studies_ts: str) -> tuple[set[str], dict[str, str]]:
    """Slugs already written, and each one's archetype (for rotation)."""
    start = studies_ts.find("export const studies")
    if start == -1:
        return set(), {}
    region = studies_ts[start:]
    marks = [(m.group(1), m.start()) for m in re.finditer(r"\bslug:\s*'([^']+)'", region)]
    slugs: set[str] = set()
    archetypes: dict[str, str] = {}
    for i, (slug, at) in enumerate(marks):
        chunk = region[at: marks[i + 1][1] if i + 1 < len(marks) else len(region)]
        if re.search(r"\bdraft:\s*true", chunk):
            continue
        slugs.add(slug)
        a = re.search(r"\barchetype:\s*'([^']+)'", chunk)
        if a:
            archetypes[slug] = a.group(1)
    return slugs, archetypes


def _parse_testimonials(src: str) -> dict[tuple[str, str], int]:
    """(name, country) -> id. The join key onto a project's client + country."""
    out: dict[tuple[str, str], int] = {}
    for block in re.finditer(r"\{[^{}]*?\bid:\s*(\d+)[^{}]*?\}", src, re.DOTALL):
        t = block.group(0)
        name, country = _f(t, "name"), _f(t, "country")
        if not name or not country:
            continue
        # Later entries win: where a client left two messages, the later one is
        # usually the more specific (Jodie Wayatt's second names her projects).
        out[(name.lower(), country.lower())] = int(block.group(1))
    return out


def load_corpus(site_dir: Path | str | None = None) -> Corpus:
    site_dir = Path(site_dir) if site_dir else _resolve_site_dir()

    projects = _parse_projects(_read(site_dir, CONFIG.projects_rel), is_product=False)
    projects += _parse_projects(_read(site_dir, CONFIG.products_rel), is_product=True)

    written, archetypes = _parse_written(_read(site_dir, CONFIG.studies_registry_rel))
    testimonials = _parse_testimonials(_read(site_dir, CONFIG.testimonials_rel))

    posts = _read(site_dir, CONFIG.posts_registry_rel)
    blog_slugs = re.findall(r"\bslug:\s*'([^']+)'", posts)

    return Corpus(
        projects=projects,
        written_slugs=written,
        study_archetypes=archetypes,
        testimonial_by_client=testimonials,
        blog_slugs=blog_slugs,
    )


def _resolve_site_dir() -> Path:
    if (CONFIG.site_repo_dir / CONFIG.projects_rel).exists():
        return CONFIG.site_repo_dir
    return CONFIG.local_site_dir


# ── Briefs ──

@dataclass
class Brief:
    project_id: str
    path: Path
    exists: bool = False
    needs_review: int = 0
    confidential: list[str] = field(default_factory=list)
    safe: str = ""
    story: str = ""
    # The "## Metrics — PROJECTED, not measured" section. Kept SEPARATE from
    # `safe` because the two do different jobs: both are evidence the claims
    # validator traces numbers against, but only this one carries figures whose
    # FRAMING is constrained (targets, never achieved results). Splitting them
    # means the writer prompt can treat them differently.
    metrics: str = ""

    @property
    def blocked(self) -> bool:
        """A brief with unresolved [NEEDS REVIEW] markers must not reach the writer."""
        return not self.exists or self.needs_review > 0


def _section(text: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}.*?$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def load_brief(project_id: str) -> Brief:
    path = CONFIG.briefs_dir / f"{project_id}.md"
    if not path.exists():
        return Brief(project_id=project_id, path=path, exists=False)

    text = path.read_text(encoding="utf-8", errors="replace")
    confidential_raw = _section(text, "Confidential")

    return Brief(
        project_id=project_id,
        path=path,
        exists=True,
        needs_review=text.count(NEEDS_REVIEW),
        # Every non-empty line of the confidential section becomes a denylist
        # entry. This section is NEVER shown to the writer — only to the scanner.
        confidential=[
            ln.strip(" -\t") for ln in confidential_raw.splitlines()
            if ln.strip(" -\t") and NEEDS_REVIEW not in ln
        ],
        safe=_section(text, "Safe to publish"),
        story=_section(text, "The story"),
        metrics=_section(text, "Metrics"),
    )
