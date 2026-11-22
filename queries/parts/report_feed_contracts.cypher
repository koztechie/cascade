// Report section: feed contracts on the SKU's category.
// Consumer: scripts/report.sh (section 3).
MATCH (p:Product {sku: $sku})-[:IN_CATEGORY]->(c:Category)
      <-[:APPLIES_TO]-(m:Mapping)<-[:HAS_MAPPING]-(f:Feed)
RETURN f.name AS feed, m.target_field AS required_field, m.required AS required;
