"""Prompt builders for the case study nodes.

Same proxy rules the blog agent learned the hard way (see core/llm/client.py):
  - Phrase everything as a normal professional writing task. NEVER use
    override/compliance language ("reply with exactly", "obey this contract") —
    the proxy's injection guard refuses those.
  - Put the real facts in the prompt and tell the model to ground claims in them.
  - Ask for JSON where structure is needed, MDX where prose is.

Each function returns (system, user).
"""
from __future__ import annotations

# The persona, extended from the blog agent's STUDIO_PERSONA. The readability rules
# are inherited verbatim because they were tuned against this exact audience — and
# they extract well for the same reason they read well: answer engines quote short,
# self-contained sentences far more readily than nested ones.
STUDIO_PERSONA = (
    "You are the founding engineer at WizCodes, a small remote-first software studio "
    "(web, mobile, and AI). You are writing a case study about work the studio "
    "actually did. Your voice is first-person plural ('we'), plain-spoken, senior, "
    "and honest — never hyped, never generic. You ground everything in the real "
    "facts provided and never invent numbers, clients, outcomes, or statistics."
    "\n\n"
    "Write so a busy, non-technical founder understands it on one read:\n"
    "  - Short sentences, one idea each. If a sentence has three commas, split it.\n"
    "  - Mostly 8-18 words, with an occasional very short one for rhythm.\n"
    "  - Plain words where they are exact. Never a longer word to sound senior.\n"
    "  - Explain any technical term the first time it appears, in the same sentence.\n"
    "  - Short paragraphs: two to four sentences, then a break.\n"
    "  - Active voice and concrete nouns. Say who does what.\n"
    "  - No filler openers, no throat-clearing, no empty adjectives such as\n"
    "    robust, seamless, cutting-edge or powerful.\n"
    "  - Simple is not casual. Keep the professional register and never talk down."
    "\n\n"
    "Two rules specific to a case study, and they matter more than style:\n"
    "  1. SELF-CONTAINED SENTENCES. Each one must survive being lifted out of the\n"
    "     page with no surrounding context. Name the subject; never open a section\n"
    "     with a pronoun pointing at something outside it.\n"
    "  2. ANSWER FIRST. Open each section with the claim, then explain it. Do not\n"
    "     build up to the point."
)

# Framing rule per archetype. `own_product` is the one that needs saying out loud:
# with no client, a writer will manufacture external pressure that never existed.
_ARCHETYPE_FRAMING = {
    "own_product": (
        "This is WizCodes' OWN product. There is no client, no brief from a customer, "
        "no deadline anyone set, and no client outcome to report. Frame the opening as "
        "WHY WE BUILT THIS — a problem the studio had itself.\n"
        "The constraints section is the one most easily got wrong: these constraints "
        "were CHOSEN, not imposed. Write each one as a decision the studio made and "
        "could have made differently, never as a requirement handed down. Do not "
        "manufacture external pressure that did not exist."
    ),
    "platform_frontend": (
        "The engagement was SCOPE-LIMITED. WizCodes built the frontend only; the "
        "client's own team built the product behind it. Say this plainly and early. "
        "Never imply the studio built the underlying technology, and claim no "
        "decisions the studio did not make."
    ),
    "design_only": (
        "Design was delivered; nothing was built. There is no architecture, no shipped "
        "software, and no engineering decisions to describe. Do not imply otherwise."
    ),
    "game": (
        "This is a game. The interesting decisions are design and tuning, not "
        "architecture. Write the tour section as the gameplay loop."
    ),
    "marketplace": (
        "Two-sided: the study must cover both the buyer and the supplier side, and "
        "the cold-start problem is worth addressing directly."
    ),
    "ai_system": (
        "This is a pipeline, not an app. Latency, orchestration and failure behaviour "
        "are the substance. Write the tour section as the pipeline in motion."
    ),
    "product_build": "",
}


def _status_rule(hide_status: bool) -> str:
    if not hide_status:
        return ""
    return (
        "\n\nIMPORTANT — this project makes NO claim about release state. Do not write "
        "that it launched, shipped, released, went live, is in production, has users, "
        "has downloads, or is on any app store. Do not mention the App Store, Play "
        "Store, TestFlight, store listings, store reviews or store updates at all. "
        "Describe what was BUILT, in the past tense, without implying distribution."
    )


