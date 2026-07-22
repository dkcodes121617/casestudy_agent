# WizChat

<!-- drafted by casestudy.brief from products.ts — review before use -->

## Confidential — never publish

- [NEEDS REVIEW] Anything this client would object to seeing published.
  One bullet per item. These are fed to the confidentiality scanner
  as a denylist and are NEVER shown to the writer.

## Safe to publish

- No client recorded in products.ts. Own product.
- Stack: React, WebSockets, Node.js, Redis   (source: products.ts)
- [NEEDS REVIEW] Any REAL number we may cite? Latency, volume, timeline, team size.
  Leave this empty rather than estimating — the claims validator
  rejects any numeral it cannot trace back to here or to projects.ts.
- hideStatus is not set in products.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- [NEEDS REVIEW] No testimonial found. If one exists, add it to testimonials.ts first.

## The story

- Why they came to us: Teams and communities require a lightweight real-time communication platform that combines messaging, channels, and media sharing without unnecessary complexity.   (source: deck)
- What was hard: Real-time messaging, WebSocket scalability, file sharing, synchronization, notification delivery, and responsive cross-device experience.   (source: deck)
- How we solved it: Built a modern communication platform supporting instant messaging, channels, media sharing, and scalable real-time collaboration.   (source: deck)
- Technical highlights: Low-latency communication; Scalable WebSocket architecture; Efficient message synchronization; Modular backend services   (source: deck)
- Architecture: React → Node.js → WebSockets → Redis → Database   (source: deck)
- Business value: Provides a clean and scalable communication platform suitable for teams, communities, and collaborative environments.   (source: deck)
- What we decided and why, X over Y: [NEEDS REVIEW]
  THE deck names the technologies but never says why one was chosen
  over another. No data file records rationale. This is the section
  that makes a case study worth reading, and it can only come from you.
  Two or three decisions is enough. If there genuinely were none worth
  writing about, say so and the archetype will drop the section.
- What was delivered: A powerful communication platform with real-time messaging, channels, and collaboration tools — built and deployed by WizCodes.   (source: products.ts)

## Screens (mockup registry keys)

- [NEEDS REVIEW] Which mockups should this study use?
  See src/components/mockups/index.tsx in the site repo for the
  current keys. If none fit, that mockup needs building first.
