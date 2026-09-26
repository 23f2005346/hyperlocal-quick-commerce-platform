"""
Komal Mart (कोमल मार्ट) — Master Catalog Seeder Runner
Safely wipes old trial products/variants and seeds all 13 categories, 110+ products,
~350 variants, and default wholesale tiered pricing into kirana.db.
Preserves user and admin accounts.
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

from app import create_app, seed_database
from models import db, Product, Category, ProductVariant, TieredPricing, User

app = create_app()

with app.app_context():
    print("Clearing old trial products and applying the Master Kirana Catalog...")
    seed_database()
    
    print("\n--- Verification Summary ---")
    cat_count = Category.query.count()
    prod_count = Product.query.count()
    var_count = ProductVariant.query.count()
    tier_count = TieredPricing.query.count()
    user_count = User.query.count()
    
    print(f"Categories: {cat_count}")
    print(f"Products: {prod_count}")
    print(f"Product Variants: {var_count}")
    print(f"Tiered Pricing Slabs: {tier_count}")
    print(f"Users (Preserved): {user_count}")
    
    # Check 4 wheat grain types
    gehu_prods = Product.query.filter(Product.name.ilike('%wheat%') | Product.name.ilike('%गहू%') | Product.name.ilike('%atta%') | Product.name.ilike('%आटा%')).all()
    print(f"\nWheat / Gehu / Atta Items ({len(gehu_prods)}):")
    for g in gehu_prods:
        prices = [f"{v.unit_size}: ₹{v.selling_price}" for v in g.variants]
        print(f"  • {g.name} -> {', '.join(prices)}")
        
    # Check 1L and 5L oils
    oil_prods = Product.query.filter(Product.category.has(slug='oils-ghee')).all()
    print(f"\nOils & Ghee Items ({len(oil_prods)}):")
    for o in oil_prods:
        prices = [f"{v.unit_size}: ₹{v.selling_price}" for v in o.variants]
        print(f"  • {o.name} -> {', '.join(prices)}")
        
    # Check dry fruits ₹50 pouches and 5kg wholesale
    df_prods = Product.query.filter(Product.category.has(slug='dry-fruits-nuts')).all()
    print(f"\nDry Fruits Items ({len(df_prods)}):")
    for d in df_prods:
        prices = [f"{v.unit_size}: ₹{v.selling_price}" for v in d.variants]
        print(f"  • {d.name} -> {', '.join(prices)}")
