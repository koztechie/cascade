# Cascade — build, verify and demo the Relate store.
# Uses ./bin/relate: the official CLI when the CPU supports it, otherwise the
# embedded Python client (same engine, same store format).
RELATE  ?= ./bin/relate
PYTHON  ?= python3
STORE   := store/catalog.rl
export PATH := $(HOME)/.local/bin:$(PATH)

.PHONY: all setup venv data store check-committed verify demo viewer report golden golden-update check-claims clean

all: verify

setup:
	@$(RELATE) --version >/dev/null 2>&1 || $(MAKE) --no-print-directory venv
	@$(RELATE) --version >/dev/null 2>&1 || { \
	  echo "relate is not usable. Install it:"; \
	  echo "  curl -sSfL https://relatedb.ai/install.sh | bash"; \
	  exit 1; }

venv:
	$(PYTHON) -m venv .venv
	.venv/bin/pip install -q relate_db
	@echo "created .venv with the embedded relate_db client"

data:
	$(PYTHON) scripts/generate_data.py

store: setup data
	@mkdir -p store
	@rm -rf $(STORE)
	$(RELATE) query --database $(STORE) < data/load.cypher
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
