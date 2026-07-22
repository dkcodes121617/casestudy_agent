# Vistara

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Nothing. The owner has confirmed there is no confidential material
  for this project beyond what is already withheld from projects.ts.

## Safe to publish

- Client: Artem, Belarus   (source: projects.ts)
  Artem is already published in projects.ts and rendered on
  the live /work pages, so naming them here discloses nothing new.
- Industry: Entertainment   (source: projects.ts)
- Stack: Flutter, Dart   (source: projects.ts)
- Scope: Application architecture, reusable UI strategy, and API design are shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- A testimonial exists for this client and will be joined automatically.

## Metrics — PROJECTED, not measured

Reusable UI components and a dedicated API layer should reduce load times on search and recommendation screens compared to a monolithic, screen-specific implementation.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: Movie discovery applications often suffer from cluttered interfaces and inconsistent cross-platform performance.   (source: deck)
- What was hard: Fast content loading, clean navigation, scalable UI architecture, responsive layouts.   (source: deck)
- How we solved it: Developed a streamlined movie discovery application prioritizing simplicity and performance.   (source: deck)
- Technical highlights: Performance optimization; Reusable UI components; Cross-platform consistency   (source: deck)
- Architecture: Flutter → API Layer → Mobile Application   (source: deck)
- Business value: Makes discovering movies faster and more enjoyable.   (source: deck)
- What we decided and why: Movie discovery apps contain highly repetitive interface patterns — poster grids, detail pages. Building reusable components and supplying them through a consistent API layer reduces both development effort and runtime inconsistency across the app.   (source: owner)
- What was delivered: Modern movie discovery app with a clean, responsive interface, built for performance across platforms.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
