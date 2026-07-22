# Task Manager

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Nothing. The owner has confirmed there is no confidential material
  for this project beyond what is already withheld from projects.ts.

## Safe to publish

- Client: Traffic Cat Org, Belarus   (source: projects.ts)
  Traffic Cat Org is already published in projects.ts and rendered on
  the live /work pages, so naming them here discloses nothing new.
- Industry: Productivity   (source: projects.ts)
- Stack: Flutter, Firebase, Dart   (source: projects.ts)
- Scope: System architecture, synchronization strategy, and technical implementation are shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- No testimonial for this client in testimonials.ts. The section will
  not render; add one there first if that is wrong.

## Metrics — PROJECTED, not measured

Firebase real-time synchronization should propagate task updates to all team members within roughly 1-2 seconds of a change, effectively eliminating stale views in collaborative workspaces.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: Teams struggle to coordinate tasks, monitor deadlines, and track work progress across multiple tools.   (source: deck)
- What was hard: Real-time synchronization, task ownership, deadline management, scalable data organization, team collaboration.   (source: deck)
- How we solved it: Built a centralized task management platform supporting assignments, tracking, and collaborative workflows.   (source: deck)
- Technical highlights: Firebase synchronization; Scalable architecture; Collaborative workflows   (source: deck)
- Architecture: Flutter → Firebase → Cloud Database → Authentication   (source: deck)
- Business value: Improves team productivity by centralizing project management.   (source: deck)
- What we decided and why: Team collaboration tools fail when users act on inconsistent information. Firebase's real-time listeners solve that synchronization problem without custom polling or WebSocket infrastructure, so every member works from the same project state.   (source: owner)
- What was delivered: B2B productivity app for team task management, deadline tracking, and progress reporting.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
