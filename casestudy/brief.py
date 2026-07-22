"""Draft `briefs/<project-id>.md` from what we actually know.

A SEPARATE command from publishing, on purpose. Drafting and writing are different
jobs with different review needs: you can draft twenty briefs in an afternoon and
clear their flags over the following months, at the rate you publish.

    python -m casestudy.brief cubbi        # or: make brief P=cubbi
    python -m casestudy.brief --all        # draft every project missing one

What it will and will not do:

  - It sources everything it can from projects.ts, products.ts and testimonials.ts,
    and tags each line with where it came from.
  - It marks everything else `[NEEDS REVIEW]` and never guesses. The two things it
    can NEVER source are (a) permission — whether a client may be named, what may
    be published — and (b) rationale, because no data file records why a decision
    was made. Those are always flagged.

The `## Confidential` section starts empty with a single flagged prompt. It is the
one section a human must fill in, and it is never shown to the writer — only to the
confidentiality scanner, as a denylist.
"""
from __future__ import annotations

import argparse
import sys

from casestudy.corpus import Project, load_corpus
from casestudy.deck import entry as deck_entry
from casestudy.briefdata import entry as brief_entry
from core.config import CONFIG

NR = "[NEEDS REVIEW]"


def _draft(p: Project, has_testimonial: bool) -> str:
    d = deck_entry(p.id) or {}
    b = brief_entry(p.id) or {}
    src = "products.ts" if p.is_product else "projects.ts"
    lines: list[str] = [f"# {p.name}", ""]
    lines.append(f"<!-- drafted by casestudy.brief from {src} — review before use -->")
    lines.append("")

    lines.append("## Confidential — never publish")
    lines.append("")
    if b.get("confidential"):
        for c in b["confidential"]:
            lines.append(f"- {c}")
        lines.append("  (owner-supplied; fed to the confidentiality scanner as a denylist,")
        lines.append("   never shown to the writer)")
    elif b:
        lines.append("- Nothing. The owner has confirmed there is no confidential material")
        lines.append("  for this project beyond what is already withheld from projects.ts.")
    else:
        lines.append(f"- {NR} Anything this client would object to seeing published.")
    lines.append("")

    lines.append("## Safe to publish")
    lines.append("")
    if p.client:
        lines.append(f"- Client: {p.client}"
                     + (f", {p.client_country}" if p.client_country else "")
                     + f"   (source: {src})")
        lines.append(f"  {p.client} is already published in projects.ts and rendered on")
        lines.append("  the live /work pages, so naming them here discloses nothing new.")
        if not b:
            lines.append(f"  {NR} Confirm.")
    elif p.client_country:
        lines.append(f"- Client country: {p.client_country}   (source: {src})")
        if b:
            lines.append(f"  Client is deliberately unnamed in {src}; the owner's scope note")
            lines.append("  above governs what may be published.")
        else:
            lines.append(f"- {NR} Client kept confidential in {src} — confirm that still holds.")
    else:
        note = " Own product." if p.is_product else ""
        if not p.is_product and not b:
            note = f" {NR} Confirm why."
        elif not p.is_product:
            note = " No client field recorded; the owner's scope note above governs."
        lines.append(f"- No client recorded in {src}.{note}")

    if p.industry:
        lines.append(f"- Industry: {p.industry}   (source: {src})")
    if p.tech:
        lines.append(f"- Stack: {', '.join(p.tech)}   (source: {src})")
    for m in p.metrics:
        lines.append(f"- {m}   (source: {src} metrics[])")

    if b.get("shareable"):
        lines.append(f"- Scope: {b['shareable']}   (source: owner)")
    if not b:
        lines.append(f"- {NR} Any REAL number we may cite? Latency, volume, timeline, team size.")
        lines.append("  Leave this empty rather than estimating — the claims validator")
        lines.append("  rejects any numeral it cannot trace back to here or to projects.ts.")

    if p.hide_status:
        lines.append(f"- hideStatus is TRUE in {src}: no live, shipped, launched, released")
        lines.append("  or app-store claim may appear anywhere in the study.")
    else:
        lines.append(f"- hideStatus is not set in {src}, so release language is permitted.")
        lines.append("  projects.ts is the source of truth for this and is kept current.")

    if has_testimonial:
        lines.append("- A testimonial exists for this client and will be joined automatically.")
    else:
        lines.append("- No testimonial for this client in testimonials.ts. The section will")
        lines.append("  not render; add one there first if that is wrong.")
    lines.append("")

    # ── PROJECTED, not measured. See the note at the top of briefdata.py. ──
    if b.get("metrics"):
        lines.append("## Metrics — PROJECTED, not measured")
        lines.append("")
        lines.append(f"{b['metrics']}   (source: owner, projected)")
        lines.append("")
        lines.append("Every figure above is a design target or an expected characteristic.")
        lines.append("Nobody instrumented this project and recorded a number. Any figure")
        lines.append("taken from here must be written as a TARGET or a design goal —")
        lines.append('"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim')
        lines.append("built on a projection is the failure this separation exists to stop.")
        lines.append("")

    lines.append("## The story")
    lines.append("")
    if d.get("problem"):
        lines.append(f"- Why they came to us: {d['problem']}   (source: deck)")
    else:
        lines.append(f"- Why they came to us: {NR}")

    if d.get("challenges"):
        lines.append(f"- What was hard: {d['challenges']}   (source: deck)")
    else:
        lines.append(f"- What was hard: {NR}")

    if d.get("solution"):
        lines.append(f"- How we solved it: {d['solution']}   (source: deck)")
    if d.get("highlights"):
        lines.append(f"- Technical highlights: {'; '.join(d['highlights'])}   (source: deck)")
    if d.get("architecture"):
        lines.append(f"- Architecture: {d['architecture']}   (source: deck)")
    if d.get("value"):
        lines.append(f"- Business value: {d['value']}   (source: deck)")

    if b.get("rationale"):
        lines.append(f"- What we decided and why: {b['rationale']}   (source: owner)")
    else:
        lines.append(f"- What we decided and why, X over Y: {NR}")
        lines.append("  No data file records rationale. It can only come from the owner.")
    lines.append(f"- What was delivered: {p.description}   (source: {src})")
    lines.append("")

    lines.append("## Screens (mockup registry keys)")
    lines.append("")
    lines.append("- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and")
    lines.append("  the PR is where a real key is chosen from")
    lines.append("  src/components/mockups/index.tsx. Deliberately not a blocking flag:")
    lines.append("  the brief gate exists for FACTS — permission, numbers, rationale —")
    lines.append("  and a missing mockup is a completeness issue caught at review, not a")
    lines.append("  truth issue that should block writing.")
    lines.append("")
    return "\n".join(lines)


