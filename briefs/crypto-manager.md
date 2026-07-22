# Crypto Manager

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Nothing. The owner has confirmed there is no confidential material
  for this project beyond what is already withheld from projects.ts.

## Safe to publish

- Client: Traffic Cat Org, Belarus   (source: projects.ts)
  Traffic Cat Org is already published in projects.ts and rendered on
  the live /work pages, so naming them here discloses nothing new.
- Industry: Finance   (source: projects.ts)
- Stack: React Native, Web3, Crypto APIs   (source: projects.ts)
- Scope: The non-custodial architecture is a security-relevant design decision and is fully shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- No testimonial for this client in testimonials.ts. The section will
  not render; add one there first if that is wrong.

## Metrics — PROJECTED, not measured

Non-custodial architecture eliminates custody risk for the platform operator by keeping private keys under user control. Multi-chain portfolio synchronization should refresh balances within a few seconds of blockchain confirmation.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: Cryptocurrency users need a secure, non-custodial way to manage multiple digital assets without relying on centralized exchanges.   (source: deck)
- What was hard: Multi-chain support, portfolio synchronization, wallet security, transaction tracking, responsive UI.   (source: deck)
- How we solved it: Developed a portfolio manager and wallet following a non-custodial architecture with multi-coin support.   (source: deck)
- Technical highlights: Non-custodial architecture; Secure wallet integration; Scalable API connectivity   (source: deck)
- Architecture: React Native → Crypto APIs → Blockchain Services   (source: deck)
- Business value: Enables users to monitor digital assets securely while retaining complete control over their funds.   (source: deck)
- What we decided and why: Holding user private keys or funds sharply increases regulatory responsibility and security risk. A non-custodial architecture where the app only reads blockchain data, and users retain their keys, minimises operational liability without sacrificing usability.   (source: owner)
- What was delivered: Non-custodial cryptocurrency wallet and portfolio tracker. Sparrow-style architecture with multi-coin support.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
