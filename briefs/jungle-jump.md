# Jungle Jump

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Nothing. The owner has confirmed there is no confidential material
  for this project beyond what is already withheld from projects.ts.

## Safe to publish

- Client: Jodie Wayatt, United Kingdom   (source: projects.ts)
  Jodie Wayatt is already published in projects.ts and rendered on
  the live /work pages, so naming them here discloses nothing new.
- Industry: Gaming   (source: projects.ts)
- Stack: Flutter, Flame Engine, Dart   (source: projects.ts)
- Scope: Gameplay architecture, optimization techniques, and engineering decisions are shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- A testimonial exists for this client and will be joined automatically.

## Metrics — PROJECTED, not measured

Optimized physics and collision handling should sustain a consistent frame rate, targeting 60 FPS on mid-range mobile hardware.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: The client wanted an enjoyable 2D platformer with responsive controls, fair difficulty progression, and engaging gameplay.   (source: deck)
- What was hard: Physics tuning, collision detection, animation performance, level balancing, and maintaining smooth gameplay on mobile devices.   (source: deck)
- How we solved it: Developed a lightweight platformer with optimized physics, structured level progression, and responsive controls.   (source: deck)
- Technical highlights: Physics optimization; Efficient collision handling; Reusable game architecture; Optimized animation rendering   (source: deck)
- Architecture: Flutter → Flame Engine → Game Loop   (source: deck)
- Business value: Provides an entertaining mobile gaming experience with polished mechanics and scalable level design.   (source: deck)
- What we decided and why: Platform games are extremely sensitive to input latency and inconsistent physics — even a slight delay in jump response hurts the game. Careful tuning of physics and collision detection was essential because the whole experience depends directly on those systems.   (source: owner)
- What was delivered: 2D platformer mobile game with smooth physics, progressive difficulty, and satisfying level design.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
