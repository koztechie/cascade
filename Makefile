# Cascade — build, verify and demo the Relate store.
# Uses ./bin/relate: the official CLI when the CPU supports it, otherwise the
# embedded Python client (same engine, same store format).
RELATE  ?= ./bin/relate
PYTHON  ?= python3
STORE   := store/catalog.rl
export PATH := $(HOME)/.local/bin:$(PATH)

.PHONY: all setup venv data store verify demo clean

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

verify: store
	@RELATE=$(RELATE) bash scripts/verify.sh $(STORE)

demo: store
	@RELATE=$(RELATE) bash scripts/demo.sh $(STORE)

clean:
	rm -rf store data/load.cypher data/demo_params.json .venv
