# AI Game Guide

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Nothing. The owner has confirmed there is no confidential material
  for this project beyond what is already withheld from projects.ts.

## Safe to publish

- Client: Jacob, Nigeria   (source: projects.ts)
  Jacob is already published in projects.ts and rendered on
  the live /work pages, so naming them here discloses nothing new.
- Industry: Gaming   (source: projects.ts)
- Stack: AI, 3D Game, LLM   (source: projects.ts)
- Scope: Gameplay guidance architecture, recommendation engine, and adaptive onboarding strategy are shareable.   (source: owner)
- hideStatus is TRUE in projects.ts: no live, shipped, launched, released
  or app-store claim may appear anywhere in the study.
- A testimonial exists for this client and will be joined automatically.

## Metrics — PROJECTED, not measured

Context-aware onboarding guidance should reduce early player drop-off compared to static tutorials by adapting recommendations to each player's progress and behaviour.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: New players often struggle during onboarding, reducing engagement and increasing early abandonment in complex games.   (source: deck)
- What was hard: Context-aware recommendations, AI decision-making, gameplay event tracking, scalable inference, and responsive integration into the game environment.   (source: deck)
- How we solved it: Built an AI assistant that analyzes player progress and provides contextual guidance, tutorials, and recommendations during gameplay.   (source: deck)
- Technical highlights: Context-aware AI; Gameplay analytics; Scalable recommendation system; Lightweight integration   (source: deck)
- Architecture: Game Engine → AI Service → Recommendation Engine → Player Interface   (source: deck)
- Business value: Improves player onboarding and overall engagement by providing personalized in-game assistance.   (source: deck)
- What we decided and why: Traditional tutorials treat every player identically regardless of skill. Tracking gameplay events and feeding them to an adaptive recommendation engine gives personalised guidance that responds to how someone is actually playing, rather than a fixed instructional sequence.   (source: owner)
- What was delivered: In-game AI assistant for a 3D title that walks new players through onboarding and suggests what to do next based on how they are playing.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
