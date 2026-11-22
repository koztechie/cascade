# Conventions — Cascade

Companion to `docs/architecture.md`. These rules close the root cause of
accumulated duplication: SQL was previously added wherever was convenient.
Counts referenced here are contracts asserted by `make verify`.

---

##1. Where Cypher lives

**The rule:**

1. **Anything shown to a user, or promised in the README, lives in
   `queries/NN_snake_case_name.cypher`** — one file per question. The
   filename is a stable API: README, `report`, `verify` and MCP tools
   reference it; files are never renumbered (renumbering breaks links).
   Every file carries a header: `// NN — Title` and a `// Usage:` line.
   Parameters are bound via `$name` only — never string interpolation.
2. **Tiny assertion one-liners inside `verify.sh` may stay inline** —
   baseline counts (`total nodes`, `rels`, `products`, `control`). They are
   test fixtures, not product queries: single-purpose, grepped not displayed,
   under ~10 lines. If one grows a WHERE clause, promote it.
3. **Viewer projections may stay inline** in `build_viewer.py` — they serve
   rendering (`elementId` projections), have exactly one consumer, and are
   not answers shown to users.
4. **Everything else inline is a declared exception to be closed by pass R3.**

**Current declared exceptions (until R3 closes them):**

| Location | What | Plan |
| --- | --- | --- |
| `scripts/build_viewer.py` | node/edge/own projections | **permanent exception** (rule3): rendering projections, one consumer, not user answers |
| `scripts/verify.sh` | count heredocs | **permanent exception** (rule2): assertion one-liners |

**Closed by pass R3** (now file-backed in `queries/parts/`): the report's
summary/listings/feed-contract/verdict queries and the `blast_radius` tool's
three projections — loaded via stdin (`report.sh`) and `_load_query`
(compat). Two of them are **shared by two consumers each**:
`parts/direct_counts.cypher` and `parts/category_machinery.cypher`.
The `type` vs `impact_type` alias split between `impact_ball.cypher` and
`impact_summary.cypher` is deliberate: tool payload keys and markdown headers
are published shapes (see `docs/architecture.md`).

**Consumers of the canon today:** `verify.sh`, `report.sh`, `demo.sh`,
MCP tools (`_load_query`), README. A new question = a new file in
`queries/` first, then wire consumers to it — never the reverse.

##2. Honesty rule — every number has a gate

1. **No number about the store or behavior appears in README / CHECKLIST /
   SKILL / limitations unless `make verify` asserts it** (baseline counts,
   negative control, planted defects, tool payloads) or it is reproducible by
   a documented command (`make report`, `PROFILE`).
2. **Measured numbers name their machine.** Timings live in the README table
   with the CPU stated (a2013 AMD A4-4020 — a floor, not a benchmark).
3. **Limits live in `docs/limitations.md`** under "What this demo does not
   prove" — including small-N disclosures (one SKU walkthrough) and the
   verified-surface boundary.
4. **Forbidden:** superlatives without data ("<9ms"-style claims without
   scale), safety readings of empty results (absence of impact ≠ proof of
   safety), and claims about Cypher features the seven queries and five tools
   do not execute.
5. **`scripts/check_claims.sh` (pass P0.4)** mechanically reconciles the
   headline counts in README/CHECKLIST/SKILL against the code, so claim drift
   (the `3731 → 3730` class) fails a gate instead of waiting for a reader.

##3. Python / shell conventions

- **`PYTHON`:** Makefile declares `PYTHON ?= python3`; shell scripts must use
  `${PYTHON:-python3}` instead of a bare `python3`. *(Closed by pass R5:*
  `demo.sh`, `report.sh`, `verify.sh` now all use it, and the Makefile passes
  `PYTHON=$(PYTHON)` to every script target — override with
  `make verify PYTHON=/path/to/python`.)*
- **Every shell script starts with `set -euo pipefail`.**
- **Failure messages follow `FAIL NN: reason`** — stable, grep-able; `verify`
  tests and the golden fixture depend on this exact wording.
- **Retry policy is content, not habit:** transient-aware retry-once lives in
  exactly two places — the `verify` target in `Makefile` and `run_verify` in
  `scripts/golden.sh`. New gates must reuse them, not invent their own loop.

##4. Golden rule (behavior changes)

- **Refactor pass:** `make golden` ×2 green **and** `make verify` ×2 green
  before the next pass starts.
- **Intentional output change:** `make golden-update`, then review
  `git diff tests/golden` in the same commit, with the reason in the commit
  message. Never regenerate fixtures to make a failing gate green.

##5. Naming and file hygiene

- Files: `snake_case`; generated artifacts (`store/`, `data/`, `viewer.html`)
  are never hand-edited — change the generator or the template.
- Python: `snake_case` functions; MCP tools are keyed by their public MCP
  name in the `TOOLS` dict; tool descriptions carry the honesty notes
  ("no rows → no evidence in the graph").
- Commits: one pass = one commit; message starts with the pass id
  (`P0.4:`, `R3:`) or a scoped subject; `git add` is explicit (no `add -A`).
- Docs that are process records (`PLAN64.md`, `CHECKLIST.md`,
  `docs/competitor-analysis.md`) are append/update-only — never rewritten
  to look tidy.
