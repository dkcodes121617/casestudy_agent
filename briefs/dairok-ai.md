# DAIROK AI

<!-- drafted by casestudy.brief from products.ts — review before use -->

## Confidential — never publish

- Trading strategy details remain commercially sensitive.
- Live performance metrics remain commercially sensitive.
  (owner-supplied; fed to the confidentiality scanner as a denylist,
   never shown to the writer)

## Safe to publish

- No client recorded in products.ts. Own product.
- Stack: Python, FastAPI, Bybit API, LangGraph, Technical Analysis, React   (source: products.ts)
- Scope: A WizCodes-owned product. The agent architecture and risk-control approach are shareable.   (source: owner)
- hideStatus is not set in products.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- No testimonial for this client in testimonials.ts. The section will
  not render; add one there first if that is wrong.

## Metrics — PROJECTED, not measured

Paper trading and historical backtesting give a controlled environment for evaluating strategies before deploying real capital. The emphasis is validation and risk management, not advertised profitability.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: Crypto traders require continuous market monitoring and disciplined execution, which is difficult to maintain manually.   (source: deck)
- What was hard: Market analysis, autonomous decision-making, exchange integration, risk management, backtesting, portfolio tracking, and scalable architecture.   (source: deck)
- How we solved it: Built an AI-powered trading platform capable of analyzing markets, selecting trading opportunities, managing risk, and supporting paper trading and historical testing.   (source: deck)
- Technical highlights: Agentic AI workflows; Technical analysis pipeline; Modular trading engine; Scalable backend   (source: deck)
- Architecture: LangGraph Agents → Trading Engine → Bybit APIs → Analytics Dashboard   (source: deck)
- Business value: Establishes the foundation for an intelligent autonomous trading platform focused on disciplined decision-making.   (source: deck)
- What we decided and why: Autonomous trading systems need extensive verification before handling live funds. Making paper trading and historical backtesting first-class components enables iterative strategy improvement, while LangGraph structures market analysis, decision-making and risk controls as transparent, auditable workflows instead of one opaque process.   (source: owner)
- What was delivered: Connects to Bybit, analyzes market conditions, selects the best-performing coins, and trades autonomously on your behalf. Full portfolio management with risk controls built-in.   (source: products.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
