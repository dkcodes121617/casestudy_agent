# WizCodes Case Study System — Audit & Implementation Plan

Date: 2026-07-22
Scope: `blog_agent/`, `casestudy_agent/`, `wizcodes_next/`

---

## Part 0 — TL;DR of the recommendations

| # | Decision | Resolution |
|---|---|---|
| 1 | Where does the agent live? | **LOCKED: separate `casestudy_agent` repo.** `core/` is copied once from the blog agent, with `make sync-core` to surface upstream proxy fixes instead of letting them go stale. See §5.1. |
| 2 | Content model | **Hybrid**: typed registry (`studies.ts`, rich spec) + MDX narrative body. Not pure-MDX (blog), not pure-typed (today). |
| 3 | Publishing | **Open a PR, never push to main.** Case studies carry NDA/client risk that blog posts do not. |
| 4 | Hero visual | **LOCKED: generated visuals only, zero screenshots, no exceptions.** CSS/JSX mockups + the architecture generator carry all 30. |
| 5 | Architecture visual | **New `ArchitectureDiagram` SVG generator** driven by the PDF's one-line architecture string. 30 diagrams from 30 strings. |
| 6 | AEO/LLMO centrepiece | **The PDF's 7 fields rendered as an HTML `<dl>`** near the top. That structure is already a perfect extractable-chunk layout. |
| 7 | Cadence | **LOCKED: coverage-gap-first**, 1–2/month, seeded with **3** hand-built gold specimens (Destiny, CuePilot, Cyber Agent). 24 remaining ≈ 12–24 months runway. |
| 8 | Schema | `Article` + `about: SoftwareApplication` + `mentions[]` + `isPartOf: CollectionPage`. Keep `FAQPage` for LLMs only — Google deprecated its rich result in May 2026. |
| 9 | Briefs | **LOCKED: agent-drafted from the PDF**, with `[NEEDS REVIEW]` on anything unverifiable. See §5.3. |
| 10 | Own products | **LOCKED: same kit**, under a dedicated `own_product` archetype. See §3.2. |

---

## Part 1 — Audit: how the three folders actually connect

### 1.1 System topology

```
blog_agent (public GitHub repo)
  └─ .github/workflows/publish.yml   cron: hourly
       └─ python main.py
            ├─ scheduler/planner.py   "is a slot due?" (date-seeded, stateless)
            ├─ facts/snapshot.py      clones/reads the SITE repo → real-facts block
            ├─ knowledge/store.py     MiniLM embeddings → uniqueness gate
            ├─ graph/build.py         LangGraph pipeline (Opus strategy, Sonnet writing)
            └─ publish/github_publisher.py
                 └─ git commit + PUSH to main of ↓

wizcodes_next  (private repo: dkcodes121617/wizcodes_main_website)
  └─ .github/workflows/deploy.yml   on: push to src/**
       ├─ npm ci
       ├─ npm run build
       │    └─ prebuild: scripts/export-graphics.mjs
       │         ├─ parse every .mdx for kit components
       │         ├─ render each to public/graphics/*.svg
       │         ├─ write src/lib/graphics/manifest.json
       │         └─ scripts/fitcheck.mjs → HARD FAIL if text overflows its box
       └─ firebase deploy → wizcodes.site

casestudy_agent (public GitHub repo)
  └─ EMPTY. .gitignore + a 1-line requirements.txt + a venv. One commit.
```

**The coupling is a single file write.** The agent's only contract with the frontend is:
1. write `src/content/blog/<slug>.mdx`
2. insert one object literal at the head of the `posts[]` array in `src/content/blog/posts.ts`
3. push

Everything downstream (routing, sitemap, RSS, JSON-LD, OG image, graphics export, image sitemap) is derived automatically. This is a genuinely good design and the case study system should copy it exactly.

### 1.2 The blog generation pipeline, node by node

```
load_context
  → pick_topic ──────┐ (Opus; focus assigned deterministically by pick_focus())
  ← check_topic ─────┘ retry ≤4 on cosine ≥0.82 OR dev-facing OR blocked archetype
  → outline           (Opus; archetype → H2 scaffold + illustration plan)
  → write             (Sonnet; ONE CALL PER SECTION — intro, each H2, closing)
  → validate ────┐    (deterministic mdx_validator.py — cheap, runs BEFORE factcheck)
  ← rewrite ≤2 ──┘
  → factcheck ───┐    (Sonnet; narrow: only fabrications ABOUT WizCodes)
  ← fix_claims ──┘    surgical, budget 2, then ships anyway if MDX-valid
  → humanize          (best-effort; failure keeps the prior body)
  → registry          (slug/title/description/tags)
  → final_uniqueness  abort if body cosine ≥0.86
  → finalize → publish_post()
```

Design decisions worth carrying forward verbatim:

- **Sectioned writing.** Many short calls beat one long call — a proxy 502 costs one section, not the article. This is why the agent survives an unreliable proxy.
- **Deterministic-first ordering.** `validate` (free, instant) runs before `factcheck` (an API call). A malformed draft never spends a fact-check call.
- **Best-effort steps never sink the run.** `humanize` and `fix_claims` both keep the prior body on failure and re-validate before accepting a revision. Never regress.
- **Anti-convergence is structural, not prompted.** `pick_focus()` assigns a focus from the least-covered axis of the *real project corpus* before the LLM is asked anything. The comment in `prompts/library.py:214` is the key lesson: four "cost of X" posts scored max 0.693 pairwise against an 0.82 threshold — cosine finds near-duplicates, not thematic sameness. The fix was to stop asking an open question.
- **Archetype rotation is inferred from published titles** (`infer_archetype`) because the registry doesn't store the archetype. Clever, but it is a lossy round-trip. **The case study registry should store its archetype explicitly.**
- **Prompt-caching on the ~17k-char facts block** (`llm/client.py`) — the facts block is resent on 9+ calls per run. Marked `cache_control: ephemeral` above 2000 chars.
- **Proxy quirks are load-bearing**: CLI User-Agent (`claude-cli/1.0.0 (external, cli)`) or Cloudflare 403s everything; injection-guard-safe phrasing (no "reply with exactly", no "never break character").

### 1.3 How a blog post renders

`src/app/blog/[slug]/page.tsx`:
- `generateStaticParams()` from the registry, `dynamicParams = false`
- dynamic `import('@/content/blog/${slug}.mdx')`
- emits `BlogPosting` + `BreadcrumbList` JSON-LD, canonical, OG, Twitter
- author = the **Organization**, not a Person (deliberate — an honest E-E-A-T call, since nobody reviews the automated posts)
- body wrapped in a `.prose` container; the 13-component kit is registered globally in `src/mdx-components.tsx` so MDX needs **zero imports**

