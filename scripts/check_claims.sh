#!/usr/bin/env bash
# Meta-verify (P0.4): reconcile headline claims in README / CHECKLIST / SKILL
# against the codebase, so claim drift (the `3731 -> 3730` class) fails a gate
# instead of waiting for a reader to notice.
#
# Ground truth is taken from the CODE and the LIVE server, never from docs:
#   - query count      : ls queries/*.cypher
#   - gate count       : numbered sections in scripts/verify.sh
#   - tool count/names : tools/list over the real MCP server
#   - baseline numbers : the constants verify.sh itself asserts
set -euo pipefail

RELATE="${RELATE:-./bin/relate}"
STORE="${1:-store/catalog.rl}"
PYTHON="${PYTHON:-python3}"
fail=0

need_in() { # file, fixed-string, claim
  if ! grep -qF "$2" "$1" 2>/dev/null; then
    echo "CLAIM FAIL: '$1' does not contain \"$2\"  ($3)"
    fail=1
  fi
}
need_in_any() { # file, fixed-string-A, fixed-string-B, claim
  if ! grep -qF "$2" "$1" 2>/dev/null && ! grep -qF "$3" "$1" 2>/dev/null; then
    echo "CLAIM FAIL: '$1' contains neither \"$2\" nor \"$3\"  ($4)"
    fail=1
  fi
}

# --- ground truth ----------------------------------------------------------
NQ=$(ls queries/*.cypher | wc -l | tr -d ' ')
NGATE=$(grep -c 'echo "-- [0-9]' scripts/verify.sh || true)

TOOLS_LINE=$(printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | "$RELATE" serve --mcp stdio --database "$STORE" --read-only 2>/dev/null | tail -1)
NTOOLS=$(printf '%s' "$TOOLS_LINE" | "$PYTHON" -c 'import json,sys; print(len(json.load(sys.stdin)["result"]["tools"]))')

echo "ground truth: queries=$NQ gates=$NGATE tools=$NTOOLS"

# --- structural claims -----------------------------------------------------
[ "$NQ" = "7" ]   || { echo "CLAIM FAIL: expected7 queries, found $NQ"; fail=1; }
[ "$NGATE" = "11" ] || { echo "CLAIM FAIL: expected 11 verify gates, found $NGATE"; fail=1; }
[ "$NTOOLS" = "5" ] || { echo "CLAIM FAIL: expected 5 MCP tools, found $NTOOLS"; fail=1; }

need_in README.md "seven queries"          "query count in README"
need_in README.md "eleven gates"           "gate count in README"
need_in README.md "five read-only tools"   "tool count in README"
need_in CHECKLIST.md "11 gates"            "gate count in CHECKLIST"
need_in CHECKLIST.md "seven queries"       "query count in CHECKLIST"
need_in .agents/skills/cascade/SKILL.md "eleven gates" "gate count in SKILL"

# --- every public tool must be named in the docs AND asserted by verify ----
for t in read_cypher get_schema blast_radius rejection_causes remediation; do
  need_in README.md "$t" "tool '$t' listed in README"
  need_in .agents/skills/cascade/SKILL.md "$t" "tool '$t' listed in SKILL"
  need_in scripts/verify.sh "\"name\": \"$t\"" "tool '$t' asserted in verify.sh"
done

# --- baseline constants: verify's expectations must be what the docs claim --
for c in 1667 3730 600 553; do
  need_in scripts/verify.sh "$c" "baseline $c asserted by verify"
done
need_in README.md "1,667"      "node baseline in README"
need_in README.md "3,730"      "relationship baseline in README"
need_in README.md "600 products" "product baseline in README"
need_in README.md "553"        "negative-control baseline in README"

# --- summary ---------------------------------------------------------------
if [ "$fail" -ne 0 ]; then
  echo "== check-claims: FAILED =="
  exit 1
fi
echo "== check-claims: OK (docs match the code) =="
