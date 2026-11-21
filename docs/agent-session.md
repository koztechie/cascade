# Agent session transcript — Cascade × Relate MCP

**Recorded:** 21 November 2026, live (not simulated) through the MCP server
configured in `opencode.json`:

```text
./bin/relate serve --mcp stdio --database store/catalog.rl --read-only
```

**Tools the agent has:** `get_schema`, `read_cypher` (read-only; rows capped at
200 with a truncation marker). The agent reads the schema itself and writes its
own Cypher — no queries are pre-baked into a prompt.

---

## Scene 1 — "What breaks if we stop selling PU-1004?"

**Human:** What breaks if we stop selling PU-1004?

**Agent → `get_schema`** (excerpt of the result):

```text
12 node types: Listing(769), Product(600), Page(175), Mapping(34), Category(17),
Brand(15), Rule(15), Campaign(15), Supplier(8), Segment(8), Marketplace(6), Feed(5)
13 relationship types: OFFERS, PUBLISHED_ON, IN_CATEGORY, HAS_BRAND, SUPPLIED_BY,
HAS_MAPPING, APPLIES_TO, TARGETS, FILTERS_BY, FEATURES, COVERS, LINKS_TO,
HAS_SUBCATEGORY
```

**Agent → `read_cypher` #1 — impact summary (own query):**

```cypher
MATCH (p:Product {sku: $sku})-[*1..4]-(x)
WHERE x:Listing OR x:Feed OR x:Rule OR x:Campaign OR x:Page OR x:Segment
RETURN labels(x)[0] AS impact_type, count(DISTINCT x) AS nodes
ORDER BY nodes DESC
```

```text
Listing 381 · Page 56 · Rule 15 · Campaign 15 · Segment 8 · Feed 1
```

> Honest note: the first draft of this query counted *paths*, not distinct
> nodes, which inflated the numbers. The agent corrected itself to
> `count(DISTINCT x)` before answering. The381 listings are **neighbours**
> (sibling SKUs in the category) — they are context, not breakage.

**Agent → `read_cypher` #2 — direct listings (own query):**

```cypher
MATCH (l:Listing)-[:OFFERS]->(p:Product {sku: $sku})
RETURN l.id AS listing, l.platform AS platform, l.status AS status
ORDER BY l.platform
```

```text
L-0004-0 | Google Shopping | live
L-0004-1 | Rozetka         | live
```

**Agent → `read_cypher` #3 — pages and price rules (own query):**

```cypher
MATCH (p:Product {sku: $sku})-[:IN_CATEGORY]->(c:Category)
OPTIONAL MATCH (pg:Page)-[:FEATURES]->(p)
OPTIONAL MATCH (cp:Page)-[:COVERS]->(c)
OPTIONAL MATCH (r:Rule)-[:APPLIES_TO]->(c)
RETURN DISTINCT c.name AS category, pg.url AS product_page,
       cp.url AS category_page, r.name AS rule
```

```text
Sneakers | /p/pu-1004 | /c/sneakers | Sneakers margin floor
Sneakers | /p/pu-1004 | /c/sneakers | Sneakers winter promo -15%
```

**Agent → `read_cypher` #4 — feed contract (own query):**

```cypher
MATCH (p:Product {sku: $sku})-[:IN_CATEGORY]->(c:Category)
      <-[:APPLIES_TO]-(m:Mapping)<-[:HAS_MAPPING]-(f:Feed)
RETURN f.name AS feed, m.target_field AS contract_field, m.required AS required
```

```text
Google Merchant Center | gtin | true
```

**Agent → `read_cypher` #5 — campaigns and segments (own query):**

```cypher
MATCH (p:Product {sku: $sku})-[:IN_CATEGORY]->(c:Category)
OPTIONAL MATCH (ca:Campaign)-[:TARGETS]->(c)
OPTIONAL MATCH (sg:Segment)-[:FILTERS_BY]->(c)
OPTIONAL MATCH (p)-[:HAS_BRAND]->(b:Brand)
OPTIONAL MATCH (ca2:Campaign)-[:TARGETS]->(b)
OPTIONAL MATCH (sg2:Segment)-[:FILTERS_BY]->(b)
RETURN collect(DISTINCT ca.name) AS category_campaigns,
       collect(DISTINCT sg.name) AS category_segments,
       collect(DISTINCT ca2.name) AS brand_campaigns,
       collect(DISTINCT sg2.name) AS brand_segments
```

```text
category_campaigns: ["Sneakers / Viber", "Sneakers / Email (SendPulse)"]
category_segments:  ["Sneakers viewers 30d", "Win-back 180d"]
brand_campaigns:    []   brand_segments: []
```

### Answer (agent)

**Breaks directly:**

