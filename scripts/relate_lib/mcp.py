"""stdio JSON-RPC loop for `relate serve --mcp stdio` (moved verbatim)."""
import json
import sys

from .query import usage
from .tools import TOOLS, ToolError


def send(msg):
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def mcp_loop(db, read_only):
    try:
        import relate
    except ImportError:
        print("embedded Python client not installed; run: make venv",
              file=sys.stderr)
        sys.exit(1)
    try:
        conn = relate.connect(db, read_only=read_only)
    except Exception as e:
        print(json.dumps({"error": {"message": str(e)}}))
        sys.exit(1)

    tool_names = ["read_cypher", "get_schema", "blast_radius",
                  "rejection_causes", "remediation"]
    if not read_only:
        tool_names.append("write_cypher")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            send({"jsonrpc": "2.0", "id": None,
                  "error": {"code": -32700, "message": "Parse error"}})
            continue

        mid = msg.get("id")
        method = msg.get("method", "")

        if method == "initialize":
            client_ver = (msg.get("params") or {}).get(
                "protocolVersion", "2024-11-05")
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": client_ver,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "relate",
                               "version": "embedded-python-fallback"},
            }})
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": mid, "result": {}})
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "tools": [
                    {"name": name,
                     "description": TOOLS[name]["description"],
                     "inputSchema": TOOLS[name]["inputSchema"]}
                    for name in tool_names
                ],
            }})
        elif method == "tools/call":
            params = msg.get("params") or {}
            name = params.get("name")
            args = params.get("arguments") or {}
            if name not in tool_names or name not in TOOLS:
                send({"jsonrpc": "2.0", "id": mid, "result": {
                    "content": [{"type": "text",
                                 "text": "unknown tool: %s" % name}],
                    "isError": True,
                }})
                continue
            try:
                text = TOOLS[name]["fn"](conn, args)
                send({"jsonrpc": "2.0", "id": mid, "result": {
                    "content": [{"type": "text", "text": text}],
                }})
            except ToolError as e:
                send({"jsonrpc": "2.0", "id": mid, "result": {
                    "content": [{"type": "text", "text": str(e)}],
                    "isError": True,
                }})
            except Exception as e:
                send({"jsonrpc": "2.0", "id": mid, "result": {
                    "content": [{"type": "text",
                                 "text": "query error: %s" % e}],
                    "isError": True,
                }})
        elif method.startswith("notifications/"):
            continue
        elif mid is not None:
            send({"jsonrpc": "2.0", "id": mid,
                  "error": {"code": -32601, "message": "Method not found"}})


def parse_serve_args(argv):
    transport = None
    db = None
    read_only = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--mcp":
            i += 1
            if i >= len(argv):
                usage("--mcp needs a transport")
            transport = argv[i]
        elif a in ("--database", "-d"):
            i += 1
            if i >= len(argv):
                usage("--database needs a path")
            db = argv[i]
        elif a == "--read-only":
            read_only = True
        elif a == "stdio":
            transport = transport or "stdio"
        elif a.startswith("--"):
            # --host, --port, --auth ... : accepted and ignored only if the
            # transport is stdio (stdio skips auth by design)
            i += 1
            if i < len(argv) and not argv[i].startswith("-"):
                i += 1
        elif a.isdigit():
            usage("the shim serves stdio only; use "
                  "'serve --mcp stdio --database PATH'")
        else:
            usage("unexpected argument '%s'" % a)
        i += 1
    if transport != "stdio":
        usage("the shim serves stdio only; use "
              "'serve --mcp stdio --database PATH'")
    if db is None:
        usage("serve requires --database")
    return db, read_only
