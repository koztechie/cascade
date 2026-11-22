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

Public entry point (pass R4): this file stays the stable entry point that
`bin/relate` execs; the implementation now lives in the relate_lib package
(render / query / tools / mcp). Flags, exit codes and JSON shapes are
unchanged — proven by the verify gates and the golden fixtures.
"""
import sys

from relate_lib.mcp import mcp_loop, parse_serve_args
from relate_lib.query import run_query, usage, version


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
