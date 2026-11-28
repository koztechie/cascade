# Cascade — build, verify and demo the Relate store.
# Every target runs through ./bin/relate with RELATE_PREFER=embedded: the
# pinned engine (see RELATE_DB_VERSION) is what produced the committed store
# and the golden fixtures, and it reproduces both byte for byte. The official
# CLI writes the same graph with different bytes, so letting it rebuild would
# dirty the working tree and drift the fixtures. Called directly, ./bin/relate
# prefers the official CLI — except `serve`, which always carries this
# project's five MCP tools (see bin/relate and scripts/relate_lib).
RELATE  ?= ./bin/relate
PYTHON  ?= python3
STORE   := store/catalog.rl
# Engine pin (M4): the embedded engine (`relate_db`) version this repository
# is tested against. Bumping it is a dependency change — the procedure lives
# in docs/versions.md (recreate .venv, full verify + golden + check-claims,
# CI green) and `make check-claims` fails while the pin and that page disagree.
RELATE_DB_VERSION := 1.2.0
export PATH := $(HOME)/.local/bin:$(PATH)
# Row cap (found by dry run #2): the official CLI defaults to 100 rows per
# statement when it detects an agent harness and stdout is not a terminal.
# Under an agent that silently truncates gate output, so verify fails for a
# reason that has nothing to do with the store. 0 = unlimited, which is what
# a human in a terminal gets anyway.
export RELATE_MAX_ROWS := 0
# Pinned engine for every target (see the header): byte-identical store and
# golden outputs, whatever version of the official CLI happens to be installed.
export RELATE_PREFER := embedded

.PHONY: all setup venv data store check-committed verify demo viewer report golden golden-update check-claims clean

all: verify

setup:
	@test -x .venv/bin/python || $(MAKE) --no-print-directory venv
	@$(RELATE) --version >/dev/null 2>&1 || { \
	  echo "relate is not usable. Install it:"; \
	  echo "  curl -sSfL https://relatedb.ai/install.sh | bash"; \
	  exit 1; }

venv:
	$(PYTHON) -m venv .venv
	.venv/bin/pip install -q relate_db==$(RELATE_DB_VERSION)
	@echo "created .venv with the embedded relate_db client (relate_db $(RELATE_DB_VERSION))"

data:
	$(PYTHON) scripts/generate_data.py

store: setup data
	@mkdir -p store
	@rm -rf $(STORE)
	$(RELATE) query --database $(STORE) < data/load.cypher
	$(PYTHON) scripts/normalize_store.py $(STORE)
	@echo "built $(STORE)"

# Credit-trail's lesson: validate the committed store BEFORE rebuilding it.
check-committed: setup
	@RELATE=$(RELATE) bash scripts/check-committed.sh $(STORE)

verify: setup data check-committed store
	@if RELATE=$(RELATE) PYTHON=$(PYTHON) bash scripts/verify.sh $(STORE); then :; else \
	  echo "== verify: first pass hit a failure — retrying once on the same store =="; \
	  echo "== (documented transient class: one content check returns incomplete output; a real bug fails both passes) =="; \
	  RELATE=$(RELATE) PYTHON=$(PYTHON) bash scripts/verify.sh $(STORE); \
	fi

demo: store
	@RELATE=$(RELATE) PYTHON=$(PYTHON) bash scripts/demo.sh $(STORE)

viewer: setup store
	$(PYTHON) scripts/build_viewer.py

report: setup store
	@RELATE=$(RELATE) PYTHON=$(PYTHON) bash scripts/report.sh $(STORE)

# --- Golden fixtures (P0.1): the parity anchor for every refactor pass. ---
# `make golden`        — compares fresh outputs against the committed snapshots.
# `make golden-update` — refreshes snapshots (only after an INTENTIONAL change;
#                        review `git diff tests/golden` before committing).
golden: setup store
	@RELATE=$(RELATE) PYTHON=$(PYTHON) bash scripts/golden.sh check "$(STORE)"

golden-update: setup store
	@RELATE=$(RELATE) PYTHON=$(PYTHON) bash scripts/golden.sh update "$(STORE)"

check-claims: setup store
	@RELATE=$(RELATE) PYTHON=$(PYTHON) bash scripts/check_claims.sh "$(STORE)"

clean:
	rm -rf store data/load.cypher data/demo_params.json .venv viewer.html
