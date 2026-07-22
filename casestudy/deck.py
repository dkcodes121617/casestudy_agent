"""Project reference data, transcribed from Project_Case_Studies.pdf.

The deck records seven fields per project — business problem, technical challenges,
engineering solution, core features, architecture, technical highlights, business
value. That is the studio's own document, so it is a legitimate source, and it
answers a large part of what a brief needs.

Why this file exists rather than the drafter guessing: before it, every brief came
back with "why they came to us: [NEEDS REVIEW]" and "what was hard: [NEEDS REVIEW]"
even though the deck answers both. That put nine flags on a brief where two would
do, and a nine-flag brief does not get filled in.

WHAT THE DECK STILL DOES NOT CONTAIN, and no amount of transcription will add:
  - rationale. It says Groq was used; it never says why Groq over anything else.
  - permission. It says who the client is; it never says what may be published.
  - real numbers beyond the handful already in projects.ts metrics[].

Those stay [NEEDS REVIEW] in every brief, permanently and by design.
"""
from __future__ import annotations

# key = project id in projects.ts / products.ts
DECK: dict[str, dict] = {
    "noorly": {
        "problem": "Managing professional and personal contacts across multiple apps becomes fragmented and difficult to maintain.",
        "challenges": "Designing intuitive contact organization, fast search, responsive performance, and cross-platform consistency.",
        "solution": "Built a clean contact management application with organized profiles and simplified networking workflows.",
        "features": ["Contact organization", "Profile management", "Search", "Categorization"],
        "architecture": "Flutter → Local Storage / Cloud APIs",
        "highlights": ["Cross-platform optimization", "Responsive UI", "Efficient data organization"],
        "value": "Simplifies relationship management and improves productivity.",
    },
    "tiny-talk-hub": {
        "problem": "Existing communication applications often become bloated with unnecessary functionality, reducing usability.",
        "challenges": "Delivering smooth messaging, minimizing UI complexity, maintaining responsive performance across devices.",
        "solution": "Built a lightweight messaging application focused on speed and simplicity.",
        "features": ["Chat interface", "Messaging", "Responsive UI", "User-friendly navigation"],
        "architecture": "Flutter → Backend Messaging Services",
        "highlights": ["Lightweight architecture", "Optimized rendering", "Clean mobile UX"],
        "value": "Enables fast and intuitive communication without overwhelming users.",
    },
    "cine-duniya": {
        "problem": "Users struggle to discover entertainment content through cluttered interfaces and slow applications.",
        "challenges": "Designing engaging browsing experiences, handling large content catalogs efficiently, responsive UI rendering.",
        "solution": "Created a modern entertainment discovery platform focused on intuitive navigation and smooth browsing.",
        "features": ["Content discovery", "Search", "Browsing", "Responsive interface"],
        "architecture": "Flutter → Content APIs → Mobile Client",
        "highlights": ["Optimized rendering", "Modern UI patterns", "Smooth navigation"],
        "value": "Enhances entertainment discovery through a polished mobile experience.",
    },
    "vistara": {
        "problem": "Movie discovery applications often suffer from cluttered interfaces and inconsistent cross-platform performance.",
        "challenges": "Fast content loading, clean navigation, scalable UI architecture, responsive layouts.",
        "solution": "Developed a streamlined movie discovery application prioritizing simplicity and performance.",
        "features": ["Movie browsing", "Search", "Recommendations", "Responsive interface"],
        "architecture": "Flutter → API Layer → Mobile Application",
        "highlights": ["Performance optimization", "Reusable UI components", "Cross-platform consistency"],
        "value": "Makes discovering movies faster and more enjoyable.",
    },
    "task-manager": {
        "problem": "Teams struggle to coordinate tasks, monitor deadlines, and track work progress across multiple tools.",
        "challenges": "Real-time synchronization, task ownership, deadline management, scalable data organization, team collaboration.",
        "solution": "Built a centralized task management platform supporting assignments, tracking, and collaborative workflows.",
        "features": ["Task creation", "Assignments", "Deadlines", "Progress tracking", "Team management"],
        "architecture": "Flutter → Firebase → Cloud Database → Authentication",
        "highlights": ["Firebase synchronization", "Scalable architecture", "Collaborative workflows"],
        "value": "Improves team productivity by centralizing project management.",
    },
    "crypto-manager": {
        "problem": "Cryptocurrency users need a secure, non-custodial way to manage multiple digital assets without relying on centralized exchanges.",
        "challenges": "Multi-chain support, portfolio synchronization, wallet security, transaction tracking, responsive UI.",
        "solution": "Developed a portfolio manager and wallet following a non-custodial architecture with multi-coin support.",
        "features": ["Wallet management", "Portfolio tracking", "Multi-coin support", "Transaction history"],
        "architecture": "React Native → Crypto APIs → Blockchain Services",
        "highlights": ["Non-custodial architecture", "Secure wallet integration", "Scalable API connectivity"],
        "value": "Enables users to monitor digital assets securely while retaining complete control over their funds.",
    },
    "bmi-calculator": {
        "problem": "BMI calculations alone are difficult for users to understand without clear visual interpretation.",
        "challenges": "Presenting health information intuitively, maintaining responsive visualizations, simple user experience.",
        "solution": "Built an application combining BMI calculations with engaging visual feedback and simplified health metrics.",
        "features": ["BMI calculator", "Visual indicators", "Health insights", "Responsive interface"],
        "architecture": "Flutter → Local Calculations → Mobile UI",
        "highlights": ["Interactive visualizations", "Optimized rendering", "Lightweight calculations"],
        "value": "Helps users better understand BMI information through visual representation.",
    },
    "coffee-delivery": {
        "problem": "The client required a complete mobile ordering experience before investing in application development.",
        "challenges": "Designing intuitive user journeys, optimizing ordering flow, creating scalable design systems, validating usability.",
        "solution": "Delivered a comprehensive UI/UX design system including customer journeys, ordering flows, wireframes, and high-fidelity interfaces.",
        "features": ["Mobile ordering flow", "Product browsing", "Checkout journey", "Design system", "Prototypes"],
        "architecture": "Figma Design System → Wireframes → High-Fidelity Mockups → Interactive Prototype",
        "highlights": ["User-centered design", "Reusable design components", "Accessibility considerations", "Mobile-first layouts"],
        "value": "Reduced design uncertainty and established a validated blueprint for future application development.",
    },
    "mindmaze-junior": {
        "problem": "Parents wanted an educational game that helps young children learn through interactive gameplay without requiring reading skills or internet connectivity.",
        "challenges": "Designing child-friendly interactions, maintaining smooth performance across six platforms, creating reusable game logic, and ensuring intuitive gameplay.",
        "solution": "Built a cross-platform educational game using custom rendering without external dependencies, ensuring consistent behavior across Android, iOS, Web, Windows, Linux, and macOS.",
        "features": ["Four educational game modes", "Colorful visuals", "Offline gameplay", "Child-friendly UI"],
        "architecture": "Flutter → CustomPaint Rendering Engine → Local Storage",
        "highlights": ["CustomPaint rendering", "Zero third-party packages", "Multi-platform deployment", "Optimized rendering pipeline"],
        "value": "Delivers engaging educational gameplay while minimizing maintenance and maximizing platform reach.",
    },
    "jungle-jump": {
        "problem": "The client wanted an enjoyable 2D platformer with responsive controls, fair difficulty progression, and engaging gameplay.",
        "challenges": "Physics tuning, collision detection, animation performance, level balancing, and maintaining smooth gameplay on mobile devices.",
        "solution": "Developed a lightweight platformer with optimized physics, structured level progression, and responsive controls.",
        "features": ["Platforming", "Collectibles", "Obstacles", "Progressive difficulty", "Level system"],
        "architecture": "Flutter → Flame Engine → Game Loop",
        "highlights": ["Physics optimization", "Efficient collision handling", "Reusable game architecture", "Optimized animation rendering"],
        "value": "Provides an entertaining mobile gaming experience with polished mechanics and scalable level design.",
    },
    "bubble-io": {
        "problem": "Casual mobile games often lose player engagement because progression becomes repetitive over time.",
        "challenges": "Designing addictive gameplay loops, balancing increasing difficulty, maintaining responsive animations, and optimizing performance.",
        "solution": "Built an arcade-style bubble game with progressive difficulty, score tracking, and responsive touch controls.",
        "features": ["Bubble popping", "Scoring system", "Increasing difficulty", "Smooth animations"],
        "architecture": "React Native → Animated API → Local Score Storage",
        "highlights": ["Optimized animation handling", "Lightweight rendering", "Responsive touch interactions"],
        "value": "Creates an enjoyable casual gaming experience with replayability and minimal resource usage.",
    },
    "snow-world-game": {
        "problem": "The client wanted a casual mobile game capable of generating revenue while maintaining enjoyable gameplay.",
        "challenges": "Integrating advertisements without interrupting gameplay, maintaining frame rates, balancing progression, and ensuring smooth user experience.",
        "solution": "Built a snow-themed casual game with optimized gameplay loops and carefully integrated advertisement placements.",
        "features": ["Casual gameplay", "Score system", "Advertisements", "Multiple levels"],
        "architecture": "Flutter → Game Engine → Google Ads Integration",
        "highlights": ["Advertisement integration", "Performance optimization", "Smooth rendering pipeline"],
        "value": "Combines enjoyable gameplay with sustainable monetization while preserving user experience.",
    },
    "detective-game": {
        "problem": "Build a detective-themed mobile game combining storytelling with engaging gameplay while supporting monetization.",
        "challenges": "Managing game progression, integrating third-party services, optimizing advertisement performance, and maintaining immersive gameplay.",
        "solution": "Developed a structured game architecture supporting investigation mechanics, advertisements, and scalable future content.",
        "features": ["Detective missions", "Progression system", "Ads", "Achievements", "Interactive gameplay"],
        "architecture": "Flutter → Game Engine → Google Ads → Third-party Services",
        "highlights": ["Modular architecture", "Scalable level management", "Optimized performance"],
        "value": "Establishes a flexible foundation for expanding game content while maintaining enjoyable gameplay.",
    },
    "cubbi": {
        "problem": "Existing software solutions could not accommodate the client's specialized business workflow and operational requirements.",
        "challenges": "Designing custom business logic, scalable backend APIs, secure database architecture, responsive frontend, and maintainable codebase.",
        "solution": "Built a full-stack web platform tailored specifically to the client's operational workflow with a modern responsive interface.",
        "features": ["Dashboard", "Workflow management", "Custom business logic", "Responsive UI", "Authentication"],
        "architecture": "React → Node.js → PostgreSQL → REST APIs",
        "highlights": ["Full-stack architecture", "Modular backend", "Scalable database design", "Reusable frontend components"],
        "value": "Enables the client to streamline operations through software designed specifically for their business processes.",
    },
    "3d-model-viewer": {
        "problem": "Real estate agencies and product businesses required an interactive method of presenting 3D assets online instead of static images.",
        "challenges": "Rendering complex 3D models efficiently, optimizing WebGL performance, managing large assets, and maintaining responsive interaction.",
        "solution": "Developed a browser-based marketplace combining real-time 3D visualization with asset management and sharing capabilities.",
        "features": ["Interactive 3D viewer", "Asset management", "Broker sharing", "Real-time rendering"],
        "architecture": "React → Three.js → WebGL → Node.js Backend",
        "highlights": ["WebGL optimization", "Asset streaming", "Responsive rendering", "Modular frontend architecture"],
        "value": "Enhances product visualization and improves customer engagement through immersive 3D experiences.",
    },
    "ai-business-platform": {
        "problem": "Businesses relied on multiple disconnected systems for managing operations, expenses, and internal workflows, creating inefficiencies.",
        "challenges": "Integrating AI capabilities, designing scalable workflows, managing business data securely, creating unified dashboards, and supporting future automation.",
        "solution": "Built a centralized business platform combining operational management, expense tracking, and AI-assisted workflows within a single application.",
        "features": ["Expense management", "Operations dashboard", "AI assistance", "Workflow automation", "Reporting"],
        "architecture": "Web Platform → AI Services → Backend APIs → Database",
        "highlights": ["Modular architecture", "AI workflow integration", "Scalable dashboard design", "Automation-ready infrastructure"],
        "value": "Reduces operational complexity by consolidating multiple business systems into one intelligent platform.",
    },
    "custom-crm-platform": {
        "problem": "The client relied on multiple disconnected SaaS tools that failed to match their unique sales and customer management workflow.",
        "challenges": "Designing flexible CRM modules, workflow automation, scalable APIs, role-based access control, reporting dashboards, and seamless data management.",
        "solution": "Developed a custom CRM platform tailored to the client's business processes, consolidating lead management, customer records, sales pipelines, and automation into one system.",
        "features": ["Lead management", "Customer database", "Pipeline tracking", "Workflow automation", "Reporting dashboard", "Authentication"],
        "architecture": "Web Frontend → REST APIs → Backend Services → Database → Automation Engine",
        "highlights": ["Modular architecture", "Reusable APIs", "Scalable business workflows", "Role-based permissions", "Responsive dashboard design"],
        "value": "Eliminates dependency on multiple SaaS products while improving operational efficiency and workflow consistency.",
    },
    "medical-ocr": {
        "problem": "Manual processing of complex medical questionnaires consumed significant time and increased the risk of data entry errors.",
        "challenges": "OCR accuracy, handling multi-page documents, extracting structured information, validation, AI-assisted corrections, and secure document processing.",
        "solution": "Built an OCR pipeline capable of extracting structured JSON from complex medical documents using AI-assisted validation and processing.",
        "features": ["OCR processing", "Structured JSON output", "Document validation", "Automated extraction", "Workflow automation"],
        "architecture": "Document Upload → OCR Engine → AI Processing → Validation → Structured JSON Output",
        "highlights": ["AI-assisted OCR", "Document parsing", "Validation pipeline", "Scalable processing architecture"],
        "value": "Significantly reduces manual processing effort while improving consistency and structured data extraction.",
    },
    "ai-whatsapp-automation": {
        "problem": "Businesses manually handled customer inquiries, appointment scheduling, and lead capture, resulting in slower response times.",
        "challenges": "WhatsApp API integration, conversation management, AI response generation, backend integration, scalability, and secure messaging workflows.",
        "solution": "Developed an AI-powered WhatsApp assistant capable of automating customer communication, booking management, and lead qualification.",
        "features": ["AI conversations", "Booking automation", "Lead capture", "Backend integration", "Conversation history"],
        "architecture": "WhatsApp Business API → FastAPI → LLM → Backend Services → Database",
        "highlights": ["AI conversation management", "Workflow automation", "API integration", "Scalable backend services"],
        "value": "Improves customer response times while reducing manual support workload.",
    },
    "ai-game-guide": {
        "problem": "New players often struggle during onboarding, reducing engagement and increasing early abandonment in complex games.",
        "challenges": "Context-aware recommendations, AI decision-making, gameplay event tracking, scalable inference, and responsive integration into the game environment.",
        "solution": "Built an AI assistant that analyzes player progress and provides contextual guidance, tutorials, and recommendations during gameplay.",
        "features": ["Intelligent onboarding", "Contextual recommendations", "AI guidance", "Gameplay analysis"],
        "architecture": "Game Engine → AI Service → Recommendation Engine → Player Interface",
        "highlights": ["Context-aware AI", "Gameplay analytics", "Scalable recommendation system", "Lightweight integration"],
        "value": "Improves player onboarding and overall engagement by providing personalized in-game assistance.",
    },
    "dairok-ai": {
        "problem": "Crypto traders require continuous market monitoring and disciplined execution, which is difficult to maintain manually.",
        "challenges": "Market analysis, autonomous decision-making, exchange integration, risk management, backtesting, portfolio tracking, and scalable architecture.",
        "solution": "Built an AI-powered trading platform capable of analyzing markets, selecting trading opportunities, managing risk, and supporting paper trading and historical testing.",
        "features": ["Market analysis", "Automated trading", "Risk controls", "Paper trading", "Portfolio dashboard", "Backtesting"],
        "architecture": "LangGraph Agents → Trading Engine → Bybit APIs → Analytics Dashboard",
        "highlights": ["Agentic AI workflows", "Technical analysis pipeline", "Modular trading engine", "Scalable backend"],
        "value": "Establishes the foundation for an intelligent autonomous trading platform focused on disciplined decision-making.",
    },
    "yovela": {
        "problem": "People increasingly seek a safe platform to journal, express emotions, and connect with others who share similar experiences while maintaining privacy.",
        "challenges": "AI-assisted journaling, secure authentication, emotion matching, scalable social feed, privacy controls, notification systems, and mobile performance.",
        "solution": "Developed a social journaling platform combining AI-powered journaling, emotion-based peer discovery, social interactions, and fine-grained privacy settings.",
        "features": ["Daily journaling", "AI assistance", "Social feed", "Reactions", "Emotion matching", "Privacy controls"],
        "architecture": "React Native → FastAPI → Supabase → AI Services → Mobile Application",
        "highlights": ["AI integration", "Emotion-based recommendations", "Scalable backend", "Cross-platform architecture", "Modern mobile UX"],
        "value": "Creates a supportive digital journaling community while empowering users with AI-assisted self-reflection.",
    },
    "wizchat": {
        "problem": "Teams and communities require a lightweight real-time communication platform that combines messaging, channels, and media sharing without unnecessary complexity.",
        "challenges": "Real-time messaging, WebSocket scalability, file sharing, synchronization, notification delivery, and responsive cross-device experience.",
        "solution": "Built a modern communication platform supporting instant messaging, channels, media sharing, and scalable real-time collaboration.",
        "features": ["Messaging", "Channels", "Media sharing", "File sharing", "Notifications", "User management"],
        "architecture": "React → Node.js → WebSockets → Redis → Database",
        "highlights": ["Low-latency communication", "Scalable WebSocket architecture", "Efficient message synchronization", "Modular backend services"],
        "value": "Provides a clean and scalable communication platform suitable for teams, communities, and collaborative environments.",
    },
}


def entry(project_id: str) -> dict | None:
    return DECK.get(project_id)