**The dual-layer graphics system is the standout piece of engineering here.** Each visual generator (`src/lib/graphics/*.mjs`) is a *string builder*, not a React component, precisely so the same output can be produced twice: inline on the page, and as a standalone `public/graphics/*.svg` that Google Images and AI scrapers can index independently. `useExportedGraphic.tsx` resolves a component's props → a stable key → the manifest → the published filename, so the two can never drift. Filenames are `<page-slug>-<caption-keywords>-<hash>.svg`, and `fitcheck.mjs` fails the build if any text line escapes its box.

### 1.4 How case studies are implemented today — the honest assessment

**There is no case study system.** There is a hardcoded object literal.

`src/app/work/[slug]/page.tsx` contains `CASE_STUDY_CONTENT: Record<string, CaseStudyContent>` — 143 lines of prose **inside a route file** — covering 6 of 26 projects. `CaseStudyLayout.tsx` renders it as:

```
breadcrumb → h1 + tagline → metrics row (from projects.ts) → Overview (2 <p>)
→ What Was Built (<ul>) → Challenge/Solution (2 cards) → CTA
```

A 51.25rem single column. Seven prose fields. Concretely, it is missing:

| Missing | Consequence |
|---|---|
| Any image or visual whatsoever | Zero dwell time, zero image search surface, nothing to share |
| Case-study-specific JSON-LD (only `BreadcrumbList`) | Invisible as an entity; no `about`, no `mentions`, no `datePublished` |
| A registry / typed content model | Can't be listed, sorted, filtered, related, or agent-generated |
| MDX or any narrative flexibility | Every study is exactly the same 7 fields |
| FAQ, testimonial, related-work, related-service | No trust cascade, no internal linking, one CTA at the very bottom only |
| Per-study OG image | All 26 share the generic template |
| Entry in `llms.txt` / `llms-full.txt` | `/work` is mentioned; **not one project is named** |
| `CollectionPage` / `ItemList` on `/work` | The portfolio isn't a machine-readable set |
| Sticky TOC / progress / anchor nav | Long-form is unnavigable |

And 20 of 26 projects render `ProjectSummary` — an honest, deliberately short page (name, description, 4 meta rows, CTA). Those are ~120-word pages sitting in the sitemap at priority 0.5. Truthful, but thin-content risk at scale.

### 1.5 Assets you already own and are not using

| Asset | Location | Status |
|---|---|---|
| `BrowserFrame` | `src/components/BrowserFrame.tsx` | **Built. Zero usages.** Chrome dots + lock icon + URL bar. |
| `NullzecMockup` | `src/components/NullzecMockup.tsx` | **Built. Zero usages.** |
| `DashboardMockup` | `src/components/DashboardMockup.tsx` | Home page only. Interactive: period tabs, animated sparkline, counting KPIs, live ticker. |
| `CopilotMockup`, `DestinyJournalMockup` | `src/components/` | Home page only. |
| `PhoneFrame` | `src/components/PhoneFrame.tsx` | Home page only. Notch, status bar, light/dark screen. |
| 13 real testimonials | `src/data/testimonials.ts` | `/testimonials` + home only. **Not one is attached to a project.** |
| SVG generator + fitcheck system | `src/lib/graphics/` | Blog only. |
| The 30-project PDF | your attachment | Not in the repo at all. |

The mockup components are the single most valuable under-used asset in the repo. They are exactly what a premium case study needs, and they were already built to the site's design tokens.

---

## Part 2 — Strategy: why a Case Study Agent is a *different shape* of agent

| | Blog Agent | Case Study Agent |
|---|---|---|
| Subject space | Open, infinite | **Closed, 30 items, already enumerated** |
| Core risk | Repeating itself | **Leaking client confidential info / inventing outcomes** |
| Uniqueness gate | Essential (embeddings) | Unnecessary for *subject*; essential for *narrative shape* |
| Topic selection | LLM strategist + deterministic focus | **Pure deterministic priority queue — no LLM needed** |
| Cadence | 1–2/day | 1–2/month |
| Runway | Infinite | ~24 studies ≈ 12–24 months, then maintenance mode |
| Publish | Push to main, unattended | **Open a PR. Human merges.** |
| Grounding | Facts snapshot from repo | Facts snapshot **+ per-project brief file** |

The three consequences that shape the whole design:

1. **Drop the topic strategist.** Replace with a scored queue. An LLM choosing "which project should we write about" adds nondeterminism and zero value when the answer is computable from coverage gaps + business priority.
2. **Add a confidentiality firewall.** `details.md §20.1` already enumerates the forbidden classes (revenue/ad-revenue figures, client KPIs, internal workflows, customer conversations, user data, API credentials, internal prompt design, unreleased game mechanics, licensing/roadmap). This must become a deterministic denylist plus an LLM adjudicator, and it must be a **hard abort**, not a warning.
3. **Add a claims-traceability audit.** Every number in a case study must map to `projects.ts:metrics[]`, the brief, or be explicitly qualitative. The blog agent's `factcheck` node is narrow by design ("only flag fabrications about WizCodes"). For case studies it must be *strict*: unsourced number → abort.

---

## Part 3 — The Case Study Kit (frontend)

### 3.1 Content model — hybrid typed + MDX

Why hybrid:
- **Typed** because the hero, metric band, spec rail, schema, `/work` cards, OG image and related-study logic all need the *same* fields in the *same* shape across 30 studies. That structural identity is what makes 30 pages read as one system instead of 30 articles.
- **MDX** because the narrative and its visuals need arbitrary composition, and because the proven blog pipeline already knows how to write and validate MDX.

```
src/content/case-studies/
  studies.ts                  ← typed registry (the spec sheet)
  destiny-ai-journal.mdx      ← narrative body only (sections 4–9)
  cuepilot.mdx
  ...
```

```ts
// src/content/case-studies/studies.ts
export type StudyArchetype =
  | 'product_build'      // full-stack app  → Destiny, YOVELA, Tocablox, Task Manager
  | 'ai_system'          // pipeline/agent  → CuePilot, Lead Agent, Medical OCR, WhatsApp
  | 'platform_frontend'  // scope-limited   → Nullzec
  | 'marketplace'        // two-sided       → SolarSathi, 3D Viewer
  | 'game'               // Flame/CustomPaint → MindMaze, Jungle Jump, Snow World
  | 'design_only'        // Coffee Delivery

export interface CaseStudy {
  slug: string
  projectId: string                 // FK → projects.ts (single source of truth)
  archetype: StudyArchetype
  published: string                 // ISO
  updated: string

  // ── Hero ──
  headline: string                  // OUTCOME-led, not the project name
  summary: string                   // 140–160 chars → meta description
  hero: {
    kind: 'phone' | 'browser' | 'dashboard' | 'split' | 'terminal'
    mockup: string                  // registry key → a mockup component
    caption: string
  }

  // ── Spec rail ──
  role: string[]                    // ['Design','Frontend','Backend','AI','Deploy']
  platforms: string[]
  stack: string[]                   // mirrors projects.ts tech, may be narrower
  duration?: string                 // only if genuinely known

  // ── Outcome band (Hero Data Density) ──
  metrics: {
    value: string; unit?: string; label: string
    source: 'brief' | 'projects.ts' | 'qualitative'   // traceability, enforced
  }[]

  // ── At a Glance — the AEO block. Mirrors the 30-project PDF exactly. ──
  glance: {
    businessProblem: string
    technicalChallenges: string
    engineeringSolution: string
    coreFeatures: string[]
    architecture: string            // "React Native (Expo) → FastAPI → Supabase"
    technicalHighlights: string[]
    businessValue: string
  }

  // ── Trust cascade ──
  testimonialId?: number            // FK → testimonials.ts (join on client+country)

  // ── Internal linking ──
  relatedService: 'web' | 'mobile' | 'ai'
  relatedPosts: string[]            // blog slugs
  relatedStudies: string[]

  faq: { q: string; a: string }[]
  seo: { primaryKeyword: string; secondary: string[] }

  /** Mirrors projects.ts. When true: no live/shipped/store claim anywhere. */
  hideStatus?: boolean
}
```

