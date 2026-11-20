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

if [ "$fail" -ne 0 ]; then
  echo "== verify: FAILED =="
  exit 1
fi
echo "== verify: OK =="
