#!/usr/bin/env bash
# Verify every demo query against the built store.
# Fails (exit 1) if any query errors or does not return the expected rows.
set -euo pipefail

RELATE="${RELATE:-./bin/relate}"
STORE="${1:-store/catalog.rl}"
PARAMS="data/demo_params.json"

# Row-cap guard (found by dry run #2): the official CLI defaults to 100 rows
# per statement when it detects an agent harness and stdout is not a terminal,
# which truncates gate output and fails verify for a reason that has nothing to
# do with the store. `make verify` exports RELATE_MAX_ROWS=0 for every target;
# this line covers running this script directly.
export RELATE_MAX_ROWS="${RELATE_MAX_ROWS:-0}"

SKU=$(${PYTHON:-python3} -c "import json;print(json.load(open('$PARAMS'))['sku'])")
FROM=$(${PYTHON:-python3} -c "import json;print(json.load(open('$PARAMS'))['merge_from'])")
TO=$(${PYTHON:-python3} -c "import json;print(json.load(open('$PARAMS'))['merge_into'])")

fail=0

# R1 helper — replaces the twelve copies of the old inline pattern
#   if ! out=$(...); then echo "FAIL NN: ..."; fail=1; else sed; greps; fi
#
#   query_out <display-lines | -> <exact-fail-message> <command...>
#
# On failure it prints the message verbatim, sets fail=1 and returns 1, so the
# caller's grep block is skipped — byte-identical stdout to the old pattern,
# on both the success and the error path. $out stays global on purpose: the
# caller greps the FULL output, not the displayed head.
query_out() {
  local lines="$1" msg="$2"
  shift 2
  if ! out=$("$@"); then
    echo "$msg"
    fail=1
    out=""
    return 1
  fi
  if [ "$lines" != "-" ]; then
    echo "$out" | sed -n "1,${lines}p"
  fi
  return 0
}

echo "== verify: $STORE (demo sku: $SKU) =="

echo "-- 01 blast radius"
if query_out 15 "FAIL 01: query errored" "$RELATE" query --database "$STORE" --read-only --param "sku=$SKU" --mode table < queries/01_blast_radius.cypher; then
  echo "$out" | grep -q 'Listing' || { echo "FAIL 01: no Listing impact"; fail=1; }
  echo "$out" | grep -q 'Rule'    || { echo "FAIL 01: no Rule impact";    fail=1; }
  echo "$out" | grep -q 'Page'    || { echo "FAIL 01: no Page impact";    fail=1; }
fi

echo "-- 02 rejected root cause"
if query_out 15 "FAIL 02: query errored" "$RELATE" query --database "$STORE" --read-only --param "sku=$SKU" --mode table < queries/02_rejected_root_cause.cypher; then
  echo "$out" | grep -q 'gtin' || { echo "FAIL 02: missing_field 'gtin' not found"; fail=1; }
fi

echo "-- 03 invisible inventory"
if query_out 15 "FAIL 03: query errored" "$RELATE" query --database "$STORE" --read-only --mode table < queries/03_orphans.cypher; then
  echo "$out" | grep -q 'orphan_page'       || { echo "FAIL 03: no orphan pages";       fail=1; }
  echo "$out" | grep -q 'invisible_product' || { echo "FAIL 03: no invisible products"; fail=1; }
fi

echo "-- 04 merge counterfactual ($FROM -> $TO)"
if query_out 20 "FAIL 04: query errored" "$RELATE" query --database "$STORE" --read-only --param "from=$FROM" --param "to=$TO" --mode table < queries/04_merge_conflicts.cypher; then
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
    '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"blast_radius","arguments":{"sku":"PU-1004"}}}' \
    '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"rejection_causes","arguments":{}}}' \
    '{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"remediation","arguments":{}}}' \
    | "$RELATE" serve --mcp stdio --database "$STORE" --read-only); then
  echo "FAIL 05: MCP server exited non-zero"; fail=1
