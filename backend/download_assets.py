import os
import shutil
import urllib.request
import ssl

# Create SSL context to ignore expired certs if any
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
}

DEST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'public', 'products')
DIST_DEST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist', 'products')

os.makedirs(DEST_DIR, exist_ok=True)
os.makedirs(DIST_DEST_DIR, exist_ok=True)

IMAGE_URLS = {
    'toor-dal.jpg': 'https://upload.wikimedia.org/wikipedia/commons/a/a2/Tur_Dal.JPG',
    'tata-toor-dal.jpg': 'https://www.bbassets.com/media/uploads/p/l/40000291_14-tata-sampann-unpolished-toor-dalarhar-dal.jpg',
    'moong-dal-dhuli.jpg': 'https://upload.wikimedia.org/wikipedia/commons/2/2a/Moong_Dal.jpg',
    'moong-dal-chilka.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Mung_beans.jpg/800px-Mung_beans.jpg',
    'sabut-moong.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Mung_beans.jpg/800px-Mung_beans.jpg',
    'urad-dhuli.jpg': 'https://upload.wikimedia.org/wikipedia/commons/a/a2/Tur_Dal.JPG',
    'urad-sabut.jpg': 'https://upload.wikimedia.org/wikipedia/commons/6/6f/Black_gram.jpg',
    'masoor-dal.jpg': 'https://upload.wikimedia.org/wikipedia/commons/3/38/Masoor_dal.JPG',
    'chana-dal.jpg': 'https://upload.wikimedia.org/wikipedia/commons/a/a5/Chana_Dal_%28split_Bengal_gram%29.JPG',
    'chakki-atta.jpg': 'https://upload.wikimedia.org/wikipedia/commons/2/26/Atta_flour.jpg',
    'aashirvaad-atta.jpg': 'https://rukminim2.flixcart.com/image/480/480/l3dcl8w0/flour/m/o/r/5-superior-mp-atta-5-kg-1-whole-wheat-flour-aashirvaad-original-imageggrxysdyvyt.jpeg?q=90',
    'fortune-atta.jpg': 'https://www.fortunefoods.com/wp-content/uploads/2022/12/Chakki-fresh-atta-FOP-1-kg-1.png',
    'maida.jpg': 'https://upload.wikimedia.org/wikipedia/commons/4/49/Maida_flour.jpg',
    'besan.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Gram_flour_AvL.jpg/800px-Gram_flour_AvL.jpg',
    'suji.jpg': 'https://upload.wikimedia.org/wikipedia/commons/c/c6/Sa_semolina_far.jpg',
    'kolam-rice.jpg': 'https://upload.wikimedia.org/wikipedia/commons/f/f8/Basmati_Rice_India%2C_raw.jpg',
    'basmati-rice.jpg': 'https://upload.wikimedia.org/wikipedia/commons/f/f8/Basmati_Rice_India%2C_raw.jpg',
    'poha.jpg': 'https://upload.wikimedia.org/wikipedia/commons/8/80/Poha.jpg',
    'rajma-chitra.jpg': 'https://upload.wikimedia.org/wikipedia/commons/e/e3/Chitra_Rajma.jpg',
    'rajma-red.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Rajma_Red_Kidney_Bean_dish_India.jpg/800px-Rajma_Red_Kidney_Bean_dish_India.jpg',
    'kabuli-chana.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Split_Chickpeas.jpg/800px-Split_Chickpeas.jpg',
    'kala-chana.jpg': 'https://upload.wikimedia.org/wikipedia/commons/c/c0/Chana_%28Hindi-_%E0%A4%9A%E0%A4%A3%E0%A4%BE_or_%E0%A4%9A%E0%A4%A8%E0%A4%BE%29_%284217745699%29.jpg',
    'tata-tea-gold.jpg': 'https://www.tatanutrikorner.com/cdn/shop/files/6144r39VBeL._SL1000.jpg?v=1745836949&width=1445',
    'tata-tea-agni.jpg': 'https://upload.wikimedia.org/wikipedia/commons/3/3b/CTC_tea.jpg',
    'red-label.jpg': 'https://5.imimg.com/data5/ANDROID/Default/2023/12/365631317/FU/RZ/DN/133529333/product-jpeg-500x500.jpg',
    'taaza-tea.jpg': 'https://upload.wikimedia.org/wikipedia/commons/3/3b/CTC_tea.jpg',
    'taj-mahal.jpg': 'https://cdn.zeptonow.com/production/ik-seo/cms/product_variant/916dc3cf-e6aa-43c3-a458-74b7a36455a2/Taj-Mahal-Tea.jpg',
    'girnar-tea.jpg': 'https://upload.wikimedia.org/wikipedia/commons/3/3b/CTC_tea.jpg',
    'colgate-strong.jpg': 'https://www.colgate.com/content/dam/cp-sites-aem/oral-care/oral-care-center/en_in/brand-pages/colgate-strong-teeth/strong-teeth-product-mobile2.png',
    'colgate-maxfresh.jpg': 'https://upload.wikimedia.org/wikipedia/commons/d/d4/2022_Colgate_Toothpaste_for_Russia_market_Total_12_Pro_Visible_Action.jpg',
    'sensodyne.jpg': 'https://i-cf65.ch-static.com/content/dam/cf-consumer-healthcare/sensodyne-v3/en_IN/image-update26/fresh-gel-toothpaste-new.png?auto=format',
    'dabur-red.jpg': 'https://upload.wikimedia.org/wikipedia/commons/d/d4/2022_Colgate_Toothpaste_for_Russia_market_Total_12_Pro_Visible_Action.jpg',
    'dant-kanti.jpg': 'https://upload.wikimedia.org/wikipedia/commons/d/d4/2022_Colgate_Toothpaste_for_Russia_market_Total_12_Pro_Visible_Action.jpg',
    'mustard-oil.jpg': 'https://upload.wikimedia.org/wikipedia/commons/8/8b/North_Indian_mango_pickle_marinated_in_mustard_oil_and_mixed_with_Indian_spices.JPG',
    'fortune-mustard-oil.jpg': 'https://www.fortunefoods.com/wp-content/uploads/2022/12/Chakki-fresh-atta-FOP-1-kg-1.png',
    'amul-ghee.jpg': 'https://shop.amul.com/s/62fa94df8c13af2e242eba16/65ba25a7a55405fa02e1881f/01-hero-image_amul-pure-ghee-tetrapack-1l-480x480.png',
    'desi-ghee.jpg': 'https://upload.wikimedia.org/wikipedia/commons/d/db/Desi_ghee.JPG',
    'haldi-powder.jpg': 'https://upload.wikimedia.org/wikipedia/commons/f/f0/Turmeric_Powder_on_a_Spoon_-_Black_Background.jpg',
    'mirch-powder.jpg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Byadgi_chili_powder.jpg/640px-Byadgi_chili_powder.jpg',
    'dhaniya-powder.jpg': 'https://upload.wikimedia.org/wikipedia/commons/f/f0/Turmeric_Powder_on_a_Spoon_-_Black_Background.jpg',
    'tata-salt.jpg': 'https://rukminim3.flixcart.com/image/480/480/xif0q/salt/e/w/q/2-na-iodized-salt-tata-enriched-transparent-2-original-imafavbpwh7ub5r8.png?q=90',
    'everest-garam-masala.jpg': 'https://www.bbassets.com/media/uploads/p/l/30004966_3-everest-masala-royal-garam.jpg',
    'surf-excel.jpg': 'https://www.starquik.com/cdn/shop/files/SQ102576_FOP_5fc368fd-e928-4e66-9ebb-fc1941b5ece9.jpg?v=1776844299&width=533',
    'rin-bar.jpg': 'https://www.bbassets.com/media/uploads/p/l/1206447_3-rin-detergent-bar.jpg',
    'vim-bar.jpg': 'https://www.bigbasket.com/media/uploads/p/m/317229_14-vim-dishwash-bar-lemon.jpg',
    'dettol-soap.jpg': 'https://www.dettol.co.in/static/5b87a0437187fb8f9e909ae9494e0c1a/478c2/dettol-org-plain-front.png'
}

def download_images():
    print(f"Downloading {len(IMAGE_URLS)} authentic product images...")
    success_count = 0
    for filename, url in IMAGE_URLS.items():
        dest_path = os.path.join(DEST_DIR, filename)
        dist_path = os.path.join(DIST_DEST_DIR, filename)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, context=ctx, timeout=12) as response:
                content = response.read()
                if len(content) > 1000:
                    with open(dest_path, 'wb') as f:
                        f.write(content)
                    with open(dist_path, 'wb') as f:
                        f.write(content)
                    print(f" [OK] {filename} ({len(content)} bytes)")
                    success_count += 1
                else:
                    print(f" [!] {filename} too small, skipped")
        except Exception as e:
            print(f" [ERR] {filename}: {e}")

    print(f"\nFinished! Downloaded {success_count}/{len(IMAGE_URLS)} images.")

if __name__ == '__main__':
    download_images()