| What | Concrete | Path as proof |
| --- | --- | --- |
| 2 listings | `L-0004-0` Google Shopping (live), `L-0004-1` Rozetka (live) | `(:Listing)-[:OFFERS]->(:Product {sku:'PU-1004'})-[:PUBLISHED_ON]->(:Marketplace)` |
| Product page | `/p/pu-1004` becomes dead | `(:Page)-[:FEATURES]->(:Product {sku:'PU-1004'})` |
| Category page | `/c/sneakers` loses a position | `(:Page)-[:COVERS]->(:Category)<-[:IN_CATEGORY]-(:Product)` |
| Feed contract | Google Merchant Center requires `gtin` (`required: true`) on Sneakers; delisting creates a feed-vs-catalog mismatch | `(:Feed)-[:HAS_MAPPING]->(:Mapping {target_field:'gtin'})-[:APPLIES_TO]->(:Category)` |

**Attached commercial machinery (affected, not broken):** rules
`Sneakers margin floor`, `Sneakers winter promo -15%`; campaigns
`Sneakers / Viber`, `Sneakers / Email (SendPulse)`; segments
`Sneakers viewers 30d`, `Win-back 180d`.

**Neighbourhood (context only, not breakage):** the 4-hop ball holds 381
listings, 56 pages, 15 rules, 15 campaigns, 8 segments, 1 feed — sibling SKUs
that removing PU-1004 does **not** touch.

**One-line version (video):** *"Two listings, one dead page, one feed contract
and six commercial objects — every claim proven by a path in the graph."*

---

## Scene 2 — "Why was this listing rejected?"

**Human:** Why is this listing rejected?

**Agent → `get_schema`** first (fresh), then `read_cypher` root cause (own query):

```cypher
MATCH (l:Listing {status: 'rejected'})-[:OFFERS]->(p:Product)-[:IN_CATEGORY]->(c:Category)
MATCH (f:Feed)-[:HAS_MAPPING]->(m:Mapping)-[:APPLIES_TO]->(c)
WHERE m.required AND p.gtin IS NULL
RETURN l.id AS listing, l.platform AS platform, p.sku AS sku,
       c.name AS category, f.name AS feed, m.target_field AS missing_field
ORDER BY l.platform, l.id
LIMIT 10
```

```text
L-0012-0 | Amazon | QU-1012 | Fitness   | Google Merchant Center | gtin
L-0093-0 | Amazon | VE-1093 | Wearables | Meta Catalog           | gtin
L-0093-0 | Amazon | VE-1093 | Wearables | Google Merchant Center | gtin
L-0123-0 | Amazon | PU-1123 | Audio     | Meta Catalog           | gtin
L-0123-0 | Amazon | PU-1123 | Audio     | Google Merchant Center | gtin
... (10+ rows, every one: missing_field = gtin)
```

**Agent → `read_cypher` — the rejection path itself (own query):**

```cypher
MATCH path = (l:Listing {id: $id})-[:OFFERS]->(p:Product)-[:IN_CATEGORY]->(c:Category)
      <-[:APPLIES_TO]-(m:Mapping)<-[:HAS_MAPPING]-(f:Feed)
RETURN [n IN nodes(path) | labels(n)[0]] AS node_sequence,
       m.target_field AS missing_field, m.required AS required
```

```text
[Listing, Product, Category, Mapping, Feed] | gtin     | true   ← the cause
[Listing, Product, Category, Mapping, Feed] | material | false  ← excluded
```

### Answer (agent)

**Cause: missing `gtin`.** The product lacks a `gtin` that its category's feed
contract marks as **required**.

**Path as proof (example `L-0012-0`, Amazon):**

```text
(:Listing 'L-0012-0')
  -[:OFFERS]->      (:Product 'QU-1012', no gtin)
  -[:IN_CATEGORY]-> (:Category 'Fitness')
  <-[:APPLIES_TO]-  (:Mapping {target_field:'gtin', required:true})
  <-[:HAS_MAPPING]- (:Feed 'Google Merchant Center')
```

**Trap handled:** the same traversal also matches a `material` mapping with
`required: false`. The agent filters on `required = true` — only the mandatory
`gtin` explains a rejection. This is the difference between an agent that
understands the graph and one that returns the first row.

---

## Why this matters

- Every answer is a **path**, not an assertion: judges (and users) can replay
  each claim with one Cypher statement.
- The agent **reads the schema before writing** — labels and relationship types
  come from `get_schema`, not from guesses.
- Everything runs **read-only** through `relate serve --mcp stdio … --read-only`;
  write attempts are refused with `isError` (verified by `make verify`, check 05).
- The whole session ran on a 2013 AMD A4-4020 (no AVX2) through the embedded
  Python fallback — the same commands work on any modern machine via the
  official `relate` CLI.
