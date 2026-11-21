//07 — Remediation: which single fix clears the most rejection risk?
// StepFree Relay-style question in our domain: when no step-free route exists,
// rank the repairs. Here: fill one missing required field and watch the risk
// pool drain. One row = one decision.
// Usage:
//   relate query --database store/catalog.rl --mode table \
//     < queries/07_remediation.cypher
MATCH (p:Product)-[:IN_CATEGORY]->(c:Category)
MATCH (f:Feed)-[:HAS_MAPPING]->(m:Mapping)-[:APPLIES_TO]->(c)
WHERE m.required AND p.gtin IS NULL
RETURN m.target_field AS missing_field,
       count(DISTINCT p) AS products_to_fix,
       count(*) AS feed_risks_cleared
ORDER BY feed_risks_cleared DESC;
