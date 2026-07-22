"""Which project gets written next.

DETERMINISTIC. No LLM.

The blog agent needs an LLM topic strategist because its subject space is open and
infinite. This one's is closed: thirty known projects, already enumerated. Asking a
model "which should we write about" would add nondeterminism and zero value when
the answer is computable from coverage gaps and a few business facts.

That is the same lesson `pick_focus()` encodes upstream — the fix for convergence
was to stop asking an open question, not to phrase it better.

Scoring, highest first:

    +3.0  category coverage gap    (fewest published studies in its category wins)
    +2.5  industry coverage gap    (11 industries, mostly uncovered)
    +2.0  a testimonial exists     (the trust cascade is available)
    +1.5  featured project
    +1.0  feeds an under-served service page
    -3.0  archetype used by either of the last two studies

`has_brief` is NOT a score — it is a hard gate. A project without a clean brief is
never selected, because the alternative is an agent inventing the facts the brief
would have supplied.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from casestudy.corpus import Corpus, Project, load_brief

log = logging.getLogger("agent.queue")

# Project category → the study archetype it will use. The selector needs this to
# apply archetype rotation before the planner has run.
CATEGORY_ARCHETYPE = {
    "mobile": "product_build",
    "web": "product_build",
    "ai": "ai_system",
    "game": "game",
    "product": "own_product",
}

# Category → the service page a study under it feeds.
CATEGORY_SERVICE = {
    "mobile": "mobile",
    "game": "mobile",
    "web": "web",
    "ai": "ai",
    "product": "ai",
}


@dataclass
class Candidate:
    project: Project
    score: float
    archetype: str
    reasons: list[str]
    blocked_reason: str = ""

    @property
    def eligible(self) -> bool:
        return not self.blocked_reason


def _archetype_for(project: Project, corpus: Corpus) -> str:
    if project.is_product:
        return "own_product"
    # A few projects need a shape their category does not imply.
    if project.id in ("solarsathi", "3d-model-viewer"):
        return "marketplace"
    if project.id == "nullzec":
        return "platform_frontend"
    if project.id == "coffee-delivery":
        return "design_only"
    return CATEGORY_ARCHETYPE.get(project.category, "product_build")


def _recent_archetypes(corpus: Corpus, lookback: int = 2) -> list[str]:
    """Archetypes of the most recently written studies.

    studies.ts is append-ordered, and corpus preserves that, so the LAST entries
    are the newest. Rotation stops three consecutive studies sharing a shape,
    which is the same failure the blog agent hit with four cost-breakdowns.
    """
    slugs = list(corpus.study_archetypes.keys())
    return [corpus.study_archetypes[s] for s in slugs[-lookback:]]


def rank(corpus: Corpus) -> list[Candidate]:
    written = corpus.written_slugs
    recent = _recent_archetypes(corpus)

    # Coverage counts, computed once.
    cat_counts: dict[str, int] = {}
    ind_counts: dict[str, int] = {}
    svc_counts: dict[str, int] = {}
    for p in corpus.projects:
        if p.slug not in written:
            continue
        cat_counts[p.category] = cat_counts.get(p.category, 0) + 1
        if p.industry:
            ind_counts[p.industry] = ind_counts.get(p.industry, 0) + 1
        svc = CATEGORY_SERVICE.get(p.category, "web")
        svc_counts[svc] = svc_counts.get(svc, 0) + 1

    out: list[Candidate] = []
    for p in corpus.projects:
        if p.slug in written:
            continue

        archetype = _archetype_for(p, corpus)
        reasons: list[str] = []
        score = 0.0

        cat_n = cat_counts.get(p.category, 0)
        score += 3.0 / (1 + cat_n)
        reasons.append(f"category {p.category} has {cat_n} study(s)")

        if p.industry:
            ind_n = ind_counts.get(p.industry, 0)
            score += 2.5 / (1 + ind_n)
            reasons.append(f"industry {p.industry} has {ind_n}")

        has_quote = (p.client.lower(), p.client_country.lower()) in corpus.testimonial_by_client
        if has_quote:
            score += 2.0
            reasons.append("testimonial available")

        if p.featured:
            score += 1.5
            reasons.append("featured")

        svc = CATEGORY_SERVICE.get(p.category, "web")
        svc_n = svc_counts.get(svc, 0)
        score += 1.0 / (1 + svc_n)
        reasons.append(f"/services/{svc} has {svc_n}")

        if archetype in recent:
            score -= 3.0
            reasons.append(f"archetype {archetype} used recently")

        # ── Hard gate ──
        brief = load_brief(p.id)
        blocked = ""
        if not brief.exists:
            blocked = f"no brief at briefs/{p.id}.md"
        elif brief.needs_review:
            blocked = f"brief has {brief.needs_review} unresolved [NEEDS REVIEW] marker(s)"

        out.append(Candidate(
            project=p, score=round(score, 3), archetype=archetype,
            reasons=reasons, blocked_reason=blocked,
        ))

    out.sort(key=lambda c: (-c.score, c.project.id))
    return out


def select_next(corpus: Corpus) -> Candidate | None:
    """The highest-scoring project with a clean brief, or None."""
    ranked = rank(corpus)
    if not ranked:
        log.info("queue: every project already has a study")
        return None

    log.info("queue: %d project(s) awaiting a study", len(ranked))
    for c in ranked[:8]:
        mark = "  " if c.eligible else "x "
        log.info("  %s%-24s %5.2f  %-18s %s", mark, c.project.id, c.score,
                 c.archetype, c.blocked_reason or "; ".join(c.reasons[:2]))

    chosen = next((c for c in ranked if c.eligible), None)
    if chosen is None:
        log.warning(
            "queue: no project has a clean brief. Draft one with "
            "`python -m casestudy.brief <project-id>`, clear its [NEEDS REVIEW] "
            "markers, and re-run.")
        return None

    log.info("queue: selected %s (%s, score %.2f)",
             chosen.project.id, chosen.archetype, chosen.score)
    return chosen