`glance` is deliberately the exact 7-field structure of your PDF. That structure is not just convenient — see §4.2 for why it is the single best AEO asset you have.

### 3.2 Page architecture

Twelve sections, mapping the late-stage buyer's evaluation sequence (does this work → at my scale → in my industry → what does implementation look like → what if it doesn't work):

```
┌─ 1  HERO ─────────────────────────────── dark band, full-bleed
│    eyebrow: CATEGORY · Industry · Country
│    h1: Project name
│    sub: one-sentence OUTCOME (never a tagline)
│    ▸ HERO MOCKUP — tilted device/browser, --shadow-mockup
│    spec rail: role · platforms · stack chips
│
├─ 2  OUTCOME BAND ─────────────────────── 3–4 big metrics, on the fold seam
│                                          (Pillar: Hero Data Density)
├─ 3  AT A GLANCE ──────────────────────── the 7-field <dl>   ◄── AEO GOLDMINE
│
├─ 4  THE PROBLEM ──────────────────────── narrative + "before" visual
├─ 5  THE CONSTRAINTS ──────────────────── annotated challenge list
├─ 6  HOW WE BUILT IT ──────────────────── ▸ ArchitectureDiagram (SVG) + prose
├─ 7  PRODUCT TOUR ─────────────────────── ▸ 2–3 mockups + annotation callouts
│                                          (the dwell-time section)
├─ 8  WHAT SHIPPED ─────────────────────── feature grid + metrics
│                                          ▸ SECONDARY CTA HERE (peak engagement)
├─ 9  TECH DECISIONS ───────────────────── "why X over Y"  ◄── CITATION MAGNET
├─ 10 TESTIMONIAL ──────────────────────── if one exists for this client
├─ 11 FAQ ──────────────────────────────── buyer questions (cost/time/risk/ownership)
└─ 12 NEXT ─────────────────────────────── CTA + related studies + related service
```

Plus: sticky left TOC with scroll-spy (desktop), `ScrollProgress` (already built), and a floating "Start a project" pill after 40% scroll.

**Archetype variants** — not every project supports all 12:

| Archetype | Sections | Required visuals |
|---|---|---|
| `product_build` | all 12 | phone mockup + architecture + product tour |
| `ai_system` | all 12, §7 becomes "Pipeline in motion" | architecture + flow + terminal/log mockup |
| `platform_frontend` | drop §9; §5 becomes "Scope & boundaries" | browser + dashboard mockup |
| `marketplace` | all 12, add "Both sides of the market" | split browser+phone + flow |
| `game` | drop §9; §7 becomes "Gameplay loop" | phone mockup + loop diagram |
| `design_only` | 9 sections; drop §6, §8, §9 | screen-flow strip, **no architecture** |
| `own_product` | drop §10; §4 becomes "Why we built this" | mockup + architecture |

This directly mirrors the blog agent's archetype system, which is proven to prevent template fatigue.

**Why `own_product` is its own archetype rather than `product_build`.** DAIROK AI, Cyber Agent, YOVELA and WizChat have no client, no customer brief, no delivery deadline, no handover and no testimonial. Run through the client template, four sections can only be filled by inventing a client outcome — the exact failure the claims and confidentiality layers exist to prevent. They get a "why we built this" spine, no testimonial section, and `hideStatus` enforced everywhere (all four are in-development or launching-soon; none may carry a shipped, live or store claim).

Implemented as `SECTION_PLAN` in [`studies.ts`](../wizcodes_next/src/content/case-studies/studies.ts) — one map read by the layout, the MDX validator and the agent's section planner, so the three cannot disagree.

### 3.3 The visual system — my recommendation, and why

You asked whether to keep SVG illustrations or move to mockups. The answer is **both, but re-scoped**. Your SVG kit is genuinely good engineering (dual-layer, fitchecked, SEO filenames) — it is just being asked to do a job it cannot do. An abstract flow diagram does not prove you built a product. A product surface does.

**Four tiers:**

#### Tier 1 — Product surface: CSS/JSX mockups in device frames ★ the hero
This is the recommendation. Not screenshots, not images.

| Reason | Detail |
|---|---|
| **NDA-safe** | `details.md §20.1` forbids publishing client internals, customer conversations, user data. A real screenshot of Nullzec's dashboard or Destiny's journal entries would violate your own guardrails. A representative CSS mockup does not. |
| **Nothing to screenshot** | 7 projects carry `hideStatus: true` (in-development). YOVELA/DAIROK/Cyber Agent/WizChat are unreleased. There is no shippable screenshot for a third of the corpus. |
| **Crawlable** | An LLM reading the page sees `Revenue $84.2k`, `Won`, `Negotiation` as *text*. A PNG is opaque to every answer engine. This is a large LLMO advantage that image mockups simply cannot match. |
| **Zero weight** | No LCP hit, no CDN, retina-perfect, responsive, themeable from your existing tokens. |
| **Already built** | `DashboardMockup`, `CopilotMockup`, `DestinyJournalMockup`, `NullzecMockup`, `PhoneFrame`, `BrowserFrame`. Two are orphaned. |
| **Interactive** | `DashboardMockup` already animates on tab change. That is your dwell-time lever, and no static image has it. |

Build a **mockup registry**: `src/components/mockups/index.ts` mapping a key → component, so `studies.ts` references `mockup: 'crm-dashboard'` and the agent never writes JSX. Target ~10 reusable mockups covering all 30 projects:

```
phone/    journal · chat · pet-game · wallet · movie-list · bmi · platformer
browser/  marketplace · crm-dashboard · security-dashboard · 3d-viewer · admin-table
system/   terminal-log · agent-trace · websocket-stream · ocr-extract
```

Rules (from the device-mockup research): **one frame style and one device generation across the whole site.** Mixing them is the single most common thing that makes an otherwise good set look careless. Prefer minimal/clay frames where the UI is the point; keep the realistic notched `PhoneFrame` for app heroes only.

