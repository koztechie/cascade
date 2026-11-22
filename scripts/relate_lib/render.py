"""Output rendering for query results (moved verbatim from relate_compat)."""
import json


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
