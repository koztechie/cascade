#!/usr/bin/env python3
"""Cascade demo-data generator (synthetic, deterministic, no real business data).

Writes:
  data/load.cypher       - MERGE/CREATE statements that build the catalog graph
  data/demo_params.json  - SKU and category pair used by the demo

Usage: python3 scripts/generate_data.py
"""
import json
import os
import random
from pathlib import Path

SEED = 42
random.seed(SEED)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
# CASCADE_OUT lets `make verify` regenerate into a temp file and prove the
# generator is byte-identical under a different PYTHONHASHSEED (KidneyLoop's
# reproducibility lesson).
OUT = Path(os.environ.get("CASCADE_OUT") or (DATA / "load.cypher"))
PARAMS = DATA / "demo_params.json"


def q(s):
    """Cypher string literal."""
    return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"


def slug(s):
    return str(s).lower().replace(" ", "-").replace("/", "-")


BRANDS = [
    ("NovaStep", "Poland"), ("AuroraHome", "Ukraine"), ("TerraGrip", "Germany"),
    ("BrightNest", "Poland"), ("OrbitAudio", "Taiwan"), ("VelvetLine", "France"),
    ("IronTrail", "Czechia"), ("PureGlow", "Ukraine"), ("KraftWerk Home", "Germany"),
    ("BlueHarbor", "Lithuania"), ("SunField", "Turkiye"), ("QuietWave", "Japan"),
    ("NordicPine", "Sweden"), ("AmberRoot", "Ukraine"), ("PulseKit", "South Korea"),
]

CATEGORIES = {
    "Footwear": ["Sneakers", "Boots", "Sandals"],
    "Home": ["Kitchen", "Lighting", "Storage"],
    "Electronics": ["Audio", "Wearables"],
    "Beauty": ["Skincare", "Haircare"],
    "Sports": ["Fitness", "Outdoor"],
}

SUPPLIERS = [
    ("Kyiv Logistics Hub", "Ukraine", 3),
    ("Baltic Freight OU", "Estonia", 7),
    ("Carpathian Textiles", "Ukraine", 5),
    ("Danube Components", "Romania", 10),
    ("Eastern Gear Supply", "Poland", 6),
    ("Prague Packaging", "Czechia", 4),
    ("Anatolia Trade", "Turkiye", 12),
    ("Rheinware GmbH", "Germany", 9),
]

MARKETPLACES = [
    "Rozetka", "Prom.ua", "Google Shopping", "Amazon", "Epicenter", "Facebook Shop",
]

FEEDS = [
    ("Google Merchant Center", "Google Shopping"),
    ("Rozetka Feed", "Rozetka"),
    ("Prom.ua Feed", "Prom.ua"),
    ("Price Creator", "Google Shopping"),
    ("Meta Catalog", "Facebook Shop"),
]

PRICE_RANGES = {
    "Footwear": (650, 4500),
    "Home": (390, 6200),
    "Electronics": (990, 12900),
    "Beauty": (240, 2400),
    "Sports": (490, 8900),
}

COLORS = ["Black", "Sand", "Navy", "Olive", "Grey", "Burgundy", "Ivory", "Graphite"]
MODELS = ["Prime", "Core", "Flex", "Ultra", "Lite", "Pro", "Classic", "Edge"]
CHANNELS = ["Google Ads", "Meta Ads", "Email (SendPulse)", "Viber"]
# Categories that carry TWO overlapping price rules -> counterfactual conflicts.
CONFLICT_CATEGORIES = ["Sneakers", "Audio", "Skincare"]

PRODUCT_COUNT = 600


