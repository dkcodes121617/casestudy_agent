# MindMaze Junior

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Nothing. The owner has confirmed there is no confidential material
  for this project beyond what is already withheld from projects.ts.

## Safe to publish

- Client: Ulyanovich, Poland   (source: projects.ts)
  Ulyanovich is already published in projects.ts and rendered on
  the live /work pages, so naming them here discloses nothing new.
- Industry: Education   (source: projects.ts)
- Stack: Flutter, CustomPaint, Dart   (source: projects.ts)
- Scope: Game architecture, rendering techniques, and cross-platform engineering approach are shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- A testimonial exists for this client and will be joined automatically.

## Metrics — PROJECTED, not measured

Zero third-party packages plus CustomPaint rendering means consistent behaviour across all six target platforms (Android, iOS, Web, Windows, Linux, macOS) with no per-platform plugin compatibility risk, and a smaller long-term maintenance surface.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: Parents wanted an educational game that helps young children learn through interactive gameplay without requiring reading skills or internet connectivity.   (source: deck)
- What was hard: Designing child-friendly interactions, maintaining smooth performance across six platforms, creating reusable game logic, and ensuring intuitive gameplay.   (source: deck)
- How we solved it: Built a cross-platform educational game using custom rendering without external dependencies, ensuring consistent behavior across Android, iOS, Web, Windows, Linux, and macOS.   (source: deck)
- Technical highlights: CustomPaint rendering; Zero third-party packages; Multi-platform deployment; Optimized rendering pipeline   (source: deck)
- Architecture: Flutter → CustomPaint Rendering Engine → Local Storage   (source: deck)
- Business value: Delivers engaging educational gameplay while minimizing maintenance and maximizing platform reach.   (source: deck)
- What we decided and why: Third-party Flutter packages frequently lag on niche platform support, particularly Linux and Windows, or break after framework updates. Building the rendering layer directly on CustomPaint eliminates those dependency risks entirely. It cost more engineering effort up front and removed an entire class of cross-platform compatibility issues.   (source: owner)
- What was delivered: Educational game for children ages 3+. Four game modes, custom CustomPaint rendering, zero external packages. Targets Android, iOS, Web, Windows, Linux, macOS.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
