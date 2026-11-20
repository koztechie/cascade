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
4. **What collides** if we merge category X into Y? → `queries/04_merge_conflicts.cypher`

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

Every answer in Cascade is a **path**: the query returns the route from the
change to the consequence, so the consequence is proven, not asserted.

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

`make verify` regenerates the synthetic catalog (deterministic, seed 42),
builds `store/catalog.rl`, runs all four demo queries and fails if any of them
returns the wrong rows. Expected output ends with `== verify: OK ==`.

If your CPU predates AVX2, the prebuilt binary refuses to start — that is
exactly the hardware this project is for. The repository ships `bin/relate`,
a wrapper that uses the official CLI when it runs on your machine and
otherwise drives the same engine through the embedded Python client
(`relate_db` on PyPI, installed into `.venv` by `make venv`): same commands,
same engine, same store file. `make verify` bootstraps whatever your machine
needs.

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
business data.

## Look first, run later

[`viewer.html`](viewer.html) is the pre-built blast-radius view of the demo
product: open it in any browser — no install, no server, works offline.
Rebuild it from the store with `make viewer`.

## The store in numbers

| Metric | Value |
| --- | --- |
| Nodes | **1,667** — 600 products, 769 listings, 175 pages, 34 feed mappings, 38 rules/campaigns/segments, 51 catalog entities |
| Relationships | **3,731** |
| Store file | `store/catalog.rl` — **1.1 MB**, single file, committed |

Query timings, measured on a 2013 AMD A4-4020 without AVX2 — the floor, not
the ceiling:

| Query | Rows | Median |
| --- | --- | --- |
| 01 blast radius | 475 | 206 ms |
| 02 rejected root cause | 25 | 3.4 ms |
| 03 invisible inventory | 150 | 9.1 ms |
| 04 merge counterfactual | 15 | 1.2 ms |

## Limitations

See [`docs/limitations.md`](docs/limitations.md) — what Cascade does not do
and why, in the same spirit as Relate's own limitations page.

## Beyond one file

The Cypher here is standard: when a catalog outgrows a single process, the same
queries run on Neo4j / Neo4j Aura, and a subgraph can be pulled into Relay for
local work and pushed back. Nothing in Cascade needs rewriting to get there.