#### Tier 2 — Architecture: a new SVG generator ★ highest ROI new build
Your PDF gives a machine-parseable architecture string for all 30:

```
"React Native (Expo) → FastAPI → AI services (Groq, Replicate, Edge TTS) → Supabase → Background workers"
"Browser → WebSockets → FastAPI → Whisper → LLM → React Dashboard"
"Scan Orchestrator → Security Tools → AI Analysis → Report Generator → Dashboard"
```

Add `src/lib/graphics/architecture.mjs` following the exact `kitGenerators.mjs` contract (`{ svg, alt, file }`, `standalone` flag, watermark, `charsFor` budgeting). Classify each node by layer (client / backend / AI / data / external / design) — the same colour coding your PDF already uses — and reuse `ACCENTS`. **30 indexable architecture diagrams from 30 one-line strings, fitchecked, zero LLM involvement.** They become image-search entry points and they are exactly what a technical buyer screenshots and shares.

#### Tier 3 — Evidence
- `MetricBand` — the outcome band. Reuse `OdometerCounter` (already built) so numbers count up on reveal.
- `BeforeAfter` — the PDF's `Business Problem` → `Business Value` is a literal before/after pair for all 30. Two-column, tone-coded.
- `Timeline` — already exists in the blog kit; reuse for delivery phases.

#### Tier 4 — Annotation ★ the differentiator
An `<Annotated>` wrapper that places numbered pins over a mockup with a matching legend below. This is what separates a portfolio from a case study: it shows you made *decisions*, not just pixels. Pins are absolutely positioned `%` coordinates in `studies.ts`; the legend is real HTML text, so it is crawlable and the whole thing degrades to a plain list on mobile.

#### What to explicitly avoid
- **Stock/AI-generated mockups** — generic imagery actively dilutes trust on the exact page where trust is the product.
- **Photographs of devices on desks** — dates instantly, adds weight, communicates nothing.
- **Video/GIF heroes** — LCP and CLS cost is real, and INP < 200ms / CLS < 0.1 is the 2026 bar.
- **Lottie / animation libraries** — you have zero animation dependencies today. Keep it that way; CSS is enough.

### 3.4 Design direction — premium SaaS, concretely

Your tokens are already good (`--shadow-mockup`, `--radius-lg`, the grain overlay, the ambient radial wash, category accents with proper `base`/`soft`/`ink` contrast roles). The case study kit should *use* them harder rather than introduce new ones. What actually creates the "premium" read:

1. **Band rhythm.** Alternate `--page-bg` / `--surface` / `--surface-navy` full-bleed bands. Today's case study is one continuous 51rem column — that alone is why it reads as an article. The hero and the "Next" band go dark; everything else stays light. Dark bands are where the mockups get their `--shadow-mockup` to actually read.
2. **Break the measure.** Prose stays at ~68ch, but mockups, architecture diagrams, and metric bands go **wider than the text column** (~1100px) or full-bleed. That contrast between narrow text and wide visual is 80% of the premium feel.
3. **Type scale.** Hero h1 at `clamp(2.6rem, 6vw, 4.5rem)` with `-0.045em` tracking. Section labels as small-caps eyebrows in `--text-muted` at `0.72rem / 0.14em`. Metric values at `clamp(2.5rem, 5vw, 4rem)`, weight 800, `--blue`. One display face, one text face — you already have Poppins only; keep it.
4. **Restraint on colour.** One accent per study, derived from `project.category` (`--cat-web` / `--cat-mobile` / `--cat-ai`). Everything else is ink and greys. A study that uses four accents looks like a template; one that uses one looks designed.
5. **Motion.** `RevealObserver` already exists. Add: hero mockup 3D tilt on scroll (reuse `useCardTilt`), metric odometers on reveal, architecture nodes staggering in. All gated by `useReducedMotion` (already built). Nothing that moves without user intent.
6. **The sticky rail.** Left TOC with scroll-spy on desktop ≥1200px; collapses to `ScrollProgress` below. Signals depth before the reader commits.

---

## Part 4 — SEO / GEO / AEO / LLMO

### 4.1 Query classes case studies win (that blogs do not)

| Class | Example | Why case studies win |
|---|---|---|
| Proof-seeking | `flutter game development company portfolio` | Late-stage buyers verify vendors, not categories |
| Industry-vertical | `software development for solar industry` | You have 11 industries in `projects.ts`, zero pages targeting them |
| Stack-specific | `langgraph agent case study` | Named-entity density |
| Build-story | `how was solarsathi built` | Genuinely unique content nobody else can write |
| Entity | `wizcodes projects`, `who built solarsathi` | Brand entity consolidation |

Research is consistent that when a buyer has narrowed to a shortlist, ~90% are comparing no more than two vendors. Case studies are the last page read before contact. They should be optimised for *verification*, not discovery.

### 4.2 The `glance` block is your best AEO asset ★

Answer engines chunk pages, embed the chunks, and retrieve whichever chunk is the most semantically self-contained match. They bypass narrative intros and grab the scannable answer-first block.

Your PDF's 7 fields are *already* seven self-contained, single-idea, answer-shaped chunks:

| Field | Answers the query |
|---|---|
| Business Problem | "why do companies build X" |
| Technical Challenges | "what's hard about building X" |
| Engineering Solution | "how do you build X" |
| Core Features | "what features does an X need" |
| Architecture Summary | "what stack for X" |
| Technical Highlights | "what makes X performant" |
| Business Value | "what's the ROI of X" |

Render it as a semantic `<dl>` near the top of every study, each `<dd>` a complete standalone sentence naming the entity ("Destiny AI Journal is…", not "It is…"). Thirty studies × 7 chunks = **210 independently retrievable, attributable facts.** That is the whole LLMO play, and it costs you a component.

Rule for the agent: **every `glance` value must be a complete sentence that survives being read with zero surrounding context.** No pronouns referring outside the field.

### 4.3 Schema

```jsonc
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Article",
      "@id": "https://wizcodes.site/work/<slug>#article",
      "headline": "<headline>",
      "description": "<summary>",
      "datePublished": "...", "dateModified": "...",
      "author":    { "@id": "https://wizcodes.site/#organization" },
      "publisher": { "@id": "https://wizcodes.site/#organization" },
      "isPartOf":  { "@id": "https://wizcodes.site/work#collection" },
      "about":     { "@id": "https://wizcodes.site/work/<slug>#product" },
      "mentions": [ /* one node per stack entity */ ],
      "image": { "@type": "ImageObject", "contentUrl": ".../opengraph-image", ... }
    },
    {
      "@type": "SoftwareApplication",
      "@id": "https://wizcodes.site/work/<slug>#product",
      "name": "<project.name>",
      "applicationCategory": "MobileApplication | WebApplication | GameApplication",
      "operatingSystem": "iOS, Android",
      "featureList": "<glance.coreFeatures joined>"
      // NO aggregateRating, NO offers — you have neither. Never invent them.
    },
    { "@type": "BreadcrumbList", ... },
    { "@type": "FAQPage", ... }   // LLM parsing only — see below
  ]
}
```

