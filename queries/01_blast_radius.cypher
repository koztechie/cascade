// 01 — Blast radius
// What breaks if we stop selling this product?
// Usage:
//   relate query --database store/catalog.rl --param sku=NS-1000 --mode table \
//     < queries/01_blast_radius.cypher
MATCH path = (p:Product {sku: $sku})-[*1..4]-(x)
WHERE x:Listing OR x:Feed OR x:Rule OR x:Campaign OR x:Page OR x:Segment
RETURN DISTINCT labels(x)[0] AS impact_type,
       coalesce(x.name, x.url, x.id) AS name,
       min(length(path)) AS hops
ORDER BY impact_type, hops, name;
