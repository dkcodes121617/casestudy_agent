# Custom CRM Platform

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Specific sales workflows remain confidential.
  (owner-supplied; fed to the confidentiality scanner as a denylist,
   never shown to the writer)

## Safe to publish

- Client: Jacob, Nigeria   (source: projects.ts)
  Jacob is already published in projects.ts and rendered on
  the live /work pages, so naming them here discloses nothing new.
- Industry: CRM & Business Automation   (source: projects.ts)
- Stack: Web, REST API, Automation   (source: projects.ts)
- Scope: CRM architecture, automation engine, and role-based access implementation are shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- A testimonial exists for this client and will be joined automatically.

## Metrics — PROJECTED, not measured

Consolidating lead management, customer records and pipeline tracking into one platform should significantly reduce manual data re-entry and the context switching caused by multiple disconnected SaaS tools.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: The client relied on multiple disconnected SaaS tools that failed to match their unique sales and customer management workflow.   (source: deck)
- What was hard: Designing flexible CRM modules, workflow automation, scalable APIs, role-based access control, reporting dashboards, and seamless data management.   (source: deck)
- How we solved it: Developed a custom CRM platform tailored to the client's business processes, consolidating lead management, customer records, sales pipelines, and automation into one system.   (source: deck)
- Technical highlights: Modular architecture; Reusable APIs; Scalable business workflows; Role-based permissions; Responsive dashboard design   (source: deck)
- Architecture: Web Frontend → REST APIs → Backend Services → Database → Automation Engine   (source: deck)
- Business value: Eliminates dependency on multiple SaaS products while improving operational efficiency and workflow consistency.   (source: deck)
- What we decided and why: Generic CRM platforms could not model the organisation's sales process accurately. Rather than configuring around rigid third-party limits, the solution implemented workflow-specific business logic, role-based permissions, and an automation engine that enforces the operational process instead of merely storing customer data.   (source: owner)
- What was delivered: Custom CRM built around one client workflow - leads, customers, pipelines, and business automation in a single place instead of several SaaS subscriptions.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
