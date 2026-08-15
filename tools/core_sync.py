"""Keep `core/` in step with the blog agent it was copied from.

`core/llm/client.py` encodes non-obvious, hard-won knowledge about the LLMsRelay
proxy: the CLI User-Agent its Cloudflare requires, the injection-guard phrasing
rules, the 2000-char prompt-caching threshold, the retry/backoff shape. That file
lives in two repos now. Two copies drift, and this particular drift surfaces six
months later as a mystery 403 that nobody connects to a fix made upstream.

So: a sha256 manifest of each copied file at the commit it came from.

    python tools/core_sync.py check    # non-zero if upstream moved. Runs weekly in CI.
    python tools/core_sync.py pull     # copy upstream in, restamp the lock

`check` is deliberately noisy rather than clever — it prints the diff and fails.
Deciding whether an upstream change belongs here is a judgement call, and a script
that silently merged would be worse than one that just tells you.

RULE: never edit anything under core/ in this repo. A case-study-specific need is a
new file in casestudy/, not a fork of a core file — otherwise `pull` starts
producing conflicts and the whole mechanism gets ignored.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOCK = REPO / "core" / "CORE_SOURCE.lock"

# Files copied verbatim from the blog agent. `config.py` is deliberately ABSENT:
# the two agents have legitimately different cadence knobs, so it is forked on
# purpose rather than synced.
TRACKED = {
    "core/llm/client.py": "llm/client.py",
    "core/llm/sanitize.py": "llm/sanitize.py",
    "core/facts/snapshot.py": "facts/snapshot.py",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_lock() -> dict:
    if not LOCK.exists():
        return {}
    return json.loads(LOCK.read_text(encoding="utf-8"))


def write_lock(data: dict) -> None:
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cmd_check(upstream: Path) -> int:
    lock = load_lock()
    problems: list[str] = []

    for local_rel, up_rel in TRACKED.items():
        local = REPO / local_rel
        up = upstream / up_rel

        if not local.exists():
            problems.append(f"{local_rel}: missing locally")
            continue
        if not up.exists():
            print(f"  ?  {local_rel}: upstream not found at {up} — skipping")
            continue

        local_sha, up_sha = sha(local), sha(up)
        recorded = lock.get(local_rel, {}).get("sha256")

        if local_sha != recorded:
            problems.append(
                f"{local_rel}: EDITED LOCALLY. core/ is a copy — put case-study "
                f"changes in casestudy/ instead, then re-run `pull`."
            )
        elif up_sha != local_sha:
            problems.append(
                f"{local_rel}: upstream has changed. Review the diff and run "
                f"`python tools/core_sync.py pull` to take it.\n"
                f"        diff {up} {local}"
            )
        else:
            print(f"  ok {local_rel}")

    if problems:
        print(f"\n{len(problems)} core-sync problem(s):\n")
        for p in problems:
            print(f"  {p}\n")
        return 1

    print("core-sync: every tracked file matches upstream")
    return 0


def cmd_pull(upstream: Path) -> int:
    lock = load_lock()
    changed = 0
    for local_rel, up_rel in TRACKED.items():
        up = upstream / up_rel
        if not up.exists():
            print(f"  ?  {up_rel}: not found upstream — skipped")
            continue
        local = REPO / local_rel
        local.parent.mkdir(parents=True, exist_ok=True)
        before = sha(local) if local.exists() else None
        shutil.copy2(up, local)
        after = sha(local)
        lock[local_rel] = {"sha256": after, "source": up_rel}
        if before != after:
            changed += 1
            print(f"  updated {local_rel}")
        else:
            print(f"  ok      {local_rel}")
    write_lock(lock)
    print(f"core-sync: {changed} file(s) updated, lock restamped")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync core/ with the blog agent.")
    ap.add_argument("command", choices=("check", "pull"))
    ap.add_argument(
        "--upstream",
        default=str(REPO.parent / "blog_agent"),
        help="path to the blog_agent checkout (default: sibling directory)",
    )
    args = ap.parse_args()

    upstream = Path(args.upstream).resolve()
    if not upstream.exists():
        print(f"upstream not found: {upstream}")
        print("Clone the blog agent beside this repo, or pass --upstream.")
        return 1

    return cmd_check(upstream) if args.command == "check" else cmd_pull(upstream)


if __name__ == "__main__":
    sys.exit(main())
