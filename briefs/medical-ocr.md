# Medical OCR System

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- [NEEDS REVIEW] Anything this client would object to seeing published.
  One bullet per item. These are fed to the confidentiality scanner
  as a denylist and are NEVER shown to the writer.

## Safe to publish

- Client country: India   (source: projects.ts)
- [NEEDS REVIEW] Client kept confidential in projects.ts — confirm that still holds.
- Industry: Healthcare   (source: projects.ts)
- Stack: Python, Document AI, OCR, FastAPI, LLM   (source: projects.ts)
- Medical-grade accuracy   (source: projects.ts metrics[])
- Complex form processing   (source: projects.ts metrics[])
- Structured output   (source: projects.ts metrics[])
- [NEEDS REVIEW] Any REAL number we may cite? Latency, volume, timeline, team size.
  Leave this empty rather than estimating — the claims validator
  rejects any numeral it cannot trace back to here or to projects.ts.
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- [NEEDS REVIEW] No testimonial found. If one exists, add it to testimonials.ts first.

## The story

- Why they came to us: Manual processing of complex medical questionnaires consumed significant time and increased the risk of data entry errors.   (source: deck)
- What was hard: OCR accuracy, handling multi-page documents, extracting structured information, validation, AI-assisted corrections, and secure document processing.   (source: deck)
- How we solved it: Built an OCR pipeline capable of extracting structured JSON from complex medical documents using AI-assisted validation and processing.   (source: deck)
- Technical highlights: AI-assisted OCR; Document parsing; Validation pipeline; Scalable processing architecture   (source: deck)
- Architecture: Document Upload → OCR Engine → AI Processing → Validation → Structured JSON Output   (source: deck)
- Business value: Significantly reduces manual processing effort while improving consistency and structured data extraction.   (source: deck)
- What we decided and why, X over Y: [NEEDS REVIEW]
  THE deck names the technologies but never says why one was chosen
  over another. No data file records rationale. This is the section
  that makes a case study worth reading, and it can only come from you.
  Two or three decisions is enough. If there genuinely were none worth
  writing about, say so and the archetype will drop the section.
- What was delivered: Advanced OCR pipeline for a medical agency. Processes complex multi-page questionnaires and deep medical forms with structured JSON output and validation layers.   (source: projects.ts)

## Screens (mockup registry keys)

- [NEEDS REVIEW] Which mockups should this study use?
  See src/components/mockups/index.tsx in the site repo for the
  current keys. If none fit, that mockup needs building first.
