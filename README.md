# Cascade

**One question instead of seven tables: what breaks if we change this? — with the exact graph path as proof for every consequence.**

## Use case

E-commerce teams change something every week: a SKU is discontinued, a brand is
renamed, prices rise 10%, two categories merge. The blast radius of that one
change is scattered across product feeds, marketplace listings, price rules,
campaigns, landing pages and CRM segments — today it lives in spreadsheets and
tribal knowledge, and nobody finds the seventh consequence until it breaks.

Cascade models that blast radius as a graph and answers, in one Cypher
statement each:

1. **What breaks** if we stop selling this product? → `queries/01_blast_radius.cypher`
2. **Why** is this listing rejected? → `queries/02_rejected_root_cause.cypher`
3. **What is invisible or unlinked** right now? → `queries/03_orphans.cypher`
4. **Dry run: what collides** if we merge category X into Y — rehearse the merge before you make it → `queries/04_merge_conflicts.cypher`
5. **Which products will be rejected next** (required field missing, found early)? → `queries/05_rejection_risk.cypher`
6. **Is this promo still in force?** — standing of every promo rule as of a fixed date → `queries/06_active_vs_expired.cypher`
7. **What single fix clears the most risk?** — remediation ranked by payoff → `queries/07_remediation.cypher`

Each check is **one Cypher file** — swap `$sku` / `$from` / `$to` to ask the
same questions of any product. Together they form a **verified query pack**:
`make verify` asserts the expected output of every one of them, so nothing in
this README is a hand-picked screenshot. Orphan pages and invisible stock are
edges that *should exist and don't* — **the missing link is the answer**.

Findings are **candidates for review, not verdicts**: an orphan page may be
deliberate, and a risk row is a prompt to fix the field — not a judgment on the
product. The graph also runs **without any AI account**: every query, the
report and the viewer work standalone; the MCP agent layer is optional.

**Cypher next to the SQL it replaces:** blast radius is one variable-length
pattern (query `01`). The relational equivalent joins the `Product`,
`Listing`, `Marketplace`, `Feed`, `Mapping`, `Category`, `Rule`, `Campaign`,
`Page` and `Segment` tables with a recursive CTE for the hops — ten tables deep,
which is why nobody writes it on a Friday.

**Who benefits:** e-commerce operators, marketplace/feed managers, and the AI
agents that assist them (the same queries are served over MCP). The author runs
these systems for a living — this is the weekly spreadsheet conversation, moved
into a graph.

## How it uses Relate

- **Mode:** single file (`store/catalog.rl`)
- **Why this mode:** one file *is* the whole database — judges can inspect it,
  commit it, move it, open it. No server, no directory to reconcile; the whole
  interface is `relate query --database store/catalog.rl`.
- **What the graph models:**

  | Node | Meaning |
  | --- | --- |
  | `Product`, `Brand`, `Category`, `Supplier` | the catalog itself |
  | `Listing`, `Marketplace`, `Feed`, `Mapping` | where it is published and the field contract each feed enforces |
  | `Rule`, `Campaign`, `Segment` | the commercial machinery pointed at the catalog |
  | `Page` | landing/category/product pages on the site |

  | Relationship | Meaning |
  | --- | --- |
  | `IN_CATEGORY`, `HAS_BRAND`, `SUPPLIED_BY` | what a product is |
  | `OFFERS`, `PUBLISHED_ON` | where it is sold |
  | `HAS_MAPPING`, `APPLIES_TO` | which feed requires which field, for which category |
  | `TARGETS`, `FILTERS_BY` | which campaigns and segments touch which products |
  | `FEATURES`, `COVERS`, `LINKS_TO` | what the site shows and links |

Where the answer is a consequence, it arrives as a **path** — the route from
the change to the consequence, so the consequence is proven, not asserted.
Queries that check existence (`03`, `05`) report the objects themselves; every
*why*-question answers with a path.

## Setup and run

Prerequisites: Python 3.8+ and the `relate` binary (no server, no signup).

```bash
# 1. install relate — one binary
curl -sSfL https://relatedb.ai/install.sh | bash

# 2. clone this repository, then build the store and verify everything
git clone <this-repository>
cd cascade
make verify
```

