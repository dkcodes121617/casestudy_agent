"""Owner-supplied brief material: permission, projected metrics, and rationale.

The three things `deck.py` cannot contain, supplied by the studio owner on
2026-07-22. Kept separate from deck.py because the deck is a transcription of a
document and this is a judgement record — they have different provenance and
different review lifecycles.

── The `metrics` field is PROJECTED, and that word is load-bearing ──

Every figure here is a design target or an expected characteristic, not a measured
outcome. Nobody instrumented these projects and recorded a number.

That distinction is invisible to `validators/claims.py`, which checks whether a
number is TRACEABLE, not whether it is framed honestly. "60 FPS" traced to this
file passes the validator whether the draft says "targeting 60 FPS" or "sustained
60 FPS" — and only one of those is true.

So the framing rule lives in two places instead:
  - the brief renders this section under a heading that says PROJECTED, and
  - `prompts/library.py` instructs the writer to render any figure from it as a
    target or design goal, never as an achieved result.

If a real measured number ever exists for a project, it belongs in `projects.ts`
metrics[] with source "projects.ts" — not here.
"""
from __future__ import annotations

# key = project id. `confidential` becomes the scanner denylist; it is NEVER
# shown to the writer.
BRIEF_DATA: dict[str, dict] = {
    "noorly": {
        "shareable": "Feature scope is shareable.",
        "confidential": [],
        "metrics": "Local-first storage makes search and profile lookups near-instant; cloud sync where used is incremental rather than blocking, so the app stays responsive on poor connections.",
        "rationale": "Contact apps are opened for quick lookups, not sustained sessions, so any lag on search is disproportionately annoying. Keeping data local-first with optional cloud sync avoids making every open dependent on network state.",
    },
    "tiny-talk-hub": {
        "shareable": "Product architecture, messaging workflow, and engineering approach are shareable.",
        "confidential": [],
        "metrics": "Lightweight architecture should keep app size and cold-start time meaningfully lower than feature-bloated competitors, translating to faster installs and a better first-open experience.",
        "rationale": "The explicit brief was that existing apps are bloated, so the engineering answer is subtractive: fewer dependencies, a narrower feature surface, and a messaging-only backend rather than a general-purpose communications platform. That keeps both the bundle and the interface simple.",
    },
    "cine-duniya": {
        "shareable": "Application architecture, content delivery approach, and feature scope are shareable.",
        "confidential": [],
        "metrics": "Optimized rendering and API-backed catalog browsing should keep scroll and search interactions smooth as the catalog grows, avoiding the performance issues typical of large-list applications.",
        "rationale": "Content discovery apps live or die on browsing experience. If scrolling a large catalog stutters, users lose interest quickly. A dedicated content API plus rendering optimization addresses that directly instead of over-engineering unrelated features.",
    },
    "vistara": {
        "shareable": "Application architecture, reusable UI strategy, and API design are shareable.",
        "confidential": [],
        "metrics": "Reusable UI components and a dedicated API layer should reduce load times on search and recommendation screens compared to a monolithic, screen-specific implementation.",
        "rationale": "Movie discovery apps contain highly repetitive interface patterns — poster grids, detail pages. Building reusable components and supplying them through a consistent API layer reduces both development effort and runtime inconsistency across the app.",
    },
    "task-manager": {
        "shareable": "System architecture, synchronization strategy, and technical implementation are shareable.",
        "confidential": [],
        "metrics": "Firebase real-time synchronization should propagate task updates to all team members within roughly 1-2 seconds of a change, effectively eliminating stale views in collaborative workspaces.",
        "rationale": "Team collaboration tools fail when users act on inconsistent information. Firebase's real-time listeners solve that synchronization problem without custom polling or WebSocket infrastructure, so every member works from the same project state.",
    },
    "crypto-manager": {
        "shareable": "The non-custodial architecture is a security-relevant design decision and is fully shareable.",
        "confidential": [],
        "metrics": "Non-custodial architecture eliminates custody risk for the platform operator by keeping private keys under user control. Multi-chain portfolio synchronization should refresh balances within a few seconds of blockchain confirmation.",
        "rationale": "Holding user private keys or funds sharply increases regulatory responsibility and security risk. A non-custodial architecture where the app only reads blockchain data, and users retain their keys, minimises operational liability without sacrificing usability.",
    },
    "bmi-calculator": {
        "shareable": "Product architecture and visualization approach are shareable.",
        "confidential": [],
        "metrics": "All calculations execute entirely on-device with no network communication, so results appear immediately after user input.",
        "rationale": "BMI calculation is simple arithmetic that gains nothing from server-side processing. Routing it through a backend would only add latency and failure points. Engineering effort went into meaningful visual interpretation rather than unnecessary infrastructure.",
    },
    "coffee-delivery": {
        "shareable": "A design-only engagement. The design process, wireframes, interactive prototypes, and UX methodology are shareable.",
        "confidential": [],
        "metrics": "A validated prototype allows usability problems such as confusing checkout flows and unclear ordering states to be found before development begins, where changes are far cheaper to make.",
        "rationale": "Building the whole app before validating the ordering experience risks expensive redesign mid-development. Delivering wireframes, high-fidelity mockups and an interactive prototype enables usability testing early, so engineering is only invested after the experience is validated.",
    },
    "mindmaze-junior": {
        "shareable": "Game architecture, rendering techniques, and cross-platform engineering approach are shareable.",
        "confidential": [],
        "metrics": "Zero third-party packages plus CustomPaint rendering means consistent behaviour across all six target platforms (Android, iOS, Web, Windows, Linux, macOS) with no per-platform plugin compatibility risk, and a smaller long-term maintenance surface.",
        "rationale": "Third-party Flutter packages frequently lag on niche platform support, particularly Linux and Windows, or break after framework updates. Building the rendering layer directly on CustomPaint eliminates those dependency risks entirely. It cost more engineering effort up front and removed an entire class of cross-platform compatibility issues.",
    },
    "jungle-jump": {
        "shareable": "Gameplay architecture, optimization techniques, and engineering decisions are shareable.",
        "confidential": [],
        "metrics": "Optimized physics and collision handling should sustain a consistent frame rate, targeting 60 FPS on mid-range mobile hardware.",
        "rationale": "Platform games are extremely sensitive to input latency and inconsistent physics — even a slight delay in jump response hurts the game. Careful tuning of physics and collision detection was essential because the whole experience depends directly on those systems.",
    },
    "bubble-io": {
        "shareable": "Game architecture, scoring system, and animation optimization techniques are shareable.",
        "confidential": [],
        "metrics": "Lightweight local score storage and optimized animation handling should keep the game responsive to rapid touch input with minimal dropped frames.",
        "rationale": "Casual arcade games are replayed dozens of times in one session, which makes responsiveness critical. Keeping score calculations local and optimising the animation pipeline avoids unnecessary delay and keeps play consistently smooth.",
    },
    "snow-world-game": {
        "shareable": "Gameplay architecture, monetization strategy, and performance optimization techniques are shareable.",
        "confidential": [],
        "metrics": "Carefully timed advertisement placement, rather than interruptive mid-game interstitials, should preserve gameplay performance while reducing the perceived intrusiveness that commonly leads to player frustration and uninstalls.",
        "rationale": "Advertising SDKs frequently introduce frame drops and UI interruptions when integrated without planning. Engineering focused specifically on when and where ads appear relative to gameplay state, balancing monetisation against player experience.",
    },
    "detective-game": {
        "shareable": "Game architecture, mission system design, and scalability approach are shareable.",
        "confidential": [],
        "metrics": "Modular mission architecture should allow new investigation scenarios to be added without restructuring the game, enabling faster long-term content expansion than a hard-coded level system.",
        "rationale": "Story-driven games need a content pipeline that outlives the initial release. Structuring missions as reusable modules makes future updates significantly easier, reduces maintenance cost, and supports continuous content growth.",
    },
    "cubbi": {
        "shareable": "The application architecture and engineering implementation are shareable.",
        "confidential": [
            "Specific business workflow details remain confidential.",
        ],
        "metrics": "A workflow-specific full-stack solution should significantly reduce the manual steps and workarounds previously required when adapting generic software to specialised business processes.",
        "rationale": "When commercial software fails to fit a unique operational workflow, businesses compensate with spreadsheets and manual process. Building a tailored React, Node.js and PostgreSQL solution replaced those workarounds with maintainable business logic designed for the organisation's actual requirements.",
    },
    "3d-model-viewer": {
        "shareable": "Rendering pipeline, asset streaming architecture, and WebGL optimization techniques are shareable.",
        "confidential": [],
        "metrics": "Progressive asset streaming and WebGL optimization should let large 3D models become interactive before the complete asset finishes downloading, reducing perceived loading time on slower connections.",
        "rationale": "Browser-based 3D rendering is computationally demanding, and loading full-resolution assets before rendering would significantly delay interaction. Streaming assets progressively and optimising the rendering pipeline addresses that directly and improves responsiveness across a wide device range.",
    },
    "ai-business-platform": {
        "shareable": "Platform architecture and modular system design are shareable.",
        "confidential": [
            "Operational and financial business data remain confidential.",
        ],
        "metrics": "Consolidating expense management, operational workflows and AI-powered automation into one platform should reduce manual reconciliation and remove the need to switch between disconnected business applications.",
        "rationale": "The primary business problem was operational fragmentation caused by separate tools managing different workflows. Designing a modular but unified platform addressed that directly, letting teams work from a single system rather than introducing another isolated application.",
    },
    "custom-crm-platform": {
        "shareable": "CRM architecture, automation engine, and role-based access implementation are shareable.",
        "confidential": [
            "Specific sales workflows remain confidential.",
        ],
        "metrics": "Consolidating lead management, customer records and pipeline tracking into one platform should significantly reduce manual data re-entry and the context switching caused by multiple disconnected SaaS tools.",
        "rationale": "Generic CRM platforms could not model the organisation's sales process accurately. Rather than configuring around rigid third-party limits, the solution implemented workflow-specific business logic, role-based permissions, and an automation engine that enforces the operational process instead of merely storing customer data.",
    },
    "medical-ocr": {
        "shareable": "OCR processing architecture and the AI-assisted validation pipeline are shareable.",
        "confidential": [
            "Medical documents and patient-related information remain confidential.",
        ],
        "metrics": "AI-assisted OCR combined with a validation stage should significantly reduce manual data entry time while minimising the transcription errors common to fully automated OCR.",
        "rationale": "Medical questionnaires often contain handwritten or inconsistently formatted information, which makes raw OCR unreliable in production. Adding an AI-assisted validation stage before structured JSON output improves accuracy and makes the extracted data immediately consumable downstream.",
    },
    "ai-whatsapp-automation": {
        "shareable": "WhatsApp Business API integration and automation architecture are shareable.",
        "confidential": [
            "Customer conversations remain confidential.",
        ],
        "metrics": "AI-powered first-response automation should reduce customer response times from hours to near-instant for common inquiries, and enable booking and lead capture without human intervention.",
        "rationale": "Customers prefer messaging on WhatsApp rather than switching platforms. Integrating the official WhatsApp Business API with FastAPI services and AI-driven response generation gives reliable, compliant automation while keeping conversation context across interactions.",
    },
    "ai-game-guide": {
        "shareable": "Gameplay guidance architecture, recommendation engine, and adaptive onboarding strategy are shareable.",
        "confidential": [],
        "metrics": "Context-aware onboarding guidance should reduce early player drop-off compared to static tutorials by adapting recommendations to each player's progress and behaviour.",
        "rationale": "Traditional tutorials treat every player identically regardless of skill. Tracking gameplay events and feeding them to an adaptive recommendation engine gives personalised guidance that responds to how someone is actually playing, rather than a fixed instructional sequence.",
    },
    "dairok-ai": {
        "shareable": "A WizCodes-owned product. The agent architecture and risk-control approach are shareable.",
        "confidential": [
            "Trading strategy details remain commercially sensitive.",
            "Live performance metrics remain commercially sensitive.",
        ],
        "metrics": "Paper trading and historical backtesting give a controlled environment for evaluating strategies before deploying real capital. The emphasis is validation and risk management, not advertised profitability.",
        "rationale": "Autonomous trading systems need extensive verification before handling live funds. Making paper trading and historical backtesting first-class components enables iterative strategy improvement, while LangGraph structures market analysis, decision-making and risk controls as transparent, auditable workflows instead of one opaque process.",
    },
    "yovela": {
        "shareable": "A WizCodes-owned product. Only the platform architecture is shareable.",
        "confidential": [
            "User journal entries remain private.",
            "Emotional content of user entries remains private.",
        ],
        "metrics": "Emotion-based matching should help users find relevant communities and conversations more effectively than a generic social feed, while granular privacy controls encourage journaling by letting users decide what is shared.",
        "rationale": "Social journaling means balancing personal privacy against meaningful interaction. Fine-grained privacy controls let users set visibility per entry, and emotion-based matching connects people through shared experience rather than an engagement-driven feed algorithm.",
    },
    "wizchat": {
        "shareable": "A WizCodes-owned product. Platform architecture is shareable.",
        "confidential": [
            "Customer and community data remain confidential.",
        ],
        "metrics": "A Redis-backed WebSocket architecture should support low-latency real-time messaging as concurrent users and channels increase, scaling better than a single-server socket implementation.",
        "rationale": "Scalable real-time messaging needs publish/subscribe infrastructure that distributes messages across multiple application instances. Redis fills that role by decoupling publication from delivery, so the platform scales horizontally without an architectural redesign as usage grows.",
    },
}


def entry(project_id: str) -> dict | None:
    return BRIEF_DATA.get(project_id)
