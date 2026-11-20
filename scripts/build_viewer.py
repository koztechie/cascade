#!/usr/bin/env python3
"""Build viewer.html — a static blast-radius view generated from the store.

Runs through ./bin/relate (official CLI or embedded fallback), so it works on
every machine this repository runs on. Output: viewer.html at the repo root,
opens offline in any browser.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RELATE = str(ROOT / "bin" / "relate")
DB = "store/catalog.rl"
TEMPLATE = ROOT / "templates" / "viewer.template.html"
OUTPUT = ROOT / "viewer.html"

FOCUS_SQL = """
MATCH (p:Product {sku: $sku})
RETURN elementId(p) AS id, 'Product' AS label, p.name AS name
"""

NODES_SQL = """
MATCH (p:Product {sku: $sku})-[*1..4]-(n)
RETURN DISTINCT elementId(n) AS id, labels(n)[0] AS label,
       coalesce(n.name, n.url, n.id, n.sku, n.source_field) AS name
"""

EDGES_SQL = """
MATCH (p:Product {sku: $sku})-[rs*1..4]-(end)
UNWIND rs AS r
RETURN DISTINCT elementId(r) AS id, elementId(startNode(r)) AS a,
       elementId(endNode(r)) AS b, type(r) AS rel
"""

# The focus product's own listings and their marketplaces: the only Listing
# and Marketplace nodes that belong to *this* blast radius.
OWN_SQL = """
MATCH (l:Listing)-[:OFFERS]->(p:Product {sku: $sku})
MATCH (l)-[:PUBLISHED_ON]->(m:Marketplace)
RETURN elementId(l) AS lid, elementId(m) AS mid
"""


def query(stmt, sku):
    cmd = [RELATE, "query", "--database", DB, "--mode", "json",
           "--param", "sku=" + sku]
    proc = subprocess.run(cmd, input=stmt, capture_output=True,
                          text=True, cwd=ROOT)
    if proc.returncode != 0:
        sys.exit("query failed (%d): %s" % (proc.returncode,
                                            proc.stdout or proc.stderr))
    text = proc.stdout.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = [json.loads(line) for line in text.splitlines() if line.strip()]
    if isinstance(data, dict):
        for key in ("rows", "data", "records", "results"):
            if key in data:
                data = data[key]
                break
    return data if isinstance(data, list) else []


def main():
    params = json.loads((ROOT / "data" / "demo_params.json").read_text())
    sku = params["sku"]

    focus = query(FOCUS_SQL, sku)
    if not focus:
        sys.exit("focus product %r not found in %s" % (sku, DB))
    focus_id = focus[0]["id"]
    focus_name = focus[0].get("name") or sku

    nodes = {focus_id: {"id": focus_id, "label": "Product", "name": focus_name}}
    for row in query(NODES_SQL, sku):
        nodes.setdefault(row["id"], row)

    # Keep the focus product, its own listings/marketplaces, and everything
    # that is not a sibling SKU: sibling products are context noise, and a
    # marketplace hub would drag in half the store.
    own = {focus_id}
    for row in query(OWN_SQL, sku):
        own.add(row["lid"])
        own.add(row["mid"])
    drop_labels = {"Product", "Listing", "Marketplace"}
    keep = ({i for i, r in nodes.items() if r["label"] not in drop_labels}
            | own)
    nodes = {i: r for i, r in nodes.items() if i in keep}

    edges = [e for e in query(EDGES_SQL, sku)
             if e.get("a") in keep and e.get("b") in keep]

    # Drop nodes that ended up isolated (their neighbours were filtered out):
    # a floating dot is noise, not blast radius.
    connected = {e["a"] for e in edges} | {e["b"] for e in edges}
    nodes = {i: r for i, r in nodes.items()
             if i in connected or i == focus_id}

    # Keep only the component that contains the focus product — anything
    # else is a disconnected island and does not belong to this radius.
    adj = {}
    for e in edges:
        adj.setdefault(e["a"], set()).add(e["b"])
        adj.setdefault(e["b"], set()).add(e["a"])
    seen, stack = {focus_id}, [focus_id]
    while stack:
        cur = stack.pop()
        for nxt in adj.get(cur, ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    nodes = {i: r for i, r in nodes.items() if i in seen}
    edges = [e for e in edges if e["a"] in seen and e["b"] in seen]

    payload = {
        "focus_name": focus_name,
        "nodes": [
            {"id": r["id"], "label": r["label"],
             "name": r.get("name") or r["label"],
             "focus": r["id"] == focus_id}
            for r in nodes.values()
        ],
        "edges": edges,
    }

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("/*__GRAPH_DATA__*/", json.dumps(payload, ensure_ascii=False))
    OUTPUT.write_text(html, encoding="utf-8")
    print("wrote %s (%d nodes, %d edges)" %
          (OUTPUT.name, len(payload["nodes"]), len(payload["edges"])))


if __name__ == "__main__":
    main()