`make verify` first opens the **committed** store read-only (a broken commit
must fail before anything rebuilds it), then regenerates the synthetic catalog
(deterministic, seed 42), rebuilds `store/catalog.rl`, and runs every check:
seven queries, the MCP surface, baseline counts (self-grading, including the
negative control of553 clean products) and temporal standing. Expected output
ends with `== verify: OK ==`.
`make report` produces a paste-into-a-ticket markdown impact report with a
one-line verdict; `make demo` runs all seven queries interactively.

If your CPU predates AVX2, the prebuilt binary refuses to start — that is
exactly the hardware this project is for. The repository ships `bin/relate`,
a wrapper that uses the official CLI when it runs on your machine and
otherwise drives the same engine through the embedded Python client
(`relate_db` on PyPI, installed into `.venv` by `make venv`): same commands,
same engine, same store file. `make verify` bootstraps whatever your machine
needs.

**Windows:** the wrapper is a shell script — run under **WSL or Git Bash**
(the official `relate` CLI itself supports Windows natively, but `make` and
`bin/relate` expect a POSIX shell). If Windows security blocks the unsigned
Relate binary (Smart App Control / SmartScreen), WSL sidesteps it — another
contestant hit exactly this and moved to WSL2.

Run the whole demo with recorded parameters:

```bash
make demo
```

Explore the store by hand:

```bash
relate query --database store/catalog.rl \
  "MATCH (n) RETURN labels(n)[0] AS label, count(*) AS n ORDER BY n DESC"
```

## Where the data lives

- `store/catalog.rl` — the persistent Relate store, committed to this repository.
- `data/load.cypher` — the generated load script (produced by
  `scripts/generate_data.py`, seed 42).
- `data/demo_params.json` — the demo SKU and category pair used by the queries.

The dataset is **synthetic**: realistic structure, deliberate defects, no real
business data — a public dataset of e-commerce *operations* does not exist, and
publishing a real catalog is not an option (see [`docs/limitations.md`](docs/limitations.md)).
The generator ships in this repository, so every row can be audited.

### Planted defects — check the claims

The dataset carries deliberate defects and `make verify` asserts them, so the
demo is falsifiable rather than hand-picked:

| Planted defect | Found by |
| --- | --- |
| Missing `gtin` on products → rejected listings + a live risk pool | queries `02`, `05` |
| Orphan pages nothing links to | query `03` |
| Active products with no listing and no page | query `03` |
| Two overlapping price rules on one category (Sneakers) | query `04` |
| An expired promo still sitting in the graph (Skincare) | query `06` |
| **Negative control:** the553 products that carry `gtin` are never flagged (47 form the entire risk pool) | queries `05`, `07` |

## What a judge can explore in 60 seconds

1. **Open [`viewer.html`](viewer.html)** — the pre-built blast-radius graph of
   the demo product: offline, no install, no server. Click a node to isolate
   its edges. Rebuild it any time with `make viewer`.
2. **Run `make verify`** — eleven gates: every query, the MCP surface with all
   five tools, baseline counts, temporal standing, remediation and a
   parameter-injection test. Ends with `== verify: OK ==`.
3. **Run `make report`** — a paste-into-a-ticket markdown impact report that
   opens with a one-line verdict.
4. **Ask an agent** — the committed `.mcp.json` wires any MCP client to five
   read-only tools: `read_cypher`, `get_schema`, `blast_radius`,
   `rejection_causes`, `remediation`.
5. **Read [`docs/agent-session.md`](docs/agent-session.md)** — a real recorded
   Q&A, query by query, including the agent correcting its own first query.

## The store in numbers

| Metric | Value |
| --- | --- |
| Nodes | **1,667** — 600 products, 769 listings, 175 pages, 34 feed mappings, 38 rules/campaigns/segments, 51 catalog entities |
| Relationships | **3,730** |
| Store file | `store/catalog.rl` — **1.1 MB**, single file, committed |

Query timings, measured on a 2013 AMD A4-4020 without AVX2 — the floor, not
the ceiling:

| Query | Rows | Median |
| --- | --- | --- |
| 01 blast radius | 475 | 206 ms |
| 02 rejected root cause | 25 | 3.4 ms |
| 03 invisible inventory | 150 | 9.1 ms |
| 04 merge counterfactual | 15 | 1.2 ms |

## Connect an agent (MCP)

