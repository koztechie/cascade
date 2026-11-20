// 04 — Counterfactual: merge two categories
// What collides if we merge $from into $to? Every object that touches either
// category is a decision someone has to make after the merge.
// Usage:
//   relate query --database store/catalog.rl --param from=Sneakers --param to=Boots \
//     --mode table < queries/04_merge_conflicts.cypher
MATCH (r:Rule)-[:APPLIES_TO]->(x:Category)
WHERE x.name IN [$from, $to]
RETURN 'rule' AS object, r.name AS detail, x.name AS category
UNION
MATCH (c:Campaign)-[:TARGETS]->(x:Category)
WHERE x.name IN [$from, $to]
RETURN 'campaign' AS object, c.name AS detail, x.name AS category
UNION
MATCH (m:Mapping)-[:APPLIES_TO]->(x:Category)
WHERE x.name IN [$from, $to]
RETURN 'feed_mapping' AS object, m.target_field AS detail, x.name AS category
UNION
MATCH (s:Segment)-[:FILTERS_BY]->(x:Category)
WHERE x.name IN [$from, $to]
RETURN 'segment' AS object, s.name AS detail, x.name AS category
UNION
MATCH (pg:Page)-[:COVERS]->(x:Category)
WHERE x.name IN [$from, $to]
RETURN 'page' AS object, pg.url AS detail, x.name AS category;
