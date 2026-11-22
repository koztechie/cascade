// Shared projection: direct breakage counts for one SKU.
// Consumers: scripts/report.sh (verdict) AND the blast_radius MCP tool
// (scripts/relate_compat.py) — this file is the single source for both.
MATCH (p:Product {sku: $sku})
OPTIONAL MATCH (l:Listing)-[:OFFERS]->(p)
OPTIONAL MATCH (pg:Page)-[:FEATURES]->(p)
RETURN count(DISTINCT l) AS listings, count(DISTINCT pg) AS pages;
