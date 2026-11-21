#!/usr/bin/env python3
"""Drop-in subset of the `relate` CLI, backed by the embedded Python client.

Why this exists: the prebuilt `relate` binary requires a newer CPU (x86-64
with AVX2). On older machines it refuses to start. The engine itself runs
fine there as an embedded library (`relate_db` on PyPI), so this shim speaks
the same command line our scripts use and drives the same engine against the
same store format.

Supported surface (all Cascade needs):

    relate query --database PATH [--param NAME=VALUE]... [--mode MODE]
        < script.cypher        # statements separated by ';' at end of line
    relate serve --mcp stdio --database PATH [--read-only]
    relate --version

Exit codes follow the official CLI: 0 ok, 2 usage error, 6 statement rejected.
"""
import json
import sys

MAX_ROWS = 200
READ_KEYWORDS = {"MATCH", "OPTIONAL", "WITH", "RETURN", "UNWIND", "CALL",
                 "SHOW", "EXPLAIN", "PROFILE"}


def usage(msg):
    print(json.dumps({"error": {"message": msg}}))
    sys.exit(2)


def version():
    try:
        import relate  # noqa: F401
    except ImportError:
        print("embedded Python client not installed; run: make venv",
              file=sys.stderr)
        sys.exit(1)
    print("relate (embedded Python fallback, engine from relate_db)")
    sys.exit(0)


# ---------------------------------------------------------------------------
# query
# ---------------------------------------------------------------------------

