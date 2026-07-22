"""Generate one case study, end to end.

── Why this is a sequential pipeline and not a LangGraph graph ──

The blog agent's graph earns its keep: it has five distinct loops (topic re-pick,
MDX rewrite, surgical claim fix, humanize, final uniqueness) with conditional edges
between them, and expressing that as straight-line code would be worse.

This pipeline has ONE loop — validate → rewrite — and everything else is a gate
that either passes or aborts the run. Wrapping that in a graph would add a
dependency and a layer of indirection to model control flow that `if` already
expresses. So `langgraph` is deliberately absent from requirements.txt.

The ordering below is the blog agent's hard-won lesson, applied:

    deterministic checks BEFORE any LLM call that could be wasted,
    and cheap checks before expensive ones.

So mdx validation (free, instant) runs before the confidentiality adjudicator (an
API call), and both run before anything is written to git.

Every gate is a HARD ABORT. There is no fix budget. The blog agent can ship a draft
with a remaining flag because its worst case is a slightly wrong sentence about the
industry; here the worst case is a breached client confidence, and "the model had
two attempts at removing it" is not a defence.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from casestudy.corpus import Corpus, load_brief
from casestudy.prompts import library as P
from casestudy.queue import Candidate
from casestudy.validators import claims, confidentiality, mdx as mdxv, status as statusv
from core.config import CONFIG
from core.llm.client import LLMClient, LLMError, LLMTransient
from core.llm.sanitize import sanitize_prose

log = logging.getLogger("agent.run")

MAX_REWRITES = 2


def _abort(reason: str, report: list[str], *, slug: str = "", body: str = "") -> dict:
    """Abort the run, and WRITE THE EVIDENCE.

    Originally this wrote nothing, so a failed run left no trace of the draft that
    failed or the finding that stopped it — one log line, and you had to re-run
    (and re-pay) to see anything. An abort is precisely when the artefact is most
    useful, so the report always lands and the rejected draft lands beside it as
    `<slug>.aborted.mdx`.

    Note the adjudicator and the writer are both non-deterministic: the same
    project can abort on one run and pass on the next because the draft differed.
    That is the guard working, not flapping — but it does mean the saved artefact
    is the only record of what the rejected draft actually said.
    """
    log.error("ABORT: %s", reason)
    full = "\n".join(report + [f"\nABORTED: {reason}"])
    if slug:
        try:
            CONFIG.output_dir.mkdir(parents=True, exist_ok=True)
            (CONFIG.output_dir / f"{slug}.report.txt").write_text(full, encoding="utf-8")
            if body:
                (CONFIG.output_dir / f"{slug}.aborted.mdx").write_text(body, encoding="utf-8")
        except OSError as e:
            log.warning("could not write abort artefacts: %s", e)
    return {"status": "aborted", "abort_reason": reason, "report": full}


def run_once(candidate: Candidate, corpus: Corpus, site_dir=None) -> dict:
    project = candidate.project
    archetype = candidate.archetype
    slug = project.slug
    report: list[str] = []

    brief = load_brief(project.id)
    if CONFIG.require_clean_brief and brief.blocked:
        return _abort(
            f"brief is blocked: {'missing' if not brief.exists else f'{brief.needs_review} [NEEDS REVIEW] marker(s)'}",
            report)

    # The writer sees "Safe to publish" and "The story". It NEVER sees
    # "## Confidential" — that goes only to the scanner, as a denylist. That
    # asymmetry is the mechanism that makes unattended generation safe.
    # The Metrics section keeps its heading, verbatim, so the persona's
    # projected-framing rule (STUDIO_PERSONA rule 3) has something to key off.
    brief_for_writer = "\n\n".join(x for x in (
        brief.safe,
        f"## Metrics — PROJECTED, not measured\n{brief.metrics}" if brief.metrics else "",
        brief.story,
    ) if x.strip()).strip()

    from core.facts.snapshot import build_snapshot
    facts = build_snapshot(site_dir).to_prompt_block()

    llm = LLMClient()
    pdict = {
        "name": project.name,
        "description": project.description,
        "hide_status": project.hide_status,
    }

    # ── 1. Plan (Opus) ──
    log.info("node: plan (%s, %s)", project.id, archetype)
    try:
        sys_p, usr_p = P.plan_prompt(facts, brief_for_writer, pdict, archetype)
        plan = llm.complete_json(system=sys_p, user=usr_p, max_tokens=1400,
                                 model=CONFIG.strategy_model)
    except (LLMError, LLMTransient) as e:
        return _abort(f"planning failed: {e}", report)

    # ── 2. Spec (Opus) → the typed registry fields ──
    log.info("node: spec")
    try:
        sys_s, usr_s = P.spec_prompt(facts, brief_for_writer, pdict, archetype, plan)
        spec = llm.complete_json(system=sys_s, user=usr_s, max_tokens=2200,
                                 model=CONFIG.strategy_model)
    except (LLMError, LLMTransient) as e:
        return _abort(f"spec derivation failed: {e}", report)

    # ── 3. Write, one call per section (Sonnet) ──
    sections = mdxv.SECTION_PLAN.get(archetype, mdxv.SECTION_PLAN["product_build"])
    body = ""
    feedback = ""

    for attempt in range(1, MAX_REWRITES + 2):
        log.info("node: write (attempt %d, %d sections)", attempt, len(sections))
        parts: list[str] = []
        for section in sections:
            heading = mdxv.section_heading(section, archetype=archetype,
                                           hide_status=project.hide_status)
            extras = _section_extras(
                section, slug, plan, corpus,
                is_last=(section == sections[-1]),
                mockups=sorted(_mockup_keys(site_dir, project_id=project.id)),
            )
            sys_w, usr_w = P.section_prompt(facts, brief_for_writer, pdict, archetype,
                                            plan, section, heading, extras)
            if feedback:
                usr_w += "\n\nFix these problems from the last draft:\n" + feedback
            try:
                raw = llm.complete(system=sys_w, user=usr_w, max_tokens=1200, temperature=0.75)
            except (LLMError, LLMTransient) as e:
                return _abort(f"section '{section}' failed: {e}", report)
            parts.append(sanitize_prose(raw))

        body = "\n\n".join(p.strip() for p in parts if p.strip())

        # ── 4. MDX contract (deterministic, free — runs before any paid check) ──
        r = mdxv.validate(
            body, archetype=archetype, hide_status=project.hide_status, slug=slug,
            known_blog_slugs=set(corpus.blog_slugs),
            known_study_slugs=corpus.written_slugs,
            mockup_keys=_mockup_keys(site_dir),
        )
        if r.ok:
            report.append(r.render())
            break
        log.warning("mdx validation failed (attempt %d):\n%s", attempt, r.render())
        feedback = "\n".join(r.errors)
    else:
        return _abort("could not produce contract-valid MDX within the rewrite budget",
                      report + [r.render()], slug=slug, body=body)

    # ── 5. Status guard (deterministic) ──
    sr = statusv.scan(body, hide_status=project.hide_status)
    report.append(sr.render())
    if not sr.clean:
        return _abort("release claims on a hideStatus study", report + [sr.render()], slug=slug, body=body)

    # ── 6. Claims traceability (deterministic) ──
    # Evidence = "Safe to publish" AND "Metrics". Both are legitimate sources for
    # traceability; the PROJECTED framing constraint on the metrics figures is
    # enforced by the writer prompt, not by hiding them from the validator.
    cr = claims.scan(body, project_metrics=project.metrics,
                     brief_safe=brief.safe + "\n" + brief.metrics,
                     project_description=project.description)
    report.append(cr.render())
    if not cr.clean:
        return _abort("untraceable numbers in the draft", report + [cr.render()], slug=slug, body=body)

    # ── 7. Confidentiality: patterns + denylist, then the adjudicator ──
    spec_text = json.dumps(spec, ensure_ascii=False)
    conf = confidentiality.scan(body, spec_text=spec_text, denylist=brief.confidential)
    if not conf.clean:
        report.append(conf.render())
        return _abort("confidentiality scan failed", report, slug=slug, body=body)

    try:
        sys_a, usr_a = confidentiality.adjudicator_prompt(body, project.client, project.name)
        verdict = llm.complete_json(system=sys_a, user=usr_a, max_tokens=900)
        concerns = verdict.get("concerns", []) if isinstance(verdict, dict) else []
    except (LLMError, LLMTransient) as e:
        # A failed adjudicator is NOT a pass. The deterministic layer is the floor,
        # not the ceiling, and a case study should not ship on a skipped check.
        return _abort(f"confidentiality adjudicator unavailable: {e}", report)

    if concerns:
        report.append(f"confidentiality adjudicator raised {len(concerns)} concern(s):")
        for c in concerns:
            report.append(f"  - {c.get('quote', '')!r}: {c.get('why', '')}")
        return _abort("confidentiality adjudicator raised concerns", report, slug=slug, body=body)
    report.append("confidentiality: PASS (patterns, denylist and adjudicator)")

    # ── 8. Assemble ──
    state = {
        "status": "ready",
        "slug": slug,
        "project_name": project.name,
        "archetype": archetype,
        "body_mdx": body,
        "spec": spec,
        "plan": plan,
        "registry_entry": _render_registry_entry(project, archetype, plan, spec, corpus),
        "report": "\n".join(report),
    }

    _write_output(state)

    if CONFIG.dry_run:
        log.info("DRY_RUN — wrote output/%s.mdx, nothing pushed", slug)
        return state

    from core.publish.pr_publisher import publish_pr
    branch = publish_pr(state, _pr_body(report))
    state["status"] = "published"
    state["branch"] = branch
    return state


def _section_extras(section: str, slug: str, plan: dict, corpus: Corpus,
                    *, is_last: bool = False, mockups: list[str] | None = None) -> str:
    """Per-section component and linking requirements the validator will enforce.

    `is_last` carries the internal-link requirement. It used to live on the
    `decisions` section — which the `game`, `platform_frontend` and `design_only`
    archetypes DROP, so nothing ever asked for the links and every study of those
    shapes failed validation three times and aborted. Found on the first live run.
    """
    parts: list[str] = []

    if is_last:
        parts.append(
            f"End the section with internal links, which every study must carry: one "
            f"to a /blog/ post chosen from {corpus.blog_slugs[:8]}, and one to the "
            f"relevant /services/ page (web, mobile or ai). Write them as natural "
            f"markdown links in a closing sentence, not as a list.")

    if section == "build":
        parts.append(f'Include this exact component on its own line:\n'
                     f'    <ArchitectureDiagram study="{slug}" caption="…" />\n'
                     f'    It reads the architecture from the registry, so pass only the slug.')

    elif section == "tour":
        # Only offer keys that EXIST and are scoped to this project. Left open, the
        # writer invents a plausible key every single attempt — "mindmaze-junior-
        # gameplay", then "/mockups/mindmaze-junior-gameplay.png" — fails validation,
        # and burns the entire rewrite budget doing it. Observed on the first two
        # live runs. If nothing has been built yet, say so plainly: the validator
        # treats a missing <Annotated> as a warning, so prose alone is valid.
        if mockups:
            parts.append(
                f'Include one <Annotated mockup="KEY" caption="…" pins={{[…]}} /> with '
                f'3-4 pins. The mockup value must be EXACTLY one of these existing '
                f'registry keys: {mockups}. Do not invent a key. Each pin needs x and y '
                f'as percentages, a short label, and a note saying WHY it is built that '
                f'way — not what it is.')
        else:
            parts.append(
                "No mockup exists for this project yet. Write this section as PROSE "
                "ONLY. Do not include an <Annotated> component, do not reference an "
                "image file, and do not invent a mockup key — a visual is added at "
                "review time.")

    elif section == "decisions":
        rows = plan.get("decisions") or []
        listed = "; ".join(f"{d.get('choice')} over {d.get('over')}" for d in rows if d.get("choice"))
        parts.append(f"Cover these decisions, each as a bold lead-in followed by the "
                     f"reasoning: {listed or 'the two or three choices that mattered most'}.")

    elif section == "problem":
        parts.append("No components. Prose only.")

    return "\n".join(f"  - {p}" for p in parts) if parts else "  - (prose only)"


def _mockup_keys(site_dir, *, project_id: str | None = None) -> set[str]:
    """Registry keys, optionally filtered to those valid for one project.

    Each entry declares `projects: [...]`. An empty list means generic/reusable.
    Passing a project_id returns only the keys that project may legitimately use,
    which is what stops a study reaching for another project's UI.
    """
    import re
    base = Path(site_dir) if site_dir else CONFIG.local_site_dir
    path = base / "src" / "components" / "mockups" / "index.tsx"
    if not path.exists():
        return set()
    src = path.read_text(encoding="utf-8", errors="replace")

    blocks = re.split(r"^\s*'([a-z]+/[a-z0-9-]+)':\s*\{", src, flags=re.M)
    out: set[str] = set()
    for i in range(1, len(blocks), 2):
        key, body = blocks[i], blocks[i + 1]
        if project_id is None:
            out.add(key)
            continue
        m = re.search(r"projects:\s*\[([^\]]*)\]", body)
        owners = [t.strip().strip("'\"") for t in (m.group(1).split(",") if m else []) if t.strip()]
        if not owners or project_id in owners:
            out.add(key)
    return out


def _esc(s: str) -> str:
    return str(s).replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ").strip()


def _render_registry_entry(project, archetype: str, plan: dict, spec: dict, corpus: Corpus) -> str:
    """Build the TypeScript object literal for studies.ts."""
    from datetime import date
    today = date.today().isoformat()
    g = spec.get("glance", {})

    def arr(items, indent="      "):
        return "\n".join(f"{indent}'{_esc(i)}'," for i in items)

    metrics = "\n".join(
        "      { value: '%s', unit: '%s', label: '%s', context: '%s', source: '%s' },"
        % (_esc(m.get("value", "")), _esc(m.get("unit", "")), _esc(m.get("label", "")),
           _esc(m.get("context", "")), _esc(m.get("source", "qualitative")))
        for m in spec.get("metrics", [])
    )
    faq = "\n".join(
        "      { q: '%s', a: '%s' }," % (_esc(f.get("q", "")), _esc(f.get("a", "")))
        for f in spec.get("faq", [])
    )
    tid = corpus.testimonial_by_client.get(
        (project.client.lower(), project.client_country.lower()))

    return f"""  {{
    slug: '{_esc(project.slug)}',
    projectId: '{_esc(project.id)}',
    archetype: '{archetype}',
    published: '{today}',
    updated: '{today}',

    headline:
      '{_esc(plan.get("headline", ""))}',
    summary:
      '{_esc(plan.get("summary", ""))}',

    hero: {{
      kind: 'browser',
      mockup: 'REVIEW-ME',
      caption: '{_esc(plan.get("headline", ""))}',
    }},

    role: [{", ".join(f"'{_esc(r)}'" for r in spec.get("role", []))}],
    platforms: [{", ".join(f"'{_esc(p)}'" for p in spec.get("platforms", []))}],
    stack: [{", ".join(f"'{_esc(t)}'" for t in spec.get("stack", []))}],

    metrics: [
{metrics}
    ],

    glance: {{
      businessProblem:
        '{_esc(g.get("businessProblem", ""))}',
      technicalChallenges:
        '{_esc(g.get("technicalChallenges", ""))}',
      engineeringSolution:
        '{_esc(g.get("engineeringSolution", ""))}',
      coreFeatures: [
{arr(g.get("coreFeatures", []))}
      ],
      architecture:
        '{_esc(g.get("architecture", ""))}',
      technicalHighlights: [
{arr(g.get("technicalHighlights", []))}
      ],
      businessValue:
        '{_esc(g.get("businessValue", ""))}',
    }},
{f"    testimonialId: {tid}," if tid else ""}
    relatedService: '{_service_for(project)}',
    relatedPosts: [],
    relatedStudies: [],

    faq: [
{faq}
    ],

    seo: {{
      primaryKeyword: '{_esc(plan.get("primary_keyword", ""))}',
      secondary: [{", ".join(f"'{_esc(k)}'" for k in plan.get("secondary_keywords", []))}],
    }},
{"    hideStatus: true," if project.hide_status else ""}
  }},
"""


def _service_for(project) -> str:
    from casestudy.queue import CATEGORY_SERVICE
    return CATEGORY_SERVICE.get(project.category, "web")


def _write_output(state: dict) -> None:
    out = CONFIG.output_dir
    (out / f"{state['slug']}.mdx").write_text(state["body_mdx"], encoding="utf-8")
    (out / f"{state['slug']}.entry.ts").write_text(state["registry_entry"], encoding="utf-8")
    (out / f"{state['slug']}.report.txt").write_text(state["report"], encoding="utf-8")


def _pr_body(report: list[str]) -> str:
    return "```\n" + "\n".join(report) + "\n```"
