# Medical OCR System

<!-- drafted by casestudy.brief from projects.ts — review before use -->

## Confidential — never publish

- Medical documents and patient-related information remain confidential.
  (owner-supplied; fed to the confidentiality scanner as a denylist,
   never shown to the writer)

## Safe to publish

- Client country: India   (source: projects.ts)
  Client is deliberately unnamed in projects.ts; the owner's scope note
  above governs what may be published.
- Industry: Healthcare   (source: projects.ts)
- Stack: Python, Document AI, OCR, FastAPI, LLM   (source: projects.ts)
- Medical-grade accuracy   (source: projects.ts metrics[])
- Complex form processing   (source: projects.ts metrics[])
- Structured output   (source: projects.ts metrics[])
- Scope: OCR processing architecture and the AI-assisted validation pipeline are shareable.   (source: owner)
- hideStatus is not set in projects.ts, so release language is permitted.
  projects.ts is the source of truth for this and is kept current.
- No testimonial for this client in testimonials.ts. The section will
  not render; add one there first if that is wrong.

## Metrics — PROJECTED, not measured

AI-assisted OCR combined with a validation stage should significantly reduce manual data entry time while minimising the transcription errors common to fully automated OCR.   (source: owner, projected)

Every figure above is a design target or an expected characteristic.
Nobody instrumented this project and recorded a number. Any figure
taken from here must be written as a TARGET or a design goal —
"targeting 60 FPS", not "sustained 60 FPS". A measured-sounding claim
built on a projection is the failure this separation exists to stop.

## The story

- Why they came to us: Manual processing of complex medical questionnaires consumed significant time and increased the risk of data entry errors.   (source: deck)
- What was hard: OCR accuracy, handling multi-page documents, extracting structured information, validation, AI-assisted corrections, and secure document processing.   (source: deck)
- How we solved it: Built an OCR pipeline capable of extracting structured JSON from complex medical documents using AI-assisted validation and processing.   (source: deck)
- Technical highlights: AI-assisted OCR; Document parsing; Validation pipeline; Scalable processing architecture   (source: deck)
- Architecture: Document Upload → OCR Engine → AI Processing → Validation → Structured JSON Output   (source: deck)
- Business value: Significantly reduces manual processing effort while improving consistency and structured data extraction.   (source: deck)
- What we decided and why: Medical questionnaires often contain handwritten or inconsistently formatted information, which makes raw OCR unreliable in production. Adding an AI-assisted validation stage before structured JSON output improves accuracy and makes the extracted data immediately consumable downstream.   (source: owner)
- What was delivered: Advanced OCR pipeline for a medical agency. Processes complex multi-page questionnaires and deep medical forms with structured JSON output and validation layers.   (source: projects.ts)

## Screens (mockup registry keys)

- Set at PR time, not here. The agent emits mockup: 'REVIEW-ME' and
  the PR is where a real key is chosen from
  src/components/mockups/index.tsx. Deliberately not a blocking flag:
  the brief gate exists for FACTS — permission, numbers, rationale —
  and a missing mockup is a completeness issue caught at review, not a
  truth issue that should block writing.
