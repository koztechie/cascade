// Blast-radius ball for one SKU, grouped by type.
// Consumer: the blast_radius MCP tool (scripts/relate_compat.py).
// NOTE: the alias `type` is part of the published tool payload — do not
// rename it to `impact_type` without a migration (docs/architecture.md).
MATCH (p:Product {sku: $sku})-[*1..4]-(x)
WHERE x:Listing OR x:Feed OR x:Rule OR x:Campaign OR x:Page OR x:Segment
RETURN labels(x)[0] AS type, count(DISTINCT x) AS objects
ORDER BY objects DESC;
