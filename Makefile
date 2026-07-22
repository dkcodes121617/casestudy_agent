BLOG ?= ../blog_agent

.PHONY: help check-core sync-core plan brief run dry selftest

help:
	@echo "check-core   fail if core/ drifted from the blog agent (runs weekly in CI)"
	@echo "sync-core    pull upstream core/ changes in and restamp the lock"
	@echo "plan         show the ranked project queue and exit"
	@echo "brief        draft a brief:  make brief P=cubbi"
	@echo "dry          generate one study to output/, touching no git"
	@echo "run          generate one study and open a PR"
	@echo "selftest     run every validator against the 7 hand-written specimens"

check-core:
	@python tools/core_sync.py check --upstream $(BLOG)

sync-core:
	@python tools/core_sync.py pull --upstream $(BLOG)

plan:
	@python main.py --plan

brief:
	@python -m casestudy.brief $(P)

dry:
	@DRY_RUN=1 python main.py --now

run:
	@DRY_RUN=0 python main.py --now

selftest:
	@python tools/selftest.py
	@echo ""
	@python tools/entrycheck.py
