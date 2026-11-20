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
    relate --version

Exit codes follow the official CLI: 0 ok, 2 usage error, 6 statement rejected.
"""
import json
import sys


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


def parse_args(argv):
    if not argv:
        usage("missing command")
    if argv[0] in ("--version", "-V", "version"):
        version()
    if argv[0] != "query":
        usage("unsupported command '%s' (this shim supports: query)" % argv[0])

    db = None
    mode = "table"
    params = {}
    i = 1
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
        elif a in ("--json",):
            mode = "json"
        elif a in ("--csv",):
            mode = "csv"
        elif a in ("--markdown",):
            mode = "markdown"
        elif a.startswith("-"):
            usage("unknown flag '%s' (shim supports: --database, --param, --mode)" % a)
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
    # table (default)
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


def main():
    db, mode, params = parse_args(sys.argv[1:])
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
    except Exception as e:  # store open failure
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
    else:
        print("(ok)") if mode == "table" else None
    sys.exit(0)


if __name__ == "__main__":
    main()
