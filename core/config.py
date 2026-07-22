"""Central configuration for the WizCodes case study agent.

Deliberately FORKED from the blog agent's config rather than synced (see
tools/core_sync.py — config.py is absent from TRACKED). The two agents have
genuinely different cadence and safety settings, and syncing this file would
overwrite them every time.

Everything is env-driven so the GitHub Actions workflow is the only place
production values live.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

AGENT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(AGENT_ROOT / ".env")


def _clean(raw: str | None) -> str:
    """Strip whitespace and any trailing inline '# comment' (dotenv keeps those)."""
    if raw is None:
        return ""
    return raw.split("#", 1)[0].strip()


def _int(name: str, default: int) -> int:
    try:
        return int(_clean(os.getenv(name)) or default)
    except (TypeError, ValueError):
        return default


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, "1" if default else "0").strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Config:
    # ── Proxy / LLM ──
    # Identical to the blog agent: same proxy, same models, same quirks. The CLI
    # User-Agent and injection-guard phrasing rules live in core/llm/client.py.
    anthropic_base_url: str = os.getenv("ANTHROPIC_BASE_URL", "https://api3.claudestore.store")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4.6")
    small_model: str = os.getenv("ANTHROPIC_SMALL_FAST_MODEL", "claude-haiku-4.5")
    # Planning and spec derivation set the shape of the whole study, so they get
    # the strongest model; per-section writing stays on the default.
    strategy_model: str = os.getenv("ANTHROPIC_STRATEGY_MODEL", "claude-opus-4-8")

    # ── GitHub publishing ──
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    github_repo: str = os.getenv("GITHUB_REPO", "dkcodes121617/wizcodes_main_website")
    github_branch: str = os.getenv("GITHUB_BRANCH", "main")
    git_author_name: str = os.getenv("GIT_AUTHOR_NAME", "WizCodes Case Study Bot")
    git_author_email: str = os.getenv("GIT_AUTHOR_EMAIL", "business@wizcodes.site")

    # ── Cadence ──
    # 1-2 per MONTH, not per day. The corpus is finite (30 projects), so there is
    # no reason to rush through it — and each study is a page a prospect reads
    # closely, which is a different quality bar from a blog post.
    studies_per_month: int = _int("STUDIES_PER_MONTH", 1)

    # ── Safety ──
    # A case study names a real client. Unlike the blog agent, this one NEVER
    # pushes to main: it opens a pull request for a human to merge. Set to 0 only
    # if you genuinely want unattended publishing, which is not recommended.
    open_pr: bool = _bool("OPEN_PR", True)
    # A brief containing [NEEDS REVIEW] blocks the writer. Turning this off would
    # let the agent invent the very things the marker exists to flag.
    require_clean_brief: bool = _bool("REQUIRE_CLEAN_BRIEF", True)

    # ── Behaviour ──
    dry_run: bool = _bool("DRY_RUN", True)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # ── Paths ──
    root: Path = AGENT_ROOT
    briefs_dir: Path = AGENT_ROOT / "briefs"
    output_dir: Path = AGENT_ROOT / "output"
    site_repo_dir: Path = AGENT_ROOT / "site_repo"
    local_site_dir: Path = field(default=AGENT_ROOT.parent / "wizcodes_next")

    # Derived content paths, relative to whichever site dir is in use.
    studies_registry_rel: str = "src/content/case-studies/studies.ts"
    studies_content_rel: str = "src/content/case-studies"
    projects_rel: str = "src/data/projects.ts"
    products_rel: str = "src/data/products.ts"
    testimonials_rel: str = "src/data/testimonials.ts"
    site_config_rel: str = "src/config/site.ts"
    data_dir_rel: str = "src/data"
    blog_content_rel: str = "src/content/blog"
    posts_registry_rel: str = "src/content/blog/posts.ts"

    def validate_for_publish(self) -> list[str]:
        problems = []
        if not self.anthropic_api_key:
            problems.append("ANTHROPIC_API_KEY is not set")
        if not self.dry_run and not self.github_token:
            problems.append("GITHUB_TOKEN is not set (required when DRY_RUN=0)")
        return problems


CONFIG = Config()

CONFIG.briefs_dir.mkdir(parents=True, exist_ok=True)
CONFIG.output_dir.mkdir(parents=True, exist_ok=True)
