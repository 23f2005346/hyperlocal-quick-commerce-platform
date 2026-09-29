import os
import sys
import pprint

base = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base)

from ingest_user_catalog import CATALOG_MAPPING

seed_file = os.path.join(base, 'seed_data.py')

with open(seed_file, 'r', encoding='utf-8') as f:
    content = f.read()

end_cat_marker = "PRODUCTS_DATA = ["
end_cat_idx = content.find(end_cat_marker)

header_and_cats = content[:end_cat_idx]

prods = []
for orig_file, meta in CATALOG_MAPPING.items():
    prod = {
        "name": meta["name"],
        "name_hi": meta["name_hi"],
        "category_slug": meta["slug"],
        "brand": meta["brand"],
        "is_loose": meta["is_loose"],
        "description": meta["description"],
        "image_url": f"/products/{meta['clean_filename']}",
        "variants": [
            {
                "unit_size": v["unit_size"],
                "selling_price": float(v["price"]),
                "mrp": float(v["mrp"]),
                "stock_quantity": v["stock"]
            }
            for v in meta["variants"]
        ]
    }
    prods.append(prod)

prods_str = "PRODUCTS_DATA = " + pprint.pformat(prods, indent=4, width=120) + "\n"

with open(seed_file, 'w', encoding='utf-8') as f:
    f.write(header_and_cats + prods_str)

print(f"Successfully synced seed_data.py with {len(prods)} products using Python booleans!")
