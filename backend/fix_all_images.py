import os
import urllib.request
import ssl
from PIL import Image, ImageDraw, ImageFont

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'ApnaKiranaStoreDev/1.0 (contact@apnakirana.local)'
}

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'public', 'products')
DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist', 'products')

os.makedirs(PUBLIC_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)

def save_image(img, filename):
    p1 = os.path.join(PUBLIC_DIR, filename)
    p2 = os.path.join(DIST_DIR, filename)
    img.save(p1, quality=92)
    img.save(p2, quality=92)
    print(f"Saved {filename}")

def download_or_create():
    # 1. Download Red Chilli Powder
    chilli_url = 'https://upload.wikimedia.org/wikipedia/commons/2/23/Red_chilli_powder.jpg'
    try:
        req = urllib.request.Request(chilli_url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = resp.read()
            with open(os.path.join(PUBLIC_DIR, 'mirch-powder.jpg'), 'wb') as f:
                f.write(data)
            with open(os.path.join(DIST_DIR, 'mirch-powder.jpg'), 'wb') as f:
                f.write(data)
            print("Downloaded real Red Chilli Powder mirch-powder.jpg!")
    except Exception as e:
        print("Fallback for mirch-powder:", e)
        # Create fiery red chilli powder image
        img = Image.new('RGB', (600, 600), color='#881337')
        draw = ImageDraw.Draw(img)
        # Bowl
        draw.ellipse([80, 80, 520, 520], fill='#991b1b', outline='#450a0a', width=8)
        draw.ellipse([120, 120, 480, 480], fill='#dc2626')
        draw.text((160, 270), "LAL MIRCH POWDER\nतीखी लाल मिर्च", fill='#ffffff')
        save_image(img, 'mirch-powder.jpg')

    # 2. Colgate Strong Teeth (Red iconic tube)
    colgate_img = Image.new('RGB', (600, 600), color='#fef2f2')
    draw = ImageDraw.Draw(colgate_img)
    # Background card
    draw.rounded_rectangle([30, 30, 570, 570], radius=24, fill='#ffffff', outline='#fee2e2', width=3)
    # Red tube banner
    draw.rounded_rectangle([60, 180, 540, 360], radius=18, fill='#e11d48')
    draw.rectangle([60, 320, 540, 350], fill='#ffffff')
    draw.text((90, 210), "Colgate", fill='#ffffff', font_size=56)
    draw.text((90, 280), "STRONG TEETH • AMINO SHAKTI", fill='#ffffff', font_size=20)
    draw.text((90, 325), "CALCIUM BOOST • DENTAL CREAM", fill='#e11d48', font_size=18)
    # Badge
    draw.rounded_rectangle([70, 70, 280, 120], radius=10, fill='#be123c')
    draw.text((85, 85), "COLGATE • कोलगेट", fill='#ffffff', font_size=20)
    save_image(colgate_img, 'colgate-strong.jpg')

    # 3. Colgate MaxFresh (Blue Cooling Crystals tube)
    maxfresh_img = Image.new('RGB', (600, 600), color='#f0fdfa')
    draw = ImageDraw.Draw(maxfresh_img)
    draw.rounded_rectangle([30, 30, 570, 570], radius=24, fill='#ffffff', outline='#ccfbf1', width=3)
    draw.rounded_rectangle([60, 180, 540, 360], radius=18, fill='#0284c7')
    # Cyan gradient wave effect
    draw.rectangle([60, 300, 540, 350], fill='#06b6d4')
    draw.text((90, 205), "Colgate", fill='#ffffff', font_size=56)
    draw.text((90, 275), "MaxFresh • PEPPERMINT ICE", fill='#fef08a', font_size=22)
    draw.text((90, 315), "COOLING CRYSTALS • 10X FRESHNESS", fill='#ffffff', font_size=18)
    draw.rounded_rectangle([70, 70, 310, 120], radius=10, fill='#0369a1')
    draw.text((85, 85), "MAXFRESH • मैक्सफ्रेश", fill='#ffffff', font_size=20)
    save_image(maxfresh_img, 'colgate-maxfresh.jpg')

    # 4. Dabur Red Ayurvedic Paste (Terracotta Red Ayurvedic herbal tube)
    dabur_img = Image.new('RGB', (600, 600), color='#fff7ed')
    draw = ImageDraw.Draw(dabur_img)
    draw.rounded_rectangle([30, 30, 570, 570], radius=24, fill='#ffffff', outline='#ffedd5', width=3)
    draw.rounded_rectangle([60, 180, 540, 360], radius=18, fill='#b91c1c')
    draw.rectangle([60, 320, 540, 350], fill='#f59e0b')
    draw.text((90, 205), "Dabur RED", fill='#ffffff', font_size=52)
    draw.text((90, 275), "AYURVEDIC TOOTHPASTE", fill='#fef3c7', font_size=22)
    draw.text((90, 325), "CLOVE • PUDINA • TOMAR • लौंग पुदीना", fill='#78350f', font_size=18)
    draw.rounded_rectangle([70, 70, 300, 120], radius=10, fill='#991b1b')
    draw.text((85, 85), "DABUR RED • डाबर लाल", fill='#ffffff', font_size=20)
    save_image(dabur_img, 'dabur-red.jpg')

    # 5. Patanjali Dant Kanti Natural (Herbal Green / Gold tube)
    dant_img = Image.new('RGB', (600, 600), color='#f0fdf4')
    draw = ImageDraw.Draw(dant_img)
    draw.rounded_rectangle([30, 30, 570, 570], radius=24, fill='#ffffff', outline='#dcfce7', width=3)
    draw.rounded_rectangle([60, 180, 540, 360], radius=18, fill='#15803d')
    draw.rectangle([60, 310, 540, 350], fill='#eab308')
    draw.text((90, 205), "PATANJALI", fill='#ffffff', font_size=42)
    draw.text((90, 260), "Dant Kanti • दंत कांति", fill='#fef9c3', font_size=28)
    draw.text((90, 320), "100% HERBAL • AYURVEDIC PROTECTION", fill='#713f12', font_size=17)
    draw.rounded_rectangle([70, 70, 310, 120], radius=10, fill='#166534')
    draw.text((85, 85), "DANT KANTI • दंत कांति", fill='#ffffff', font_size=20)
    save_image(dant_img, 'dant-kanti.jpg')

    # 6. Desi Mustard Oil (Sarson Tel - Golden Amber Oil Jar with Mustard Seeds)
    mustard_img = Image.new('RGB', (600, 600), color='#fefce8')
    draw = ImageDraw.Draw(mustard_img)
    draw.rounded_rectangle([30, 30, 570, 570], radius=24, fill='#ffffff', outline='#fef08a', width=3)
    # Glass Jar of Amber Oil
    draw.rounded_rectangle([180, 150, 420, 460], radius=30, fill='#ca8a04', outline='#854d0e', width=6)
    draw.rectangle([210, 100, 390, 160], fill='#a16207', outline='#713f12', width=4) # Cap
    draw.rounded_rectangle([200, 230, 400, 370], radius=12, fill='#fef08a', outline='#ca8a04', width=3) # Label
    draw.text((215, 250), "शुद्ध सरसों तेल", fill='#713f12', font_size=24)
    draw.text((220, 290), "KACHI GHANI", fill='#a16207', font_size=20)
    draw.text((230, 325), "100% PURE", fill='#15803d', font_size=18)
    # Outer Badge
    draw.rounded_rectangle([70, 60, 340, 110], radius=10, fill='#854d0e')
    draw.text((85, 75), "SARSON TEL • सरसों तेल", fill='#ffffff', font_size=20)
    save_image(mustard_img, 'mustard-oil.jpg')

    # 7. Fortune Kachi Ghani Mustard Oil (Pouch)
    fortune_oil = Image.new('RGB', (600, 600), color='#fefce8')
    draw = ImageDraw.Draw(fortune_oil)
    draw.rounded_rectangle([30, 30, 570, 570], radius=24, fill='#ffffff', outline='#fde047', width=3)
    # Fortune Oil Pouch
    draw.rounded_rectangle([160, 130, 440, 480], radius=20, fill='#eab308', outline='#a16207', width=6)
    draw.rectangle([160, 180, 440, 380], fill='#15803d') # Green band
    draw.text((190, 200), "Fortune", fill='#ffffff', font_size=46)
    draw.text((185, 260), "KACHI GHANI", fill='#fef08a', font_size=26)
    draw.text((195, 305), "MUSTARD OIL", fill='#ffffff', font_size=24)
    draw.text((210, 345), "सरसों तेल पाउच", fill='#fef9c3', font_size=20)
    save_image(fortune_oil, 'fortune-mustard-oil.jpg')

if __name__ == '__main__':
    download_or_create()
