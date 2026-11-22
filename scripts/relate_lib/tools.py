"""MCP tool implementations and the TOOLS registry (moved verbatim)."""
import json
from pathlib import Path

from .query import split_statements

MAX_ROWS = 200
READ_KEYWORDS = {"MATCH", "OPTIONAL", "WITH", "RETURN", "UNWIND", "CALL",
                 "SHOW", "EXPLAIN", "PROFILE"}


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


def tool_blast_radius(conn, args):
    """Domain tool (CodeContext-style): direct breakage + category machinery +
    the bounded 4-hop neighbourhood, with an honest label on each layer."""
    sku = args.get("sku")
    if not isinstance(sku, str) or not sku.strip():
        raise ToolError("missing 'sku' (e.g. 'PU-1004')")
    direct = conn.execute(_load_query("parts/direct_counts.cypher"),
                          {"sku": sku}).fetchall()
    category = conn.execute(_load_query("parts/category_machinery.cypher"),
                            {"sku": sku}).fetchall()
    ball = conn.execute(_load_query("parts/impact_ball.cypher"),
                        {"sku": sku}).fetchall()
    payload = {
        "sku": sku,
        "direct_breakage": direct[0] if direct else {},
        "category_machinery": category,
        "neighbourhood_4hops": ball,
        "label": "direct = real breakage; neighbourhood = context, not breakage",
    }
    return json.dumps(payload, ensure_ascii=False, default=str)


def _load_query(filename):
    """Single source of truth (Yokoten/Morrow/ToldOnce pattern): MCP tools run
    the very same .cypher files as the CLI, report and verify.

    NOTE (pass R4): this file now lives one level deeper than the shim did,
    so the repo root is three parents up (scripts/relate_lib/tools.py).
    """
    path = Path(__file__).resolve().parent.parent.parent / "queries" / filename
    stmts = list(split_statements(path.read_text(encoding="utf-8")))
    if not stmts:
        raise ToolError("query file is empty: " + filename)
    return stmts[0]


def tool_rejection_causes(conn, args):
    """Why listings are rejected: trace from a rejected listing to the
    required field it lacks and the feed that demands it. Runs queries/02."""
    rows = conn.execute(_load_query("02_rejected_root_cause.cypher")).fetchall()
    return json.dumps({
        "causes": rows,
        "note": "proof path for every row: Listing -OFFERS-> Product "
                "-IN_CATEGORY-> Category <-APPLIES_TO- Mapping <-HAS_MAPPING- Feed",
    }, ensure_ascii=False, default=str)


def tool_remediation(conn, args):
    """Which single missing field, once filled, clears the most rejection
    risk: products to fix and feed risks cleared. Runs queries/07."""
    rows = conn.execute(_load_query("07_remediation.cypher")).fetchall()
    return json.dumps({
        "fix": rows,
        "note": "fill the missing field on the listed products to clear the "
                "risk pool; existing rejected listings still need re-submission",
    }, ensure_ascii=False, default=str)


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
            "like (p:Product {sku:'...'})-[*1..4]-(x) to trace blast radius. "
            "If a query returns no rows, the answer is 'no evidence in the "
            "graph' — say that and do not invent a result."),
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
    "blast_radius": {
        "description": (
            "Domain tool: what breaks if we stop selling a SKU. Returns three "
            "layers with an honest label — direct breakage (its listings and "
            "product page), the category machinery attached to it (rules, "
            "campaigns, segments, feed contracts) and the bounded 4-hop "
            "neighbourhood (context, not breakage)."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "sku": {"type": "string",
                        "description": "product SKU, e.g. \"PU-1004\""},
            },
            "required": ["sku"],
        },
        "fn": tool_blast_radius,
    },
    "rejection_causes": {
        "description": (
            "Why listings are rejected: trace from each rejected listing to "
            "the required field the product lacks and the feed that demands "
            "it. Rows carry the proof path Listing to Product to Category to "
            "Mapping to Feed."),
        "inputSchema": {"type": "object", "properties": {}},
        "fn": tool_rejection_causes,
    },
    "remediation": {
        "description": (
            "Which single missing field, once filled, clears the most "
            "rejection risk: products to fix and feed risks cleared, ranked "
            "by payoff. Existing rejected listings still need re-submission."),
        "inputSchema": {"type": "object", "properties": {}},
        "fn": tool_remediation,
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
