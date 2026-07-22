"""The confidentiality firewall.

The most important file in this project.

A blog post talks in general terms. A case study names a real client and describes
work done for them under an agreement. `details.md §20.1` enumerates what may never
be published: revenue or ad-revenue figures, client KPIs, internal business
workflows, customer conversations, user data, API credentials, internal AI prompt
design, unreleased game features or mechanics, licensing and roadmap detail.

Two layers, and the ORDER matters:

  1. Deterministic patterns + the brief's own denylist. Free, instant, and the
     part that cannot have an off day.
  2. An LLM adjudicator, asked one narrow question. Catches the paraphrase a regex
     cannot: "their biggest customer told us" discloses a customer conversation
     without using any word on any list.

Any hit is a HARD ABORT. Never a warning, never a best-effort fix. The blog agent
can afford `fix_claims` with a budget because its worst case is a slightly wrong
sentence about the industry. The worst case here is a breached agreement, and
"the model had two attempts at removing it" is not a defence.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

log = logging.getLogger("agent.confidentiality")

# Ordered by the §20.1 classes they implement.
FORBIDDEN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("revenue", re.compile(
        r"\b(revenue|arr|mrr|turnover|profit|margin)\b.{0,24}\b[\d$£€₹]"
        r"|[\d$£€₹][\d,.]*\s*(k|m|bn|lakh|crore)?\s*(in\s+)?(revenue|arr|mrr|turnover|profit)",
        re.I)),
    ("ad-revenue", re.compile(r"\b(ad|advert(ising)?)\s+(revenue|earnings|income)\b", re.I)),
    ("client-kpi", re.compile(
        r"\b\d+(\.\d+)?\s*%\s*(increase|decrease|uplift|growth|conversion|retention|churn|"
        r"engagement|activation|drop-?off)\b", re.I)),
    ("user-counts", re.compile(
        r"\b[\d,]{3,}\+?\s*(daily |monthly |active |registered )?(users|customers|installs|"
        r"downloads|subscribers|accounts)\b", re.I)),
    ("credentials", re.compile(
        r"\b(api[_ -]?key|secret[_ -]?key|access[_ -]?token|bearer\s+[A-Za-z0-9]|"
        r"password|credential|private[_ -]?key|\.env\b)", re.I)),
    ("prompt-design", re.compile(
        r"\b(system prompt|our prompt|the prompt (we|they) (use|wrote)|prompt template|"
        r"few-?shot example)\b", re.I)),
    ("customer-conversation", re.compile(
        r"\b(their (biggest |largest |key )?(customer|client|user)s? (said|told|complained|"
        r"reported|asked)|in (a|the) (call|meeting) with their)\b", re.I)),
    ("roadmap", re.compile(
        r"\b(unreleased|not yet announced|upcoming (feature|release)|on (their|the) roadmap|"
        r"licens(ing|e) (terms|agreement)|under NDA we)\b", re.I)),
    ("internal-workflow", re.compile(
        r"\b(their internal (process|workflow|system|tooling)|how they (internally|actually) "
        r"(run|operate|price))\b", re.I)),
]


@dataclass
class Finding:
    rule: str
    match: str
    context: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    adjudicator_verdict: str = ""

    @property
    def clean(self) -> bool:
        return not self.findings

    def render(self) -> str:
        if self.clean:
            return "confidentiality: PASS"
        lines = [f"confidentiality: {len(self.findings)} finding(s) — ABORT"]
        for f in self.findings:
            lines.append(f"  [{f.rule}] {f.match!r}\n      …{f.context}…")
        return "\n".join(lines)


def _contexts(text: str, pattern: re.Pattern[str], rule: str) -> list[Finding]:
    out = []
    for m in pattern.finditer(text):
        lo = max(0, m.start() - 50)
        out.append(Finding(rule=rule, match=m.group(0).strip(),
                           context=text[lo: m.end() + 50].replace("\n", " ").strip()))
    return out


def _denylist_hits(text: str, denylist: list[str]) -> list[Finding]:
    """Fuzzy match against the brief's own `## Confidential` section.

    Matching is on distinctive content words rather than whole lines: a brief line
    reads like a note ("their margin on installs is thin"), and the draft would
    paraphrase it rather than quote it. Requiring 3+ rare words from one line to
    co-occur in a paragraph catches the paraphrase without firing on common words.
    """
    findings: list[Finding] = []
    lowered = text.lower()
    for line in denylist:
        words = [w for w in re.findall(r"[a-z]{5,}", line.lower())]
        if len(words) < 3:
            continue
        hits = [w for w in words if w in lowered]
        if len(hits) >= max(3, len(words) // 2):
            findings.append(Finding(
                rule="brief-denylist",
                match=", ".join(hits[:5]),
                context=f"draft echoes a '## Confidential' brief line: {line[:90]}",
            ))
    return findings


def scan(body_mdx: str, spec_text: str = "", denylist: list[str] | None = None) -> Report:
    """Deterministic layer. Runs over the MDX body AND the typed spec."""
    text = f"{body_mdx}\n\n{spec_text}"
    report = Report()

    for rule, pattern in FORBIDDEN_PATTERNS:
        report.findings.extend(_contexts(text, pattern, rule))

    if denylist:
        report.findings.extend(_denylist_hits(text, denylist))

    if report.findings:
        # Log the RULE and the MATCH, not just a count. A bare count tells you
        # nothing about whether it was a real disclosure or a pattern misfiring
        # on ordinary prose, and that is the first thing you need to know.
        log.error("confidentiality scan found %d issue(s):", len(report.findings))
        for f in report.findings:
            log.error("  [%s] %r — …%s…", f.rule, f.match, f.context[:110])
    return report


ADJUDICATOR_SYSTEM = (
    "You review a draft case study for disclosure risk on behalf of the studio that "
    "wrote it. You answer one narrow question and nothing else."
)


def adjudicator_prompt(body_mdx: str, client: str, project: str) -> tuple[str, str]:
    """One narrow question, phrased to survive the proxy's injection guard.

    Deliberately NOT 'check for policy violations' — that phrasing reads as a
    compliance instruction and the proxy's guard refuses it. Framing it as a normal
    editorial review is both safer and produces better judgement.
    """
    user = f"""Here is a draft case study about a project called "{project}"{f' delivered for {client}' if client else ''}.

'''
{body_mdx}
'''

Read it as if you were the client seeing it for the first time. Would anything in
it make you uncomfortable to see published? Specifically, does it reveal:
  - money the client makes or spends, or any business metric of theirs;
  - how the client runs their business internally;
  - anything a customer of theirs said;
  - user data, credentials, or configuration;
  - features or plans the client has not announced.

General descriptions of the software, the technical approach, and the engineering
decisions are all fine and expected — those are the point of the article.

Reply as JSON:
{{"concerns": [{{"quote": "the exact phrase", "why": "what it reveals"}}]}}
Return {{"concerns": []}} if nothing would trouble the client."""
    return ADJUDICATOR_SYSTEM, user
