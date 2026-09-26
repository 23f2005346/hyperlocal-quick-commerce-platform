"""
Database seed data for authentic Indian Kirana & General Store.
Provides categories, products (both loose/open and packaged), variants with realistic MRP and Selling Prices,
and accurate local image paths located in /products/.
"""

CATEGORIES_DATA = [
    {
        "name": "Dals & Pulses",
        "name_hi": "दालें एवं दलहन",
        "slug": "dals-pulses",
        "icon": "beans",
        "display_order": 1
    },
    {
        "name": "Atta, Flours & Suji",
        "name_hi": "आटा, मैदा एवं सूजी",
        "slug": "atta-flours",
        "icon": "wheat",
        "display_order": 2
    },
    {
        "name": "Rice & Grains",
        "name_hi": "चावल एवं अनाज",
        "slug": "rice-grains",
        "icon": "grain",
        "display_order": 3
    },
    {
        "name": "Beans & Rajma / Chana",
        "name_hi": "राजमा, छोले एवं चना",
        "slug": "beans-legumes",
        "icon": "shapes",
        "display_order": 4
    },
    {
        "name": "Tea & Coffee",
        "name_hi": "चाय पत्ती एवं कॉफ़ी",
        "slug": "tea-beverages",
        "icon": "coffee",
        "display_order": 5
    },
    {
        "name": "Toothpaste & Personal Care",
        "name_hi": "टूथपेस्ट एवं पर्सनल केयर",
        "slug": "oral-care",
        "icon": "sparkles",
        "display_order": 6
    },
    {
        "name": "Oils & Desi Ghee",
        "name_hi": "तेल एवं शुद्ध देसी घी",
        "slug": "oils-ghee",
        "icon": "droplet",
        "display_order": 7
    },
    {
        "name": "Spices & Salt (Masale)",
        "name_hi": "मसाले एवं नमक",
        "slug": "spices-masalas",
        "icon": "flame",
        "display_order": 8
    },
    {
        "name": "Cleaning & Detergents",
        "name_hi": "सफाई एवं डिटर्जेंट",
        "slug": "household-cleaning",
        "icon": "shield-check",
        "display_order": 9
    }
]

