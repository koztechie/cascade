// Shared projection: the category machinery attached to one SKU.
// Consumers: scripts/report.sh (verdict) AND the blast_radius MCP tool
// (scripts/relate_compat.py) — this file is the single source for both.
MATCH (p:Product {sku: $sku})-[:IN_CATEGORY]->(c:Category)
OPTIONAL MATCH (r:Rule)-[:APPLIES_TO]->(c)
OPTIONAL MATCH (ca:Campaign)-[:TARGETS]->(c)
OPTIONAL MATCH (sg:Segment)-[:FILTERS_BY]->(c)
OPTIONAL MATCH (f:Feed)-[:HAS_MAPPING]->(m:Mapping)-[:APPLIES_TO]->(c)
RETURN c.name AS category,
       count(DISTINCT r) AS rules, count(DISTINCT ca) AS campaigns,
       count(DISTINCT sg) AS segments, count(DISTINCT f) AS feeds;
