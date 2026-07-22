"""Import shim so `core/` can stay BYTE-IDENTICAL to the blog agent.

The copied files under `core/` do `from config import CONFIG` and
`from llm.sanitize import clean_text`, because that is the blog agent's flat
layout. This repo nests them under `core/`.

Rewriting those imports would be the obvious fix and the wrong one: it edits files
that `tools/core_sync.py` tracks by hash, so every upstream fix would land as a
conflict and the sync mechanism would get switched off within a month.

A shim costs two files and keeps `core/` a verbatim copy forever.
"""
from core.config import CONFIG, Config, AGENT_ROOT  # noqa: F401
