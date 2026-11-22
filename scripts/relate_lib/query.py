"""Query path of the `relate` CLI fallback shim (moved verbatim)."""
import json
import sys

from .render import render


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


def parse_query_args(argv):
    db = None
    mode = "table"
    params = {}
    read_only = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--read-only":
            read_only = True
        elif a in ("--database", "-d"):
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
    return db, mode, params, read_only


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


def run_query(argv):
    db, mode, params, read_only = parse_query_args(argv)
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
        conn = relate.connect(db, read_only=read_only)
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