def draft(project_id: str, *, force: bool = False) -> int:
    corpus = load_corpus()
    p = corpus.project(project_id)
    if p is None:
        print(f"unknown project: {project_id}")
        print("Known ids: " + ", ".join(sorted(x.id for x in corpus.projects)))
        return 1

    path = CONFIG.briefs_dir / f"{project_id}.md"
    if path.exists() and not force:
        print(f"{path.name} already exists — pass --force to overwrite")
        return 1

    has_quote = (p.client.lower(), p.client_country.lower()) in corpus.testimonial_by_client
    text = _draft(p, has_quote)
    path.write_text(text, encoding="utf-8")

    flags = text.count(NR)
    print(f"wrote {path}  ({flags} [NEEDS REVIEW] marker(s) to clear)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Draft a case study brief.")
    ap.add_argument("project_id", nargs="?", help="project id, e.g. cubbi")
    ap.add_argument("--all", action="store_true", help="draft every project missing a brief")
    ap.add_argument("--force", action="store_true", help="overwrite an existing brief")
    args = ap.parse_args(argv)

    if args.all:
        corpus = load_corpus()
        todo = [p for p in corpus.projects
                if p.slug not in corpus.written_slugs
                and not (CONFIG.briefs_dir / f"{p.id}.md").exists()]
        for p in todo:
            draft(p.id)
        print(f"\n{len(todo)} brief(s) drafted. Clear the [NEEDS REVIEW] markers before publishing.")
        return 0

    if not args.project_id:
        ap.error("give a project id, or --all")
    return draft(args.project_id, force=args.force)


if __name__ == "__main__":
    sys.exit(main())
