# Noorly

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Nothing. The owner has confirmed there is no confidential material
  for this project beyond what is already withheld from projects.ts.

## Safe to publish

- Client: Artem, Belarus   (source: projects.ts)
  Artem is already published in projects.ts and rendered on
  the live /work pages, so naming them here discloses nothing new.
- Industry: Productivity   (source: projects.ts)
- Stack: Flutter, Dart   (source: projects.ts)
- Scope: Feature scope is shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- A testimonial exists for this client and will be joined automatically.

## Metrics — PROJECTED, not measured

Local-first storage makes search and profile lookups near-instant; cloud sync where used is incremental rather than blocking, so the app stays responsive on poor connections.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: Managing professional and personal contacts across multiple apps becomes fragmented and difficult to maintain.   (source: deck)
- What was hard: Designing intuitive contact organization, fast search, responsive performance, and cross-platform consistency.   (source: deck)
- How we solved it: Built a clean contact management application with organized profiles and simplified networking workflows.   (source: deck)
- Technical highlights: Cross-platform optimization; Responsive UI; Efficient data organization   (source: deck)
- Architecture: Flutter → Local Storage / Cloud APIs   (source: deck)
- Business value: Simplifies relationship management and improves productivity.   (source: deck)
- What we decided and why: Contact apps are opened for quick lookups, not sustained sessions, so any lag on search is disproportionately annoying. Keeping data local-first with optional cloud sync avoids making every open dependent on network state.   (source: owner)
- What was delivered: Contact organiser that makes personal networking simple - a clean, cross-platform way to keep track of who you know.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
