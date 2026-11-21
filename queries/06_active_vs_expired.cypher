//06 — Temporal standing: is this promo still in force?
// Precedent-style question in Cascade's domain: a rule exists in the graph,
// but is it active? Dates are compared against a FIXED reference (the
// submission date) so `make verify` stays deterministic forever.
// Usage:
//   relate query --database store/catalog.rl --mode table \
//     < queries/06_active_vs_expired.cypher
MATCH (r:Rule {type: 'promo'})-[:APPLIES_TO]->(c:Category)
RETURN r.name AS promo,
       c.name AS category,
       r.active_until AS valid_until,
       CASE WHEN r.active_until < '2026-12-09' THEN 'expired' ELSE 'active' END AS status
ORDER BY status, promo;