else
  echo "$mcp_out" | grep -q '"name": "read_cypher"' || { echo "FAIL 05: read_cypher missing"; fail=1; }
  echo "$mcp_out" | grep -q '"name": "get_schema"'  || { echo "FAIL 05: get_schema missing"; fail=1; }
  echo "$mcp_out" | grep -q 'row_count'             || { echo "FAIL 05: query through MCP failed"; fail=1; }
  echo "$mcp_out" | grep -q '"isError": true'       || { echo "FAIL 05: write not refused"; fail=1; }
  echo "$mcp_out" | grep -q '"name": "blast_radius"' || { echo "FAIL 05: blast_radius missing from catalog"; fail=1; }
  echo "$mcp_out" | grep -q '"name": "rejection_causes"' || { echo "FAIL 05: rejection_causes missing from catalog"; fail=1; }
  echo "$mcp_out" | grep -q '"name": "remediation"' || { echo "FAIL 05: remediation missing from catalog"; fail=1; }
  echo "$mcp_out" | grep -q 'listings'              || { echo "FAIL 05: blast_radius call failed"; fail=1; }
  echo "$mcp_out" | grep -q 'missing_field'         || { echo "FAIL 05: rejection_causes call failed"; fail=1; }
  echo "$mcp_out" | grep -q 'feed_risks_cleared'    || { echo "FAIL 05: remediation call failed"; fail=1; }
  # blast_radius numeric parity (P0.5): the SAME expected values must come
  # from the CLI path and from the MCP tool, so moving SQL (pass R3) cannot
  # silently change them. Update these six numbers together with the baseline
  # in gate 07 when the data changes intentionally.
  # Pattern styles are empirically verified against the real wire format:
  #   MCP stdout double-encodes the tool payload  -> grep -F 'key\": value'
  #   CLI --mode json is plain JSON, spacing may
  #   differ on the official binary               -> grep -E '"key": *value'
  cli_direct=$("$RELATE" query --database "$STORE" --read-only --mode json <<'CYPHER'
MATCH (p:Product {sku: 'PU-1004'})
OPTIONAL MATCH (l:Listing)-[:OFFERS]->(p)
OPTIONAL MATCH (pg:Page)-[:FEATURES]->(p)
RETURN count(DISTINCT l) AS listings, count(DISTINCT pg) AS pages
CYPHER
)
  echo "$cli_direct" | grep -Eq '"listings": *2' || { echo "FAIL 05: CLI direct listings != 2"; fail=1; }
  echo "$cli_direct" | grep -Eq '"pages": *1'    || { echo "FAIL 05: CLI direct pages != 1"; fail=1; }
  echo "$mcp_out" | grep -Fq 'listings\": 2'     || { echo "FAIL 05: blast_radius listings != 2"; fail=1; }
  echo "$mcp_out" | grep -Fq 'pages\": 1'        || { echo "FAIL 05: blast_radius pages != 1"; fail=1; }
  echo "$mcp_out" | grep -Fq 'category\": \"Sneakers' || { echo "FAIL 05: blast_radius category != Sneakers"; fail=1; }
  echo "$mcp_out" | grep -Fq 'rules\": 2'        || { echo "FAIL 05: blast_radius rules != 2"; fail=1; }
  echo "$mcp_out" | grep -Fq 'campaigns\": 2'    || { echo "FAIL 05: blast_radius campaigns != 2"; fail=1; }
  echo "$mcp_out" | grep -Fq 'segments\": 2'     || { echo "FAIL 05: blast_radius segments != 2"; fail=1; }
  echo "$mcp_out" | grep -Fq 'feeds\": 1'        || { echo "FAIL 05: blast_radius feeds != 1"; fail=1; }
  echo "$mcp_out" | grep -Fq 'direct = real breakage' || { echo "FAIL 05: blast_radius honesty label missing"; fail=1; }
  cli_count=$("$RELATE" query --database "$STORE" --read-only --mode table <<'CYPHER'
MATCH (n:Product) RETURN count(n) AS products
CYPHER
)
  echo "$cli_count" | grep -q '600' || { echo "FAIL 05: CLI product count not 600"; fail=1; }
  echo "$mcp_out" | grep -q '600'  || { echo "FAIL 05: MCP product count not 600 (CLI/MCP parity broken)"; fail=1; }
  echo "MCP handshake, reads, blast_radius tool, write refusal and CLI/MCP parity checked"
fi