And on `/work`:
```jsonc
{ "@type": "CollectionPage", "@id": ".../work#collection",
  "mainEntity": { "@type": "ItemList", "numberOfItems": 30, "itemListElement": [...] } }
```

**Important accuracy note:** Google added a deprecation notice to FAQ structured data on 7 May 2026; FAQ rich results no longer appear in Search, the Search Console report and Rich Results Test support were removed in June 2026, and the API data goes in August 2026. `HowTo` has produced nothing on any surface since May 2026. Both remain *valid schema.org* and are still parsed by LLM crawlers. **Keep `FAQPage`, but stop counting it as an SEO lever.** Complete `Article` schema with proper author/organization/`about` is what feeds AI Overviews now.

Also note: Google's 2026 guidance explicitly says `llms.txt`, content chunking, and special schema are **not required** for generative search — standard SEO plus genuinely experience-driven content remains the reliable path. Treat everything in this section as compounding advantage, not a shortcut. Your real moat is that you have 30 projects nobody else can write about.

### 4.4 Concrete SEO tasks

1. **`llms.txt` — add a `## Case studies` section listing every published study with a one-line outcome.** Currently `/work` is mentioned and not one project is named. This is the biggest single LLMO gap on the site.
2. **`llms-full.txt` — append the full `glance` block for each study.** That file is exactly the right home for 210 extractable facts.
3. **`/work` gets `CollectionPage` + `ItemList`.**
4. **Per-study OG image** rendering the actual mockup + the top metric, not the generic template. Extend `src/lib/og-template.tsx`.
5. **Image sitemap**: register architecture SVGs in `manifest.json` under a `studies` key and emit them in `sitemap.ts` alongside the OG card (the mechanism already exists for blog charts).
6. **Internal link graph.** Today a case study links only to `/contact`. Enforce: ≥1 `/services/*`, ≥1 `/blog/*`, ≥2 `/work/*`, ≥1 `/testimonials`. And add reverse links — service pages and blog posts should link *into* case studies. This is the cheapest ranking gain available to you.
7. **Industry landing pages** (later): `/industries/healthcare` etc., each aggregating the studies in that vertical. You have 11 industries and zero pages for them.
8. **`STATIC_LASTMOD` in `sitemap.ts` is hand-maintained** and will go stale — derive `/work` and study `lastModified` from `studies.ts:updated`.
9. **Thin-page decision**: 20 projects render a ~120-word `ProjectSummary`. Either upgrade them through the kit over time, or `noindex` them until they have a study. Leaving 20 thin pages at priority 0.5 in the sitemap is the worse option.

---

## Part 5 — The Case Study Agent

### 5.1 Repo shape — LOCKED: separate repo + `sync-core`

`casestudy_agent` stays its own repo. `core/` is copied once from the blog agent, and a checked-in manifest of file hashes makes upstream drift **loud** rather than silent.

```
casestudy_agent/
  core/                  ← copied from blog_agent. Never edited here.
    config.py  llm/client.py  llm/sanitize.py  facts/snapshot.py  publish/git.py
    CORE_SOURCE.lock     ← sha256 of each file @ the blog_agent commit it came from
  casestudy/
    graph/  prompts/  queue.py  validators/  main.py
  briefs/                ← agent-drafted, human-corrected (see 5.3)
  Makefile               ← sync-core, check-core
  .github/workflows/
    publish-casestudy.yml   cron: monthly + workflow_dispatch
    check-core.yml          cron: weekly — fails if core/ is behind upstream
```

```makefile
BLOG ?= ../blog_agent
CORE := config.py llm/client.py llm/sanitize.py facts/snapshot.py

check-core:   ## fail if any core file drifted upstream — runs weekly in CI
	@python tools/core_sync.py check --upstream $(BLOG)

sync-core:    ## pull upstream changes in and restamp the lock
	@python tools/core_sync.py pull --upstream $(BLOG)
```

`core_sync.py` compares each file's sha256 against `CORE_SOURCE.lock`. `check` exits non-zero on any difference and prints the diff; `pull` copies the file in and restamps. The weekly workflow turns "the proxy fix never reached the case study agent" from a silent six-month bug into a failing check three days later.

Rule: **never edit anything under `core/` in this repo.** A case-study-specific need means a new file in `casestudy/`, not a fork of a core file — otherwise `sync-core` starts producing conflicts and the whole mechanism gets ignored.

The files worth syncing are the ones carrying non-obvious knowledge: `llm/client.py` (the CLI User-Agent, the injection-guard phrasing rules, the 2000-char prompt-caching threshold, the retry/backoff shape) and `facts/snapshot.py` (the tolerant TS regex extraction). `config.py` will diverge legitimately — different cadence knobs — so it is synced as a *review prompt*, not an overwrite.

### 5.2 The graph

```
load_corpus            deterministic — projects.ts + briefs/ + testimonials.ts + studies.ts
   ↓
select_subject         deterministic — scored priority queue, NO LLM
   ↓
load_brief             deterministic — the project's brief file + facts snapshot
   ↓
plan_study             LLM (Opus) — archetype, headline, angle, section plan, visual plan
   ↓
derive_spec            LLM (Opus) — → typed CaseStudy JSON (metrics, glance, role, stack)
   ↓
validate_spec ─────┐   deterministic — required fields, metric traceability, hideStatus
   ← replan ≤2 ────┘
   ↓
write_sections         LLM (Sonnet) — ONE CALL PER SECTION (copy the blog's chunking)
   ↓
compose_mdx            deterministic
   ↓
validate_mdx ──────┐   deterministic — the case study contract
   ← rewrite ≤2 ───┘
   ↓
confidentiality_scan   deterministic denylist  +  LLM adjudicator   → HARD ABORT
   ↓
claims_audit ──────┐   LLM — every number traceable to brief/projects.ts?
   ← fix_claims ───┘   surgical, budget 2, then ABORT (stricter than blog)
   ↓
humanize               best-effort, re-validate, never regress
   ↓
build_visuals          deterministic — ArchitectureDiagram SVG from glance.architecture
   ↓
seo_pack               LLM (Haiku) — title, description, FAQ, keywords
   ↓
open_pr                git: branch → commit .mdx + studies.ts entry → gh pr create
```

Nodes in bold-deterministic positions stay deterministic. That is the clearest lesson from the blog agent: `pick_focus()` fixed convergence precisely because it *stopped asking the LLM an open question*.

### 5.3 Briefs — LOCKED: agent-drafted, human-corrected

A separate one-shot command (`python -m casestudy.brief <project-id>`) drafts `briefs/<project-id>.md` from the PDF row + `projects.ts` + `testimonials.ts`. It never runs inside the publish pipeline — drafting and writing are separate jobs, so a brief is always reviewed before any prose is generated from it.

