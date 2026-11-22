#!/usr/bin/env bash
# Run all seven demo queries (queries/01..07) with the parameters recorded
# at data generation.
set -euo pipefail

RELATE="${RELATE:-./bin/relate}"
STORE="${1:-store/catalog.rl}"
PARAMS="data/demo_params.json"

SKU=$(${PYTHON:-python3} -c "import json;print(json.load(open('$PARAMS'))['sku'])")
FROM=$(${PYTHON:-python3} -c "import json;print(json.load(open('$PARAMS'))['merge_from'])")
TO=$(${PYTHON:-python3} -c "import json;print(json.load(open('$PARAMS'))['merge_into'])")

echo "## Cascade demo — store: $STORE"

echo
echo "### 01 — What breaks if we stop selling $SKU?"
"$RELATE" query --database "$STORE" --param "sku=$SKU" --mode table \
  < queries/01_blast_radius.cypher

echo
echo "### 02 — Why are listings rejected? (root cause with proof)"
"$RELATE" query --database "$STORE" --mode table \
  < queries/02_rejected_root_cause.cypher

echo
echo "### 03 — What is invisible or unlinked right now?"
"$RELATE" query --database "$STORE" --mode table \
  < queries/03_orphans.cypher

echo
echo "### 04 — What collides if we merge $FROM into $TO?"
"$RELATE" query --database "$STORE" --param "from=$FROM" --param "to=$TO" --mode table \
  < queries/04_merge_conflicts.cypher

echo
echo "### 05 — What will the marketplace reject next? (proactive, before it says no)"
"$RELATE" query --database "$STORE" --mode table \
  < queries/05_rejection_risk.cypher

echo
echo "### 06 — Which promos are active vs expired as of 2026-12-09?"
"$RELATE" query --database "$STORE" --mode table \
  < queries/06_active_vs_expired.cypher

echo
echo "### 07 — Which single fix clears the most rejection risk?"
"$RELATE" query --database "$STORE" --mode table \
  < queries/07_remediation.cypher
