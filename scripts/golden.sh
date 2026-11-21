#!/usr/bin/env bash
# Golden fixtures (P0.1) — the parity anchor for every refactor pass.
#
#   scripts/golden.sh check    compare fresh outputs against tests/golden/
#   scripts/golden.sh update   refresh the snapshots (only after an
#                              INTENTIONAL change; review `git diff tests/golden`)
#
# Design notes:
# - verify.sh runs with the SAME retry-once policy as `make verify`
#   (the known transient class must not fail the parity gate); the retry
#   notice goes to stderr so the captured stdout stays byte-stable.
# - Fixtures are captured through the same command substitution used for
#   comparison, so trailing-newline handling is identical on both sides.
set -euo pipefail

RELATE="${RELATE:-./bin/relate}"
MODE="${1:-check}"
STORE="${2:-store/catalog.rl}"
GOLDEN=tests/golden

case "$MODE" in
  check|update) ;;
  *) echo "usage: golden.sh [check|update] [store-path]" >&2; exit 2 ;;
esac

# Output of a passing verify run; one retry on failure (transient policy).
run_verify() {
  local out attempt
  for attempt in 1 2; do
    if out=$(RELATE="$RELATE" bash scripts/verify.sh "$STORE"); then
      printf '%s\n' "$out"
      return 0
    fi
    echo "golden: verify attempt ${attempt} failed — retrying (transient policy)" >&2
  done
  printf '%s\n' "$out" >&2
  echo "golden: verify failed twice — this is a REAL failure, not a transient" >&2
  return 1
}

demo_out=$(RELATE="$RELATE" bash scripts/demo.sh)
report_out=$(RELATE="$RELATE" bash scripts/report.sh)
verify_out=$(run_verify)

if [ "$MODE" = "update" ]; then
  mkdir -p "$GOLDEN"
  printf '%s\n' "$demo_out" > "$GOLDEN/demo.txt"
  printf '%s\n' "$report_out" > "$GOLDEN/report.md"
  printf '%s\n' "$verify_out" > "$GOLDEN/verify.txt"
  echo "golden fixtures updated — review 'git diff tests/golden' before committing"
  exit 0
fi

fail=0
check() { # golden-file-name, actual-output
  if ! printf '%s\n' "$2" | diff -u "$GOLDEN/$1" -; then
    echo "GOLDEN FAIL: $1 output drifted"
    fail=1
  fi
}
check demo.txt "$demo_out"
check report.md "$report_out"
check verify.txt "$verify_out"

if [ "$fail" -ne 0 ]; then
  echo "== golden: FAILED =="
  exit 1
fi
echo "== golden: OK =="