```markdown
# Destiny AI Journal
<!-- drafted 2026-07-22 from Project_Case_Studies.pdf p.2 + projects.ts -->

## Confidential — never publish
- [NEEDS REVIEW] anything the client considers private

## Safe to publish
- Client: Thomas, Canada. Industry: Mental Wellness.        (source: projects.ts)
- Voice AI narration                                        (source: projects.ts metrics[])
- Mood tracking & heatmaps                                  (source: projects.ts metrics[])
- RevenueCat billing integrated                             (source: projects.ts metrics[])
- [NEEDS REVIEW] May we name Thomas as the client in prose?
- [NEEDS REVIEW] Any real number for latency / entries / users?
- [NEEDS REVIEW] hideStatus is true — confirm no shipped/store claim anywhere.

## The story
- Why they came to us: [NEEDS REVIEW]
- What was hard: coordinating transcription → summarisation → TTS without
  visible latency                                           (source: PDF, Technical Challenges)
- What we decided and why: [NEEDS REVIEW] — PDF names Groq, Replicate, Edge TTS
  but gives no rationale
- What shipped: voice journaling, AI summaries, narration, mood tracking,
  social feed, subscriptions, auth                           (source: PDF, Core Features)

## Screens (mockup registry keys)
- phone/journal-entry, phone/mood-heatmap, phone/social-feed
```

Three rules make this safe:

1. **Every line carries a provenance tag or `[NEEDS REVIEW]`.** No untagged line is permitted — the drafter emits `[NEEDS REVIEW]` rather than a guess, always. The PDF says *what* was built; it never says what may be *published*, and it contains no rationale for any decision, so "why X over Y" is always `[NEEDS REVIEW]`.
2. **`[NEEDS REVIEW]` is a hard gate.** The writer refuses to run against a brief containing one. This is why drafting is a separate command: the agent can get 80% of 30 briefs written in an afternoon, and you clear the flags at the rate you publish.
3. **`## Confidential` is never shown to the writer.** It is fed only to the confidentiality scanner as a fuzzy denylist. That asymmetry is the whole mechanism that makes unattended generation safe.

Expected review load: ~5 flags per brief, ~5 minutes each. One brief per fortnight keeps pace with a 1–2/month cadence.

### 5.4 The selector (deterministic)

```python
score(project) = (
    3.0 * category_coverage_gap(project.category)     # fewest published studies wins
  + 2.5 * industry_coverage_gap(project.industry)     # 11 industries, mostly uncovered
  + 2.0 * has_testimonial(project)                    # trust cascade available
  + 1.5 * project.featured
  + 1.5 * has_brief(project)                          # hard gate, not just a score
  + 1.0 * links_to_underserved_service(project)
  - 3.0 * archetype_used_in_last_two_studies(project)  # anti-template rotation
)
```

Refuse to select anything without a brief. Log the full ranked queue every run so you can see what is coming.

### 5.5 The validators (`casestudy/validators/`)

**`spec.py`** — required fields; ≥3 metrics; every metric with `source != 'qualitative'` must string-match `projects.ts:metrics[]` or the brief; `glance.architecture` must parse into 2–6 arrow-separated nodes; `coreFeatures` 4–8 items; `testimonialId` must resolve.

**`confidentiality.py`** — **the most important file in the project.**
```python
FORBIDDEN_PATTERNS = [
    r"\$[\d,]+(?:k|m)?\s*(?:in\s+)?(?:revenue|arr|mrr|ad revenue)",
    r"\b\d+%\s*(?:conversion|retention|churn|growth)\b",   # unless in brief
    r"\b(api[_ ]?key|secret|token|credential|password)\b",
    r"\b(system prompt|prompt template|our prompt)\b",
    r"\b(unreleased|roadmap|upcoming feature|licensing)\b",
]
```
Plus: every line of every `## Confidential` brief section becomes a fuzzy denylist entry. Plus an LLM adjudicator asking only *"does this draft disclose anything a client would object to?"*. Any hit → **abort the run**. Never a warning, never a best-effort fix.

**`claims.py`** — extract every numeral and superlative; each must trace to brief / `projects.ts` / an allowlisted qualitative phrase. Untraceable → abort.

**`status.py`** — **the deterministic half already exists and runs today**: [`scripts/status-check.mjs`](../wizcodes_next/scripts/status-check.mjs), wired into `prebuild` and runnable standalone (`node scripts/status-check.mjs [slug]`). It was pulled out of Phase 5 because the risk it guards is not hypothetical: the first hand-written specimen shipped **four** release claims, written by someone actively trying to write none.

The original spec here was a literal phrase list (`live`, `shipped`, `launched`, `on the App Store`, `users are`). Every one of those four real misses would have walked straight past it:

| written | phrase list had | gap |
|---|---|---|
| "in the weeks after launch" | `launched` | wrong conjugation |
| "fixes reached users" | `users are` | wrong word order |
| "for both the App Store" | `on the App Store` | wrong preposition |
| "without waiting on a store review" | — | not on the list at all |

Four near-misses in one paragraph is not bad luck; it is what exact matching does against ordinary prose. Widening the *list* loses the same game to a fifth variant. So the approach changed, not the list:

1. **Stem families**, word-bounded — `launch/ship/release/download` across every conjugation. `\brelationship\b` and `\bshipping container\b` do not trip.
2. **Banned entities** — App Store, Play Store, Google Play, TestFlight, store listing/review/submission are rejected outright for a `hideStatus` study, with no verb required. There is no legitimate reason to discuss app-store distribution for something we make no distribution claim about.
3. **Ambiguous words matched only as phrases** — bare `live` is *not* a stem, because "the social feed needed live updates" is a correct sentence about realtime data. Only `went live` / `is live` / `now live` and friends match.

**Known false-positive class, accepted:** the `ship` stem catches the data-transfer sense ("the pipeline ships data between services"). Fail-closed is the right direction for a trust guard, the reword is trivial, and there is deliberately **no inline escape hatch** — an override on a safety check is how safety checks get neutered.

Phase 5 still adds an **LLM adjudicator** on top for the soft cases regex cannot reach cleanly: past-tense outcome claims, implied adoption, and testimonial-shaped statements about results. The deterministic layer is the floor, not the ceiling.

**`mdx.py`** — mirrors `seo/mdx_validator.py` with case-study rules: required section headings for the archetype; ≥2 visual components of ≥2 types; ≥1 must be a mockup; internal-link quotas; no raw `<`/`{`; word band 900–1800.

### 5.6 Publishing — PR, not push

```python
branch = f"case-study/{slug}"
# write src/content/case-studies/<slug>.mdx
# insert the typed entry into studies.ts
# commit, push branch
# gh pr create --title "Case study: {name}" --body <the review checklist>
```

PR body checklist — each line is a check that already ran, not a prompt to go and look:

