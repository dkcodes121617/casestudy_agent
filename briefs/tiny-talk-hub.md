# Tiny Talk Hub

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Nothing. The owner has confirmed there is no confidential material
  for this project beyond what is already withheld from projects.ts.

## Safe to publish

- Client: Kristina, Ukraine   (source: projects.ts)
  Kristina is already published in projects.ts and rendered on
  the live /work pages, so naming them here discloses nothing new.
- Industry: Communication   (source: projects.ts)
- Stack: Flutter, Dart   (source: projects.ts)
- Scope: Product architecture, messaging workflow, and engineering approach are shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- A testimonial exists for this client and will be joined automatically.

## Metrics — PROJECTED, not measured

Lightweight architecture should keep app size and cold-start time meaningfully lower than feature-bloated competitors, translating to faster installs and a better first-open experience.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: Existing communication applications often become bloated with unnecessary functionality, reducing usability.   (source: deck)
- What was hard: Delivering smooth messaging, minimizing UI complexity, maintaining responsive performance across devices.   (source: deck)
- How we solved it: Built a lightweight messaging application focused on speed and simplicity.   (source: deck)
- Technical highlights: Lightweight architecture; Optimized rendering; Clean mobile UX   (source: deck)
- Architecture: Flutter → Backend Messaging Services   (source: deck)
- Business value: Enables fast and intuitive communication without overwhelming users.   (source: deck)
- What we decided and why: The explicit brief was that existing apps are bloated, so the engineering answer is subtractive: fewer dependencies, a narrower feature surface, and a messaging-only backend rather than a general-purpose communications platform. That keeps both the bundle and the interface simple.   (source: owner)
- What was delivered: Lightweight cross-platform communication app built for smooth, responsive everyday conversations.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