PRODUCTS_DATA = [
    # 1. DALS & PULSES
    {
        "category_slug": "dals-pulses",
        "name": "Toor Dal / Arhar Dal (Unpolished Loose)",
        "name_hi": "अरहर दाल / तुअर दाल (खुली देसी)",
        "brand": "Loose / Desi Mandi",
        "is_loose": True,
        "description": "High protein, natural unpolished Arhar/Toor Dal. Direct from grain mandi, perfect for everyday tadka dal and sambar.",
        "image_url": "/products/toor-dal.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 85.0, "selling_price": 75.0, "stock_quantity": 40},
            {"unit_size": "1kg", "mrp": 165.0, "selling_price": 145.0, "stock_quantity": 80},
            {"unit_size": "5kg (Bachat Bag)", "mrp": 800.0, "selling_price": 710.0, "stock_quantity": 15}
        ]
    },
    {
        "category_slug": "dals-pulses",
        "name": "Tata Sampann Toor Dal (Unpolished)",
        "name_hi": "टाटा सम्पन्न तुअर दाल (पैकेट)",
        "brand": "Tata Sampann",
        "is_loose": False,
        "description": "Premium unpolished toor dal rich in natural nutrients and dietary fibre, sorted with multi-stage lasers.",
        "image_url": "/products/tata-toor-dal.jpg",
        "variants": [
            {"unit_size": "1kg Pouch", "mrp": 195.0, "selling_price": 175.0, "stock_quantity": 30}
        ]
    },
    {
        "category_slug": "dals-pulses",
        "name": "Moong Dal Dhuli (Yellow Split)",
        "name_hi": "धुली मूंग दाल (पीली)",
        "brand": "Loose / Desi Mandi",
        "is_loose": True,
        "description": "Easy to digest yellow moong dal for khichdi, dal fry, cheela, and light daily meals.",
        "image_url": "/products/moong-dal-dhuli.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 72.0, "selling_price": 64.0, "stock_quantity": 45},
            {"unit_size": "1kg", "mrp": 140.0, "selling_price": 125.0, "stock_quantity": 60}
        ]
    },
    {
        "category_slug": "dals-pulses",
        "name": "Moong Dal Chilka (Green Split)",
        "name_hi": "मूंग दाल छिलका (हरी टूक)",
        "brand": "Loose / Desi Mandi",
        "is_loose": True,
        "description": "Nutrient-rich split green gram with peel intact. Great for digestion, halwa and healthy tadka.",
        "image_url": "/products/moong-dal-dhuli.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 68.0, "selling_price": 60.0, "stock_quantity": 35},
            {"unit_size": "1kg", "mrp": 132.0, "selling_price": 118.0, "stock_quantity": 50}
        ]
    },
    {
        "category_slug": "dals-pulses",
        "name": "Sabut Moong (Whole Green Gram)",
        "name_hi": "साबुत हरी मूंग (अंकुरण स्पेशल)",
        "brand": "Loose / Desi Mandi",
        "is_loose": True,
        "description": "Whole green moong beans, excellent for sprouting (ankurit moong) and protein-packed curry.",
        "image_url": "/products/moong-dal-dhuli.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 62.0, "selling_price": 55.0, "stock_quantity": 30},
            {"unit_size": "1kg", "mrp": 120.0, "selling_price": 105.0, "stock_quantity": 40}
        ]
    },
    {
        "category_slug": "dals-pulses",
        "name": "Urad Dal Dhuli (White Split)",
        "name_hi": "धुली उड़द दाल (सफ़ेद - इडली/डोसा)",
        "brand": "Loose / Desi Mandi",
        "is_loose": True,
        "description": "Skinless white urad dal. Essential grain for fluffy South Indian Idli, crispy Dosa batter, and Medu Vada.",
        "image_url": "/products/toor-dal.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 78.0, "selling_price": 70.0, "stock_quantity": 35},
            {"unit_size": "1kg", "mrp": 150.0, "selling_price": 135.0, "stock_quantity": 50}
        ]
    },
    {
        "category_slug": "dals-pulses",
        "name": "Urad Sabut / Kali Dal (Dal Makhani Special)",
        "name_hi": "उड़द साबुत / काली दाल (दाल मखनी)",
        "brand": "Loose / Desi Mandi",
        "is_loose": True,
        "description": "Rich black whole urad beans used to slow-cook authentic restaurant-style Dal Makhani and Maa ki Dal.",
        "image_url": "/products/urad-sabut.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 82.0, "selling_price": 74.0, "stock_quantity": 40},
            {"unit_size": "1kg", "mrp": 155.0, "selling_price": 140.0, "stock_quantity": 60}
        ]
    },
    {
        "category_slug": "dals-pulses",
        "name": "Lal Masoor Dal (Red Lentil Malka)",
        "name_hi": "लाल मसूर दाल / मलका मसूर",
        "brand": "Loose / Desi Mandi",
        "is_loose": True,
        "description": "Quick-cooking pink/orange split lentils with a silky smooth texture when boiled with garlic and jeera.",
        "image_url": "/products/masoor-dal.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 58.0, "selling_price": 50.0, "stock_quantity": 30},
            {"unit_size": "1kg", "mrp": 110.0, "selling_price": 95.0, "stock_quantity": 55}
        ]
    },
    {
        "category_slug": "dals-pulses",
        "name": "Chana Dal (Desi Yellow Bengal Gram)",
        "name_hi": "चना दाल (देसी दाना)",
        "brand": "Loose / Desi Mandi",
        "is_loose": True,
        "description": "Polished or unpolished split chickpeas, hearty bite for tadka chana dal, lauki-chana, and puran poli.",
        "image_url": "/products/chana-dal.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 52.0, "selling_price": 45.0, "stock_quantity": 40},
            {"unit_size": "1kg", "mrp": 100.0, "selling_price": 88.0, "stock_quantity": 70},
            {"unit_size": "5kg", "mrp": 480.0, "selling_price": 430.0, "stock_quantity": 10}
        ]
    },

    # 2. ATTA, FLOURS & SUJI
    {
        "category_slug": "atta-flours",
        "name": "Chakki Fresh Wheat Atta (Khula / Loose)",
        "name_hi": "चक्की का ताजा गेहूं आटा (खुला)",
        "brand": "Fresh Chakki Pisai",
        "is_loose": True,
        "description": "Freshly stone-ground MP Sharbati wheat, 100% whole grain with natural bran. Softest rotis guaranteed at budget price.",
        "image_url": "/products/chakki-atta.jpg",
        "variants": [
            {"unit_size": "1kg", "mrp": 40.0, "selling_price": 34.0, "stock_quantity": 150},
            {"unit_size": "5kg", "mrp": 195.0, "selling_price": 165.0, "stock_quantity": 50},
            {"unit_size": "10kg Bori", "mrp": 380.0, "selling_price": 320.0, "stock_quantity": 30}
        ]
    },
    {
        "category_slug": "atta-flours",
        "name": "Aashirvaad Shudh Chakki Atta (Packed)",
        "name_hi": "आशीर्वाद शुद्ध चक्की आटा (पैकेट)",
        "brand": "ITC Aashirvaad",
        "is_loose": False,
        "description": "Made from the finest grains with heavy grains and golden amber color. 4-step mechanized cleaning.",
        "image_url": "/products/aashirvaad-atta.jpg",
        "variants": [
            {"unit_size": "5kg Pack", "mrp": 270.0, "selling_price": 245.0, "stock_quantity": 35},
            {"unit_size": "10kg Bag", "mrp": 525.0, "selling_price": 475.0, "stock_quantity": 25}
        ]
    },
    {
        "category_slug": "atta-flours",
        "name": "Fortune Chakki Fresh Atta",
        "name_hi": "फॉर्च्यून चक्की फ्रेश आटा",
        "brand": "Adani Fortune",
        "is_loose": False,
        "description": "Traditional stone-ground process locks in natural aroma and dietary fibre for puffed rotis.",
        "image_url": "/products/fortune-atta.jpg",
        "variants": [
            {"unit_size": "5kg Pack", "mrp": 255.0, "selling_price": 230.0, "stock_quantity": 20},
            {"unit_size": "10kg Bag", "mrp": 490.0, "selling_price": 440.0, "stock_quantity": 20}
        ]
    },
    {
        "category_slug": "atta-flours",
        "name": "Maida (All Purpose Refined Flour - Loose)",
        "name_hi": "मैदा (खुला रिफाइंड आटा)",
        "brand": "Loose / Local",
        "is_loose": True,
        "description": "Finely milled wheat flour for crispy samosas, bhature, naan, cakes, and mathri snacks.",
        "image_url": "/products/maida.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 26.0, "selling_price": 22.0, "stock_quantity": 50},
            {"unit_size": "1kg", "mrp": 50.0, "selling_price": 40.0, "stock_quantity": 80}
        ]
    },
    {
        "category_slug": "atta-flours",
        "name": "Besan / Gram Flour (Chana Dal Pisai)",
        "name_hi": "शुद्ध चना दाल बेसन (खुला)",
        "brand": "Loose / Local",
        "is_loose": True,
        "description": "100% pure chana dal flour for crispy pakoras, kadhi, dhokla, and besan ke laddoo.",
        "image_url": "/products/besan.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 56.0, "selling_price": 48.0, "stock_quantity": 40},
            {"unit_size": "1kg", "mrp": 108.0, "selling_price": 92.0, "stock_quantity": 60}
        ]
    },
    {
        "category_slug": "atta-flours",
        "name": "Suji / Rawa (Semolina - Loose)",
        "name_hi": "सूजी / रवा (खुली)",
        "brand": "Loose / Local",
        "is_loose": True,
        "description": "Granular wheat semolina for halwa, sooji upma, instant idli, and rava dosa.",
        "image_url": "/products/suji.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 30.0, "selling_price": 25.0, "stock_quantity": 40},
            {"unit_size": "1kg", "mrp": 58.0, "selling_price": 46.0, "stock_quantity": 60}
        ]
    },

    # 3. RICE & GRAINS
    {
        "category_slug": "rice-grains",
        "name": "Wada Kolam / Sona Masoori Rice (Loose)",
        "name_hi": "कोलम / सोना मसूरी चावल (रोजाना खुला)",
        "brand": "Loose / Mandi",
        "is_loose": True,
        "description": "Medium-grain fragrant daily eating rice. Fluffy, non-sticky, easily digestible.",
        "image_url": "/products/basmati-rice.jpg",
        "variants": [
            {"unit_size": "1kg", "mrp": 68.0, "selling_price": 58.0, "stock_quantity": 100},
            {"unit_size": "5kg", "mrp": 330.0, "selling_price": 280.0, "stock_quantity": 40},
            {"unit_size": "25kg Bori", "mrp": 1600.0, "selling_price": 1350.0, "stock_quantity": 15}
        ]
    },
    {
        "category_slug": "rice-grains",
        "name": "India Gate Basmati Rice Feast Rozzana",
        "name_hi": "इंडिया गेट बासमती चावल (रोज़ाना पैकेट)",
        "brand": "India Gate",
        "is_loose": False,
        "description": "Long aromatic basmati grains carefully aged to give slender, distinct grains when cooked.",
        "image_url": "/products/basmati-rice.jpg",
        "variants": [
            {"unit_size": "1kg Pouch", "mrp": 135.0, "selling_price": 115.0, "stock_quantity": 30},
            {"unit_size": "5kg Bag", "mrp": 620.0, "selling_price": 540.0, "stock_quantity": 20}
        ]
    },
    {
        "category_slug": "rice-grains",
        "name": "Thick Poha (Flattened Rice - Loose)",
        "name_hi": "मोटा पोहा (नाश्ता स्पेशल - खुला)",
        "brand": "Loose / Local",
        "is_loose": True,
        "description": "Crisp thick beaten rice flakes. Retains texture and doesn't turn mushy in Kanda Poha or Indori Poha.",
        "image_url": "/products/poha.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 34.0, "selling_price": 28.0, "stock_quantity": 50},
            {"unit_size": "1kg", "mrp": 65.0, "selling_price": 52.0, "stock_quantity": 70}
        ]
    },
    {
        "category_slug": "rice-grains",
        "name": "Sharbati Whole Wheat Grain (शरबती अखंड गहू)",
        "name_hi": "शरबती अखंड गहू (गेहूं दाना - खुला)",
        "brand": "Sehore Mandi / Loose",
        "is_loose": True,
        "description": "Golden MP Sehore Sharbati whole wheat grains. Heavy, lustrous grain perfect for home milling or fresh chakki pisai.",
        "image_url": "/products/sharbati-wheat.jpg",
        "variants": [
            {"unit_size": "1kg", "mrp": 42.0, "selling_price": 38.0, "stock_quantity": 80},
            {"unit_size": "5kg", "mrp": 200.0, "selling_price": 185.0, "stock_quantity": 30},
            {"unit_size": "10kg Bori", "mrp": 395.0, "selling_price": 365.0, "stock_quantity": 20}
        ]
    },
    {
        "category_slug": "rice-grains",
        "name": "Lokwan Whole Wheat Grain (लोकवन गहू)",
        "name_hi": "लोकवन गहू (अखंड दाना - खुला)",
        "brand": "Maharashtra Mandi / Loose",
        "is_loose": True,
        "description": "Authentic Maharashtra Lokwan whole wheat grain. Crisp texture, ideal for everyday soft chapatis, rotis and bhakri.",
        "image_url": "/products/lokwan-wheat.jpg",
        "variants": [
            {"unit_size": "1kg", "mrp": 38.0, "selling_price": 34.0, "stock_quantity": 100},
            {"unit_size": "5kg", "mrp": 180.0, "selling_price": 165.0, "stock_quantity": 40},
            {"unit_size": "10kg Bori", "mrp": 350.0, "selling_price": 325.0, "stock_quantity": 25}
        ]
    },

    # 4. BEANS & RAJMA / CHANA
    {
        "category_slug": "beans-legumes",
        "name": "Rajma Chitra (Himalayan Spotted Kidney Beans)",
        "name_hi": "चित्रा राजमा (हिमाचली दानेदार)",
        "brand": "Loose / Desi Mandi",
        "is_loose": True,
        "description": "Authentic Chitra Rajma with light reddish-brown specks. Soft melt-in-mouth texture for Punjabi Rajma Chawal.",
        "image_url": "/products/rajma-chitra.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 88.0, "selling_price": 75.0, "stock_quantity": 40},
            {"unit_size": "1kg", "mrp": 170.0, "selling_price": 145.0, "stock_quantity": 50}
        ]
    },
    {
        "category_slug": "beans-legumes",
        "name": "Rajma Kashmiri Red (Dark Red)",
        "name_hi": "कश्मीरी लाल राजमा",
        "brand": "Loose / Desi Mandi",
        "is_loose": True,
        "description": "Small glossy dark-red kidney beans that hold their shape while soaking in rich spicy tomato gravy.",
        "image_url": "/products/rajma-chitra.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 98.0, "selling_price": 85.0, "stock_quantity": 30},
            {"unit_size": "1kg", "mrp": 190.0, "selling_price": 165.0, "stock_quantity": 45}
        ]
    },
    {
        "category_slug": "beans-legumes",
        "name": "Kabuli Chana (Big White Chickpeas / Chhole)",
        "name_hi": "काबुली चना / बड़ा सफेद छोले",
        "brand": "Loose / Desi Mandi",
        "is_loose": True,
        "description": "Extra large jumbo chickpeas for spicy Amritsari Chhole Bhature and hummus.",
        "image_url": "/products/chana-dal.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 82.0, "selling_price": 70.0, "stock_quantity": 40},
            {"unit_size": "1kg", "mrp": 158.0, "selling_price": 135.0, "stock_quantity": 60}
        ]
    },
    {
        "category_slug": "beans-legumes",
        "name": "Kala Chana (Desi Brown Chickpeas)",
        "name_hi": "देसी काला चना (नवरात्र भोग / चाट)",
        "brand": "Loose / Desi Mandi",
        "is_loose": True,
        "description": "High fiber small brown chickpeas, great for morning sprouts, sukha kala chana, and ghugni.",
        "image_url": "/products/kala-chana.jpg",
        "variants": [
            {"unit_size": "500g", "mrp": 50.0, "selling_price": 42.0, "stock_quantity": 35},
            {"unit_size": "1kg", "mrp": 95.0, "selling_price": 80.0, "stock_quantity": 55}
        ]
    },

    # 5. TEA & BEVERAGES
    {
        "category_slug": "tea-beverages",
        "name": "Tata Tea Gold (Assam CTC & Long Leaves)",
        "name_hi": "टाटा टी गोल्ड (कड़क चाय)",
        "brand": "Tata Consumer",
        "is_loose": False,
        "description": "Exquisite blend of rich Assam CTC tea and 15% gently rolled long leaves for rich aroma.",
        "image_url": "/products/tata-tea-gold.jpg",
        "variants": [
            {"unit_size": "250g Pack", "mrp": 160.0, "selling_price": 145.0, "stock_quantity": 40},
            {"unit_size": "500g Pack", "mrp": 310.0, "selling_price": 280.0, "stock_quantity": 30},
            {"unit_size": "1kg Pouch", "mrp": 600.0, "selling_price": 540.0, "stock_quantity": 15}
        ]
    },
    {
        "category_slug": "tea-beverages",
        "name": "Tata Tea Agni",
        "name_hi": "टाटा टी अग्नि (जोश भरी कड़क चाय)",
        "brand": "Tata Consumer",
        "is_loose": False,
        "description": "Strong cup with 10% extra long leaves, delivering deep amber liquor and strong taste at great price.",
        "image_url": "/products/ctc-tea.jpg",
        "variants": [
            {"unit_size": "250g Pack", "mrp": 95.0, "selling_price": 85.0, "stock_quantity": 50},
            {"unit_size": "500g Pack", "mrp": 185.0, "selling_price": 165.0, "stock_quantity": 40}
        ]
    },
    {
        "category_slug": "tea-beverages",
        "name": "Brooke Bond Red Label Tea",
        "name_hi": "ब्रुक बॉन्ड रेड लेबल चाय",
        "brand": "Hindustan Unilever",
        "is_loose": False,
        "description": "India's favorite family tea touched with warmth and taste from finest tea gardens.",
        "image_url": "/products/red-label.jpg",
        "variants": [
            {"unit_size": "250g Pack", "mrp": 145.0, "selling_price": 130.0, "stock_quantity": 35},
            {"unit_size": "500g Pack", "mrp": 280.0, "selling_price": 250.0, "stock_quantity": 30}
        ]
    },
    {
        "category_slug": "tea-beverages",
        "name": "Brooke Bond Taaza Tea",
        "name_hi": "ब्रुक बॉन्ड ताज़ा चाय (हरी पत्ती)",
        "brand": "Hindustan Unilever",
        "is_loose": False,
        "description": "Fresh high quality CTC granules infused with green tea leaves for natural refreshing energy.",
        "image_url": "/products/ctc-tea.jpg",
        "variants": [
            {"unit_size": "250g Pack", "mrp": 90.0, "selling_price": 80.0, "stock_quantity": 40},
            {"unit_size": "500g Pack", "mrp": 175.0, "selling_price": 155.0, "stock_quantity": 30}
        ]
    },
    {
        "category_slug": "tea-beverages",
        "name": "Taj Mahal Tea (Wah Taj!)",
        "name_hi": "ताज महल चाय (प्रीमियम वाह ताज)",
        "brand": "Hindustan Unilever",
        "is_loose": False,
        "description": "Selected tea leaves hand-picked from Upper Assam for connoisseurs who want unmatched aroma.",
        "image_url": "/products/taj-mahal.jpg",
        "variants": [
            {"unit_size": "250g Pack", "mrp": 210.0, "selling_price": 190.0, "stock_quantity": 25},
            {"unit_size": "500g Pack", "mrp": 410.0, "selling_price": 370.0, "stock_quantity": 20}
        ]
    },
    {
        "category_slug": "tea-beverages",
        "name": "Girnar Royal Cup Masala Tea",
        "name_hi": "गिरनार मसाला चाय (लौंग इलायची स्पेशल)",
        "brand": "Girnar",
        "is_loose": False,
        "description": "Authentic CTC tea blended with dried ginger, cardamom, cloves, cinnamon, black pepper and nutmeg.",
        "image_url": "/products/ctc-tea.jpg",
        "variants": [
            {"unit_size": "250g Pouch", "mrp": 180.0, "selling_price": 160.0, "stock_quantity": 25}
        ]
    },

    # 6. TOOTHPASTE & PERSONAL CARE
    {
        "category_slug": "oral-care",
        "name": "Colgate Strong Teeth Dental Cream",
        "name_hi": "कोलगेट स्ट्रॉन्ग टीथ (कैल्शियम बूस्ट)",
        "brand": "Colgate-Palmolive",
        "is_loose": False,
        "description": "With Amino Shakti formula, adds natural calcium to strengthen weak spots on teeth enamel.",
        "image_url": "/products/colgate-strong.jpg",
        "variants": [
            {"unit_size": "100g Tube", "mrp": 68.0, "selling_price": 62.0, "stock_quantity": 40},
            {"unit_size": "200g Tube", "mrp": 130.0, "selling_price": 118.0, "stock_quantity": 50},
            {"unit_size": "500g Saver Pack", "mrp": 290.0, "selling_price": 265.0, "stock_quantity": 20}
        ]
    },
    {
        "category_slug": "oral-care",
        "name": "Colgate MaxFresh Peppermint Ice",
        "name_hi": "कोलगेट मैक्सफ्रेश (कूलिंग क्रिस्टल्स)",
        "brand": "Colgate-Palmolive",
        "is_loose": False,
        "description": "Cooling crystals that dissolve in mouth for instant cooling breeze and 10x long lasting fresh breath.",
        "image_url": "/products/colgate-maxfresh.jpg",
        "variants": [
            {"unit_size": "150g Tube", "mrp": 125.0, "selling_price": 115.0, "stock_quantity": 40},
            {"unit_size": "300g (2x150g Duo)", "mrp": 235.0, "selling_price": 210.0, "stock_quantity": 25}
        ]
    },
    {
        "category_slug": "oral-care",
        "name": "Sensodyne Fresh Gel (Sensitive Teeth)",
        "name_hi": "सेंसोडाइन फ्रेश जेल (झनझनाहट से राहत)",
        "brand": "GSK / Haleon",
        "is_loose": False,
        "description": "Clinically proven desensitizing formula for instant and 24/7 protection against tooth sensitivity.",
        "image_url": "/products/sensodyne.jpg",
        "variants": [
            {"unit_size": "75g Tube", "mrp": 160.0, "selling_price": 145.0, "stock_quantity": 30},
            {"unit_size": "150g Tube", "mrp": 295.0, "selling_price": 270.0, "stock_quantity": 20}
        ]
    },
    {
        "category_slug": "oral-care",
        "name": "Dabur Red Ayurvedic Toothpaste",
        "name_hi": "डाबर लाल पेस्ट (13 आयुर्वेदिक जड़ी-बूटियां)",
        "brand": "Dabur",
        "is_loose": False,
        "description": "Time-tested herbal toothpaste with Clove, Pudina and Tomar seeds to prevent toothache and bleeding gums.",
        "image_url": "/products/dabur-red.jpg",
        "variants": [
            {"unit_size": "100g Tube", "mrp": 65.0, "selling_price": 60.0, "stock_quantity": 45},
            {"unit_size": "200g Tube", "mrp": 122.0, "selling_price": 112.0, "stock_quantity": 40},
            {"unit_size": "300g Family Pack", "mrp": 175.0, "selling_price": 160.0, "stock_quantity": 25}
        ]
    },
    {
        "category_slug": "oral-care",
        "name": "Patanjali Dant Kanti Natural",
        "name_hi": "पतंजलि दंत कांति नेचुरल पेस्ट",
        "brand": "Patanjali",
        "is_loose": False,
        "description": "Natural herbal protection with neem, vajradanti, babool and pudina for cavity protection.",
        "image_url": "/products/dant-kanti.jpg",
        "variants": [
            {"unit_size": "100g Tube", "mrp": 60.0, "selling_price": 55.0, "stock_quantity": 50},
            {"unit_size": "200g Tube", "mrp": 110.0, "selling_price": 100.0, "stock_quantity": 35}
        ]
    },

    # 7. OILS & GHEE
    {
        "category_slug": "oils-ghee",
        "name": "Desi Mustard Oil / Sarson Tel (Khula / Loose)",
        "name_hi": "शुद्ध कच्ची घानी सरसों तेल (खुला)",
        "brand": "Local Kolhu / Loose",
        "is_loose": True,
        "description": "Pure pungent mustard oil straight from the wooden expeller (Kolhu). Strong jhaanjh for pickles and spicy curries.",
        "image_url": "/products/mustard-oil.jpg",
        "variants": [
            {"unit_size": "1 Litre", "mrp": 155.0, "selling_price": 138.0, "stock_quantity": 80},
            {"unit_size": "5 Litre Can", "mrp": 750.0, "selling_price": 670.0, "stock_quantity": 20}
        ]
    },
    {
        "category_slug": "oils-ghee",
        "name": "Fortune Kachi Ghani Mustard Oil (Pouch)",
        "name_hi": "फॉर्च्यून कच्ची घानी सरसों तेल (पाउच)",
        "brand": "Adani Fortune",
        "is_loose": False,
        "description": "Cold-pressed mustard oil rich in Omega-3 and natural antioxidants, perfect for Indian cooking.",
        "image_url": "/products/fortune-mustard-oil.jpg",
        "variants": [
            {"unit_size": "1 Litre Pouch", "mrp": 165.0, "selling_price": 148.0, "stock_quantity": 50}
        ]
    },
    {
        "category_slug": "oils-ghee",
        "name": "Amul Pure Desi Ghee (Tin / Carton)",
        "name_hi": "अमूल शुद्ध देसी घी",
        "brand": "Amul",
        "is_loose": False,
        "description": "Granular golden cow and buffalo milk fat ghee. Unbeatable taste on hot rotis, parathas, and halwa.",
        "image_url": "/products/amul-ghee.jpg",
        "variants": [
            {"unit_size": "500ml Carton", "mrp": 360.0, "selling_price": 330.0, "stock_quantity": 30},
            {"unit_size": "1 Litre Tin", "mrp": 710.0, "selling_price": 650.0, "stock_quantity": 25}
        ]
    },

    # 8. SPICES & SALT
    {
        "category_slug": "spices-masalas",
        "name": "Haldi Powder / Turmeric (Chakki Ground Loose)",
        "name_hi": "हल्दी पाउडर (शुद्ध चक्की पिसी - खुली)",
        "brand": "Loose / Mandi",
        "is_loose": True,
        "description": "Pure Salem/Sangli turmeric with high natural curcumin content and bright yellow color. No artificial food colors.",
        "image_url": "/products/haldi-powder.jpg",
        "variants": [
            {"unit_size": "250g", "mrp": 52.0, "selling_price": 45.0, "stock_quantity": 40},
            {"unit_size": "500g", "mrp": 98.0, "selling_price": 85.0, "stock_quantity": 60}
        ]
    },
    {
        "category_slug": "spices-masalas",
        "name": "Lal Mirch Powder / Red Chilli (Loose)",
        "name_hi": "तीखी लाल मिर्च पाउडर (खुली)",
        "brand": "Loose / Mandi",
        "is_loose": True,
        "description": "Guntur & Byadgi stemless chillies ground to a fiery perfection for true desi kick and rich natural red tint.",
        "image_url": "/products/mirch-powder.jpg",
        "variants": [
            {"unit_size": "250g", "mrp": 75.0, "selling_price": 65.0, "stock_quantity": 40},
            {"unit_size": "500g", "mrp": 145.0, "selling_price": 125.0, "stock_quantity": 50}
        ]
    },
    {
        "category_slug": "spices-masalas",
        "name": "Tata Salt (Vacuum Evaporated Iodised)",
        "name_hi": "टाटा नमक (देश का नमक)",
        "brand": "Tata Consumer",
        "is_loose": False,
        "description": "The quintessential vacuum-evaporated table salt ensuring guaranteed iodine levels for mental health.",
        "image_url": "/products/tata-salt.jpg",
        "variants": [
            {"unit_size": "1kg Packet", "mrp": 30.0, "selling_price": 28.0, "stock_quantity": 100}
        ]
    },
    {
        "category_slug": "spices-masalas",
        "name": "Everest Garam Masala",
        "name_hi": "एवरेस्ट गरम मसाला",
        "brand": "Everest",
        "is_loose": False,
        "description": "Aromatic blend of 13 roasted whole spices to impart royal richness to curries and sabzis.",
        "image_url": "/products/everest-garam-masala.jpg",
        "variants": [
            {"unit_size": "100g Box", "mrp": 102.0, "selling_price": 92.0, "stock_quantity": 40}
        ]
    },
    {
        "category_slug": "spices-masalas",
        "name": "Madhur Pure & Hygienic Sugar (साखर)",
        "name_hi": "मधुर शुद्ध दानेदार साखर (चीनी - पैकेट)",
        "brand": "Madhur",
        "is_loose": False,
        "description": "Refined sulphur-free pure cane sugar crystals. Untouched by hand, 100% hygienic for sweet treats, tea, and desserts.",
        "image_url": "/products/madhur-sugar.jpg",
        "variants": [
            {"unit_size": "1kg Pouch", "mrp": 52.0, "selling_price": 48.0, "stock_quantity": 60},
            {"unit_size": "5kg Bag", "mrp": 255.0, "selling_price": 235.0, "stock_quantity": 25}
        ]
    },
    {
        "category_slug": "spices-masalas",
        "name": "Loose White Sugar (खुली साखर)",
        "name_hi": "खुली पांढरी साखर (चीनी - खुली)",
        "brand": "Loose / Mandi",
        "is_loose": True,
        "description": "Clean sparkling daily loose sugar direct from Maharashtra sugar mills. Best rate for daily household consumption.",
        "image_url": "/products/loose-sugar.jpg",
        "variants": [
            {"unit_size": "1kg", "mrp": 48.0, "selling_price": 44.0, "stock_quantity": 100},
            {"unit_size": "5kg", "mrp": 230.0, "selling_price": 215.0, "stock_quantity": 30}
        ]
    },

    # 9. CLEANING & DETERGENTS
    {
        "category_slug": "household-cleaning",
        "name": "Surf Excel Quick Wash Detergent Powder",
        "name_hi": "सर्फ एक्सेल क्विक वॉश डिटर्जेंट",
        "brand": "Hindustan Unilever",
        "is_loose": False,
        "description": "Enzyme-powered stain removal that tackles grease and tough collars in bucket and machine washes.",
        "image_url": "/products/surf-excel.jpg",
        "variants": [
            {"unit_size": "1kg Pack", "mrp": 155.0, "selling_price": 140.0, "stock_quantity": 50},
            {"unit_size": "2kg Pack", "mrp": 300.0, "selling_price": 270.0, "stock_quantity": 30}
        ]
    },
    {
        "category_slug": "household-cleaning",
        "name": "Rin Detergent Bar",
        "name_hi": "रिन साबुन (चमकदार सफेदी)",
        "brand": "Hindustan Unilever",
        "is_loose": False,
        "description": "Bright Clean technology giving clothes 2x more whiteness and freshness.",
        "image_url": "/products/rin-bar.jpg",
        "variants": [
            {"unit_size": "250g Single Bar", "mrp": 22.0, "selling_price": 20.0, "stock_quantity": 80},
            {"unit_size": "Pack of 4 (4x250g)", "mrp": 88.0, "selling_price": 76.0, "stock_quantity": 40}
        ]
    },
    {
        "category_slug": "household-cleaning",
        "name": "Vim Dishwash Bar with Lemon",
        "name_hi": "विम बर्तन धोने का साबुन (नींबू शक्ति)",
        "brand": "Hindustan Unilever",
        "is_loose": False,
        "description": "Power of 100 lemons cuts through burnt grease on kadhais and utensils in one swipe.",
        "image_url": "/products/vim-bar.jpg",
        "variants": [
            {"unit_size": "300g Single Bar", "mrp": 28.0, "selling_price": 25.0, "stock_quantity": 90},
            {"unit_size": "Pack of 3 Bars", "mrp": 84.0, "selling_price": 70.0, "stock_quantity": 35}
        ]
    },
    {
        "category_slug": "household-cleaning",
        "name": "Dettol Original Bathing Soap",
        "name_hi": "डेटॉल ओरिजिनल साबुन (100% जर्म प्रोटेक्शन)",
        "brand": "Reckitt Benckiser",
        "is_loose": False,
        "description": "Classic germ defence pine fragrance trusted by Indian doctors for family hygiene.",
        "image_url": "/products/dettol-soap.jpg",
        "variants": [
            {"unit_size": "75g Single Soap", "mrp": 42.0, "selling_price": 38.0, "stock_quantity": 60},
            {"unit_size": "Saver Pack of 4", "mrp": 168.0, "selling_price": 145.0, "stock_quantity": 30}
        ]
    }
]