| Line | Source |
|---|---|
| Metric traceability table (value → source → matched evidence) | `validators/claims.py` |
| Confidentiality scan: PASS + patterns tested | `validators/confidentiality.py` |
| Status guard: `hideStatus` respected | `validators/status.py` |
| **Architecture: N nodes, layers `client→backend→ai→data`, 0 errors / N warnings** | `architectureWarnings()` |
| Section word counts vs the archetype's band | `validators/mdx.py` |
| Internal links: ≥1 service, ≥1 blog, ≥2 studies | `validators/mdx.py` |
| Firebase preview channel URL | `deploy-preview.yml` |

The architecture line was missing until now, and the honest answer to "would a reviewer catch a wrong diagram?" was **no — only by eye, the way the Nullzec misclassification was actually caught.** It is now a deterministic check (see `architectureWarnings()` in `src/lib/graphics/architecture.mjs`): archetype↔layer coherence is a hard error, layer monoculture is a warning surfaced here. A reviewer confirms a flagged diagram rather than auditing every diagram.

Add a preview-channel workflow to `wizcodes_next` (`FirebaseExtended/action-hosting-deploy` with `channelId: pr-${{ github.event.number }}`) so every case study PR gets a live URL. That is the difference between reviewing a diff and reviewing a page.

---

## Part 6 — Sequencing

**Phase 1 — Frontend kit + the THREE gold specimens (no agent involved).**
Ship `studies.ts` + the route + `CaseStudyLayout` v2 + the 12 sections + `MetricBand` / `GlanceTable` / `ArchitectureDiagram` / `Annotated`. Wire the orphaned `BrowserFrame` and `NullzecMockup`. Then hand-write three specimens:

| # | Study | Archetype | What it is the first test of |
|---|---|---|---|
| 1 | Destiny AI Journal | `product_build` | The contract end to end; `hideStatus` prose rules |
| 2 | CuePilot | `ai_system` | `SECTION_PLAN` diverging by archetype; the testimonial join |
| 3 | **Cyber Agent** | `own_product` | "Constraints are chosen, not imposed"; `hideStatus` beating archetype on precedence |

Nothing else can be evaluated until these exist.

**Why Cyber Agent belongs in Phase 1, not after Phase 3.** It was originally slotted at the end of Phase 3, which was wrong on two counts. It is not a *migration* — there is no prior prose for it, the same blank-page situation Destiny and CuePilot started from, and the opposite of the Phase 3 four. And the two rules it exists to test currently live only as prose in this document, with nothing checking them; deferring it means the agent's dry run is the first time either rule meets real content.

It is also the first `hideStatus` study whose subject matter is technical enough to trip the accepted `ship`-stem false positive for real rather than hypothetically — which is a genuine data point on whether fail-closed is the right setting.

Why a third specimen rather than trusting the prompt rule: both preceding studies have a client, a scope boundary, and a testimonial. `own_product` has none of the three. An agent pattern-matching client studies will reach for client framing on DAIROK and WizChat, and the "constraints are chosen, not imposed" rule has nothing to check itself against. The same argument that justified Destiny and CuePilot applies with more force here, because `own_product` is the archetype that *differs most* from what the agent will have seen.

**Cyber Agent specifically**, over the other three:
- Clearest "why we built this" — a tool built to solve our own problem (security assessments fragmented across ten tools), which is exactly the narrative spine the archetype needs to demonstrate.
- It contains the trap. Its own description says it "automatically delivers a detailed PDF report to the client" — an implied client relationship that will pull a writer straight into client-outcome framing. A specimen that dodges the failure mode teaches nothing.
- Its architecture is a pipeline (`Scan Orchestrator → Security Tools → AI Analysis → Report Generator → Dashboard`), structurally unlike the app shapes in the other six.

**Explicitly not YOVELA.** Its architecture is `React Native → FastAPI → Supabase → AI Services → Mobile Application` — essentially Destiny's stack, in the journaling domain. It would validate nothing new and risks two specimens reading near-identically, which is the exact convergence failure the blog agent already had to engineer `pick_focus()` around.

**Phase 2 — Mockup library.** ~10 reusable mockups + the registry. This is the design-heavy phase and the one that determines whether the site reads as premium. Entries land opportunistically as the studies that need them do, rather than all at once against a schema that has not met real content.

**Phase 3 — Migrate the remaining 4** existing studies (Tocablox, Nullzec, SolarSathi, AI Lead Agent) through the kit. These are migrations of existing prose, not blank-page writing, which is why they sit *after* the three specimens rather than among them.

**Phase 4 — SEO/GEO layer.** Schema graph, `llms.txt` sections, `CollectionPage`, per-study OG, image sitemap, reverse internal links.

**Phase 5 — The agent.** `core/` extraction, selector, validators, graph, PR publisher. Run in dry-run against a project that already has a hand-built study and diff the output against your own writing — that is the only honest quality bar.

**Phase 6 — Cadence.** Monthly cron. Write one brief every two weeks. 24 studies ≈ 12–24 months.

---

## Part 7 — Site-wide observations (beyond case studies)

1. **`BrowserFrame` and `NullzecMockup` are fully built with zero usages.** Free premium visual surface.
2. **13 real testimonials, none attached to a project.** Join on `client` + `clientCountry` and surface them on `/work/<slug>` — highest-trust asset on the highest-intent page.
3. **`/work` has no `CollectionPage` schema** and no industry/stack facets. It has category + country filters; industry is the axis buyers actually search.
4. **20 thin `ProjectSummary` pages** at sitemap priority 0.5. Decide: upgrade or `noindex`.
5. **`llms.txt` names no project.** One `## Case studies` section is the cheapest LLMO win available.
6. **`STATIC_LASTMOD` is a hand-maintained constant.** Derive it.
7. **FAQ rich results are gone (May 2026).** Your `FAQ.tsx` emits `FAQPage` on every post — keep it for LLM parsing, but re-plan any SERP expectations around it.
8. **No preview deploys.** Every merge to `main` goes straight to production. A PR preview channel is ~10 lines of YAML and becomes essential once the case study agent opens PRs.
9. **`fitcheck` only runs on exported graphics.** Once mockups carry real text, consider a lightweight overflow check on them too — or accept that they use real CSS layout and cannot clip the way string-built SVG does. (The latter is true; this is an argument *for* CSS mockups.)
10. **`export-graphics.mjs` hardcodes `CASE_STUDY_SLUGS`** (line 204). That set must become derived from `studies.ts` or it will silently drift the moment the agent publishes.
11. **Blog and case studies will compete** for some queries (`react native vs flutter` post vs a Flutter case study). Set canonical intent per topic and cross-link deliberately rather than letting them cannibalise.

---

## Open asks — running ledger

Every commitment made in conversation that is not yet done, with where it lands. Added
because two items (the `own_product` specimen and the SolarSathi bug) were actioned in
PLAN.md but omitted from the round's summary — which from the outside is
indistinguishable from having dropped them. A plan this size cannot ride on either
party's memory of a chat.

