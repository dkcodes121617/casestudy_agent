"""Regression test: run every validator against the hand-written specimens.

    python tools/selftest.py

THE SPECIMENS ARE THE SPEC. Seven studies were written by hand, reviewed, and
shipped before this agent existed. If a validator rejects one of them, the
validator is wrong — and this is the only way to find that out before the agent's
first real run rather than after it.

It has already earned its place. On the first run it rejected 5 of 7, and every
rejection was a validator bug:
  - claims.py read <Annotated> pin coordinates (x: 26, y: 30) as untraceable
    numbers, blocking six per study
  - mdx.py held a 5-section `game` study to a 6-section word floor

The one remaining failure is a TRUE positive, left in deliberately as a live
example: SolarSathi's prose says "a 25 kW rooftop system", an illustrative figure
with no source. Fail-closed is right — the fix is one line in that project's brief
("illustrative system sizes: 5-100 kW, generic industry range"), not a looser rule.
"""
"""Original docstring:

The specimens ARE the spec. If a validator rejects one of them it is the validator
that is wrong, and this is the only way to find that out before the agent's first
real run rather than after it.
"""
import sys, re, json
from pathlib import Path
sys.path.insert(0, '.')
from casestudy.corpus import load_corpus
from casestudy.validators import mdx as mdxv, status as statusv, claims, confidentiality
from core.config import CONFIG

SITE = CONFIG.local_site_dir
studies_ts = (SITE / CONFIG.studies_registry_rel).read_text(encoding='utf-8')
corpus = load_corpus()
keys = set(re.findall(r"^\s*'([a-z]+/[a-z0-9-]+)':\s*\{", (SITE/'src/components/mockups/index.tsx').read_text(encoding='utf-8'), re.M))

region = studies_ts[studies_ts.index('export const studies'):]
marks = [(m.group(1), m.start()) for m in re.finditer(r"\bslug:\s*'([^']+)'", region)]
fails = 0
for i,(slug, at) in enumerate(marks):
    chunk = region[at: marks[i+1][1] if i+1 < len(marks) else len(region)]
    arche = re.search(r"archetype:\s*'([^']+)'", chunk).group(1)
    hide = bool(re.search(r"hideStatus:\s*true", chunk))
    body = (SITE / CONFIG.studies_content_rel / f'{slug}.mdx').read_text(encoding='utf-8')
    proj = corpus.project(slug) or corpus.project(re.search(r"projectId:\s*'([^']+)'", chunk).group(1))

    r = mdxv.validate(body, archetype=arche, hide_status=hide, slug=slug,
        known_blog_slugs=set(corpus.blog_slugs), known_study_slugs=corpus.written_slugs, mockup_keys=keys)
    s = statusv.scan(body, hide_status=hide)
    c = claims.scan(body, project_metrics=proj.metrics if proj else [],
                    brief_safe=chunk, project_description=proj.description if proj else '')
    f = confidentiality.scan(body, spec_text=chunk, denylist=[])

    ok = r.ok and s.clean and c.clean and f.clean
    print(f"{'ok  ' if ok else 'FAIL'} {slug:<20} {arche:<18} mdx={len(r.errors)}e/{len(r.warnings)}w status={len(s.findings)} claims={len(c.findings)} conf={len(f.findings)}")
    if not ok:
        fails += 1
        for e in r.errors: print(f"       mdx: {e}")
        for x in s.findings: print(f"       status: [{x.rule}] {x.match!r} line {x.line}")
        for x in c.findings: print(f"       claims: {x.value!r} — {x.context[:80]}")
        for x in f.findings: print(f"       conf: [{x.rule}] {x.match!r}")
    for w in r.warnings: print(f"       ! {w}")
print()
print(f"{len(marks)-fails}/{len(marks)} specimens pass every validator" if not fails else f"\n{fails} specimen(s) rejected — the VALIDATOR is likely wrong, not the study")
