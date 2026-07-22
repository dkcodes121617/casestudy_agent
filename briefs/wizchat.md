# WizChat

<!-- drafted by casestudy.brief from products.ts — review before use -->

## Confidential — never publish

- Customer and community data remain confidential.
  (owner-supplied; fed to the confidentiality scanner as a denylist,
   never shown to the writer)

## Safe to publish

- No client recorded in products.ts. Own product.
- Stack: React, WebSockets, Node.js, Redis   (source: products.ts)
- Scope: A WizCodes-owned product. Platform architecture is shareable.   (source: owner)
- hideStatus is not set in products.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- No testimonial for this client in testimonials.ts. The section will
  not render; add one there first if that is wrong.

## Metrics — PROJECTED, not measured

A Redis-backed WebSocket architecture should support low-latency real-time messaging as concurrent users and channels increase, scaling better than a single-server socket implementation.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: Teams and communities require a lightweight real-time communication platform that combines messaging, channels, and media sharing without unnecessary complexity.   (source: deck)
- What was hard: Real-time messaging, WebSocket scalability, file sharing, synchronization, notification delivery, and responsive cross-device experience.   (source: deck)
- How we solved it: Built a modern communication platform supporting instant messaging, channels, media sharing, and scalable real-time collaboration.   (source: deck)
- Technical highlights: Low-latency communication; Scalable WebSocket architecture; Efficient message synchronization; Modular backend services   (source: deck)
- Architecture: React → Node.js → WebSockets → Redis → Database   (source: deck)
- Business value: Provides a clean and scalable communication platform suitable for teams, communities, and collaborative environments.   (source: deck)
- What we decided and why: Scalable real-time messaging needs publish/subscribe infrastructure that distributes messages across multiple application instances. Redis fills that role by decoupling publication from delivery, so the platform scales horizontally without an architectural redesign as usage grows.   (source: owner)
- What was delivered: A powerful communication platform with real-time messaging, channels, and collaboration tools — built and deployed by WizCodes.   (source: products.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
