"""Import shim — see the note in the repo-root config.py.

Re-exports core/llm/sanitize.py so the copied core/llm/client.py can keep its
upstream `from llm.sanitize import clean_text` import unchanged.
"""
from core.llm.sanitize import *  # noqa: F401,F403
from core.llm.sanitize import clean_text, sanitize_prose  # noqa: F401
