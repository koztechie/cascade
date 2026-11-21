---
name: cascade
description: Query the Cascade e-commerce change-impact graph (Relate by Neo4j). Use when asked what breaks if a product, price, brand or category changes; why a listing was rejected; which products risk rejection next; or what single fix clears the most risk.
---

# Cascade — change-impact graph

Single-file Relate store: `store/catalog.rl` (relative to the repository root).

## Tools (read-only MCP, server: `./bin/relate serve --mcp stdio --database store/catalog.rl --read-only`)

1. `blast_radius(sku)` — direct breakage + category machinery + bounded 4-hop neighbourhood, each layer labelled honestly.
2. `rejection_causes` — why listings are rejected, with the proof path.
3. `remediation` — the one missing field that clears the most risk.
4. `read_cypher` — generic read-only Cypher (200-row cap).
5. `get_schema` — labels, properties, relationship patterns.

## Rules (non-negotiable)

1. Call `get_schema` before writing any Cypher; never guess labels or relationship types.
2. Prefer the domain tools over raw `read_cypher`.
3. **If a query returns no rows, the answer is "no evidence in the graph" — never invent a result.** Absence of impact is not proof of safety.
4. Every claim must carry its path (the route through the graph that proves it).
5. Direct breakage and the 4-hop neighbourhood are different things: the neighbourhood is context, not breakage.
6. One writer per store: never run `make store`, `make demo` or `make report` while an MCP server holds the file.

## Key patterns

- Blast radius: `(p:Product {sku:$sku})-[*1..4]-(x)` filtered to impact labels.
- A rejection: `(:Listing {status:'rejected'})-[:OFFERS]->(:Product)-[:IN_CATEGORY]->(:Category)<-[:APPLIES_TO]-(:Mapping {required:true})<-[:HAS_MAPPING]-(:Feed)` where the product lacks the mapped property.
- The fix: run `remediation` — filling `gtin` clears the risk pool, but already-rejected listings still need re-submission (availability ≠ review state).

## Verification

`make verify` (eleven gates) asserts every query's expected output; `make report` prints a paste-into-a-ticket impact report with a one-line verdict.
