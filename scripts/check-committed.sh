#!/usr/bin/env bash
# Credit-trail's lesson: the committed store must open read-only BEFORE we
# rebuild it — otherwise a broken commit would never be noticed by anyone
# who runs `make verify` (it deletes and rebuilds the store anyway).
set -euo pipefail

RELATE="${RELATE:-./bin/relate}"
STORE="${1:-store/catalog.rl}"

if [ ! -f "$STORE" ]; then
  echo "-- committed store: not present (skipped)"
  exit 0
fi

echo "-- committed store opens read-only (pre-rebuild check)"
if ! out=$("$RELATE" query --database "$STORE" --read-only --mode table <<'CYPHER'
MATCH (n) RETURN count(n) AS total_nodes
CYPHER
); then
  echo "FAIL committed: store does not open read-only"
  exit 1
fi
echo "$out" | tail -n +3 | sed 's/^/   /'
echo "$out" | grep -qE '[0-9]+' || { echo "FAIL committed: no row count returned"; exit 1; }
echo "   OK"
