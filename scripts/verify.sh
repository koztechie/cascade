#!/usr/bin/env bash
# Verify every demo query against the built store.
# Fails (exit 1) if any query errors or does not return the expected rows.
set -euo pipefail

RELATE="${RELATE:-./bin/relate}"
STORE="${1:-store/catalog.rl}"
PARAMS="data/demo_params.json"

SKU=$(python3 -c "import json;print(json.load(open('$PARAMS'))['sku'])")
FROM=$(python3 -c "import json;print(json.load(open('$PARAMS'))['merge_from'])")
TO=$(python3 -c "import json;print(json.load(open('$PARAMS'))['merge_into'])")

fail=0
echo "== verify: $STORE (demo sku: $SKU) =="

echo "-- 01 blast radius"
if ! out=$("$RELATE" query --database "$STORE" --param "sku=$SKU" --mode table \
      < queries/01_blast_radius.cypher); then
  echo "FAIL 01: query errored"; fail=1
else
  echo "$out" | sed -n '1,15p'
  echo "$out" | grep -q 'Listing' || { echo "FAIL 01: no Listing impact"; fail=1; }
  echo "$out" | grep -q 'Rule'    || { echo "FAIL 01: no Rule impact";    fail=1; }
  echo "$out" | grep -q 'Page'    || { echo "FAIL 01: no Page impact";    fail=1; }
fi

echo "-- 02 rejected root cause"
if ! out=$("$RELATE" query --database "$STORE" --mode table \
      < queries/02_rejected_root_cause.cypher); then
  echo "FAIL 02: query errored"; fail=1
else
  echo "$out" | sed -n '1,15p'
  echo "$out" | grep -q 'gtin' || { echo "FAIL 02: missing_field 'gtin' not found"; fail=1; }
fi

echo "-- 03 invisible inventory"
if ! out=$("$RELATE" query --database "$STORE" --mode table \
      < queries/03_orphans.cypher); then
  echo "FAIL 03: query errored"; fail=1
else
  echo "$out" | sed -n '1,15p'
  echo "$out" | grep -q 'orphan_page'       || { echo "FAIL 03: no orphan pages";       fail=1; }
  echo "$out" | grep -q 'invisible_product' || { echo "FAIL 03: no invisible products"; fail=1; }
fi

echo "-- 04 merge counterfactual ($FROM -> $TO)"
if ! out=$("$RELATE" query --database "$STORE" --param "from=$FROM" --param "to=$TO" \
      --mode table < queries/04_merge_conflicts.cypher); then
  echo "FAIL 04: query errored"; fail=1
else
  echo "$out" | sed -n '1,20p'
  echo "$out" | grep -q 'rule'       || { echo "FAIL 04: no rule conflicts";       fail=1; }
  echo "$out" | grep -q 'campaign'   || { echo "FAIL 04: no campaign conflicts";   fail=1; }
  echo "$out" | grep -q 'feed_mapping' || { echo "FAIL 04: no mapping conflicts";  fail=1; }
fi

echo "-- 05 MCP surface (read-only agent access)"
if ! mcp_out=$(printf '%s\n' \
    '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}' \
    '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
    '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"read_cypher","arguments":{"query":"MATCH (n:Product) RETURN count(n) AS c"}}}' \
    '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"read_cypher","arguments":{"query":"CREATE (x:Bad) RETURN x"}}}' \
    | "$RELATE" serve --mcp stdio --database "$STORE" --read-only); then
  echo "FAIL 05: MCP server exited non-zero"; fail=1
else
  echo "$mcp_out" | grep -q '"name": "read_cypher"' || { echo "FAIL 05: read_cypher missing"; fail=1; }
  echo "$mcp_out" | grep -q 'row_count'             || { echo "FAIL 05: query through MCP failed"; fail=1; }
  echo "$mcp_out" | grep -q '"isError": true'       || { echo "FAIL 05: write not refused"; fail=1; }
  echo "MCP handshake, read query and write refusal checked"
fi

echo "-- 06 rejection risk (proactive, before the marketplace says no)"
if ! out=$("$RELATE" query --database "$STORE" --mode table < queries/05_rejection_risk.cypher); then
  echo "FAIL 06: query errored"; fail=1
else
  echo "$out" | sed -n '1,12p'
  echo "$out" | grep -q 'gtin'   || { echo "FAIL 06: no gtin-risk rows"; fail=1; }
  echo "$out" | grep -q 'active' || { echo "FAIL 06: no active products at risk"; fail=1; }
fi

echo "-- 07 baseline counts (self-grading against the README numbers)"
if ! out=$("$RELATE" query --database "$STORE" --mode table <<'CYPHER'
MATCH (n) RETURN count(n) AS total_nodes
CYPHER
); then
  echo "FAIL 07: node count query errored"; fail=1
else
  echo "$out" | sed -n '1,4p'
  echo "$out" | grep -q '1667' || { echo "FAIL 07: node baseline drift (expected 1667)"; fail=1; }
fi
if ! out=$("$RELATE" query --database "$STORE" --mode table <<'CYPHER'
MATCH ()-[r]->() RETURN count(r) AS total_rels
CYPHER
); then
  echo "FAIL 07: relationship count query errored"; fail=1
else
  echo "$out" | grep -q '3730' || { echo "FAIL 07: relationship baseline drift (expected 3730)"; fail=1; }
fi
if ! out=$("$RELATE" query --database "$STORE" --mode table <<'CYPHER'
MATCH (p:Product) RETURN count(p) AS products
CYPHER
); then
  echo "FAIL 07: product count query errored"; fail=1
else
  echo "$out" | grep -q '600' || { echo "FAIL 07: product baseline drift (expected 600)"; fail=1; }
fi
if ! out=$("$RELATE" query --database "$STORE" --mode table <<'CYPHER'
MATCH (p:Product) WHERE p.gtin IS NOT NULL RETURN count(p) AS control_products
CYPHER
); then
  echo "FAIL 07: control count query errored"; fail=1
else
  echo "$out" | grep -q '553' || { echo "FAIL 07: negative-control drift (expected 553)"; fail=1; }
  echo "   negative control: 553 products with gtin are never flagged"
fi

echo "-- 08 temporal standing (promo active vs expired as of 2026-12-09)"
if ! out=$("$RELATE" query --database "$STORE" --mode table < queries/06_active_vs_expired.cypher); then
  echo "FAIL 08: query errored"; fail=1
else
  echo "$out" | sed -n '1,8p'
  echo "$out" | grep -q 'active'   || { echo "FAIL 08: no active promo row"; fail=1; }
  echo "$out" | grep -q 'expired' || { echo "FAIL 08: no expired promo row"; fail=1; }
fi

echo "-- 09 remediation (which one fix clears the most risk)"
if ! out=$("$RELATE" query --database "$STORE" --mode table < queries/07_remediation.cypher); then
  echo "FAIL 09: query errored"; fail=1
else
  echo "$out" | sed -n '1,6p'
  echo "$out" | grep -q 'gtin' || { echo "FAIL 09: gtin remediation row missing"; fail=1; }
fi

if [ "$fail" -ne 0 ]; then
  echo "== verify: FAILED =="
  exit 1
fi
echo "== verify: OK =="
