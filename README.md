# WizCodes Case Study Agent

Writes and publishes **1–2 case studies per month** to the WizCodes site, grounded
in real project data, gated by deterministic safety checks, and **opened as a pull
request for a human to merge**.

Same deployment shape as the [blog agent](https://github.com/dkcodes121617/blog_agent):
a scheduled GitHub Actions workflow on this public repo (unlimited free minutes, no
server), committing to the private site repo, whose own workflow builds and runs
`firebase deploy`. Only recurring cost is the ClaudeStore proxy key.

---

## How it differs from the blog agent

The two agents look similar and are shaped by opposite problems.

| | Blog agent | This agent |
|---|---|---|
| Subject space | Open, infinite | **Closed — 30 known projects** |
| Topic selection | LLM strategist + deterministic focus | **Deterministic queue, no LLM** |
| Core risk | Repeating itself | **Leaking client confidences** |
| Uniqueness gate | Essential (MiniLM embeddings) | Unnecessary — subjects are inherently unique |
| Cadence | 1–2 per day | 1–2 per **month** |
| Publishing | Push to `main`, unattended | **Pull request. A human merges.** |
| Failed check | Fix budget, then ship anyway | **Hard abort. No budget.** |

Three consequences worth understanding before changing anything:

**No LLM picks the subject.** `casestudy/queue.py` scores every unwritten project on
coverage gaps, testimonial availability and archetype rotation. Asking a model
"which project next" adds nondeterminism and zero value when the answer is
computable. That is the same lesson `pick_focus()` encodes upstream — the fix for
convergence was to stop asking an open question, not to phrase it better.

**No `langgraph`.** The blog agent's graph earns its keep: five distinct loops with
conditional edges. This pipeline has one loop and a series of gates, which `if`
already expresses. See the header of `casestudy/run.py`.

**No fix budget on any safety check.** The blog agent ships a draft with a remaining
fact-check flag because its worst case is a slightly wrong sentence about the
industry. Here the worst case is a breached client confidence, and it is not
recoverable by editing the page afterwards — it has already been read and cached.

---

## The brief gate

The agent will not write about a project without a clean brief at
`briefs/<project-id>.md`.

```bash
make brief P=cubbi        # draft one
make brief P= --all       # or: python -m casestudy.brief --all
```

The drafter sources what it can from `projects.ts`, `products.ts` and
`testimonials.ts`, tags each line with its origin, and marks everything else
`[NEEDS REVIEW]` rather than guessing. The two things it can never source are
**permission** (may we name this client? what may be published?) and **rationale**
(no data file records why a decision was made).

A brief containing `[NEEDS REVIEW]` blocks the writer. Clear them at the rate you
publish — about five per brief, five minutes each.

`## Confidential` is **never shown to the writer**. It goes only to the
confidentiality scanner, as a denylist. That asymmetry is the mechanism that makes
unattended generation safe.

---

## The gates

Deterministic checks run before any paid LLM call, and cheap before expensive —
the blog agent's ordering lesson, applied.

| Gate | Where | Behaviour |
|---|---|---|
| MDX contract | `validators/mdx.py` | 2 rewrites, then abort |
| Status claims | `validators/status.py` | Hard abort |
| Claims traceability | `validators/claims.py` | Hard abort |
| Confidentiality — patterns + brief denylist | `validators/confidentiality.py` | Hard abort |
| Confidentiality — LLM adjudicator | same | Hard abort, **including if it fails to run** |

`validators/status.py` is a port of `scripts/status-check.mjs` in the site repo.
**Keep them in sync** — the site build is the backstop, and the two disagreeing is
worse than either being slightly wrong.

There is deliberately **no escape hatch**. The human override is the PR: rewrite the
sentence and re-run. That costs an affirmative edit rather than a click past a
warning.

---

## Self-test

```bash
make selftest
```

Runs every validator against the seven hand-written studies already on the site.
**The specimens are the spec** — if a validator rejects one, the validator is wrong.

It has already earned its place: on its first run it rejected 5 of 7, and every
rejection was a validator bug (pin coordinates read as claims; a 5-section study
held to a 6-section word floor).

---

## `core/` is a copy — never edit it

`core/llm/client.py` and `core/facts/snapshot.py` are copied verbatim from the blog
agent. `client.py` in particular encodes non-obvious proxy knowledge: the CLI
User-Agent its Cloudflare requires, the injection-guard phrasing rules, the
prompt-caching threshold, the retry shape.

```bash
make check-core     # fails if upstream moved. Runs weekly in CI.
make sync-core      # pull upstream in, restamp the lock
```

A case-study-specific need is a **new file in `casestudy/`**, not a fork of a core
file. The repo-root `config.py` and `llm/` are import shims that exist precisely so
`core/` can stay byte-identical.

---

## Running it

```bash
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env          # fill in the proxy key

make plan                     # ranked queue, offline, instant
make dry                      # generate to output/, touch no git
make run                      # generate and open a PR
```

---

## Going live — two secrets

In this repo → **Settings → Secrets and variables → Actions**:

- `ANTHROPIC_API_KEY` — the ClaudeStore key.
- `PUBLISH_TOKEN` — a fine-grained PAT scoped to **only** the site repo, with
  **Contents: Read and write** *and* **Pull requests: Read and write**. (The blog
  agent's token needs only Contents; this one opens PRs.) Actions reserves the name
  `GITHUB_TOKEN`, so the secret is `PUBLISH_TOKEN` and the workflow maps it.

The workflow runs on the 1st and 15th at 09:00 UTC, plus a manual **Run workflow**
button with a `dry_run` toggle (defaulting to true) and an optional project id.

> **Keep-alive:** GitHub disables scheduled workflows after ~60 days with no commits.
> Push any small change occasionally, or use the one-click re-enable it emails you.
