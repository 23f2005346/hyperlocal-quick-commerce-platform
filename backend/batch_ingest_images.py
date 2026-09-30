"""
Komal Mart (कोमल मार्ट) — Batch Product Photo & Price Ingestion Pipeline
Zero-token automated inventory import from camera/phone photos named with prices.

Naming conventions supported:
  toor-daal-190-per-kg.jpg       -> Toor Dal, 1kg, Rs.190
  chakki-atta-38-1kg.png         -> Chakki Atta, 1kg, Rs.38
  fortune-sunflower-oil-145-1l.jpg -> Fortune Sunflower Oil, 1L, Rs.145
  tata-salt-28-1kg.jpg           -> Tata Salt, 1kg, Rs.28
  maggi-14-70g.jpg               -> Maggi Masala Noodles, 70g, Rs.14
  sugar-42-per-kg.jpg            -> White Sugar, 1kg, Rs.42
  chana-dal-90-500g.jpg          -> Chana Dal, 500g, Rs.90
"""

import os
import re
import shutil
import sys
import argparse
from pathlib import Path

# Common Indian Kirana Dictionary for high-precision auto-categorization & Marathi/Hindi nomenclature
KIRANA_COMMODITY_MAP = {
    'toor': {
        'name': 'Toor Dal / Arhar Dal (Gavran Loose)',
        'name_hi': 'तूर डाळ (गावरान मोकळी)',
        'category_slug': 'dals-pulses',
        'category_name': 'Dals & Pulses',
        'category_name_hi': 'डाळी व कडधान्ये',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'arhar': {
        'name': 'Toor Dal / Arhar Dal (Gavran Loose)',
        'name_hi': 'तूर डाळ (गावरान मोकळी)',
        'category_slug': 'dals-pulses',
        'category_name': 'Dals & Pulses',
        'category_name_hi': 'डाळी व कडधान्ये',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'chana-dal': {
        'name': 'Chana Dal (Bengal Gram Split Loose)',
        'name_hi': 'चना डाळ (हरभरा डाळ मोकळी)',
        'category_slug': 'dals-pulses',
        'category_name': 'Dals & Pulses',
        'category_name_hi': 'डाळी व कडधान्ये',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'moong-dal': {
        'name': 'Moong Dal Dhuli (Yellow Split Loose)',
        'name_hi': 'पिवळी मूग डाळ (मोकळी)',
        'category_slug': 'dals-pulses',
        'category_name': 'Dals & Pulses',
        'category_name_hi': 'डाळी व कडधान्ये',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'masoor-dal': {
        'name': 'Masoor Dal Lal (Split Red Lentils Loose)',
        'name_hi': 'लाल मसूर डाळ (मोकळी)',
        'category_slug': 'dals-pulses',
        'category_name': 'Dals & Pulses',
        'category_name_hi': 'डाळी व कडधान्ये',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'urad-dal': {
        'name': 'Urad Dal Dhuli (White Split Idli Dal Loose)',
        'name_hi': 'पांढरी उडीद डाळ (इडली/डोसा मोकळी)',
        'category_slug': 'dals-pulses',
        'category_name': 'Dals & Pulses',
        'category_name_hi': 'डाळी व कडधान्ये',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'atta': {
        'name': 'Chakki Fresh Whole Wheat Atta',
        'name_hi': 'चक्कीचे ताजे गव्हाचे पीठ (शरबती)',
        'category_slug': 'atta-flours',
        'category_name': 'Atta, Flours & Suji',
        'category_name_hi': 'पीठ, मैदा व रवा',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'gehu': {
        'name': 'Sharbati Whole Wheat Grain (Unpolished)',
        'name_hi': 'शरबती अख्खा गहू (गावरान खडा)',
        'category_slug': 'atta-flours',
        'category_name': 'Atta, Flours & Suji',
        'category_name_hi': 'पीठ, मैदा व रवा',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'rice': {
        'name': 'Wada Kolam Rice (Mandi Fresh Loose)',
        'name_hi': 'वाडा कोलम तांदूळ (मोकळा भात)',
        'category_slug': 'rice-grains',
        'category_name': 'Rice & Grains',
        'category_name_hi': 'तांदूळ व धान्य',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'kolam': {
        'name': 'Wada Kolam Rice (Mandi Fresh Loose)',
        'name_hi': 'वाडा कोलम तांदूळ (मोकळा भात)',
        'category_slug': 'rice-grains',
        'category_name': 'Rice & Grains',
        'category_name_hi': 'तांदूळ व धान्य',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'sugar': {
        'name': 'Madhur Pure & Hygienic Sugar (Loose/Pack)',
        'name_hi': 'मधुर शुद्ध पांढरी साखर (Sulfur-Free)',
        'category_slug': 'rice-grains',
        'category_name': 'Rice & Grains',
        'category_name_hi': 'तांदूळ व धान्य',
        'is_loose': True,
        'brand': 'Madhur / Mandi Sugar',
        'default_unit': '1kg'
    },
    'oil': {
        'name': 'Refined Sunflower Cooking Oil',
        'name_hi': 'रिफाइन्ड सूर्यफूल खाद्यतेल',
        'category_slug': 'oils-ghee',
        'category_name': 'Oils & Desi Ghee',
        'category_name_hi': 'तेल व शुद्ध देशी तूप',
        'is_loose': False,
        'brand': 'Fortune / Dhara',
        'default_unit': '1L'
    },
    'ghee': {
        'name': 'Amul Pure Desi Cow Ghee',
        'name_hi': 'अमुल शुद्ध देशी गायीचे तूप',
        'category_slug': 'oils-ghee',
        'category_name': 'Oils & Desi Ghee',
        'category_name_hi': 'तेल व शुद्ध देशी तूप',
        'is_loose': False,
        'brand': 'Amul',
        'default_unit': '1L'
    },
    'salt': {
        'name': 'Tata Salt Vacuum Evaporated Iodized',
        'name_hi': 'टाटा मीठ (आयोडीनयुक्त देश का नमक)',
        'category_slug': 'spices-salt',
        'category_name': 'Spices & Salt',
        'category_name_hi': 'मसाले व मीठ',
        'is_loose': False,
        'brand': 'Tata Salt',
        'default_unit': '1kg'
    },
    'tea': {
        'name': 'Tata Tea Gold Leaf Tea',
        'name_hi': 'टाटा टी गोल्ड कडक चहा पत्ती',
        'category_slug': 'tea-coffee',
        'category_name': 'Tea & Beverages',
        'category_name_hi': 'चहा पत्ती व कॉफी',
        'is_loose': False,
        'brand': 'Tata Tea',
        'default_unit': '250g'
    },
    'maggi': {
        'name': 'Maggi 2-Minute Masala Instant Noodles',
        'name_hi': 'मॅगी २-मिनिट मसाला नूडल्स',
        'category_slug': 'cleaning-household',
        'category_name': 'Snacks & Packaged Food',
        'category_name_hi': 'स्नॅक्स व पॅकेट फूड',
        'is_loose': False,
        'brand': 'Nestle Maggi',
        'default_unit': '70g'
    },
    'surf-excel': {
        'name': 'Surf Excel Quick Wash Detergent Powder',
        'name_hi': 'सर्फ एक्सेल डिटर्जंट पावडर',
        'category_slug': 'cleaning-household',
        'category_name': 'Cleaning & Soaps',
        'category_name_hi': 'स्वच्छता व डिटर्जंट',
        'is_loose': False,
        'brand': 'Surf Excel',
        'default_unit': '1kg'
    },
    'besan': {
        'name': 'Fresh Chana Dal Besan (Gram Flour)',
        'name_hi': 'ताजे हरभरा डाळ बेसन पीठ',
        'category_slug': 'atta-flours',
        'category_name': 'Atta, Flours & Suji',
        'category_name_hi': 'पीठ, मैदा व रवा',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'poha': {
        'name': 'Jada Poha (Thick Flattened Rice)',
        'name_hi': 'जाडा पोहा (कांदा पोहे विशेष)',
        'category_slug': 'rice-grains',
        'category_name': 'Rice & Grains',
        'category_name_hi': 'तांदूळ व धान्य',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'rava': {
        'name': 'Suji / Rava (Fine Semolina)',
        'name_hi': 'सुजी रवा (बारीक रवा)',
        'category_slug': 'atta-flours',
        'category_name': 'Atta, Flours & Suji',
        'category_name_hi': 'पीठ, मैदा व रवा',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'maida': {
        'name': 'Refined Wheat Maida',
        'name_hi': 'मैदा (रिफाइन्ड पीठ)',
        'category_slug': 'atta-flours',
        'category_name': 'Atta, Flours & Suji',
        'category_name_hi': 'पीठ, मैदा व रवा',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'singdana': {
        'name': 'Singdana / Peanuts (Raw Groundnuts)',
        'name_hi': 'शेंगदाणे (कच्चे गावरान)',
        'category_slug': 'dals-pulses',
        'category_name': 'Dals & Pulses',
        'category_name_hi': 'डाळी व कडधान्ये',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'peanut': {
        'name': 'Singdana / Peanuts (Raw Groundnuts)',
        'name_hi': 'शेंगदाणे (कच्चे गावरान)',
        'category_slug': 'dals-pulses',
        'category_name': 'Dals & Pulses',
        'category_name_hi': 'डाळी व कडधान्ये',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'rajma': {
        'name': 'Rajma Chitra (Kashmiri Red Kidney Beans)',
        'name_hi': 'चित्रा राजमा (कडधान्य)',
        'category_slug': 'dals-pulses',
        'category_name': 'Dals & Pulses',
        'category_name_hi': 'डाळी व कडधान्ये',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'kabuli-chana': {
        'name': 'Kabuli Chana (Chole Big White Chickpeas)',
        'name_hi': 'काबुली चणा (मोठे छोले)',
        'category_slug': 'dals-pulses',
        'category_name': 'Dals & Pulses',
        'category_name_hi': 'डाळी व कडधान्ये',
        'is_loose': True,
        'brand': 'Mandi Fresh Loose',
        'default_unit': '1kg'
    },
    'jeera': {
        'name': 'Jeera Whole (Cumin Seeds)',
        'name_hi': 'अख्खे जिरं (सुगंधी)',
        'category_slug': 'spices-salt',
        'category_name': 'Spices & Salt',
        'category_name_hi': 'मसाले व मीठ',
        'is_loose': False,
        'brand': 'Mandi Spices',
        'default_unit': '100g'
    },
    'haldi': {
        'name': 'Haldi Powder (Pure Turmeric)',
        'name_hi': 'हळद पावडर (शुद्ध)',
        'category_slug': 'spices-salt',
        'category_name': 'Spices & Salt',
        'category_name_hi': 'मसाले व मीठ',
        'is_loose': False,
        'brand': 'Mandi Spices',
        'default_unit': '100g'
    }
}


def parse_filename(filename):
    """
    Extracts product name, price, and unit size from photo filename.
    Supports formats like:
      toor-daal-190-per-kg.jpg
      chakki-atta-38-1kg.png
      fortune-sunflower-oil-145-1l.jpg
      tata-salt-28-1kg.jpg
      maggi-14-70g.jpg
    """
    stem = Path(filename).stem.lower().strip()
    
    # Normalize separators (replace underscores and spaces with hyphens)
    stem_norm = re.sub(r'[\s_]+', '-', stem)
    
    # Extract unit size pattern (e.g. 1kg, 500g, 250g, 1l, 500ml, per-kg, 5kg)
    unit_match = re.search(r'(?:per-kg|per-l|(\d+(?:\.\d+)?)\s*(?:kg|kilo|gm|g|l|ltr|litre|liter|ml|pack|bori|sachet))', stem_norm)
    unit_size = '1kg'
    if unit_match:
        matched_str = unit_match.group(0)
        if 'per-kg' in matched_str:
            unit_size = '1kg'
        elif 'per-l' in matched_str:
            unit_size = '1L'
        else:
            unit_size = matched_str.replace('-', '')
            # Clean unit capitalization (1kg, 500g, 1L)
            if unit_size.endswith('l') or unit_size.endswith('ltr'):
                unit_size = re.sub(r'(?:ltr|l)$', 'L', unit_size)
            elif unit_size.endswith('kg'):
                unit_size = unit_size.lower()
            elif unit_size.endswith('g') or unit_size.endswith('gm'):
                unit_size = re.sub(r'gm$', 'g', unit_size).lower()
        
        # Strip unit token out of stem for cleaner name extraction
        stem_no_unit = stem_norm[:unit_match.start()] + '-' + stem_norm[unit_match.end():]
    else:
        stem_no_unit = stem_norm

    # Extract price: last remaining number sequence or number near 'rs' / 'rate'
    price_match = re.search(r'(?:rs|rate|inr)?-?(\d+(?:\.\d+)?)(?:-?(?:rs|rate|inr))?', stem_no_unit)
    price = 0.0
    if price_match:
        try:
            price = float(price_match.group(1))
            # Remove price token from stem
            stem_name_only = stem_no_unit[:price_match.start()] + '-' + stem_no_unit[price_match.end():]
        except ValueError:
            stem_name_only = stem_no_unit
    else:
        stem_name_only = stem_no_unit

    # Clean remaining slug for name
    slug = re.sub(r'-+', '-', stem_name_only).strip('-')
    
    # Check commodity dictionary for highest keyword match
    matched_entry = None
    for kw, entry in KIRANA_COMMODITY_MAP.items():
        if kw in slug or kw in stem_norm:
            matched_entry = entry
            break

    if matched_entry:
        name = matched_entry['name']
        name_hi = matched_entry['name_hi']
        category_slug = matched_entry['category_slug']
        category_name = matched_entry['category_name']
        category_name_hi = matched_entry['category_name_hi']
        is_loose = matched_entry['is_loose']
        brand = matched_entry['brand']
        if not unit_match:
            unit_size = matched_entry['default_unit']
    else:
        # Generic title generation
        words = [w.capitalize() for w in slug.split('-') if w]
        name = ' '.join(words) if words else 'Kirana Item'
        name_hi = name
        is_loose = any(k in slug for k in ['dal', 'atta', 'rice', 'sugar', 'grain', 'flour', 'loose'])
        category_slug = 'atta-flours' if ('atta' in slug or 'flour' in slug) else ('dals-pulses' if 'dal' in slug else 'rice-grains')
        category_name = 'Atta, Flours & Suji' if category_slug == 'atta-flours' else ('Dals & Pulses' if category_slug == 'dals-pulses' else 'Rice & Grains')
        category_name_hi = 'पीठ, मैदा व रवा' if category_slug == 'atta-flours' else ('डाळी व कडधान्ये' if category_slug == 'dals-pulses' else 'तांदूळ व धान्य')
        brand = 'Loose / Local' if is_loose else 'General Kirana'

    # MRP calculation (standard kirana MRP is usually equal or slightly higher by ~10% for packaged)
    if is_loose:
        mrp = price # Authentic Kirana Pricing: No fake strikethroughs on loose commodities
    else:
        mrp = round(price * 1.08, 0) if price > 0 else 0.0

    return {
        'slug': slug,
        'name': name,
        'name_hi': name_hi,
        'category_slug': category_slug,
        'category_name': category_name,
        'category_name_hi': category_name_hi,
        'is_loose': is_loose,
        'brand': brand,
        'unit_size': unit_size,
        'price': price,
        'mrp': mrp,
        'raw_filename': filename
    }


def ingest_batch_photos(batch_dir='backend/batch_photos', dry_run=False, verbose=True, app_instance=None):
    """
    Processes photos in batch_dir, optimizes destination assets, and upserts into database.
    """
    # Locate project directories
    base_dir = Path(__file__).resolve().parent.parent
    input_path = Path(batch_dir)
    if not input_path.is_absolute():
        input_path = base_dir / batch_dir

    if not input_path.exists():
        os.makedirs(input_path, exist_ok=True)
        if verbose:
            print(f"[BATCH INGEST] Created input directory: {input_path}")
        return {'success': True, 'processed': 0, 'created': 0, 'updated': 0, 'items': []}

    image_exts = {'.jpg', '.jpeg', '.png', '.webp', '.jfif'}
    photo_files = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() in image_exts]

    if not photo_files:
        if verbose:
            print(f"[BATCH INGEST] No image files found in {input_path}. Place photos named like 'toor-daal-190-per-kg.jpg'.")
        return {'success': True, 'processed': 0, 'created': 0, 'updated': 0, 'items': []}

    # Import Flask app and models
    sys.path.insert(0, str(base_dir / 'backend'))
    try:
        from models import db, Product, ProductVariant, Category
        if app_instance is None:
            from app import create_app
            app_instance = create_app()
    except ImportError as e:
        print(f"[BATCH INGEST ERROR] Could not import Flask app models: {e}")
        return {'success': False, 'error': str(e)}

    dest_public = base_dir / 'frontend' / 'public' / 'products'
    dest_dist = base_dir / 'frontend' / 'dist' / 'products'
    os.makedirs(dest_public, exist_ok=True)

    results = []
    created_count = 0
    updated_count = 0

    with app_instance.app_context():
        for pf in photo_files:
            parsed = parse_filename(pf.name)
            clean_filename = f"{parsed['slug']}{pf.suffix.lower()}"
            target_asset_url = f"/products/{clean_filename}"

            item_summary = {
                'file': pf.name,
                'name': parsed['name'],
                'price': parsed['price'],
                'mrp': parsed['mrp'],
                'unit_size': parsed['unit_size'],
                'is_loose': parsed['is_loose'],
                'category': parsed['category_name'],
                'status': 'Dry-Run' if dry_run else 'Pending'
            }

            if verbose:
                print(f"[BATCH INGEST] Found: '{pf.name}' -> {parsed['name']} | Rate: Rs.{parsed['price']} | Unit: {parsed['unit_size']}")

            if dry_run:
                results.append(item_summary)
                continue

            # 1. Copy image asset into public/products
            target_public_file = dest_public / clean_filename
            shutil.copy2(pf, target_public_file)
            if dest_dist.exists():
                os.makedirs(dest_dist, exist_ok=True)
                shutil.copy2(pf, dest_dist / clean_filename)

            # 2. Find or create Category
            cat = Category.query.filter_by(slug=parsed['category_slug']).first()
            if not cat:
                cat = Category(
                    name=parsed['category_name'],
                    name_hi=parsed['category_name_hi'],
                    slug=parsed['category_slug'],
                    icon='package'
                )
                db.session.add(cat)
                db.session.flush()

            # 3. Find or create Product
            prod = Product.query.filter(
                (Product.name == parsed['name']) | (Product.name_hi == parsed['name_hi'])
            ).first()

            if not prod:
                prod = Product(
                    category_id=cat.id,
                    name=parsed['name'],
                    name_hi=parsed['name_hi'],
                    brand=parsed['brand'],
                    is_loose=parsed['is_loose'],
                    description=f"Fresh Mandi Quality {parsed['name']}. Storekeeper verified.",
                    image_url=target_asset_url
                )
                db.session.add(prod)
                db.session.flush()
                created_count += 1
                item_summary['status'] = 'Created'
            else:
                # Update image if missing or placeholder
                if not prod.image_url or 'chakki-atta.jpg' in prod.image_url:
                    prod.image_url = target_asset_url
                updated_count += 1
                item_summary['status'] = 'Updated'

            # 4. Find or create ProductVariant
            variant = ProductVariant.query.filter_by(
                product_id=prod.id,
                unit_size=parsed['unit_size']
            ).first()

            if not variant:
                variant = ProductVariant(
                    product_id=prod.id,
                    unit_size=parsed['unit_size'],
                    mrp=parsed['mrp'],
                    selling_price=parsed['price'],
                    stock_quantity=50,
                    is_available=True
                )
                db.session.add(variant)
            else:
                variant.selling_price = parsed['price']
                variant.mrp = parsed['mrp']
                variant.is_available = True

            db.session.commit()
            results.append(item_summary)

    if verbose:
        print(f"\n[BATCH INGEST COMPLETE] Processed {len(results)} items (Created: {created_count}, Updated: {updated_count}, Dry-Run: {dry_run})")

    return {
        'success': True,
        'processed': len(results),
        'created': created_count,
        'updated': updated_count,
        'items': results
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Batch Ingest Kirana Product Photos and Prices')
    parser.add_argument('--dir', default='backend/batch_photos', help='Directory with photos')
    parser.add_argument('--dry-run', action='store_true', help='Preview parsing without writing to database')
    args = parser.parse_args()

    res = ingest_batch_photos(batch_dir=args.dir, dry_run=args.dry_run, verbose=True)
    sys.exit(0 if res.get('success') else 1)
