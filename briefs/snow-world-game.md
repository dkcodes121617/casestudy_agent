# Snow World

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Nothing. The owner has confirmed there is no confidential material
  for this project beyond what is already withheld from projects.ts.

## Safe to publish

- Client: Anna, Ukraine   (source: projects.ts)
  Anna is already published in projects.ts and rendered on
  the live /work pages, so naming them here discloses nothing new.
- Industry: Gaming   (source: projects.ts)
- Stack: Flutter, Dart, Google Ads   (source: projects.ts)
- Scope: Gameplay architecture, monetization strategy, and performance optimization techniques are shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- A testimonial exists for this client and will be joined automatically.

## Metrics — PROJECTED, not measured

Carefully timed advertisement placement, rather than interruptive mid-game interstitials, should preserve gameplay performance while reducing the perceived intrusiveness that commonly leads to player frustration and uninstalls.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: The client wanted a casual mobile game capable of generating revenue while maintaining enjoyable gameplay.   (source: deck)
- What was hard: Integrating advertisements without interrupting gameplay, maintaining frame rates, balancing progression, and ensuring smooth user experience.   (source: deck)
- How we solved it: Built a snow-themed casual game with optimized gameplay loops and carefully integrated advertisement placements.   (source: deck)
- Technical highlights: Advertisement integration; Performance optimization; Smooth rendering pipeline   (source: deck)
- Architecture: Flutter → Game Engine → Google Ads Integration   (source: deck)
- Business value: Combines enjoyable gameplay with sustainable monetization while preserving user experience.   (source: deck)
- What we decided and why: Advertising SDKs frequently introduce frame drops and UI interruptions when integrated without planning. Engineering focused specifically on when and where ads appear relative to gameplay state, balancing monetisation against player experience.   (source: owner)
- What was delivered: Snow-themed casual 2D game for Android and iOS with smooth gameplay and ad-based monetisation built in.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
