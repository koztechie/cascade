// 03 — Invisible inventory
// What can customers not find right now?
//   a) pages nothing links to (orphan pages)
//   b) active products with no listing and no page (invisible stock)
// Usage:
//   relate query --database store/catalog.rl --mode table \
//     < queries/03_orphans.cypher
MATCH (pg:Page)
WHERE NOT (()-[:LINKS_TO]->(pg))
RETURN 'orphan_page' AS issue, pg.url AS detail
UNION
MATCH (p:Product {status: 'active'})
WHERE NOT (()-[:OFFERS]->(p)) AND NOT (()-[:FEATURES]->(p))
RETURN 'invisible_product' AS issue, p.sku AS detail;
