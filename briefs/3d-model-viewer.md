# 3D Model Viewer Marketplace

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Nothing. The owner has confirmed there is no confidential material
  for this project beyond what is already withheld from projects.ts.

## Safe to publish

- No client recorded in projects.ts. No client field recorded; the owner's scope note above governs.
- Industry: Marketplace   (source: projects.ts)
- Stack: React, Three.js, WebGL, Node.js   (source: projects.ts)
- Real-time 3D rendering   (source: projects.ts metrics[])
- WebGL-powered   (source: projects.ts metrics[])
- Broker tools   (source: projects.ts metrics[])
- Scope: Rendering pipeline, asset streaming architecture, and WebGL optimization techniques are shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- No testimonial for this client in testimonials.ts. The section will
  not render; add one there first if that is wrong.

## Metrics — PROJECTED, not measured

Progressive asset streaming and WebGL optimization should let large 3D models become interactive before the complete asset finishes downloading, reducing perceived loading time on slower connections.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: Real estate agencies and product businesses required an interactive method of presenting 3D assets online instead of static images.   (source: deck)
- What was hard: Rendering complex 3D models efficiently, optimizing WebGL performance, managing large assets, and maintaining responsive interaction.   (source: deck)
- How we solved it: Developed a browser-based marketplace combining real-time 3D visualization with asset management and sharing capabilities.   (source: deck)
- Technical highlights: WebGL optimization; Asset streaming; Responsive rendering; Modular frontend architecture   (source: deck)
- Architecture: React → Three.js → WebGL → Node.js Backend   (source: deck)
- Business value: Enhances product visualization and improves customer engagement through immersive 3D experiences.   (source: deck)
- What we decided and why: Browser-based 3D rendering is computationally demanding, and loading full-resolution assets before rendering would significantly delay interaction. Streaming assets progressively and optimising the rendering pipeline addresses that directly and improves responsiveness across a wide device range.   (source: owner)
- What was delivered: Interactive 3D model viewer and marketplace for real estate and product brokers. Real-time WebGL rendering, asset management, and broker-to-client sharing workflows.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