echo "-- 06 rejection risk (proactive, before the marketplace says no)"
if query_out 12 "FAIL 06: query errored" "$RELATE" query --database "$STORE" --read-only --mode table < queries/05_rejection_risk.cypher; then
  echo "$out" | grep -q 'gtin'   || { echo "FAIL 06: no gtin-risk rows"; fail=1; }
  echo "$out" | grep -q 'active' || { echo "FAIL 06: no active products at risk"; fail=1; }
fi

echo "-- 07 baseline counts (self-grading against the README numbers)"
if query_out 4 "FAIL 07: node count query errored" "$RELATE" query --database "$STORE" --read-only --mode table <<< 'MATCH (n) RETURN count(n) AS total_nodes'; then
  echo "$out" | grep -q '1667' || { echo "FAIL 07: node baseline drift (expected 1667)"; fail=1; }
fi
if query_out - "FAIL 07: relationship count query errored" "$RELATE" query --database "$STORE" --read-only --mode table <<< 'MATCH ()-[r]->() RETURN count(r) AS total_rels'; then
  echo "$out" | grep -q '3730' || { echo "FAIL 07: relationship baseline drift (expected 3730)"; fail=1; }
fi
if query_out - "FAIL 07: product count query errored" "$RELATE" query --database "$STORE" --read-only --mode table <<< 'MATCH (p:Product) RETURN count(p) AS products'; then
  echo "$out" | grep -q '600' || { echo "FAIL 07: product baseline drift (expected 600)"; fail=1; }
fi
if query_out - "FAIL 07: control count query errored" "$RELATE" query --database "$STORE" --read-only --mode table <<< 'MATCH (p:Product) WHERE p.gtin IS NOT NULL RETURN count(p) AS control_products'; then
  echo "$out" | grep -q '553' || { echo "FAIL 07: negative-control drift (expected 553)"; fail=1; }
  echo "   negative control: 553 products with gtin are never flagged"
fi

echo "-- 08 temporal standing (promo active vs expired as of 2026-12-09)"
if query_out 8 "FAIL 08: query errored" "$RELATE" query --database "$STORE" --read-only --mode table < queries/06_active_vs_expired.cypher; then
  echo "$out" | grep -q 'active'   || { echo "FAIL 08: no active promo row"; fail=1; }
  echo "$out" | grep -q 'expired' || { echo "FAIL 08: no expired promo row"; fail=1; }
fi

echo "-- 09 remediation (which one fix clears the most risk)"
if query_out 6 "FAIL 09: query errored" "$RELATE" query --database "$STORE" --read-only --mode table < queries/07_remediation.cypher; then
  echo "$out" | grep -q 'gtin' || { echo "FAIL 09: gtin remediation row missing"; fail=1; }
fi

echo "-- 10 parameter safety (injection-like sku must return nothing)"
if query_out 3 "FAIL 10: query errored" "$RELATE" query --database "$STORE" --read-only --param "sku=PU-1004'OR'1'='1" --mode table < queries/01_blast_radius.cypher; then
  if echo "$out" | grep -q 'Listing'; then
    echo "FAIL 10: injection-like parameter returned data — parameterization broken"
    fail=1
  else
    echo "   OK: injection-like parameter returned no rows"
  fi
fi

echo "-- 11 generator determinism (byte-identical under PYTHONHASHSEED=1)"
DET=/tmp/cascade-det-$$.cypher
if ! CASCADE_OUT="$DET" PYTHONHASHSEED=1 ${PYTHON:-python3} scripts/generate_data.py >/dev/null 2>&1; then
  echo "FAIL 11: generator errored under PYTHONHASHSEED=1"; fail=1
else
  if cmp -s data/load.cypher "$DET"; then
    echo "   OK: byte-identical under a different hash seed"
  else
    echo "FAIL 11: generator output differs under PYTHONHASHSEED=1 — not reproducible"
    fail=1
  fi
fi
rm -f "$DET"

# Pass M1: every gate above opened the store read-write, and a read-write
# checkpoint re-randomizes the parquet shard ids. Restore the byte-stable
# form so a rebuild equals the committed file (stderr only — stdout of this
# script is captured byte-exactly by golden.sh).
${PYTHON:-python3} scripts/normalize_store.py "$STORE" >&2

if [ "$fail" -ne 0 ]; then
  echo "== verify: FAILED =="
  exit 1
fi
echo "== verify: OK =="
