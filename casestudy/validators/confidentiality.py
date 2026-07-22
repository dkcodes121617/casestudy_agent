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
    # A leaked credential is a VALUE, not the word. The original pattern matched a
    # bare "credential" anywhere, and flagged this FAQ answer:
    #
    #   "You own 100% of the code, repository, and all credentials from day one."
    #
    # That is the studio's handover promise — client-owned accounts and credentials
    # are a core message in details.md and llms.txt — so the word appears in nearly
    # every study, and the rule would have blocked almost all of them. Talking about
    # credentials is the opposite of disclosing one.
    #
    # So: match an assignment, a bearer token, or a recognisable secret prefix.
    ("credentials", re.compile(
        r"\b(api[_ -]?key|secret[_ -]?key|access[_ -]?token|auth[_ -]?token|password|"
        r"private[_ -]?key|client[_ -]?secret)\s*[:=]\s*\S"
        r"|\bbearer\s+[A-Za-z0-9._-]{8,}"
        r"|\b(sk|pk|ghp|gho|github_pat|xox[baprs])[-_][A-Za-z0-9]{8,}"
        r"|-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I)),
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


# Words that appear in every case study and therefore prove nothing. The denylist
# matcher needs DISTINCTIVE overlap — a client's product name, a metric name, an
# internal system — not the shared vocabulary of software writing.
_COMMON = frozenset("""
about after again against already among another anything around because become
before behind being below better between beyond both build building built cannot
client clients company could course create created current customer customers
decision decisions delivered delivery design designed detail details different
during every everything example first found further given however inside instead
itself large later least little means might money months never number often other
others output overall people perhaps platform point points process product
production products project projects provide public really reason release result
results second several should similar simple since small software solution
something sometimes still system systems taking team teams technical their there
these thing things think those three through times today together toward under
until using usually value values version versions where whether which while whole
widely within without work working works would write writing written years
""".split())

# The drafter appends an explanatory parenthetical to owner-supplied entries
# ("(owner-supplied; fed to the confidentiality scanner…)"). That is documentation
# about the denylist, not an item on it, and its words would match any draft that
# happened to discuss the scanner.
_TRAILING_NOTE = re.compile(r"\s*\([^)]*\)\s*$")

# A line that DECLARES a category is confidential, rather than naming the secret
# itself. Its words are the case study's own subject matter, so it can only ever
# produce false positives here. Handed to the adjudicator instead.
_CATEGORY_LINE = re.compile(
    r"\b(remains?|are|is|stay|stays)\s+(confidential|private|commercially sensitive|sensitive)\b"
    r"|\bnot\s+(be\s+)?(disclosed|published|shared)\b"
    r"|\bnever\s+(publish|disclose|share)\b", re.I)


def _denylist_hits(text: str, denylist: list[str]) -> list[Finding]:
    """Fuzzy match against the brief's own `## Confidential` section.

    Matching is on distinctive content words: a brief line reads like a note
    ("their margin on installs is thin"), the draft would paraphrase rather than
    quote it, so 3+ rare words co-occurring is the signal.

    ── What this CANNOT do, and why that is fine ──
    Owners write two very different kinds of line in that section:

      1. CONTENT     "their margin on installs is thin"
      2. CATEGORY    "Specific business workflow details remain confidential."

    Word-matching works on the first and is meaningless on the second. A category
    line names the SUBJECT of the case study, so its words are guaranteed to appear
    — Cubbi's line above flagged Cubbi's own study, which is about a business
    workflow platform, on the words "specific, business, workflow".

    Chasing that with a bigger stopword list is whack-a-mole: the next category
    line will name a different subject. So category lines are skipped here and left
    to the LLM adjudicator, which is asked in plain language whether the draft
    reveals how the client runs their business — exactly the judgement a regex
    cannot make. The deterministic layer keeps the cases it can actually decide.
    """
    findings: list[Finding] = []
    lowered = text.lower()
    for line in denylist:
        if _CATEGORY_LINE.search(line):
            continue
        # Only DISTINCTIVE words count. A five-letter filter alone admitted
        # "project", "already" and "projects" — words present in literally every
        # case study — and a brief line containing three of them flagged every
        # draft. The vocabulary a case study is made of cannot be evidence that a
        # case study leaked something.
        words = [
            w for w in re.findall(r"[a-z]{5,}", _TRAILING_NOTE.sub("", line).lower())
            if w not in _COMMON
        ]
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
