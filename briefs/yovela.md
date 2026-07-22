# YOVELA

<!-- drafted by casestudy.brief from products.ts — review before use -->

## Confidential — never publish

- User journal entries remain private.
- Emotional content of user entries remains private.
  (owner-supplied; fed to the confidentiality scanner as a denylist,
   never shown to the writer)

## Safe to publish

- No client recorded in products.ts. Own product.
- Stack: React Native, Expo, FastAPI, Supabase, AI   (source: products.ts)
- Scope: A WizCodes-owned product. Only the platform architecture is shareable.   (source: owner)
- hideStatus is not set in products.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- No testimonial for this client in testimonials.ts. The section will
  not render; add one there first if that is wrong.

## Metrics — PROJECTED, not measured

Emotion-based matching should help users find relevant communities and conversations more effectively than a generic social feed, while granular privacy controls encourage journaling by letting users decide what is shared.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: People increasingly seek a safe platform to journal, express emotions, and connect with others who share similar experiences while maintaining privacy.   (source: deck)
- What was hard: AI-assisted journaling, secure authentication, emotion matching, scalable social feed, privacy controls, notification systems, and mobile performance.   (source: deck)
- How we solved it: Developed a social journaling platform combining AI-powered journaling, emotion-based peer discovery, social interactions, and fine-grained privacy settings.   (source: deck)
- Technical highlights: AI integration; Emotion-based recommendations; Scalable backend; Cross-platform architecture; Modern mobile UX   (source: deck)
- Architecture: React Native → FastAPI → Supabase → AI Services → Mobile Application   (source: deck)
- Business value: Creates a supportive digital journaling community while empowering users with AI-assisted self-reflection.   (source: deck)
- What we decided and why: Social journaling means balancing personal privacy against meaningful interaction. Fine-grained privacy controls let users set visibility per entry, and emotion-based matching connects people through shared experience rather than an engagement-driven feed algorithm.   (source: owner)
- What was delivered: A social platform where every feeling is valid. Share daily experiences as journals, connect with people going through similar emotions, and build a community around honest expression.   (source: products.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
