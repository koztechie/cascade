// 05 — Rejection risk, found before the marketplace says no
// Products whose required feed contract is already unsatisfied: the next feed
// sync will reject them. (Query02 explains rejections that already happened;
// this one is the early warning.)
// Usage:
//   relate query --database store/catalog.rl --mode table \
//     < queries/05_rejection_risk.cypher
MATCH (p:Product)-[:IN_CATEGORY]->(c:Category)
MATCH (f:Feed)-[:HAS_MAPPING]->(m:Mapping)-[:APPLIES_TO]->(c)
WHERE m.required AND p.gtin IS NULL
RETURN p.sku AS sku,
       p.status AS status,
       c.name AS category,
       f.name AS feed,
       m.target_field AS missing_field
ORDER BY p.status, sku
LIMIT 25;
