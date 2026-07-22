# Bubble.IO

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Nothing. The owner has confirmed there is no confidential material
  for this project beyond what is already withheld from projects.ts.

## Safe to publish

- No client recorded in projects.ts. No client field recorded; the owner's scope note above governs.
- Industry: Gaming   (source: projects.ts)
- Stack: React Native, Animated API   (source: projects.ts)
- Scope: Game architecture, scoring system, and animation optimization techniques are shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- No testimonial for this client in testimonials.ts. The section will
  not render; add one there first if that is wrong.

## Metrics — PROJECTED, not measured

Lightweight local score storage and optimized animation handling should keep the game responsive to rapid touch input with minimal dropped frames.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: Casual mobile games often lose player engagement because progression becomes repetitive over time.   (source: deck)
- What was hard: Designing addictive gameplay loops, balancing increasing difficulty, maintaining responsive animations, and optimizing performance.   (source: deck)
- How we solved it: Built an arcade-style bubble game with progressive difficulty, score tracking, and responsive touch controls.   (source: deck)
- Technical highlights: Optimized animation handling; Lightweight rendering; Responsive touch interactions   (source: deck)
- Architecture: React Native → Animated API → Local Score Storage   (source: deck)
- Business value: Creates an enjoyable casual gaming experience with replayability and minimal resource usage.   (source: deck)
- What we decided and why: Casual arcade games are replayed dozens of times in one session, which makes responsiveness critical. Keeping score calculations local and optimising the animation pipeline avoids unnecessary delay and keeps play consistently smooth.   (source: owner)
- What was delivered: 2D bubble arcade game with score tracking and increasing difficulty mechanics.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
