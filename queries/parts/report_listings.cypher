// Report section: the direct listings of one SKU.
// Consumer: scripts/report.sh (section 2).
MATCH (l:Listing)-[:OFFERS]->(p:Product {sku: $sku})
RETURN l.id AS listing, l.platform AS platform, l.status AS status
ORDER BY l.platform;