**Rule: nothing leaves this table by being finished quietly.** An item moves to
~~struck~~ with the round it shipped in, or it stays.

| # | Ask | Lands | Status |
|---|---|---|---|
| 1 | `own_product` gold specimen — Cyber Agent, hand-built | ~~Phase 1~~ | ✅ Round 6 |
| 2 | SolarSathi `url`-before-`slug` precedence bug | ~~Phase 3~~ | ✅ Round 8 — a written study now beats an external URL |
| 3 | Own-products get no hero SVG (`readProjects()` scans client region only) | Phase 3 | Tracked, §Known issues |
| 4 | `own_product` constraints framing — "chosen, not imposed" | Phase 5 prompts | Tracked, §3.2 |
| 5 | Status checker: widen from literal phrases to stem families + banned entities | ~~Round 5~~ | ✅ `scripts/status-check.mjs` |
| 6 | Pull deterministic status checking forward out of Phase 5 | ~~Round 5~~ | ✅ runs in `prebuild` |
| 7 | CuePilot specimen (`ai_system`) | ~~Phase 1~~ | ✅ Round 5 |
| 8 | Study JSON-LD (`Article` + `SoftwareApplication` + `mentions`) | ~~Phase 1~~ | ✅ Round 6 — `src/lib/studySchema.ts`, plus `CollectionPage` on /work |
| 9 | Per-study OG image | ~~Phase 1~~ | ✅ Round 6 — headline + top metric + stack chips |
| 10 | Sticky TOC + `Annotated` component | Phase 1 | Open |
| 11 | `relatedStudies` backfill on Destiny once siblings exist | ~~Phase 3~~ | ✅ Round 6 |
| 12 | hideStatus-beats-archetype precedence is **still untested** — the two override maps share no key | When an archetype overrides `shipped` | Open |
| 13 | `ship`-stem false positive **not yet observed in real prose** — Cyber Agent did not trip it | Revisit if it fires | Open |
| 14 | `llms.txt` + `llms-full.txt` case-study sections | ~~Phase 4~~ | ✅ Round 7 — generated in `prebuild` by `scripts/gen-llms.mjs` |
| 15 | Study architecture diagrams in the image sitemap | ~~Phase 4~~ | ✅ Round 7 — work routes now read `manifest.charts` |
| 16 | Reverse internal links (service pages linking INTO studies) | ~~Phase 4~~ | ✅ Round 10 — `StudyLinks` on all 3 service pages |
| 20 | Delete the dead `CASE_STUDY_CONTENT` literal + `LegacyCaseStudyLayout` | ~~Next round~~ | ✅ Round 10 |
| 21 | **Phase 5 agent scaffolded and self-testing.** Remaining: write 23 briefs, then first live run | Phase 5 | In progress |
| 22 | SolarSathi brief must whitelist the illustrative "25 kW" figure | With SolarSathi's brief | Open — live true-positive in `make selftest` |
| 17 | Sticky TOC + `Annotated` component | ~~Phase 1~~ | ✅ Round 8 — **Phase 1 kit complete** |
| 18 | Phase 3 migrations: Nullzec, SolarSathi, AI Lead Agent, Tocablox | ~~Phase 3~~ | ✅ Round 9 — **all 6 legacy studies migrated; `CASE_STUDY_CONTENT` is now empty** |
| 19 | Pre-existing lint error in `OdometerCounter.tsx` (setState in effect) — untouched by this work | Unscheduled | Open |

---

## Known issues, deferred

| Issue | Detail | Fix when |
|---|---|---|
| **`ProjectCard` links SolarSathi off-site instead of to its case study** | [`ProjectCard.tsx:61-78`](../wizcodes_next/src/components/ProjectCard.tsx) checks `project.url` **before** `project.slug`. SolarSathi is the only project carrying both (`url: 'https://solarsathi.co.in'` + `slug: 'solarsathi'`), so in the unfiltered `/work` grid its card leaves the site. Currently masked because SolarSathi is in `FEATURED_IDS` and usually renders through `FeaturedCaseCard`, which links to `/work/<slug>` correctly. | **Phase 3, when SolarSathi's study is migrated.** Invert the precedence to slug-before-url for any project with a written study, keeping url-first for projects without one. Found during the own-product slug audit, 2026-07-22. |
| **Own-products get no hero SVG** | `readProjects()` in [`export-graphics.mjs:140`](../wizcodes_next/scripts/export-graphics.mjs) regex-scans only the `rawClientProjects` region of `projects.ts`; products come from `products.ts`. Harmless — `ProjectSummary` degrades to no hero — but the four product pages have no image resource. | Phase 3, alongside the Cyber Agent specimen. |

---

## Locked decisions (2026-07-22)

1. **Repo shape** — separate `casestudy_agent` repo. `core/` copied once + `make sync-core` + a weekly `check-core` CI job. See §5.1.
2. **Brief authorship** — agent drafts `briefs/<id>.md` from the PDF; anything unverifiable (real numbers, outcome claims, permission to name a client) is emitted as `[NEEDS REVIEW]`, never guessed. `[NEEDS REVIEW]` blocks the writer. See §5.3.
3. **Own products** — same kit, dedicated `own_product` archetype: "why we built this" instead of a client outcome, no `testimonial` section, `hideStatus` enforced throughout. See §3.2. **Blocker: [projects.ts:428](../wizcodes_next/src/data/projects.ts) deliberately gives own-products no `slug`; that must be reversed before an own-product study can route.**
4. **Screenshots** — none, on any project, ever. Not a default: a constraint the whole visual system is designed around. There is no `screenshot` hero kind in the schema and there will not be one. Tier 1 mockups + `ArchitectureDiagram` carry all 30.
5. **Cadence** — coverage-gap-first (category + industry), not chronological. The selector's weights already encode this.

### Writing style — applies to everything the agent emits

Briefs, `glance` fields, section prose, FAQ answers, SEO pack. Simple and direct, never dense or corporate. The bar is whether a passage gets **cited by an answer engine**, not whether it reads well.

- **Self-contained sentences.** Every sentence must survive being lifted out of the page with zero surrounding context. Name the entity; never open a `glance` field or a section with a pronoun pointing outside it.
- **Answer first.** Each section opens with the claim, then the explanation. Answer engines skip narrative build-up and take the scannable block.
- **One idea per paragraph.** Chunk boundaries are what retrieval operates on; a paragraph carrying three ideas retrieves badly for all three.
- **Specifics wherever the brief permits, qualitative where it does not.** Never split the difference with a vague number.
- **No filler.** No throat-clearing openers, no empty adjectives (robust, seamless, cutting-edge, powerful), no triplets used as padding.
- Inherit the readability rules already encoded in `STUDIO_PERSONA` (blog agent `prompts/library.py:182`) — short sentences, plain words, active voice, terms explained on first use. They were tuned against this exact audience and they extract well for the same reason they read well.
