#!/usr/bin/env python3
"""Normalize a Relate .rl store to byte-determinism (pass M1).

Why this exists: the engine gives every parquet shard a fresh random hex id
on each checkpoint (`shard_name::canonical_id` in the native extension), so
two builds of the SAME data differ in a handful of id tokens while every
payload byte is identical. That is why `store/catalog.rl` used to churn in
git on every rebuild.

This script rewrites only those 32-hex tokens, deriving each replacement
from the token's order of first appearance — so identical input yields an
identical file. The substitution is same-length and regex-boundary-safe:
payload bytes, layout and file size are untouched, and the engine does not
require an id to be a hash of its content (verified by opening a renamed
store read-only).

Idempotent: re-running on an already-normalized file changes nothing.

Usage:
    python3 scripts/normalize_store.py store/catalog.rl
    python3 scripts/normalize_store.py --check store/catalog.rl   # exit 1
                                                                # if the
                                                                # file would
                                                                # change
"""
import hashlib
import re
import sys
from pathlib import Path

HEX32 = re.compile(rb"(?<![0-9a-f])[0-9a-f]{32}(?![0-9a-f])")


def normalized_bytes(data):
    """Return (new_bytes, mapping) with shard ids replaced deterministically."""
    mapping = {}

    def repl(match):
        token = match.group(0)
        if token not in mapping:
            key = "cascade-store-part-%d" % len(mapping)
            mapping[token] = hashlib.sha256(key.encode()).hexdigest()[:32].encode()
        return mapping[token]

    return HEX32.sub(repl, data), mapping


def main(argv):
    check = False
    args = list(argv)
    if args and args[0] == "--check":
        check = True
        args = args[1:]
    if len(args) != 1:
        print("usage: normalize_store.py [--check] PATH", file=sys.stderr)
        return 2

    path = Path(args[0])
    if not path.is_file():
        print("normalize: no such file: %s" % path, file=sys.stderr)
        return 2

    data = path.read_bytes()
    out, mapping = normalized_bytes(data)

    if not mapping:
        print("normalize: no shard ids found in %s (nothing to normalize)"
              % path)
        return 0

    if out == data:
        print("normalize: %s already deterministic (%d shard ids)"
              % (path, len(mapping)))
        return 0

    if check:
        print("FAIL committed: store is not normalized — %d shard id(s) would "
              "be rewritten. Run: make store" % len(mapping))
        return 1

    path.write_bytes(out)
    print("normalize: rewrote %d shard id(s) in %s (%d bytes, length "
          "unchanged)" % (len(mapping), path, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
