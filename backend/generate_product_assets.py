"""
Generate high-resolution, branded product cards for Komal Mart catalog items.
Saves to both frontend/public/products and frontend/dist/products.
"""

import os
from PIL import Image, ImageDraw, ImageFont

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'public', 'products')
DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist', 'products')

os.makedirs(PUBLIC_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/calibri.ttf"
BOLD_FONT_PATH = "C:/Windows/Fonts/calibrib.ttf"
if not os.path.exists(BOLD_FONT_PATH):
    BOLD_FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"
if not os.path.exists(FONT_PATH):
    FONT_PATH = "C:/Windows/Fonts/arial.ttf"

def create_card(filename, title, subtitle, brand, badge, bg_color, accent_color, text_color='#ffffff'):
    img = Image.new('RGB', (600, 600), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Outer elegant card
    draw.rounded_rectangle([20, 20, 580, 580], radius=28, fill=bg_color, outline=accent_color, width=4)
    draw.rounded_rectangle([32, 32, 568, 568], radius=22, outline='#ffffff', width=1)
    
    # Store Header Pill
    draw.rounded_rectangle([60, 50, 540, 100], radius=14, fill=accent_color)
    try:
        font_sm = ImageFont.truetype(BOLD_FONT_PATH, 20)
        font_brand = ImageFont.truetype(BOLD_FONT_PATH, 26)
        font_title = ImageFont.truetype(BOLD_FONT_PATH, 38)
        font_sub = ImageFont.truetype(FONT_PATH, 24)
        font_badge = ImageFont.truetype(BOLD_FONT_PATH, 22)
    except:
        font_sm = ImageFont.load_default()
        font_brand = font_sm
        font_title = font_sm
        font_sub = font_sm
        font_badge = font_sm

    draw.text((300, 75), "KOMAL MART • WADALA, MUMBAI", fill='#ffffff', anchor='mm', font=font_sm)
    
    # Center Product Showcase Box
    draw.rounded_rectangle([60, 120, 540, 450], radius=20, fill='#ffffff', outline=accent_color, width=2)
    
    # Brand Pill
    draw.rounded_rectangle([180, 140, 420, 185], radius=10, fill=bg_color)
    draw.text((300, 162), brand.upper(), fill=text_color, anchor='mm', font=font_brand)
    
    # Product Main Title (multi-line friendly)
    words = title.split()
    lines = []
    curr = []
    for w in words:
        curr.append(w)
        if len(' '.join(curr)) > 18:
            lines.append(' '.join(curr[:-1]))
            curr = [w]
    if curr:
        lines.append(' '.join(curr))
    
    y_start = 240 if len(lines) == 1 else (220 if len(lines) == 2 else 200)
    for i, line in enumerate(lines[:3]):
        draw.text((300, y_start + i * 46), line, fill='#1c1917', anchor='mm', font=font_title)
    
    # Subtitle / Details
    draw.text((300, 360), subtitle, fill='#57534e', anchor='mm', font=font_sub)
    
    # Feature / Quality Ribbon
    draw.rounded_rectangle([90, 395, 510, 435], radius=8, fill=accent_color)
    draw.text((300, 415), badge, fill='#ffffff', anchor='mm', font=font_badge)
    
    # Bottom Kirana Guarantee
    draw.text((300, 500), "100% Genuine Mandi Fresh Quality", fill='#ffffff', anchor='mm', font=font_sub)
    draw.text((300, 535), "Direct Kirana Savings • Free Local Wadala Delivery", fill='#e2e8f0', anchor='mm', font=font_sm)
    
    # Save to both paths
    p1 = os.path.join(PUBLIC_DIR, filename)
    p2 = os.path.join(DIST_DIR, filename)
    img.save(p1, quality=94)
    img.save(p2, quality=94)
    print(f"Generated card: {filename}")

ASSETS_TO_GENERATE = [
    # Oils & Ghee
    ('gemini-oil.jpg', 'Gemini Sunflower Oil', '1L Pouch • Nutri-V Active', 'Gemini', 'LIGHT & HEALTHY COOKING', '#ca8a04', '#a16207'),
    ('fortune-sunflower-oil.jpg', 'Fortune Sunlite Oil', '1L Pouch • Refined Sunflower', 'Fortune', 'ENRICHED WITH VITAMIN A & D', '#b91c1c', '#991b1b'),
    ('priya-oil.jpg', 'Priya Groundnut Oil', '1L Pouch • Filtered Peanuts', 'Priya', 'AUTHENTIC DESI FLAVOR', '#c2410c', '#9a3412'),
    ('palmolein-oil.jpg', 'Palmolein Cooking Oil', '1L Pouch • Premium Grade', 'Mandi Staples', 'BEST VALUE FOR DAILY FRYING', '#854d0e', '#713f12'),
    ('dhara-oil.jpg', 'Dhara Refined Oil', '1L Pouch • Daily Vegetable', 'Dhara', 'PURITY & TASTE TRUST', '#15803d', '#166534'),
    ('soyabean-oil.jpg', 'Gemini Soyabean Oil', '1L Pouch • Smart Balance', 'Gemini', 'HIGH SMOKE POINT OIL', '#b45309', '#92400e'),
    ('gemini-5l-oil.jpg', 'Gemini Sunflower Oil', '5L Jar / Dibba • Family Pack', 'Gemini', '5 LITRE BULK SAVINGS CAN', '#ca8a04', '#a16207'),
    ('fortune-5l-oil.jpg', 'Fortune Sunlite Oil', '5L Can / Dibba • Refined', 'Fortune', '5 LITRE KITCHEN DIBBA', '#b91c1c', '#991b1b'),
    ('priya-5l-oil.jpg', 'Priya Groundnut Oil', '5L Can / Dibba • Filtered', 'Priya', '5 LITRE PURE PEANUT OIL', '#c2410c', '#9a3412'),
    ('gowardhan-ghee.jpg', 'Gowardhan Cow Ghee', '100% Pure Cow Ghee • Golden', 'Gowardhan', 'DESI COW MILK TRADITION', '#eab308', '#ca8a04'),

    # Rice Varieties
    ('kolam-rice.jpg', 'Wada Kolam Rice', 'Mandi Bori • Soft Daily Rice', 'Mandi Staples', 'LOOSE & 30KG MANDI BORI', '#0f766e', '#115e59'),
    ('india-gate-basmati.jpg', 'India Gate Basmati', 'Feast Rozana • Long Grain', 'India Gate', 'SPECIAL OCCASION BIRYANI', '#7f1d1d', '#991b1b'),
    ('daawat-basmati.jpg', 'Daawat Super Basmati', 'Rozana Gold • Aged Pearls', 'Daawat', 'SLENDER AROMATIC GRAINS', '#1e3a8a', '#1e40af'),
    ('sabudana.jpg', 'Sabudana Pearls', 'Pure Tapioca • Khichdi Special', 'Mandi Staples', 'NON-STICKY FASTING STAPLE', '#334155', '#475569'),
    ('kurmura.jpg', 'Fresh Puffed Kurmura', 'Crisp White • Bhel Special', 'Mandi Staples', 'SUPER LIGHT & FRESH CRUNCH', '#ca8a04', '#a16207'),

    # Dry Fruits
    ('almonds.jpg', 'California Badam', 'Premium Giri • Rich Nutrients', 'Mandi Dry Fruits', '₹50 POUCH & 5KG WHOLESALE', '#78350f', '#92400e'),
    ('cashews.jpg', 'Goa Kaju (W320 & Kani)', 'Whole & Split Creamy Cashews', 'Mandi Dry Fruits', '₹50 POUCH & 5KG WHOLESALE', '#854d0e', '#713f12'),
    ('kishmish.jpg', 'Golden Kishmish', 'Sweet Seedless Indian Raisins', 'Mandi Dry Fruits', '₹50 POUCH & 5KG WHOLESALE', '#b45309', '#92400e'),
    ('makhana.jpg', 'Phool Makhana', 'Jumbo Foxnuts • Roasted Special', 'Mandi Dry Fruits', '₹50 POUCH & 5KG WHOLESALE', '#475569', '#334155'),
    ('walnut.jpg', 'Kashmiri Akhrot Giri', 'Fresh Halves • Brain Food', 'Mandi Dry Fruits', '₹50 POUCH & 5KG WHOLESALE', '#713f12', '#854d0e'),
    ('pista.jpg', 'Roasted Salted Pista', 'Crisp Pistachios • Jumbo Shell', 'Mandi Dry Fruits', '₹50 POUCH & 5KG WHOLESALE', '#15803d', '#166534'),

    # Spices
    ('jeera.jpg', 'Whole Desi Jeera', 'Unpolished Cumin Seeds', 'Mandi Spices', '₹10 / ₹20 / ₹50 POUCHES', '#78350f', '#92400e'),
    ('kali-mirch.jpg', 'Whole Black Pepper', 'Kerala Bold Peppercorn', 'Mandi Spices', '₹10 / ₹20 / ₹50 POUCHES', '#1c1917', '#292524'),
    ('elaichi.jpg', 'Green Cardamom', 'Chhoti Elaichi • Rich Aroma', 'Mandi Spices', '₹10 / ₹20 / ₹50 POUCHES', '#166534', '#15803d'),
    ('dhaniya-powder.jpg', 'Everest Dhaniya Powder', 'Coriander Powder • Rich Color', 'Everest', '100% PURE AROMATIC SPICE', '#15803d', '#166534'),
    ('meat-masala.jpg', 'Everest Meat Masala', 'Spicy Non-Veg Flavor Mix', 'Everest', 'PERFECT SUKHA & CURRY TASTE', '#991b1b', '#7f1d1d'),
    ('chicken-masala.jpg', 'Everest Chicken Masala', 'Traditional Chicken Gravy Mix', 'Everest', 'AUTHENTIC RICH GRAVY', '#c2410c', '#9a3412'),
    ('suhana-mutton-masala.jpg', 'Suhana Mutton Masala', 'Maharashtra Special Rassa Mix', 'Suhana', 'ASLY MAHARASHTRIAN TASTE', '#831843', '#9f1239'),
    ('pav-bhaji-masala.jpg', 'Everest Pav Bhaji Masala', 'Mumbai Street Bhaji Special', 'Everest', 'WADALA STREET PAV BHAJI', '#b91c1c', '#991b1b'),
    ('chhole-masala.jpg', 'Everest Chhole Masala', 'Punjabi Chhole Gravy Special', 'Everest', 'RICH TANGY AMRITSARI FLAVOR', '#854d0e', '#713f12'),
    ('kitchen-king.jpg', 'Everest Kitchen King', 'All-in-One Curry Seasoning', 'Everest', 'KING OF ALL SUBZI FLAVORS', '#b45309', '#92400e'),
    ('hing.jpg', 'Bandhani / Ramdev Hing', 'Strong Asafoetida Powder', 'Bandhani', 'TADKA SPECIAL NATURAL HING', '#b45309', '#92400e'),
    ('kasuri-methi.jpg', 'Kasuri Methi Leaves', 'Sun-Dried Fenugreek Leaves', 'Kasuri Pure', 'RESTAURANT STYLE AROMA', '#166534', '#15803d'),

    # Jaggery & Sweeteners
    ('desi-gud.jpg', 'Kolhapuri Desi Gud', 'Organic Pure Jaggery Block', 'Kolhapuri', 'NO CHEMICALS • HEALTHY SWEET', '#78350f', '#92400e'),
    ('gud-powder.jpg', 'Pure Jaggery Powder', 'Fine Natural Shakkar Powder', 'Desi Sweet', 'BEST SUBSTITUTE FOR WHITE SUGAR', '#92400e', '#78350f'),

    # Beverages & Cold Drinks
    ('nescafe.jpg', 'Nescafe Classic', '100% Pure Instant Coffee', 'Nescafe', '₹10 SACHET & 50G/100G JAR', '#b91c1c', '#991b1b'),
    ('bru-coffee.jpg', 'Bru Instant Coffee', 'Roasted Chicory & Coffee Blend', 'Bru', 'SOUTH INDIAN FILTER STYLE', '#78350f', '#92400e'),
    ('thums-up.jpg', 'Thums Up Toofani', '750ml & 2L • Bold Taste', 'Coca-Cola Co.', 'TASTE THE THUNDER • CHILLED', '#1e3a8a', '#991b1b'),
    ('sprite.jpg', 'Sprite Clear Lime', '750ml & 2L • Lemon Crisp', 'Coca-Cola Co.', 'CLEAR HAI • MAXIMUM CHILL', '#15803d', '#166534'),
    ('coca-cola.jpg', 'Coca-Cola Original', '750ml & 2L • Real Magic', 'Coca-Cola Co.', 'REAL REFRESHMENT • SERVE COLD', '#991b1b', '#7f1d1d'),
    ('maaza.jpg', 'Maaza Mango Drink', '600ml & 1.2L • Asli Alphonso', 'Coca-Cola Co.', 'ASLI AAM KI MASTI', '#d97706', '#b45309'),
    ('bisleri.jpg', 'Bisleri Mineral Water', '1L Bottle & 20L Water Can', 'Bisleri', 'WITH ADDED MINERALS & OZONE', '#0284c7', '#0369a1'),

    # Biscuits & Toast (No chips, no chocolate)
    ('parle-g.jpg', 'Parle-G Gluco Biscuits', '₹5, ₹10, ₹30 & Family Pack', 'Parle', 'DESH KA APNA TEA BISCUIT', '#ca8a04', '#a16207'),
    ('good-day.jpg', 'Good Day Butter', 'Rich Butter Cookies • Smile Pack', 'Britannia', 'HAR COOKIE MEIN BUTTER KHUSHI', '#d97706', '#b45309'),
    ('marie-gold.jpg', 'Marie Gold Tea Time', 'Light & Crisp Tea Companion', 'Britannia', 'HEALTHY TEA-TIME CRUNCH', '#ca8a04', '#a16207'),
    ('krackjack.jpg', 'Parle Krackjack', 'Sweet & Salty Crackers', 'Parle', 'THE ORIGINAL SWEET & SALTY', '#15803d', '#166534'),
    ('monaco.jpg', 'Parle Monaco Salted', 'Light Classic Salted Crackers', 'Parle', 'PERFECT TOPPING SNACK', '#ca8a04', '#a16207'),
    ('bourbon.jpg', 'Britannia Bourbon', 'Crunchy Sugar-Dusted Biscuit', 'Britannia', 'AUTHENTIC CREAM SANDWICH', '#78350f', '#92400e'),
    ('britannia-toast.jpg', 'Britannia Premium Rusk', 'Wheat Toast with Elaichi Flavor', 'Britannia', 'EXTRA CRISP MORNING CHAI RUSK', '#b45309', '#92400e'),

    # Cleaning & Household
    ('wheel-powder.jpg', 'Wheel 2-in-1 Powder', 'Lemon & Jasmine Clean • 1kg', 'Wheel', 'POWERFUL DIRT REMOVAL', '#15803d', '#ca8a04'),
    ('harpic.jpg', 'Harpic Power Plus', '10X Stain Remover • 500ml/1L', 'Harpic', 'DISINFECTANT TOILET CLEANER', '#1e3a8a', '#1e40af'),
    ('lizol.jpg', 'Lizol Floor Cleaner', 'Disinfectant Surface Cleaner', 'Lizol', 'KILLS 99.9% GERMS • FRESH PINE', '#b91c1c', '#991b1b'),
    ('colin.jpg', 'Colin Glass Cleaner', 'Ultra Shine Spray • 500ml', 'Colin', 'SPARKLING CLEAN SHINE', '#0284c7', '#0369a1'),

    # Personal Care & Pooja
    ('lifebuoy-soap.jpg', 'Lifebuoy Total Soap', '100% Germ Protection Bar', 'Lifebuoy', 'FAMILY HEALTH & HYGIENE', '#b91c1c', '#991b1b'),
    ('lux-soap.jpg', 'Lux Soft Glow Soap', 'Rose & Vitamin E Glow Bar', 'Lux', 'SOFT GLOWING SKIN CARE', '#be185d', '#9d174d'),
    ('parachute-coconut-oil.jpg', 'Parachute Coconut Oil', '100% Pure Edible Coconut Oil', 'Parachute', 'AUTHENTIC MARICO PURITY', '#1e3a8a', '#1e40af'),
    ('bajaj-almond-oil.jpg', 'Bajaj Almond Drops', 'Non-Sticky Hair Oil • Vitamin E', 'Bajaj', '6X VITAMIN E NOURISHMENT', '#d97706', '#b45309'),
    ('agarbatti.jpg', 'Cycle Pure Agarbatti', 'Three-in-One Fragrance Sticks', 'Cycle Pure', 'DEVOTIONAL NATURAL INCENSE', '#7c3aed', '#6d28d9'),
    ('kapoor.jpg', 'Mangalam Bhimseni Kapoor', 'Pure Camphor Tablets for Pooja', 'Mangalam', '100% PURE POOJA CAMPHOR', '#0284c7', '#0369a1')
]

def generate_all():
    print(f"Generating {len(ASSETS_TO_GENERATE)} branded grocery cards...")
    for item in ASSETS_TO_GENERATE:
        filename, title, subtitle, brand, badge, bg, accent = item
        create_card(filename, title, subtitle, brand, badge, bg, accent)
    print("All branded catalog cards created successfully!")

if __name__ == '__main__':
    generate_all()