def parse_query_args(argv):
    db = None
    mode = "table"
    params = {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--database", "-d"):
            i += 1
            if i >= len(argv):
                usage("--database needs a path")
            db = argv[i]
        elif a == "--param":
            i += 1
            if i >= len(argv) or "=" not in argv[i]:
                usage("--param needs NAME=VALUE")
            name, _, raw = argv[i].partition("=")
            try:
                params[name] = json.loads(raw)
            except (ValueError, json.JSONDecodeError):
                params[name] = raw
        elif a in ("--mode", "--format"):
            i += 1
            if i >= len(argv):
                usage("--mode needs a value")
            mode = argv[i]
        elif a in ("--json", "--csv", "--markdown"):
            mode = a.lstrip("-")
        elif a.startswith("-"):
            usage("unknown flag '%s' (shim supports: --database, --param, --mode)"
                  % a)
        else:
            usage("unexpected argument '%s'" % a)
        i += 1
    if db is None:
        usage("missing --database")
    return db, mode, params


def split_statements(text):
    """Statements are one per line, terminated by ';' (our file convention).

    Comment lines (`// ...`) are dropped so the parser never sees them.
    """
    buf = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        buf.append(line)
        if stripped.endswith(";"):
            stmt = "\n".join(buf).strip()
            if stmt.endswith(";"):
                stmt = stmt[:-1]
            yield stmt
            buf = []
    tail = "\n".join(buf).strip()
    if tail:
        yield tail


def render(rows, cols, mode):
    if mode == "json":
        print(json.dumps(rows, ensure_ascii=False, default=str))
        return
    if mode == "csv":
        print(",".join(cols))
        for r in rows:
            print(",".join(str(r.get(c, "")) for c in cols))
        return
    if mode == "markdown":
        print("| " + " | ".join(cols) + " |")
        print("| " + " | ".join("---" for _ in cols) + " |")
        for r in rows:
            print("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
        return
    if not rows:
        print("(no rows)")
        return
    cells = [[("" if r.get(c) is None else str(r.get(c))) for c in cols]
             for r in rows]
    widths = [max(len(c), *(len(row[i]) for row in cells))
              for i, c in enumerate(cols)]
    print(" | ".join(c.ljust(widths[i]) for i, c in enumerate(cols)))
    print("-+-".join("-" * w for w in widths))
    for row in cells:
        print(" | ".join(v.ljust(widths[i]) for i, v in enumerate(row)))


def run_query(argv):
    db, mode, params = parse_query_args(argv)
    script = sys.stdin.read()
    statements = list(split_statements(script))
    if not statements:
        usage("no statements on stdin")

    try:
        import relate
    except ImportError:
        print("embedded Python client not installed; run: make venv",
              file=sys.stderr)
        sys.exit(1)

    try:
        conn = relate.connect(db)
    except Exception as e:
        print(json.dumps({"error": {"message": str(e)}}))
        sys.exit(1)

    last_rows, last_cols = [], []
    for stmt in statements:
        try:
            cur = conn.execute(stmt, params or None)
            rows = cur.fetchall()
        except Exception as e:
            print(json.dumps({"error": {"message": str(e)}}))
            sys.exit(6)
        if rows:
            last_rows, last_cols = rows, list(rows[0].keys())

    if last_rows:
        render(last_rows, last_cols, mode)
    elif mode == "table":
        print("(ok)")
    sys.exit(0)


# ---------------------------------------------------------------------------
# serve --mcp stdio
# ---------------------------------------------------------------------------

class ToolError(Exception):
    pass


def first_keyword(stmt):
    """First significant word of a statement, comments stripped."""
    out = []
    i, n = 0, len(stmt)
    while i < n:
        if stmt.startswith("//", i):
            j = stmt.find("\n", i)
            i = n if j < 0 else j + 1
        elif stmt.startswith("/*", i):
            j = stmt.find("*/", i)
            i = n if j < 0 else j + 2
        elif stmt[i].isspace():
            i += 1
        else:
            j = i
            while j < n and not stmt[j].isspace():
                j += 1
            out.append(stmt[i:j])
            i = j
    return out[0].upper() if out else ""


def tool_read_cypher(conn, args, read_only=True):
    q = args.get("query")
    if not isinstance(q, str) or not q.strip():
        raise ToolError("missing 'query' (a Cypher statement)")
    kw = first_keyword(q)
    if read_only and kw not in READ_KEYWORDS:
        raise ToolError("Only read queries are allowed for read_cypher "
                        "(got: %s). Use write_cypher for writes." % (kw or "?"))
    params = args.get("params")
    if params is not None and not isinstance(params, dict):
        raise ToolError("'params' must be an object")
    cur = conn.execute(q, params)
    rows = cur.fetchall()
    payload = {"row_count": len(rows), "rows": rows[:MAX_ROWS]}
    if len(rows) > MAX_ROWS:
        payload["truncated"] = True
        payload["note"] = ("truncated at %d rows — narrow the query "
                           "(add a WHERE or LIMIT)" % MAX_ROWS)
    return json.dumps(payload, ensure_ascii=False, default=str)


def tool_get_schema(conn, args):
    counts = conn.execute(
        "MATCH (n) UNWIND labels(n) AS l "
        "RETURN l, count(*) AS c ORDER BY c DESC").fetchall()
    props = conn.execute(
        "MATCH (n) UNWIND labels(n) AS l UNWIND keys(n) AS k "
        "RETURN DISTINCT l, k").fetchall()
    pats = conn.execute(
        "MATCH (a)-[r]->(b) "
        "RETURN DISTINCT labels(a)[0] AS from, type(r) AS type, "
        "labels(b)[0] AS to ORDER BY type").fetchall()

    by_label = {}
    for row in props:
        by_label.setdefault(row["l"], []).append(row["k"])

    node_types = [
        {"label": row["l"], "node_count": row["c"],
         "properties": sorted(by_label.get(row["l"], []))}
        for row in counts
    ]
    rel_types = []
    for row in pats:
        entry = next((e for e in rel_types if e["type"] == row["type"]), None)
        if entry is None:
            entry = {"type": row["type"], "patterns": []}
            rel_types.append(entry)
        entry["patterns"].append({"from": row["from"], "to": row["to"]})

    return json.dumps({"node_types": node_types,
                       "relationship_types": rel_types},
                      ensure_ascii=False, default=str)


def tool_write_cypher(conn, args):
    q = args.get("query")
    if not isinstance(q, str) or not q.strip():
        raise ToolError("missing 'query' (a Cypher statement)")
    params = args.get("params")
    if params is not None and not isinstance(params, dict):
        raise ToolError("'params' must be an object")
    cur = conn.execute(q, params)
    rows = cur.fetchall()
    return json.dumps({"row_count": len(rows), "rows": rows[:MAX_ROWS]},
                      ensure_ascii=False, default=str)


TOOLS = {
    "read_cypher": {
        "description": (
            "Run a read-only Cypher query against the Cascade catalog graph. "
            "Returns rows as JSON, capped at 200 rows with a truncation "
            "marker. Every answer is a path: use variable-length patterns "
            "like (p:Product {sku:'...'})-[*1..4]-(x) to trace blast radius."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Cypher statement"},
                "params": {"type": "object",
                           "description": "optional parameters, e.g. {\"sku\": \"PU-1004\"}"},
            },
            "required": ["query"],
        },
        "fn": lambda conn, args: tool_read_cypher(conn, args, read_only=True),
    },
    "get_schema": {
        "description": (
            "Return this graph's node labels with counts and properties, and "
            "relationship types with the node patterns they connect. Call it "
            "before writing a query so labels and types are exact."),
        "inputSchema": {"type": "object", "properties": {}},
        "fn": tool_get_schema,
    },
    "write_cypher": {
        "description": "Run a Cypher statement that may write to the graph.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Cypher statement"},
                "params": {"type": "object",
                           "description": "optional parameters"},
            },
            "required": ["query"],
        },
        "fn": tool_write_cypher,
    },
}


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

    tool_names = ["read_cypher", "get_schema"]
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


def main():
    argv = sys.argv[1:]
    if not argv:
        usage("missing command")
    cmd = argv[0]
    if cmd in ("--version", "-V", "version"):
        version()
    elif cmd == "query":
        run_query(argv[1:])
    elif cmd == "serve":
        db, read_only = parse_serve_args(argv[1:])
        mcp_loop(db, read_only)
    else:
        usage("unsupported command '%s' (this shim supports: query, serve)"
              % cmd)


if __name__ == "__main__":
    main()
