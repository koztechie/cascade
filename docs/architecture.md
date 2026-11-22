# Architecture — Cascade

What this document locks down: **where each responsibility lives**, so future
changes go to the right file instead of wherever convenience put them last
time. Companion document: `docs/conventions.md` (placement rules for Cypher,
honesty rules, naming).

Counts referenced here are contracts asserted by `make verify`: **7 canonical
queries, 11 verify gates, 5 MCP tools,3 golden fixtures**.

---

##1. Component map

```text
ENTRY SURFACES (public API — stable)
├── make targets            verify / demo / report / viewer / golden /
│                           golden-update / store / check-committed /
│                           setup / venv / data / clean
├── bin/relate              wrapper: official CLI if the CPU supports it,
│                           else scripts/relate_compat.py (embedded engine)
├── .mcp.json               Claude-style MCP client config (repo root)
├── opencode.json           OpenCode MCP client config (repo root)
└── .agents/skills/cascade/ drop-in agent skill (tools + honesty rules)

CORE RUNTIME
├── scripts/relate_compat.py   fallback CLI entry point (stable API, exec'd by
│   │                           bin/relate) — thin main(), impl in relate_lib:
│   ├── scripts/relate_lib/     internal package (pass R4)
│   │   ├── render.py           table/json/markdown/csv rendering
│   │   ├── query.py            flag parsing, split_statements, run_query,
│   │   │                       usage/version (exit codes 0/2/6)
│   │   ├── tools.py            tool impls + TOOLS registry; file-backed via
│   │   │                       _load_query (queries/parts/, queries/02, 07)
│   │   └── mcp.py              mcp_loop (stdio JSON-RPC) + parse_serve_args
│   └── query path              parse flags → split_statements → execute
│                               → render; serve path: mcp_loop → TOOLS:
│       ├── read_cypher         generic read (200-row cap, honesty note)
│       ├── get_schema          labels / properties / patterns
│       ├── blast_radius(sku)   direct + category + 4-hop ball (file-backed)
│       ├── rejection_causes    file-backed → queries/02
│       └── remediation         file-backed → queries/07 — five tools total,
│                               read-only by design (pass R7 removed the
│                               unreachable write_cypher; no write path)
└── official `relate` binary   used verbatim by judges' machines

DATA GENERATION
└── scripts/generate_data.py   seed 42; the RNG stream is sacred
    ├── data/load.cypher       1786 statements, byte-stable (verify gate 11
    │                          re-runs it under PYTHONHASHSEED=1)
    └── data/demo_params.json  demo SKU + merge pair (PU-1004, Sneakers→Boots)

CANONICAL QUERIES — queries/01..07 (the contract)
├── 01 blast radius          02 rejected root cause   03 invisible inventory
├── 04 merge counterfactual  05 rejection risk        06 active vs expired
└── 07 remediation
    Consumers: verify.sh, report.sh, demo.sh, MCP tools (via _load_query),
    README. Anything that answers a user question belongs HERE.

VERIFICATION STACK (in execution order)
├── check-committed.sh       opens the COMMITTED store read-only BEFORE any
│                            rebuild (credit-trail's lesson)
├── store                    rm + reload from data/load.cypher
├── verify.sh                gates 01–11 (queries, MCP surface + CLI/MCP
│                            parity, baseline + negative control, temporal,
│                            remediation, injection test, determinism)
└── golden.sh check|update   byte-diff of demo/report/verify outputs against
                             tests/golden/ (same retry policy as make verify)

PRESENTATION
├── scripts/report.sh        markdown report + one-line verdict (queries
│                            from queries/parts/ via stdin; verdict is a
│                            ${PYTHON:-python3} formatter — see conventions)
├── scripts/demo.sh          all seven queries, fixed parameters
├── scripts/build_viewer.py  queries the store → viewer.html
│   ├── templates/viewer.template.html
│   └── vendor/cytoscape.min.js (MIT, vendored)
└── Makefile                 orchestration + retry-once policy only; no
                             business logic beyond that

DOCUMENTATION
├── README.md                the pitch + judging-criteria mapping
├── PLAN64.md, CHECKLIST.md  process artifacts (historical, kept as record)
└── docs/                    agent-session, limitations, this file,
                             competitor-analysis, submissions-gallery,
                             devpost-* (submission inventory)
```

##2. Data flow

```text
scripts/generate_data.py  (seed 42; byte-stable under any PYTHONHASHSEED)
        │
        ├─► data/load.cypher ──[relate query < file]──► store/catalog.rl
        └─► data/demo_params.json                            │ (single file,
                                                              │  committed)
        ┌─────────────────────────────────────────────────────┘
        │
        ├── verify.sh          gates 01–11  ──► "== verify: OK =="
        ├── golden.sh check    diff vs tests/golden/{demo,report,verify}
        ├── report.sh          markdown + verdict   (stdout)
        ├── demo.sh            all seven queries  (stdout)
        ├── build_viewer.py    ──► viewer.html (offline, no server)
        └── relate_compat serve --mcp stdio --read-only
                                ──►5 tools for any MCP client
```

Rules of the flow:

- **Nothing hand-edits a generated artifact.** `store/catalog.rl`,
  `data/load.cypher`, `data/demo_params.json`, `viewer.html` are all produced;
  change the generator or the template instead.
- **The store is asserted by counts, not bytes** (see limitations): a rebuild
  yields an equivalent file with different bytes; `verify` gate07 is the
  contract.
- **Reads can be concurrent; writes cannot** (one writer per store — stop
  `serve` before `make store|demo|report`).

##3. Responsibility boundaries

| Question | The answer lives in |
| --- | --- |
| Which Cypher answers a user/README question? | `queries/NN_*.cypher` (canonical) |
| How do we talk to the engine as a library? | `scripts/relate_compat.py` only |
| Official CLI vs embedded fallback? | `bin/relate` only |
| Orchestration, ordering, retry policy? | `Makefile` only |
| What may never change silently? | `tests/golden/` + `verify.sh` gates |
| What do we promise (and not promise)? | `README.md` + `docs/limitations.md` |
| Process/history (steps, checklists, analyses)? | `PLAN64.md`, `CHECKLIST.md`, `docs/competitor-analysis.md` |

##4. Public API — must stay stable across refactors

- `make` target names and their observable outputs.
- `./bin/relate query|serve|version` and the supported flag subset
  (`--database`, `--param`, `--mode`, `--read-only`, `serve --mcp stdio`).
- MCP: server name `cascade`; the five tool names and their input schemas;
  JSON result shapes (`row_count`, `rows`, tool payload keys); exit codes
  `0 / 2 / 6`; the200-row cap.
- Filenames `queries/01..07`, `store/catalog.rl`, `data/*`, `viewer.html`,
  `.mcp.json`, `opencode.json`, `.agents/skills/cascade/SKILL.md`.
- README section anchors (external links may point at them).

Any change to the above is a **migration task**, not a refactor pass.

##5. Known constraints (details in `docs/limitations.md`)

- One writer per store; the MCP surface is read-only by design.
- An intermittent transient class in verify content checks → retry-once policy
  in both `make verify` and `golden.sh`; real failures fail twice and are
  surfaced; final gates require two consecutive green runs.
- The prebuilt CLI requires a newer CPU; `bin/relate` falls back to the
  embedded Python client (`relate_db`), so judges' path and old-hardware path
  share the same engine and store format.
- No LLM in the answer path; the graph outranks any model.