def build():
    lines = []
    all_subs = [s for subs in CATEGORIES.values() for s in subs]

    # --- shared entities -------------------------------------------------
    for name, country in BRANDS:
        lines.append(f"MERGE (:Brand {{name: {q(name)}, country: {q(country)}}});")
    for name, country, lead in SUPPLIERS:
        lines.append(
            f"MERGE (:Supplier {{name: {q(name)}, country: {q(country)}, "
            f"lead_time_days: {lead}}});"
        )
    for parent, subs in CATEGORIES.items():
        lines.append(f"MERGE (c:Category {{name: {q(parent)}}}) SET c.level = 'parent';")
        for sub in subs:
            lines.append(f"MERGE (c:Category {{name: {q(sub)}}}) SET c.level = 'sub';")
    for parent, subs in CATEGORIES.items():
        for sub in subs:
            lines.append(
                f"MATCH (p:Category {{name: {q(parent)}}}) "
                f"MATCH (c:Category {{name: {q(sub)}}}) "
                f"CREATE (p)-[:HAS_SUBCATEGORY]->(c);"
            )
    for mp in MARKETPLACES:
        lines.append(f"MERGE (:Marketplace {{name: {q(mp)}}});")
    for fname, platform in FEEDS:
        lines.append(
            f"MERGE (:Feed {{name: {q(fname)}, platform: {q(platform)}}});"
        )

    # --- feed mappings (data-quality contract) ---------------------------
    mapping_fields = ["price", "availability", "color", "size", "mpn", "material"]
    for fname, _platform in FEEDS:
        for sub in all_subs:
            # Google Merchant Center requires gtin everywhere: the contract
            # every product in that category must satisfy.
            if fname == "Google Merchant Center":
                source = target = "gtin"
                required = True
            elif fname == "Meta Catalog" and sub in ("Audio", "Wearables",
                                                     "Skincare", "Haircare"):
                source = target = "gtin"
                required = True
            elif random.random() < 0.45:
                f = random.choice(mapping_fields)
                source = target = f
                required = False
            else:
                continue
            lines.append(
                f"MATCH (f:Feed {{name: {q(fname)}}}) "
                f"MATCH (c:Category {{name: {q(sub)}}}) "
                f"CREATE (f)-[:HAS_MAPPING]->(:Mapping "
                f"{{source_field: {q(source)}, target_field: {q(target)}, "
                f"required: {str(required).lower()}}})-[:APPLIES_TO]->(c);"
            )

    # --- rules ------------------------------------------------------------
    for sub in all_subs:
        lines.append(
            f"MATCH (c:Category {{name: {q(sub)}}}) "
            f"CREATE (:Rule {{name: {q(sub + ' margin floor')}, type: 'price', "
            f"expression: 'cost * 1.35'}})-[:APPLIES_TO]->(c);"
        )
    for sub in CONFLICT_CATEGORIES:
        # Temporal standing (Precedent-style): a promo can live in the graph
        # and still be out of force. Fixed dates -> deterministic verify.
        promo_validity = {"Sneakers": "2026-12-31", "Audio": "2026-12-15",
                          "Skincare": "2026-10-31"}[sub]
        lines.append(
            f"MATCH (c:Category {{name: {q(sub)}}}) "
            f"CREATE (:Rule {{name: {q(sub + ' winter promo -15%')}, type: 'promo', "
            f"active_until: {q(promo_validity)}, expression: 'price * 0.85'}})"
            f"-[:APPLIES_TO]->(c);"
        )

    # --- campaigns --------------------------------------------------------
    for i in range(12):
        sub = random.choice(all_subs)
        channel = CHANNELS[i % len(CHANNELS)]
        lines.append(
            f"MATCH (c:Category {{name: {q(sub)}}}) "
            f"CREATE (:Campaign {{name: {q(sub + ' / ' + channel)}, "
            f"channel: {q(channel)}, budget_uah: {random.choice([5000, 12000, 25000, 40000])}}})"
            f"-[:TARGETS]->(c);"
        )
    for brand in [b[0] for b in random.sample(BRANDS, 3)]:
        lines.append(
            f"MATCH (b:Brand {{name: {q(brand)}}}) "
            f"CREATE (:Campaign {{name: {q(brand + ' / brand awareness')}, "
            f"channel: 'Meta Ads', budget_uah: 30000}})-[:TARGETS]->(b);"
        )

    # --- segments ---------------------------------------------------------
    segments = [
        ("Loyalty 90d", "Skincare"), ("Win-back 180d", "Sneakers"),
        ("Sneakers viewers 30d", "Sneakers"), ("High AOV", "Audio"),
        ("Churn risk", "Boots"), ("NovaStep fans", None),
        ("Out-of-stock alerts", "Wearables"), ("Kitchen upsell", "Kitchen"),
    ]
    for name, sub in segments:
        if sub:
            lines.append(
                f"MATCH (c:Category {{name: {q(sub)}}}) "
                f"CREATE (:Segment {{name: {q(name)}, size: {random.randint(400, 9000)}}})"
                f"-[:FILTERS_BY]->(c);"
            )
        else:
            lines.append(
                f"MATCH (b:Brand {{name: 'NovaStep'}}) "
                f"CREATE (:Segment {{name: {q(name)}, size: {random.randint(400, 9000)}}})"
                f"-[:FILTERS_BY]->(b);"
            )

    # --- products ---------------------------------------------------------
    products = []
    for i in range(PRODUCT_COUNT):
        parent = random.choice(list(CATEGORIES))
        sub = random.choice(CATEGORIES[parent])
        brand, _country = random.choice(BRANDS)
        supplier = random.choice(SUPPLIERS)[0]
        sku = f"{brand[:2].upper()}-{1000 + i}"
        color = random.choice(COLORS)
        model = random.choice(MODELS)
        name = f"{brand} {sub} {model} {color}"
        lo, hi = PRICE_RANGES[parent]
        price = max(10, int(round(random.uniform(lo, hi) / 10.0)) * 10)
        stock = random.choice([0, 3, 7, 12, 25, 40, 80, 150])
        has_gtin = random.random() >= 0.08
        r = random.random()
        status = "active" if r < 0.86 else ("discontinued" if r < 0.94 else "pending")
        desc = (
            f"{brand} {sub.lower()} for everyday use. {color} finish, "
            f"{model} line, supplied by {supplier}."
        )
        props = (
            f"sku: {q(sku)}, name: {q(name)}, price: {price}, currency: 'UAH', "
            f"status: {q(status)}, stock: {stock}, description: {q(desc)}"
        )
        if has_gtin:
            props += f", gtin: '482{random.randint(1000000000, 9999999999)}'"
        lines.append(
            f"CREATE (p:Product {{{props}}}) "
            f"WITH p MATCH (b:Brand {{name: {q(brand)}}}) "
            f"MATCH (c:Category {{name: {q(sub)}}}) "
            f"MATCH (s:Supplier {{name: {q(supplier)}}}) "
            f"CREATE (p)-[:HAS_BRAND]->(b), (p)-[:IN_CATEGORY]->(c), "
            f"(p)-[:SUPPLIED_BY]->(s);"
        )
        products.append({
            "sku": sku, "sub": sub, "status": status,
            "has_gtin": has_gtin, "listings": [], "page": False,
        })

    # --- listings ---------------------------------------------------------
    for idx, p in enumerate(products):
        if p["status"] == "discontinued":
            continue  # delisted: no live listings at all
        if p["status"] == "active":
            n = random.choices([0, 1, 2, 3], weights=[12, 45, 30, 13])[0]
        else:  # pending
            n = random.choices([0, 1], weights=[70, 30])[0]
        picks = random.sample(MARKETPLACES, k=min(n, len(MARKETPLACES)))
        for j, mp in enumerate(picks):
            lid = f"L-{idx:04d}-{j}"
            if not p["has_gtin"] and random.random() < 0.75:
                lst = "rejected"
            elif p["status"] == "pending":
                lst = "pending"
            else:
                lst = random.choices(["live", "pending"], weights=[88, 12])[0]
            url = f"https://{slug(mp)}.example/{p['sku'].lower()}"
            lines.append(
                f"CREATE (l:Listing {{id: {q(lid)}, platform: {q(mp)}, "
                f"status: {q(lst)}, url: {q(url)}}}) "
                f"WITH l MATCH (p:Product {{sku: {q(p['sku'])}}}) "
                f"MATCH (m:Marketplace {{name: {q(mp)}}}) "
                f"CREATE (l)-[:OFFERS]->(p), (l)-[:PUBLISHED_ON]->(m);"
            )
            p["listings"].append((lid, mp, lst))

    # --- pages ------------------------------------------------------------
    for parent, subs in CATEGORIES.items():
        url = f"/c/{slug(parent)}"
        lines.append(
            f"CREATE (pg:Page {{type: 'category', url: {q(url)}, "
            f"title: {q(parent)}}}) "
            f"WITH pg MATCH (c:Category {{name: {q(parent)}}}) "
            f"CREATE (pg)-[:COVERS]->(c);"
        )
        for sub in subs:
            url = f"/c/{slug(sub)}"
            lines.append(
                f"CREATE (pg:Page {{type: 'category', url: {q(url)}, "
                f"title: {q(sub)}}}) "
                f"WITH pg MATCH (c:Category {{name: {q(sub)}}}) "
                f"CREATE (pg)-[:COVERS]->(c);"
            )

    # parent -> child links
    for parent, subs in CATEGORIES.items():
        for sub in subs:
            lines.append(
                f"MATCH (a:Page {{url: {q('/c/' + slug(parent))}}}) "
                f"MATCH (b:Page {{url: {q('/c/' + slug(sub))}}}) "
                f"CREATE (a)-[:LINKS_TO]->(b);"
            )

    # product pages: every 4th product; subcategory pages link only the
    # first half of their product pages -> deliberate orphans in the rest.
    by_sub = {s: [] for s in all_subs}
    for i, p in enumerate(products):
        if i % 4 == 0:
            p["page"] = True
            url = f"/p/{p['sku'].lower()}"
            lines.append(
                f"CREATE (pg:Page {{type: 'product', url: {q(url)}, "
                f"title: {q(p['sku'])}}}) "
                f"WITH pg MATCH (pr:Product {{sku: {q(p['sku'])}}}) "
                f"CREATE (pg)-[:FEATURES]->(pr);"
            )
            by_sub[p["sub"]].append(url)

    for sub, urls in by_sub.items():
        for url in urls[: max(1, len(urls) // 2)]:
            lines.append(
                f"MATCH (a:Page {{url: {q('/c/' + slug(sub))}}}) "
                f"MATCH (b:Page {{url: {q(url)}}}) "
                f"CREATE (a)-[:LINKS_TO]->(b);"
            )

    # landing pages -> subcategory pages
    landings = [
        "/campaigns/winter-sale", "/campaigns/new-arrivals",
        "/campaigns/footwear-week", "/campaigns/audio-days",
        "/campaigns/skincare-routine", "/campaigns/home-refresh",
        "/campaigns/sports-start", "/campaigns/brand-novastep",
    ]
    for url in landings:
        lines.append(f"CREATE (pg:Page {{type: 'landing', url: {q(url)}}});")
        for target in random.sample(all_subs, k=3):
            lines.append(
                f"MATCH (a:Page {{url: {q(url)}}}) "
                f"MATCH (b:Page {{url: {q('/c/' + slug(target))}}}) "
                f"CREATE (a)-[:LINKS_TO]->(b);"
            )

    # --- demo parameters --------------------------------------------------
    demo_sku = None
    for p in products:
        if (p["sub"] == "Sneakers" and p["status"] == "active"
                and p["has_gtin"] and len(p["listings"]) >= 2):
            demo_sku = p["sku"]
            break
    if demo_sku is None:  # deterministic fallback
        demo_sku = next(p["sku"] for p in products if p["status"] == "active")

    DATA.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    PARAMS.write_text(json.dumps({
        "sku": demo_sku,
        "merge_from": "Sneakers",
        "merge_into": "Boots",
    }, indent=2) + "\n", encoding="utf-8")

    print(f"wrote {len(lines)} statements -> {OUT}")
    print(f"demo sku: {demo_sku} (merge {PARAMS})")


if __name__ == "__main__":
    build()
