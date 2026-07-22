# AI WhatsApp Automation

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Customer conversations remain confidential.
  (owner-supplied; fed to the confidentiality scanner as a denylist,
   never shown to the writer)

## Safe to publish

- Client: CraftWorks, United Kingdom   (source: projects.ts)
  CraftWorks is already published in projects.ts and rendered on
  the live /work pages, so naming them here discloses nothing new.
- Industry: Customer Support   (source: projects.ts)
- Stack: Python, WhatsApp Business API, LLM, FastAPI   (source: projects.ts)
- Scope: WhatsApp Business API integration and automation architecture are shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- A testimonial exists for this client and will be joined automatically.

## Metrics — PROJECTED, not measured

AI-powered first-response automation should reduce customer response times from hours to near-instant for common inquiries, and enable booking and lead capture without human intervention.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: Businesses manually handled customer inquiries, appointment scheduling, and lead capture, resulting in slower response times.   (source: deck)
- What was hard: WhatsApp API integration, conversation management, AI response generation, backend integration, scalability, and secure messaging workflows.   (source: deck)
- How we solved it: Developed an AI-powered WhatsApp assistant capable of automating customer communication, booking management, and lead qualification.   (source: deck)
- Technical highlights: AI conversation management; Workflow automation; API integration; Scalable backend services   (source: deck)
- Architecture: WhatsApp Business API → FastAPI → LLM → Backend Services → Database   (source: deck)
- Business value: Improves customer response times while reducing manual support workload.   (source: deck)
- What we decided and why: Customers prefer messaging on WhatsApp rather than switching platforms. Integrating the official WhatsApp Business API with FastAPI services and AI-driven response generation gives reliable, compliant automation while keeping conversation context across interactions.   (source: owner)
- What was delivered: AI-powered WhatsApp assistant that handles customer conversations, bookings, and lead capture automatically, wired into a custom backend.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
