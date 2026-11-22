"""Internal package of the `relate` CLI fallback shim.

Public entry point stays `scripts/relate_compat.py` (invoked by bin/relate);
this package only organises its internals (pass R4):
  render.py  - output rendering (table/json/csv/markdown)
  query.py   - CLI flags, statement splitting, query execution, usage/version
  tools.py   - MCP tool implementations and the TOOLS registry
  mcp.py     - the stdio JSON-RPC loop
"""
