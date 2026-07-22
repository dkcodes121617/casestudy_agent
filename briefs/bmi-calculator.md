# Body Mirror Pro

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Nothing. The owner has confirmed there is no confidential material
  for this project beyond what is already withheld from projects.ts.

## Safe to publish

- Client: Artem, Belarus   (source: projects.ts)
  Artem is already published in projects.ts and rendered on
  the live /work pages, so naming them here discloses nothing new.
- Industry: Health & Fitness   (source: projects.ts)
- Stack: Flutter, Dart   (source: projects.ts)
- Scope: Product architecture and visualization approach are shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- A testimonial exists for this client and will be joined automatically.

## Metrics — PROJECTED, not measured

All calculations execute entirely on-device with no network communication, so results appear immediately after user input.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: BMI calculations alone are difficult for users to understand without clear visual interpretation.   (source: deck)
- What was hard: Presenting health information intuitively, maintaining responsive visualizations, simple user experience.   (source: deck)
- How we solved it: Built an application combining BMI calculations with engaging visual feedback and simplified health metrics.   (source: deck)
- Technical highlights: Interactive visualizations; Optimized rendering; Lightweight calculations   (source: deck)
- Architecture: Flutter → Local Calculations → Mobile UI   (source: deck)
- Business value: Helps users better understand BMI information through visual representation.   (source: deck)
- What we decided and why: BMI calculation is simple arithmetic that gains nothing from server-side processing. Routing it through a backend would only add latency and failure points. Engineering effort went into meaningful visual interpretation rather than unnecessary infrastructure.   (source: owner)
- What was delivered: BMI calculator with an engaging, visual interface that makes the numbers easy to read at a glance.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
