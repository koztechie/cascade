// Report section: the 4-hop impact ball for one SKU, grouped by type.
// Consumer: scripts/report.sh (section 1). NOTE: the alias `impact_type`
// shapes the markdown header — the MCP tool's sibling file
// (impact_ball.cypher) deliberately aliases `type` instead, because the tool
// payload keys are a published API (see docs/architecture.md).
MATCH (p:Product {sku: $sku})-[*1..4]-(x)
WHERE x:Listing OR x:Feed OR x:Rule OR x:Campaign OR x:Page OR x:Segment
RETURN labels(x)[0] AS impact_type, count(DISTINCT x) AS objects
ORDER BY objects DESC;