The store serves MCP over stdio with five read-only tools — `read_cypher`,
`get_schema`, and the domain tools **`blast_radius(sku)`** (direct breakage +
category machinery + the bounded 4-hop neighbourhood, each layer labelled
honestly), **`rejection_causes`** (why listings are rejected, with the proof
path) and **`remediation`** (the one fix, ranked by payoff) — so an agent can
answer "what breaks?" with paths instead of guesses:

```bash
relate serve --mcp stdio --database store/catalog.rl --read-only
# on hardware the prebuilt CLI does not support:
./bin/relate serve --mcp stdio --database store/catalog.rl --read-only
```

This repository ships a ready [.mcp.json](.mcp.json) — run your agent from
the repository root and it picks the graph up. A drop-in agent skill at
[`.agents/skills/cascade/SKILL.md`](.agents/skills/cascade/SKILL.md) teaches
any coding agent the five tools and the honesty rules before it writes a
single query (no rows → "no evidence in the graph"; every claim carries its
path). Then ask it: *"We are
discontinuing PU-1004 — what breaks?"*

### Live excerpt (recorded 21 Nov 2026 — not scripted)

**You:** What breaks if we stop selling PU-1004?

**Agent** — calls `get_schema`, then writes its own Cypher:

```cypher
MATCH (l:Listing)-[:OFFERS]->(p:Product {sku: $sku})
RETURN l.id AS listing, l.platform AS platform, l.status AS status
ORDER BY l.platform
```

**Agent:**

> **Two listings stop being sold:** `L-0004-0` — Google Shopping (live) and
> `L-0004-1` — Rozetka (live). The product page `/p/pu-1004` becomes dead and
> `/c/sneakers` loses a position; Google Merchant Center's **required `gtin`
> contract** on the Sneakers category turns the delisting into a feed-vs-catalog
> mismatch. Attached machinery that loses this product: rules
> `Sneakers margin floor` + `Sneakers winter promo -15%`, campaigns
> `Sneakers / Viber` and `Sneakers / Email (SendPulse)`, segments
> `Sneakers viewers 30d` and `Win-back 180d` — **every claim a path in the graph**.

The full transcript — all five queries of scene 1 and scene 2 (rejection root
cause → `gtin` + `Listing → Product → Category → Mapping → Feed` path) —
lives in [`docs/agent-session.md`](docs/agent-session.md). `make verify`
smoke-tests this surface too, including that write attempts are refused.

## How this maps to the judging criteria

- **Creativity** — an e-commerce *operations* change-impact graph: of the55
  entries in the gallery, none works on catalog/feed operations; the question
  ("what breaks?") is universal in a domain nobody else picked.
- **Relate and connected context** — single-file store, seven Cypher checks,
  MCP with five read-only tools (`read_cypher`, `get_schema`, `blast_radius`,
  `rejection_causes`, `remediation`), every answer a traversal with the path as
  proof.
- **Functionality and completeness** — `make verify` runs eleven gates
  end-to-end from a fresh clone; `make report`, `make demo`, `viewer.html` and
  the committed store all work with no extra setup.
- **Usefulness** — the weekly spreadsheet conversation of every e-commerce
  operator, moved into a graph; the verdict is one line you can paste into a
  ticket.
- **Documentation and reproducibility** — this README; `docs/` (live agent
  transcript, submission-form inventory, competitor analysis, limitations);
  seed-42 generator; synthetic-data disclosure.

Built with AI assistance under the owner's direction — design, code, tests and
docs — while **no AI runs inside the product**: every runtime answer is
deterministic Cypher against the store, and the graph outranks any model
(`docs/limitations.md`). The only third-party front-end asset is cytoscape.js
(MIT), vendored in `vendor/`.

## Limitations

See [`docs/limitations.md`](docs/limitations.md) — what Cascade does not do
and why, in the same spirit as Relate's own limitations page. When the graph
holds no evidence for a question, the answer is **no rows** — Cascade reports
insufficient evidence instead of inventing a confident conclusion.

## Beyond one file

The Cypher here is standard: when a catalog outgrows a single process, the same
queries run on Neo4j / Neo4j Aura, and a subgraph can be pulled into Relay for
local work and pushed back. Nothing in Cascade needs rewriting to get there.