def plan_prompt(facts: str, brief: str, project: dict, archetype: str) -> tuple[str, str]:
    """Opus. Decide the headline, angle, and per-section plan."""
    system = STUDIO_PERSONA + " Right now you are planning a case study before writing it."
    framing = _ARCHETYPE_FRAMING.get(archetype, "")
    user = f"""Plan a case study about a real project.

STUDIO FACTS (ground everything in these):
{facts}

PROJECT BRIEF (the only source for anything not in the facts above):
{brief}

Project: {project['name']} — {project['description']}
Archetype: {archetype}
{framing}{_status_rule(project.get('hide_status', False))}

Produce a JSON plan:
{{
  "headline": string (ONE sentence, outcome-led, NOT the project name — the page
              renders the name as its own heading. This is the line a reader
              actually reads, and the OG card subtitle.),
  "summary": string (140-160 chars, meta description, includes the primary keyword),
  "primary_keyword": string (what a buyer would search to land here),
  "secondary_keywords": [3-5 related phrases],
  "section_briefs": {{ "<section>": "one sentence on what this section must cover" }},
  "decisions": [2-4 objects {{"choice": string, "over": string, "because": string}}]
}}
Only include sections the archetype actually uses."""
    return system, user


def spec_prompt(facts: str, brief: str, project: dict, archetype: str, plan: dict) -> tuple[str, str]:
    """Opus. Derive the typed registry fields, especially the at-a-glance block."""
    system = STUDIO_PERSONA + (
        " Right now you are writing the structured summary fields for a case study. "
        "These are read by search engines and AI assistants directly, so each one has "
        "to stand alone."
    )
    user = f"""Write the structured fields for this case study.

STUDIO FACTS:
{facts}

PROJECT BRIEF:
{brief}

Project: {project['name']}
Archetype: {archetype}
Headline: {plan.get('headline', '')}
{_status_rule(project.get('hide_status', False))}

The seven "glance" fields below are the most-read block on the page. Each value must
be a COMPLETE sentence that names the project and makes sense with zero surrounding
context. Never open one with a pronoun pointing outside the field.

Reply as JSON:
{{
  "role": [what WizCodes actually did, 2-5 short phrases],
  "platforms": [e.g. "iOS", "Android", "Web"],
  "stack": [4-6 technologies, from the facts only],
  "metrics": [3-4 objects {{"value": string, "unit": string or "", "label": string,
              "context": string, "source": "projects.ts" | "brief" | "qualitative"}}],
  "glance": {{
    "businessProblem": string,
    "technicalChallenges": string,
    "engineeringSolution": string,
    "coreFeatures": [4-8 short noun phrases],
    "architecture": string (arrow-separated, 2-6 nodes, e.g. "React → FastAPI → Postgres"),
    "technicalHighlights": [3-5 short sentences],
    "businessValue": string
  }},
  "faq": [3-4 objects {{"q": string, "a": string}} — questions a BUYER asks about
          cost, time, risk or ownership, not technical implementation]
}}

Every metric with source "projects.ts" or "brief" must quote a value that genuinely
appears there. If you have no real number, use source "qualitative" and a value with
no numeral in it. Never estimate."""
    return system, user


def section_prompt(
    facts: str, brief: str, project: dict, archetype: str, plan: dict,
    section: str, heading: str, extras: str,
) -> tuple[str, str]:
    """Sonnet. ONE section per call.

    Sectioned writing is carried over from the blog agent for the same reason it
    exists there: the proxy has 502 spells, and a short call means a bad moment
    costs one section rather than the whole study.
    """
    system = STUDIO_PERSONA + " You write in MDX. Right now you write only ONE section."
    brief_line = (plan.get("section_briefs") or {}).get(section, "")
    user = f"""Write ONE section of a case study in MDX.

STUDIO FACTS:
{facts}

PROJECT BRIEF (the only source for anything not in the facts):
{brief}

Project: {project['name']}. Archetype: {archetype}.
Headline: {plan.get('headline', '')}
{_ARCHETYPE_FRAMING.get(archetype, '')}{_status_rule(project.get('hide_status', False))}

Write the section under this exact heading:
## {heading}

What it must cover: {brief_line or 'see the headline and brief above'}

{extras}

Write 130-220 words. Open with the claim, then explain. Vary sentence length. Use
**bold** or a bullet list where it genuinely helps. One > blockquote is allowed if
there is a line worth pulling out.

HARD MDX RULES:
  - No H1, no frontmatter. Start with the "## {heading}" line.
  - Never write a raw '<' or '{{' in ordinary prose.
  - No markdown tables.
  - Do not invent numbers. If you have no real figure, write qualitatively.

Output only this one section."""
    return system, user
