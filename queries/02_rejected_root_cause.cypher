// 02 — Root cause with proof
// Why is this listing rejected? Trace back from the listing to the exact
// required field the product is missing, through the feed contract.
// Usage:
//   relate query --database store/catalog.rl --mode table \
//     < queries/02_rejected_root_cause.cypher
MATCH (l:Listing {status: 'rejected'})-[:OFFERS]->(p:Product)-[:IN_CATEGORY]->(c:Category)
MATCH (f:Feed)-[:HAS_MAPPING]->(m:Mapping)-[:APPLIES_TO]->(c)
WHERE m.required AND p.gtin IS NULL
RETURN l.id AS listing,
       p.sku AS sku,
       c.name AS category,
       f.name AS feed,
       m.target_field AS missing_field
ORDER BY feed, sku
LIMIT 25;
