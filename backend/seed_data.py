"""
Komal Mart (कोमल मार्ट) — Master Database Seed Data
Authentic Indian Kirana & General Store inventory for Wadala, Mumbai.
Contains 13 categories, 110+ staple products with realistic retail prices, MRPs,
30kg bori options for loose grains, ₹10/₹20/₹50 pouches for spices, 1L & 5L dibba oils,
dry fruit wholesale 5kg+ tiers, biscuits (no chips, no chocolates), and verified local images.
"""

CATEGORIES_DATA = [
    {
        "name": "Dals & Pulses",
        "name_hi": "डाळी व कडधान्ये",
        "slug": "dals-pulses",
        "icon": "beans",
        "display_order": 1
    },
    {
        "name": "Atta, Flours & Whole Grains",
        "name_hi": "पीठ, मैदा व अखंड धान्य",
        "slug": "atta-flours",
        "icon": "wheat",
        "display_order": 2
    },
    {
        "name": "Rice & Mandi Staples",
        "name_hi": "तांदूळ, पोहे व साबुदाणा",
        "slug": "rice-grains",
        "icon": "grain",
        "display_order": 3
    },
    {
        "name": "Beans & Legumes",
        "name_hi": "कडधान्ये व राजमा / छोले",
        "slug": "beans-legumes",
        "icon": "shapes",
        "display_order": 4
    },
    {
        "name": "Dry Fruits & Nuts",
        "name_hi": "सुका मेवा (किरकोळ व घाऊक ५ किलो+)",
        "slug": "dry-fruits-nuts",
        "icon": "sparkles",
        "display_order": 5
    },
    {
        "name": "Edible Oils & Desi Ghee",
        "name_hi": "खाद्यतेल व शुद्ध तूप",
        "slug": "oils-ghee",
        "icon": "droplet",
        "display_order": 6
    },
    {
        "name": "Spices & Salt (Masale)",
        "name_hi": "मसाले व मीठ",
        "slug": "spices-masalas",
        "icon": "flame",
        "display_order": 7
    },
    {
        "name": "Sugar, Jaggery & Sweeteners",
        "name_hi": "साखर व गूळ",
        "slug": "sugar-jaggery",
        "icon": "sparkles",
        "display_order": 8
    },
    {
        "name": "Tea, Coffee & Beverages",
        "name_hi": "चहा, कॉफी व पेये",
        "slug": "tea-beverages",
        "icon": "coffee",
        "display_order": 9
    },
    {
        "name": "Biscuits & Bakery",
        "name_hi": "बिस्किटे व टोस्ट",
        "slug": "biscuits-bakery",
        "icon": "shopping-bag",
        "display_order": 10
    },
    {
        "name": "Cold Drinks & Bottled Water",
        "name_hi": "शीतपेये व मिनरल वॉटर",
        "slug": "cold-drinks",
        "icon": "droplet",
        "display_order": 11
    },
    {
        "name": "Cleaning & Detergents",
        "name_hi": "स्वच्छता व डिटर्जंट",
        "slug": "household-cleaning",
        "icon": "trash",
        "display_order": 12
    },
    {
        "name": "Personal Care & Pooja",
        "name_hi": "पर्सनल केअर व पूजा साहित्य",
        "slug": "pooja-samagri",
        "icon": "sparkles",
        "display_order": 13
    }
]

PRODUCTS_DATA = [
    # ==========================================
    # 1. DALS & PULSES (डाळी व कडधान्ये)
    # ==========================================
    {
        "name": "Toor Dal / Arhar Dal (Gavran Loose)",
        "name_hi": "तूर डाळ (गावरान मोकळी)",
        "category_slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "अस्सल गावरान अनपॉलिश्ड तूर डाळ. चवदार, लवकर शिजणारी आणि पचनास उत्तम.",
        "image_url": "/products/toor-dal.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 110.0, "mrp": 125.0, "stock_quantity": 100},
            {"unit_size": "1kg", "selling_price": 215.0, "mrp": 240.0, "stock_quantity": 100},
            {"unit_size": "2kg", "selling_price": 425.0, "mrp": 475.0, "stock_quantity": 50},
            {"unit_size": "5kg", "selling_price": 1050.0, "mrp": 1180.0, "stock_quantity": 25}
        ]
    },
    {
        "name": "Tata Sampann Toor Dal (Unpolished)",
        "name_hi": "टाटा सम्पन्न तुअर डाळ (पॅकेट)",
        "category_slug": "dals-pulses",
        "brand": "Tata Sampann",
        "is_loose": False,
        "description": "टाटा सम्पन्न १००% अनपॉलिश्ड प्रीमियम तूर डाळ. नैसर्गिक प्रथिने सुरक्षित.",
        "image_url": "/products/tata-toor-dal.jpg",
        "variants": [
            {"unit_size": "1kg Pouch", "selling_price": 225.0, "mrp": 255.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Moong Dal Dhuli (Yellow Split)",
        "name_hi": "धुली मूंग डाळ (पिवळी)",
        "category_slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "पिवळी मूंग डाळ. हलकी, पचायला सोपी, आजारी व्यक्ती व मुलांसाठी खिचडी स्पेशल.",
        "image_url": "/products/moong-dal-dhuli.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 65.0, "mrp": 75.0, "stock_quantity": 80},
            {"unit_size": "1kg", "selling_price": 125.0, "mrp": 140.0, "stock_quantity": 80},
            {"unit_size": "2kg", "selling_price": 245.0, "mrp": 275.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Moong Dal Chilka (Green Split)",
        "name_hi": "मूंग डाळ छिलका (हिरवी टूक)",
        "category_slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "हिरवी सालीची मूंग डाळ. फायबरयुक्त, पौष्टिक आणि खिचडी स्पेशल.",
        "image_url": "/products/moong-dal-dhuli.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 62.0, "mrp": 70.0, "stock_quantity": 60},
            {"unit_size": "1kg", "selling_price": 120.0, "mrp": 135.0, "stock_quantity": 60}
        ]
    },
    {
        "name": "Moong Sabut (Whole Green Gram)",
        "name_hi": "अखंड हिरवे मूग (गावरान)",
        "category_slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "मोड आणण्यासाठी आणि उसळीसाठी अस्सल गावरान हिरवे मूग.",
        "image_url": "/products/moong-dal-dhuli.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 60.0, "mrp": 68.0, "stock_quantity": 60},
            {"unit_size": "1kg", "selling_price": 115.0, "mrp": 130.0, "stock_quantity": 60},
            {"unit_size": "2kg", "selling_price": 225.0, "mrp": 255.0, "stock_quantity": 25}
        ]
    },
    {
        "name": "Urad Dal Dhuli (White Split - Idli/Dosa)",
        "name_hi": "धुली उडीद डाळ (सफेद - इडली/डोसा)",
        "category_slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "इडली, डोसा आणि मेदू वड्यासाठी पांढरी शुभ्र उडीद डाळ. उत्तम आंबवणे (fermentation).",
        "image_url": "/products/urad-sabut.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 70.0, "mrp": 80.0, "stock_quantity": 80},
            {"unit_size": "1kg", "selling_price": 135.0, "mrp": 150.0, "stock_quantity": 80}
        ]
    },
    {
        "name": "Urad Dal Chilka (Split Black)",
        "name_hi": "उडीद डाळ छिलका (काळी टूक)",
        "category_slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "काळी सालीची उडीद डाळ. पौष्टिक आणि चवदार.",
        "image_url": "/products/urad-sabut.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 65.0, "mrp": 75.0, "stock_quantity": 50},
            {"unit_size": "1kg", "selling_price": 125.0, "mrp": 140.0, "stock_quantity": 50}
        ]
    },
    {
        "name": "Urad Sabut / Kali Dal (Makhani Special)",
        "name_hi": "उडीद साबुत / काळी डाळ (दाल मखनी)",
        "category_slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "दाल मखनी आणि पंजाबी डाळीसाठी अखंड काळे उडीद.",
        "image_url": "/products/urad-sabut.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 68.0, "mrp": 78.0, "stock_quantity": 50},
            {"unit_size": "1kg", "selling_price": 130.0, "mrp": 145.0, "stock_quantity": 50}
        ]
    },
    {
        "name": "Chana Dal (Desi Yellow Bengal Gram)",
        "name_hi": "चना डाळ (देशी पिवळी)",
        "category_slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "पूरणपोळी, डाळ-भाजी आणि बेसनासाठी अस्सल पिवळी चणा डाळ.",
        "image_url": "/products/chana-dal.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 45.0, "mrp": 52.0, "stock_quantity": 100},
            {"unit_size": "1kg", "selling_price": 88.0, "mrp": 98.0, "stock_quantity": 100},
            {"unit_size": "2kg", "selling_price": 172.0, "mrp": 192.0, "stock_quantity": 40},
            {"unit_size": "5kg", "selling_price": 425.0, "mrp": 475.0, "stock_quantity": 20}
        ]
    },
    {
        "name": "Lal Masoor Dal (Red Lentil Malka)",
        "name_hi": "लाल मसूर डाळ / मलका मसूर",
        "category_slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "लाल मलका मसूर डाळ. झटपट शिजणारी आणि स्वादिष्ट.",
        "image_url": "/products/masoor-dal.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 50.0, "mrp": 58.0, "stock_quantity": 70},
            {"unit_size": "1kg", "selling_price": 95.0, "mrp": 110.0, "stock_quantity": 70}
        ]
    },
    {
        "name": "Masoor Sabut (Whole Brown Lentil)",
        "name_hi": "अख्खा मसूर (काळा मसूर)",
        "category_slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "कोल्हापूरी अख्खा मसूर करीसाठी अखंड काळा मसूर.",
        "image_url": "/products/masoor-dal.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 48.0, "mrp": 55.0, "stock_quantity": 60},
            {"unit_size": "1kg", "selling_price": 92.0, "mrp": 105.0, "stock_quantity": 60}
        ]
    },

    # ==========================================
    # 2. ATTA, FLOURS & WHOLE GRAINS (पीठ, आटा व अखंड गहू)
    # ==========================================
    {
        "name": "Lokwan Whole Wheat Grain (लोकवन अखंड गहू)",
        "name_hi": "लोकवन गहू (अखंड दाना - ₹४०/किलो)",
        "category_slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "अस्सल मध्य प्रदेश लोकवन गहू. स्वच्छ, टपोरा दाना, चपातीसाठी उत्तम आणि मऊ पीठ देणारा. ३० किलो बोरी खरेदीवर विशेष सूट.",
        "image_url": "/products/lokwan-wheat.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 40.0, "mrp": 45.0, "stock_quantity": 150},
            {"unit_size": "2kg", "selling_price": 80.0, "mrp": 90.0, "stock_quantity": 100},
            {"unit_size": "5kg", "selling_price": 195.0, "mrp": 220.0, "stock_quantity": 50},
            {"unit_size": "10kg Bori", "selling_price": 380.0, "mrp": 430.0, "stock_quantity": 30},
            {"unit_size": "30kg Mandi Bori", "selling_price": 1140.0, "mrp": 1290.0, "stock_quantity": 10}
        ]
    },
    {
        "name": "Tukdi / Bhalia Whole Wheat Grain (तुकडी गहू)",
        "name_hi": "तुकडी / भालिया गहू (कडक दाना - ₹४२/किलो)",
        "category_slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "कडक दाण्याचा भालिया / तुकडी गहू. गोड चव आणि जास्त पाणी धरून ठेवणारे पीठ.",
        "image_url": "/products/lokwan-wheat.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 42.0, "mrp": 48.0, "stock_quantity": 100},
            {"unit_size": "2kg", "selling_price": 84.0, "mrp": 96.0, "stock_quantity": 80},
            {"unit_size": "5kg", "selling_price": 205.0, "mrp": 235.0, "stock_quantity": 40},
            {"unit_size": "10kg Bori", "selling_price": 400.0, "mrp": 460.0, "stock_quantity": 25},
            {"unit_size": "30kg Mandi Bori", "selling_price": 1200.0, "mrp": 1380.0, "stock_quantity": 8}
        ]
    },
    {
        "name": "MP Sharbati Whole Wheat Grain (सीहोर शरबती)",
        "name_hi": "मध्य प्रदेश शरबती गहू (सोनेरी दाना - ₹४४/किलो)",
        "category_slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "मध्य प्रदेश सीहोरचा अस्सल शरबती गहू. चकाकणारा सोनेरी दाना, अतिशय मऊ आणि पांढऱ्याशुभ्र पोळ्यांसाठी प्रसिद्ध.",
        "image_url": "/products/sharbati-wheat.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 44.0, "mrp": 50.0, "stock_quantity": 120},
            {"unit_size": "2kg", "selling_price": 88.0, "mrp": 100.0, "stock_quantity": 80},
            {"unit_size": "5kg", "selling_price": 215.0, "mrp": 245.0, "stock_quantity": 40},
            {"unit_size": "10kg Bori", "selling_price": 420.0, "mrp": 480.0, "stock_quantity": 25},
            {"unit_size": "30kg Mandi Bori", "selling_price": 1260.0, "mrp": 1440.0, "stock_quantity": 10}
        ]
    },
    {
        "name": "Premium Sharbati Gold / Desi Bhal Wheat (शरबती गोल्ड)",
        "name_hi": "प्रीमियम शरबती गोल्ड गहू (निवडलेला - ₹४८/किलो)",
        "category_slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "प्रीमियम निवडलेला शरबती गोल्ड गहू. शून्य कचरा, टपोरा दाना, विशेष सण आणि मऊ फुलक्यांसाठी सर्वोत्तम.",
        "image_url": "/products/sharbati-wheat.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 48.0, "mrp": 55.0, "stock_quantity": 80},
            {"unit_size": "2kg", "selling_price": 96.0, "mrp": 110.0, "stock_quantity": 60},
            {"unit_size": "5kg", "selling_price": 235.0, "mrp": 270.0, "stock_quantity": 30},
            {"unit_size": "10kg Bori", "selling_price": 460.0, "mrp": 530.0, "stock_quantity": 20},
            {"unit_size": "30kg Mandi Bori", "selling_price": 1380.0, "mrp": 1590.0, "stock_quantity": 6}
        ]
    },
    {
        "name": "Chakki Fresh Wheat Atta (Loose / खुला चक्की आटा)",
        "name_hi": "चक्कीचे ताजे गव्हाचे पीठ (खुला आटा)",
        "category_slug": "atta-flours",
        "brand": "Komal Mart In-House",
        "is_loose": True,
        "description": "कोमल मार्टच्या चक्कीवर ताजे दळलेले १००% शुद्ध गव्हाचे पीठ. मैदा-रहित, कोंड्यासह पौष्टिक.",
        "image_url": "/products/chakki-atta.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 38.0, "mrp": 44.0, "stock_quantity": 150},
            {"unit_size": "2kg", "selling_price": 76.0, "mrp": 88.0, "stock_quantity": 100},
            {"unit_size": "5kg", "selling_price": 185.0, "mrp": 215.0, "stock_quantity": 50},
            {"unit_size": "10kg Bori", "selling_price": 360.0, "mrp": 420.0, "stock_quantity": 30},
            {"unit_size": "30kg Mandi Bori", "selling_price": 1050.0, "mrp": 1230.0, "stock_quantity": 10}
        ]
    },
    {
        "name": "Fortune Chakki Fresh Atta",
        "name_hi": "फॉर्च्युन चक्की फ्रेश आटा (पॅकेट)",
        "category_slug": "atta-flours",
        "brand": "Fortune",
        "is_loose": False,
        "description": "फॉर्च्युन चक्की फ्रेश आटा. १००% संपूर्ण गहू, मऊ पोळ्यांची हमी.",
        "image_url": "/products/fortune-atta.jpg",
        "variants": [
            {"unit_size": "5kg Bag", "selling_price": 215.0, "mrp": 245.0, "stock_quantity": 30},
            {"unit_size": "10kg Bag", "selling_price": 420.0, "mrp": 470.0, "stock_quantity": 20}
        ]
    },
    {
        "name": "Aashirvaad Shuddh Chakki Atta",
        "name_hi": "आशीर्वाद शुद्ध चक्की आटा (पॅकेट)",
        "category_slug": "atta-flours",
        "brand": "Aashirvaad",
        "is_loose": False,
        "description": "आशीर्वाद शुद्ध चक्की आटा. भारतातील नंबर १ ब्रँडेड आटा. ४-स्टेप क्लीनिंग.",
        "image_url": "/products/aashirvaad-atta.jpg",
        "variants": [
            {"unit_size": "5kg Bag", "selling_price": 235.0, "mrp": 260.0, "stock_quantity": 35},
            {"unit_size": "10kg Bag", "selling_price": 455.0, "mrp": 495.0, "stock_quantity": 25}
        ]
    },
    {
        "name": "Maida (Fine Refined Wheat Flour)",
        "name_hi": "मैदा (समोसा, भटुरे व बेकरी स्पेशल)",
        "category_slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "अतिशय बारीक पांढरा मैदा. भटुरे, समोसा, केक आणि बेकरीसाठी उत्तम.",
        "image_url": "/products/maida.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 24.0, "mrp": 28.0, "stock_quantity": 80},
            {"unit_size": "1kg", "selling_price": 45.0, "mrp": 52.0, "stock_quantity": 80},
            {"unit_size": "2kg", "selling_price": 88.0, "mrp": 100.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Suji / Rawa (Semolina - Ladu/Sheera)",
        "name_hi": "रवा / बारीक सुजी (शिरा व लाडू स्पेशल)",
        "category_slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "स्वच्छ दाणेदार रवा / सुजी. उपमा, शिरा, रवा लाडूसाठी अतिशय उत्तम.",
        "image_url": "/products/suji.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 26.0, "mrp": 30.0, "stock_quantity": 80},
            {"unit_size": "1kg", "selling_price": 48.0, "mrp": 55.0, "stock_quantity": 80}
        ]
    },
    {
        "name": "Besan (Pure Chana Dal Flour)",
        "name_hi": "शुद्ध हरभरा डाळ बेसन (खुला)",
        "category_slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "१००% चणा डाळीचे पिवळेधमक बारीक बेसन. भजी, लाडू व ढोकळ्यासाठी शुद्ध.",
        "image_url": "/products/besan.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 52.0, "mrp": 60.0, "stock_quantity": 80},
            {"unit_size": "1kg", "selling_price": 98.0, "mrp": 115.0, "stock_quantity": 80},
            {"unit_size": "2kg", "selling_price": 190.0, "mrp": 225.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Tata Sampann Besan",
        "name_hi": "टाटा सम्पन्न १००% चना डाळ बेसन (पॅकेट)",
        "category_slug": "atta-flours",
        "brand": "Tata Sampann",
        "is_loose": False,
        "description": "टाटा सम्पन्न १००% अनपॉलिश्ड चणा डाळ बेसन. शुद्धतेची खात्री.",
        "image_url": "/products/besan.jpg",
        "variants": [
            {"unit_size": "500g Pkt", "selling_price": 58.0, "mrp": 68.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Rice Flour / Tandulache Peeth",
        "name_hi": "तांदळाचे बारीक पीठ (भाकरी व मोदक)",
        "category_slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "बारीक पांढरे तांदळाचे पीठ. मऊ तांदळाची भाकरी आणि उकडीच्या मोदकासाठी स्पेशल.",
        "image_url": "/products/maida.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 28.0, "mrp": 32.0, "stock_quantity": 50},
            {"unit_size": "1kg", "selling_price": 52.0, "mrp": 60.0, "stock_quantity": 50}
        ]
    },
    {
        "name": "Jowar Flour / Jwari Peeth",
        "name_hi": "ज्वारीचे पीठ (ताजी भाकरी स्पेशल)",
        "category_slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "ताजी दळलेली ज्वारीची भाकरी. मऊ आणि पचनास हलकी.",
        "image_url": "/products/chakki-atta.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 48.0, "mrp": 55.0, "stock_quantity": 60}
        ]
    },
    {
        "name": "Bajra Flour / Bajri Peeth",
        "name_hi": "बाजरीचे पीठ (पौष्टिक हिवाळा स्पेशल)",
        "category_slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "ताजे बाजरीचे पीठ. कडाक्याच्या थंडीत आणि रोजच्या आरोग्यासाठी उत्तम.",
        "image_url": "/products/chakki-atta.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 42.0, "mrp": 48.0, "stock_quantity": 50}
        ]
    },
    {
        "name": "Makka Atta (Yellow Corn Flour)",
        "name_hi": "पिवळा मक्याचा आटा",
        "category_slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "पिवळ्या मक्याचा आटा. मक्के दी रोटी स्पेशल.",
        "image_url": "/products/besan.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 45.0, "mrp": 52.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Chakki Pisai Grinding Service",
        "name_hi": "चक्की दळण / पिसाई सेवा (गहू, डाळ)",
        "category_slug": "atta-flours",
        "brand": "Komal Mart Services",
        "is_loose": False,
        "description": "कोमल मार्ट चक्की दळण सेवा. ₹७/किलो दराने गहू, ज्वारी किंवा डाळ ताजे बारीक दळून दिले जाईल.",
        "image_url": "/products/chakki-atta.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 7.0, "mrp": 8.0, "stock_quantity": 999},
            {"unit_size": "5kg", "selling_price": 35.0, "mrp": 40.0, "stock_quantity": 999},
            {"unit_size": "10kg", "selling_price": 70.0, "mrp": 80.0, "stock_quantity": 999},
            {"unit_size": "30kg Bori", "selling_price": 210.0, "mrp": 240.0, "stock_quantity": 999}
        ]
    },
    {
        "name": "Whole Soyabean Grain for Flour Mixing",
        "name_hi": "सोयाबीन दाना (पिठात मिसळण्यासाठी)",
        "category_slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "बारीक अखंड पिवळे सोयाबीन. गव्हामध्ये १००-२०० ग्रॅम मिसळून पिसाई करण्यासाठी प्रथिनयुक्त घटक.",
        "image_url": "/products/chana-dal.jpg",
        "variants": [
            {"unit_size": "100g", "selling_price": 8.0, "mrp": 10.0, "stock_quantity": 100},
            {"unit_size": "200g", "selling_price": 15.0, "mrp": 18.0, "stock_quantity": 100},
            {"unit_size": "500g", "selling_price": 35.0, "mrp": 40.0, "stock_quantity": 80},
            {"unit_size": "1kg", "selling_price": 65.0, "mrp": 75.0, "stock_quantity": 60}
        ]
    },

    # ==========================================
    # 3. RICE & MANDI STAPLES (तांदूळ, पोहे व साबुदाणा)
    # ==========================================
    {
        "name": "Wada Kolam Rice (Daily Soft Rice)",
        "name_hi": "वाडा कोलम तांदूळ (मोकळा मऊ भात)",
        "category_slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "महाराष्ट्रातील घराघरात रोज खाल्ला जाणारा प्रसिद्ध वाडा कोलम. मऊ आणि मोकळा शिजणारा तांदूळ. ३० किलो बोरीवर घाऊक दर.",
        "image_url": "/products/kolam-rice.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 56.0, "mrp": 65.0, "stock_quantity": 150},
            {"unit_size": "2kg", "selling_price": 110.0, "mrp": 128.0, "stock_quantity": 100},
            {"unit_size": "5kg", "selling_price": 275.0, "mrp": 315.0, "stock_quantity": 50},
            {"unit_size": "10kg", "selling_price": 540.0, "mrp": 620.0, "stock_quantity": 30},
            {"unit_size": "30kg Mandi Bori", "selling_price": 1590.0, "mrp": 1850.0, "stock_quantity": 10}
        ]
    },
    {
        "name": "Surti Kolam Rice / Gujarat 17",
        "name_hi": "सुरती कोलम तांदूळ (शुभ्र लांब दाना)",
        "category_slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "सुरती कोलम (गुजरात १७). शुभ्र पांढरा, बारीक लांबट दाना. उत्कृष्ट चव.",
        "image_url": "/products/kolam-rice.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 64.0, "mrp": 72.0, "stock_quantity": 120},
            {"unit_size": "2kg", "selling_price": 126.0, "mrp": 142.0, "stock_quantity": 80},
            {"unit_size": "5kg", "selling_price": 310.0, "mrp": 350.0, "stock_quantity": 40},
            {"unit_size": "10kg", "selling_price": 610.0, "mrp": 690.0, "stock_quantity": 25},
            {"unit_size": "30kg Mandi Bori", "selling_price": 1800.0, "mrp": 2050.0, "stock_quantity": 8}
        ]
    },
    {
        "name": "Sona Masoori Rice (Medium Grain)",
        "name_hi": "सोना मसुरी तांदूळ (हलका रोजचा भात)",
        "category_slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "आंध्र प्रदेशचा हलका आणि पचायला सोपा मध्यम दाण्याचा सोना मसुरी तांदूळ.",
        "image_url": "/products/basmati-rice.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 52.0, "mrp": 60.0, "stock_quantity": 120},
            {"unit_size": "2kg", "selling_price": 102.0, "mrp": 118.0, "stock_quantity": 80},
            {"unit_size": "5kg", "selling_price": 255.0, "mrp": 295.0, "stock_quantity": 40},
            {"unit_size": "10kg", "selling_price": 500.0, "mrp": 580.0, "stock_quantity": 25},
            {"unit_size": "30kg Mandi Bori", "selling_price": 1470.0, "mrp": 1720.0, "stock_quantity": 8}
        ]
    },
    {
        "name": "Basmati Tukda / Mogra Rice",
        "name_hi": "बास्मती मोगरा तुकडा तांदूळ (रोजचा बास्मती)",
        "category_slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "बास्मती तुकडा / मोगरा. बास्मतीचा सुवास रोजच्या जेवणात परवडणाऱ्या दरात.",
        "image_url": "/products/basmati-rice.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 46.0, "mrp": 55.0, "stock_quantity": 150},
            {"unit_size": "2kg", "selling_price": 90.0, "mrp": 108.0, "stock_quantity": 100},
            {"unit_size": "5kg", "selling_price": 225.0, "mrp": 265.0, "stock_quantity": 50},
            {"unit_size": "10kg", "selling_price": 440.0, "mrp": 520.0, "stock_quantity": 30},
            {"unit_size": "30kg Mandi Bori", "selling_price": 1290.0, "mrp": 1540.0, "stock_quantity": 10}
        ]
    },
    {
        "name": "Dubar / Tibar Basmati Rice (Loose Long Grain)",
        "name_hi": "दुबार / तिबार बास्मती (बिर्याणी व पुलाव)",
        "category_slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "लांब दाण्याचा सुगंधी दुबार बास्मती. पुलाव, फ्राईड राईस आणि बिर्याणीसाठी उत्तम.",
        "image_url": "/products/basmati-rice.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 75.0, "mrp": 88.0, "stock_quantity": 80},
            {"unit_size": "2kg", "selling_price": 148.0, "mrp": 174.0, "stock_quantity": 50},
            {"unit_size": "5kg", "selling_price": 365.0, "mrp": 430.0, "stock_quantity": 25},
            {"unit_size": "10kg", "selling_price": 720.0, "mrp": 850.0, "stock_quantity": 15}
        ]
    },
    {
        "name": "Indrayani Rice (Aromatic Sticky)",
        "name_hi": "आंबेमोहोर / इंद्रायणी तांदूळ (सुगंधी चिकट)",
        "category_slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "अस्सल सुगंधी इंद्रायणी तांदूळ. मऊ, घमघमाट सुटणारा आणि वरण-भातासाठी अप्रतिम.",
        "image_url": "/products/basmati-rice.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 68.0, "mrp": 78.0, "stock_quantity": 80},
            {"unit_size": "2kg", "selling_price": 134.0, "mrp": 154.0, "stock_quantity": 50},
            {"unit_size": "5kg", "selling_price": 330.0, "mrp": 375.0, "stock_quantity": 25},
            {"unit_size": "10kg", "selling_price": 650.0, "mrp": 740.0, "stock_quantity": 15}
        ]
    },
    {
        "name": "India Gate Basmati Rice Feast Rozana",
        "name_hi": "इंडिया गेट बास्मती फीस्ट रोजाणा (पॅकेट)",
        "category_slug": "rice-grains",
        "brand": "India Gate",
        "is_loose": False,
        "description": "इंडिया गेट ब्रँडेड बास्मती राईस. मध्यम लांबीचा सुगंधी रोजचा भात.",
        "image_url": "/products/india-gate-basmati.jpg",
        "variants": [
            {"unit_size": "1kg Pouch", "selling_price": 95.0, "mrp": 115.0, "stock_quantity": 15},
            {"unit_size": "5kg Bag", "selling_price": 450.0, "mrp": 530.0, "stock_quantity": 8}
        ]
    },
    {
        "name": "Daawat Rozana Super Basmati Rice",
        "name_hi": "दावत रोजाणा सुपर बास्मती (पॅकेट)",
        "category_slug": "rice-grains",
        "brand": "Daawat",
        "is_loose": False,
        "description": "दावत रोजाणा सुपर बास्मती. जुना सुगंधी तांदूळ.",
        "image_url": "/products/daawat-basmati.jpg",
        "variants": [
            {"unit_size": "1kg Pouch", "selling_price": 88.0, "mrp": 105.0, "stock_quantity": 15},
            {"unit_size": "5kg Bag", "selling_price": 420.0, "mrp": 495.0, "stock_quantity": 8}
        ]
    },
    {
        "name": "Thick Poha (Kanda Poha Special)",
        "name_hi": "जाड पोहे (कांदे पोहे स्पेशल)",
        "category_slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "कांदे पोहे आणि बटाटा पोह्यासाठी अस्सल जाड पोहे. न तुटणारे व मऊ राहणारे.",
        "image_url": "/products/poha.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 28.0, "mrp": 32.0, "stock_quantity": 100},
            {"unit_size": "1kg", "selling_price": 52.0, "mrp": 60.0, "stock_quantity": 100},
            {"unit_size": "2kg", "selling_price": 100.0, "mrp": 118.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Thin Poha / Paper Poha (Chivda Special)",
        "name_hi": "पातळ पोहे (दिवाळी चिवडा स्पेशल)",
        "category_slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "कुरकुरीत तळणीचा व भाजका चिवडा बनवण्यासाठी अतिशय पातळ पोहे.",
        "image_url": "/products/poha.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 32.0, "mrp": 38.0, "stock_quantity": 60},
            {"unit_size": "1kg", "selling_price": 60.0, "mrp": 70.0, "stock_quantity": 60}
        ]
    },
    {
        "name": "Sabudana Regular (Khichdi Special)",
        "name_hi": "साबुदाणा (उपवास खिचडी स्पेशल)",
        "category_slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "मोती दाणेदार साबुदाणा. खिचडी अजिबात चिकट होत नाही. उपवासासाठी शुद्ध.",
        "image_url": "/products/sabudana.jpg",
        "variants": [
            {"unit_size": "250g", "selling_price": 22.0, "mrp": 26.0, "stock_quantity": 80},
            {"unit_size": "500g", "selling_price": 42.0, "mrp": 48.0, "stock_quantity": 80},
            {"unit_size": "1kg", "selling_price": 80.0, "mrp": 92.0, "stock_quantity": 80}
        ]
    },
    {
        "name": "Nylon Sabudana (Frying / Vada)",
        "name_hi": "नायलॉन साबुदाणा (तळणी स्पेशल)",
        "category_slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "तेलात टाकल्यावर टम्म फुलणारा नायलॉन साबुदाणा. उपवास चिवड्यासाठी स्पेशल.",
        "image_url": "/products/sabudana.jpg",
        "variants": [
            {"unit_size": "250g", "selling_price": 26.0, "mrp": 30.0, "stock_quantity": 50},
            {"unit_size": "500g", "selling_price": 50.0, "mrp": 58.0, "stock_quantity": 50}
        ]
    },
    {
        "name": "Murmura / Kurmura (Bhel Special)",
        "name_hi": "स्वच्छ कुरमुरे / चुरमुरे (भेळ स्पेशल)",
        "category_slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "कुरकुरीत शुभ्र कुरमुरे. भेळ, सुका भेळ व भडंगसाठी स्वच्छ निवडलेले.",
        "image_url": "/products/kurmura.jpg",
        "variants": [
            {"unit_size": "250g", "selling_price": 18.0, "mrp": 22.0, "stock_quantity": 50},
            {"unit_size": "500g Bag", "selling_price": 34.0, "mrp": 40.0, "stock_quantity": 50}
        ]
    },

    # ==========================================
    # 4. BEANS & LEGUMES (कडधान्ये व राजमा / छोले)
    # ==========================================
    {
        "name": "Rajma Chitra (Himalayan Spotted)",
        "name_hi": "चित्रा राजमा (मऊ शिजणारा)",
        "category_slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "प्रीमियम चित्रा राजमा. लवकर शिजणारा, मऊ आणि चवदार पंजाबी ग्रेव्हीसाठी.",
        "image_url": "/products/rajma-chitra.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 78.0, "mrp": 90.0, "stock_quantity": 60},
            {"unit_size": "1kg", "selling_price": 150.0, "mrp": 170.0, "stock_quantity": 60}
        ]
    },
    {
        "name": "Kabuli Chana (Big White Chhole)",
        "name_hi": "मोठे काबुली चणे (छोले स्पेशल)",
        "category_slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "टपोरे पांढरे काबुली चणे. अमृतसरी छोले आणि चाटसाठी उत्तम.",
        "image_url": "/products/chana-dal.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 75.0, "mrp": 88.0, "stock_quantity": 70},
            {"unit_size": "1kg", "selling_price": 145.0, "mrp": 165.0, "stock_quantity": 70},
            {"unit_size": "2kg", "selling_price": 285.0, "mrp": 325.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Kala Chana / Desi Harbhara",
        "name_hi": "गावरान काळे चणे / हरभरा",
        "category_slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "देशी काळा हरभरा. उसळ, चाट आणि अष्टमी प्रसादासाठी लोहयुक्त.",
        "image_url": "/products/kala-chana.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 45.0, "mrp": 52.0, "stock_quantity": 80},
            {"unit_size": "1kg", "selling_price": 85.0, "mrp": 98.0, "stock_quantity": 80},
            {"unit_size": "2kg", "selling_price": 165.0, "mrp": 190.0, "stock_quantity": 35}
        ]
    },
    {
        "name": "Matki / Moth Beans (Usal Special)",
        "name_hi": "गावरान मटकी (उसळ व मिसळ स्पेशल)",
        "category_slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "लहान दाण्याची अस्सल देशी मटकी. मोड आणून झणझणीत मिसळ आणि उसळीसाठी.",
        "image_url": "/products/kala-chana.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 65.0, "mrp": 75.0, "stock_quantity": 70},
            {"unit_size": "1kg", "selling_price": 125.0, "mrp": 140.0, "stock_quantity": 70}
        ]
    },
    {
        "name": "Safed Vatana (Dry White Peas)",
        "name_hi": "पांढरा वाटाणा (रगडा पॅटीस स्पेशल)",
        "category_slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "पांढरा सुका वाटाणा. मुंबईचा रगडा पॅटीस आणि पाणीपुरी रगड्यासाठी सर्वोत्तम.",
        "image_url": "/products/kala-chana.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 42.0, "mrp": 48.0, "stock_quantity": 80},
            {"unit_size": "1kg", "selling_price": 80.0, "mrp": 92.0, "stock_quantity": 80},
            {"unit_size": "2kg", "selling_price": 155.0, "mrp": 180.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Chavli / Lobia (Black-eyed White Peas)",
        "name_hi": "पांढरी चवळी (लोबिया)",
        "category_slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "पांढरी चवळी. गोड चवदार रस्सा भाजी आणि उसळीसाठी.",
        "image_url": "/products/chana-dal.jpg",
        "variants": [
            {"unit_size": "500g", "selling_price": 55.0, "mrp": 65.0, "stock_quantity": 60},
            {"unit_size": "1kg", "selling_price": 105.0, "mrp": 120.0, "stock_quantity": 60}
        ]
    },

    # ==========================================
    # 5. DRY FRUITS & NUTS (सुका मेवा — किरकोळ व घाऊक ५ किलो+)
    # ==========================================
    {
        "name": "California Giri Badam (Almonds)",
        "name_hi": "कॅलिफोर्निया बदाम गिरी (किरकोळ व घाऊक ५ किलो+)",
        "category_slug": "dry-fruits-nuts",
        "brand": "Mandi Dry Fruits",
        "is_loose": True,
        "description": "गोड, कुरकुरीत १००% ऑइल-रिच कॅलिफोर्निया बदाम. काउंटरवर ₹५० पुडी तसेच घाऊक ५ किलो बोरीमध्ये उपलब्ध.",
        "image_url": "/products/almonds.jpg",
        "variants": [
            {"unit_size": "₹50 Counter Pouch", "selling_price": 50.0, "mrp": 55.0, "stock_quantity": 100},
            {"unit_size": "250g", "selling_price": 220.0, "mrp": 250.0, "stock_quantity": 60},
            {"unit_size": "500g", "selling_price": 430.0, "mrp": 490.0, "stock_quantity": 50},
            {"unit_size": "1kg", "selling_price": 840.0, "mrp": 960.0, "stock_quantity": 40},
            {"unit_size": "5kg Wholesale Bag", "selling_price": 4050.0, "mrp": 4700.0, "stock_quantity": 10}
        ]
    },
    {
        "name": "Goa Whole Cashews W320 & Kani (Kaju)",
        "name_hi": "गोवा काजू (W320 अखंड व तुकडा)",
        "category_slug": "dry-fruits-nuts",
        "brand": "Mandi Dry Fruits",
        "is_loose": True,
        "description": "पांढरा शुभ्र गोड काजू. हलवा-खीर तुकडा आणि अखंड डाइनिंग काजू. ₹५० पुडी उपलब्ध.",
        "image_url": "/products/cashews.jpg",
        "variants": [
            {"unit_size": "₹50 Counter Pouch", "selling_price": 50.0, "mrp": 55.0, "stock_quantity": 100},
            {"unit_size": "250g", "selling_price": 240.0, "mrp": 275.0, "stock_quantity": 60},
            {"unit_size": "500g", "selling_price": 470.0, "mrp": 540.0, "stock_quantity": 50},
            {"unit_size": "1kg", "selling_price": 920.0, "mrp": 1050.0, "stock_quantity": 30},
            {"unit_size": "5kg Wholesale Bag", "selling_price": 4450.0, "mrp": 5100.0, "stock_quantity": 8}
        ]
    },
    {
        "name": "Golden Kishmish (Seedless Indian Raisins)",
        "name_hi": "नाशिक बेदाणा / पिवळी मनुका (किशमिश)",
        "category_slug": "dry-fruits-nuts",
        "brand": "Mandi Dry Fruits",
        "is_loose": True,
        "description": "गोड, रसाळ नाशिकचा पिवळा बेदाणा. सण, खीर, लाडू आणि रोजच्या आरोग्यासाठी.",
        "image_url": "/products/kishmish.jpg",
        "variants": [
            {"unit_size": "₹50 Counter Pouch", "selling_price": 50.0, "mrp": 55.0, "stock_quantity": 100},
            {"unit_size": "250g", "selling_price": 95.0, "mrp": 115.0, "stock_quantity": 70},
            {"unit_size": "500g", "selling_price": 185.0, "mrp": 220.0, "stock_quantity": 60},
            {"unit_size": "1kg", "selling_price": 360.0, "mrp": 430.0, "stock_quantity": 40},
            {"unit_size": "5kg Wholesale Bag", "selling_price": 1700.0, "mrp": 2050.0, "stock_quantity": 10}
        ]
    },
    {
        "name": "Phool Makhana (Jumbo Foxnuts)",
        "name_hi": "मोठा फूल मखाना (कमळाचे बी)",
        "category_slug": "dry-fruits-nuts",
        "brand": "Mandi Dry Fruits",
        "is_loose": True,
        "description": "कॅल्शियमने समृद्ध जंबो मखाना. तुपात भाजून खाण्यासाठी अथवा उपवासासाठी हलका स्नॅक.",
        "image_url": "/products/makhana.jpg",
        "variants": [
            {"unit_size": "₹50 Counter Pouch", "selling_price": 50.0, "mrp": 55.0, "stock_quantity": 80},
            {"unit_size": "250g", "selling_price": 260.0, "mrp": 310.0, "stock_quantity": 40},
            {"unit_size": "500g", "selling_price": 510.0, "mrp": 600.0, "stock_quantity": 30},
            {"unit_size": "1kg", "selling_price": 1000.0, "mrp": 1180.0, "stock_quantity": 20}
        ]
    },
    {
        "name": "Kashmiri Akhrot Giri (Walnut Kernels)",
        "name_hi": "काश्मिरी अक्रोड गिरी (मेंदूसाठी उत्तम)",
        "category_slug": "dry-fruits-nuts",
        "brand": "Mandi Dry Fruits",
        "is_loose": True,
        "description": "कडू चव नसलेली ताजी काश्मिरी अक्रोड गिरी. ओमेगा-३ युक्त स्मरणशक्तीवर्धक.",
        "image_url": "/products/walnut.jpg",
        "variants": [
            {"unit_size": "₹50 Counter Pouch", "selling_price": 50.0, "mrp": 55.0, "stock_quantity": 80},
            {"unit_size": "250g", "selling_price": 320.0, "mrp": 375.0, "stock_quantity": 40},
            {"unit_size": "500g", "selling_price": 630.0, "mrp": 730.0, "stock_quantity": 30},
            {"unit_size": "1kg", "selling_price": 1220.0, "mrp": 1420.0, "stock_quantity": 15}
        ]
    },
    {
        "name": "Roasted Salted Pista (Jumbo Shell)",
        "name_hi": "खारवलेले पिस्ता (सालीसकट भाजलेले)",
        "category_slug": "dry-fruits-nuts",
        "brand": "Mandi Dry Fruits",
        "is_loose": True,
        "description": "कुरकुरीत हलके मीठ लावलेले भाजलेले पिस्ते. प्रीमियम क्वालिटी.",
        "image_url": "/products/pista.jpg",
        "variants": [
            {"unit_size": "₹50 Counter Pouch", "selling_price": 50.0, "mrp": 55.0, "stock_quantity": 80},
            {"unit_size": "250g", "selling_price": 310.0, "mrp": 360.0, "stock_quantity": 40},
            {"unit_size": "500g", "selling_price": 600.0, "mrp": 700.0, "stock_quantity": 30},
            {"unit_size": "1kg", "selling_price": 1180.0, "mrp": 1380.0, "stock_quantity": 15}
        ]
    },

    # ==========================================
    # 6. EDIBLE OILS & DESI GHEE (खाद्यतेल व शुद्ध तूप)
    # ==========================================
    # 1L Packed Oils
    {
        "name": "Gemini Refined Sunflower Oil (1L Pouch)",
        "name_hi": "जेमिनी सूर्यफूल तेल (१ लिटर पाऊच)",
        "category_slug": "oils-ghee",
        "brand": "Gemini",
        "is_loose": False,
        "description": "महाराष्ट्राचे आवडते हलके जेमिनी सूर्यफूल तेल. Nutri-V समृद्ध.",
        "image_url": "/products/gemini-oil.jpg",
        "variants": [
            {"unit_size": "1L Pouch", "selling_price": 135.0, "mrp": 160.0, "stock_quantity": 60}
        ]
    },
    {
        "name": "Fortune Sunlite Refined Sunflower Oil (1L Pouch)",
        "name_hi": "फॉर्च्युन सनलाईट सूर्यफूल तेल (१ लिटर पाऊच)",
        "category_slug": "oils-ghee",
        "brand": "Fortune",
        "is_loose": False,
        "description": "फॉर्च्युन सनलाईट रिफाइंड सूर्यफूल तेल. व्हिटॅमिन A व D युक्त.",
        "image_url": "/products/fortune-sunflower-oil.jpg",
        "variants": [
            {"unit_size": "1L Pouch", "selling_price": 138.0, "mrp": 165.0, "stock_quantity": 50}
        ]
    },
    {
        "name": "Priya Filtered Groundnut Oil (1L Pouch)",
        "name_hi": "प्रिया शेंगदाणा तेल (१ लिटर पाऊच)",
        "category_slug": "oils-ghee",
        "brand": "Priya",
        "is_loose": False,
        "description": "अस्सल फिल्टर शेंगदाणा तेल. पारंपरिक महाराष्ट्रीयन चव आणि सुगंध.",
        "image_url": "/products/priya-oil.jpg",
        "variants": [
            {"unit_size": "1L Pouch", "selling_price": 185.0, "mrp": 210.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Fortune Kachi Ghani Pure Mustard Oil (1L Bottle)",
        "name_hi": "फॉर्च्युन कच्ची घानी मोहरी तेल (१ लिटर)",
        "category_slug": "oils-ghee",
        "brand": "Fortune",
        "is_loose": False,
        "description": "तीव्र घाणीचे शुद्ध मोहरीचे तेल. लोणचे आणि उत्तर भारतीय भाज्यांसाठी उत्तम.",
        "image_url": "/products/fortune-mustard-oil.jpg",
        "variants": [
            {"unit_size": "1L Bottle", "selling_price": 145.0, "mrp": 170.0, "stock_quantity": 45}
        ]
    },
    {
        "name": "Palmolein Cooking Oil (1L Pouch)",
        "name_hi": "पामोलिन खाद्यतेल (१ लिटर पाऊच - तळणी स्पेशल)",
        "category_slug": "oils-ghee",
        "brand": "Mandi Staples",
        "is_loose": False,
        "description": "तळणी आणि रोजच्या घरगुती बजेट स्वयंपाकासाठी शुद्ध पामोलिन तेल.",
        "image_url": "/products/palmolein-oil.jpg",
        "variants": [
            {"unit_size": "1L Pouch", "selling_price": 105.0, "mrp": 125.0, "stock_quantity": 60}
        ]
    },
    {
        "name": "Dhara Refined Vegetable Cooking Oil (1L Pouch)",
        "name_hi": "धारा रिफाइंड व्हेजिटेबल तेल (१ लिटर)",
        "category_slug": "oils-ghee",
        "brand": "Dhara",
        "is_loose": False,
        "description": "धारा ब्रँडचे विश्वासू आणि शुद्ध व्हेजिटेबल कुकिंग ऑईल.",
        "image_url": "/products/dhara-oil.jpg",
        "variants": [
            {"unit_size": "1L Pouch", "selling_price": 128.0, "mrp": 150.0, "stock_quantity": 35}
        ]
    },
    {
        "name": "Gemini Refined Soyabean Oil (1L Pouch)",
        "name_hi": "जेमिनी सोयाबीन तेल (१ लिटर पाऊच)",
        "category_slug": "oils-ghee",
        "brand": "Gemini",
        "is_loose": False,
        "description": "जेमिनी स्मार्ट बॅलन्स सोयाबीन तेल.",
        "image_url": "/products/soyabean-oil.jpg",
        "variants": [
            {"unit_size": "1L Pouch", "selling_price": 122.0, "mrp": 145.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Pure Desi Mustard Oil (Loose / सुटे मोहरी तेल)",
        "name_hi": "सुटे मोहरी तेल (कच्ची घाणी)",
        "category_slug": "oils-ghee",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "कच्ची घाणीचे शुद्ध मोहरी तेल सुटे.",
        "image_url": "/products/mustard-oil.jpg",
        "variants": [
            {"unit_size": "500ml", "selling_price": 75.0, "mrp": 85.0, "stock_quantity": 40},
            {"unit_size": "1L", "selling_price": 140.0, "mrp": 160.0, "stock_quantity": 40}
        ]
    },
    # 5L Dibba / Can Oils
    {
        "name": "Fortune Sunlite Refined Sunflower Oil (5L Can / Dibba)",
        "name_hi": "फॉर्च्युन सनलाईट सूर्यफूल तेल (५ लिटर डब्बा)",
        "category_slug": "oils-ghee",
        "brand": "Fortune",
        "is_loose": False,
        "description": "फॉर्च्युन सनलाईट ५ लिटर कौटुंबिक डब्बा. शुद्ध सूर्यफूल तेल.",
        "image_url": "/products/fortune-5l-oil.jpg",
        "variants": [
            {"unit_size": "5L Dibba / Can", "selling_price": 680.0, "mrp": 795.0, "stock_quantity": 20}
        ]
    },
    {
        "name": "Gemini Refined Sunflower Oil (5L Jar / Dibba)",
        "name_hi": "जेमिनी सूर्यफूल तेल (५ लिटर जार / डब्बा)",
        "category_slug": "oils-ghee",
        "brand": "Gemini",
        "is_loose": False,
        "description": "जेमिनी सूर्यफूल तेल ५ लिटर हँडल जार डब्बा. किमतीत मोठी बचत.",
        "image_url": "/products/gemini-5l-oil.jpg",
        "variants": [
            {"unit_size": "5L Dibba / Jar", "selling_price": 665.0, "mrp": 780.0, "stock_quantity": 25}
        ]
    },
    {
        "name": "Fortune Kachi Ghani Pure Mustard Oil (5L Can / Dibba)",
        "name_hi": "फॉर्च्युन मोहरी तेल (५ लिटर डब्बा)",
        "category_slug": "oils-ghee",
        "brand": "Fortune",
        "is_loose": False,
        "description": "फॉर्च्युन कच्ची घाणी मोहरी तेल ५ लिटर कॅन.",
        "image_url": "/products/fortune-5l-oil.jpg",
        "variants": [
            {"unit_size": "5L Can / Dibba", "selling_price": 720.0, "mrp": 840.0, "stock_quantity": 15}
        ]
    },
    {
        "name": "Priya Refined Groundnut Oil (5L Can / Dibba)",
        "name_hi": "प्रिया शेंगदाणा तेल (५ लिटर डब्बा)",
        "category_slug": "oils-ghee",
        "brand": "Priya",
        "is_loose": False,
        "description": "प्रिया फिल्टर शेंगदाणा तेल ५ लिटर जार डब्बा.",
        "image_url": "/products/priya-5l-oil.jpg",
        "variants": [
            {"unit_size": "5L Can / Dibba", "selling_price": 910.0, "mrp": 1040.0, "stock_quantity": 12}
        ]
    },
    # Desi Ghee
    {
        "name": "Amul Pure Desi Ghee",
        "name_hi": "अमूल शुद्ध तूप (पाऊच व डबा)",
        "category_slug": "oils-ghee",
        "brand": "Amul",
        "is_loose": False,
        "description": "भारताचे विश्वासू १००% शुद्ध अमूल तूप. दाणेदार पोत आणि अस्सल सुगंध.",
        "image_url": "/products/amul-ghee.jpg",
        "variants": [
            {"unit_size": "500ml Pouch", "selling_price": 315.0, "mrp": 340.0, "stock_quantity": 40},
            {"unit_size": "1L Tin", "selling_price": 620.0, "mrp": 665.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Gowardhan Pure Cow Ghee",
        "name_hi": "गोवर्धन १००% गाईचे तूप (जार)",
        "category_slug": "oils-ghee",
        "brand": "Gowardhan",
        "is_loose": False,
        "description": "गोवर्धन शुद्ध गाईचे तूप. नैसर्गिक पिवळसर दाणेदार आणि पचनास उत्तम.",
        "image_url": "/products/gowardhan-ghee.jpg",
        "variants": [
            {"unit_size": "500ml Jar", "selling_price": 335.0, "mrp": 365.0, "stock_quantity": 30},
            {"unit_size": "1L Jar", "selling_price": 660.0, "mrp": 715.0, "stock_quantity": 20}
        ]
    },
    {
        "name": "Pure Buffalo Desi Ghee (Loose / खुले म्हशीचे तूप)",
        "name_hi": "खुले म्हशीचे पांढरे दाणेदार तूप",
        "category_slug": "oils-ghee",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "शुद्ध म्हशीचे पांढरे दाणेदार देशी तूप. पारंपरिक चव.",
        "image_url": "/products/desi-ghee.jpg",
        "variants": [
            {"unit_size": "250g", "selling_price": 170.0, "mrp": 190.0, "stock_quantity": 40},
            {"unit_size": "500g", "selling_price": 330.0, "mrp": 370.0, "stock_quantity": 30},
            {"unit_size": "1kg", "selling_price": 640.0, "mrp": 720.0, "stock_quantity": 20}
        ]
    },

    # ==========================================
    # 7. SPICES, MASALAS & SALT (मसाले व मीठ)
    # ==========================================
    {
        "name": "Whole Jeera / Cumin Seeds (खड़ा जीरा / जिरं)",
        "name_hi": "खडा जिरं (सुगंधी देशी - ₹१०/₹२०/₹५० पुडी)",
        "category_slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "description": "सुगंधी स्वच्छ देशी जिरं. फोडणीसाठी आणि पचनासाठी. ग्राहकांसाठी ₹१०, ₹२०, ₹५० पुड्या उपलब्ध.",
        "image_url": "/products/jeera.jpg",
        "variants": [
            {"unit_size": "₹10 Counter Pouch", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 200},
            {"unit_size": "₹20 Counter Pouch", "selling_price": 20.0, "mrp": 20.0, "stock_quantity": 150},
            {"unit_size": "₹50 Pouch", "selling_price": 50.0, "mrp": 50.0, "stock_quantity": 100},
            {"unit_size": "100g", "selling_price": 35.0, "mrp": 42.0, "stock_quantity": 80},
            {"unit_size": "250g", "selling_price": 82.0, "mrp": 98.0, "stock_quantity": 60},
            {"unit_size": "500g", "selling_price": 160.0, "mrp": 190.0, "stock_quantity": 40},
            {"unit_size": "1kg", "selling_price": 310.0, "mrp": 370.0, "stock_quantity": 25}
        ]
    },
    {
        "name": "Whole Kali Mirch / Black Pepper (काळी मिरी)",
        "name_hi": "काळी मिरी (केरळ स्पेशल - ₹१०/₹२०/₹५० पुडी)",
        "category_slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "description": "अस्सल केरळची तिखट काळी मिरी. औषधी आणि सुगंधी. ₹१०, ₹२०, ₹५०, ₹६० पुड्या उपलब्ध.",
        "image_url": "/products/kali-mirch.jpg",
        "variants": [
            {"unit_size": "₹10 Counter Pouch", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 200},
            {"unit_size": "₹20 Counter Pouch", "selling_price": 20.0, "mrp": 20.0, "stock_quantity": 150},
            {"unit_size": "₹50 Pouch", "selling_price": 50.0, "mrp": 50.0, "stock_quantity": 100},
            {"unit_size": "₹60 Pouch", "selling_price": 60.0, "mrp": 60.0, "stock_quantity": 80},
            {"unit_size": "50g", "selling_price": 45.0, "mrp": 55.0, "stock_quantity": 60},
            {"unit_size": "100g", "selling_price": 85.0, "mrp": 105.0, "stock_quantity": 50},
            {"unit_size": "250g", "selling_price": 205.0, "mrp": 250.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Green Cardamom / Chhoti Elaichi (हिरवी वेलची)",
        "name_hi": "हिरवी वेलची (सुगंधी मोठी - ₹१०/₹२०/₹५० पुडी)",
        "category_slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "description": "मोठ्या आकाराची टपोरी हिरवी वेलची. चहा, खीर आणि गोड पदार्थांसाठी अप्रतिम सुगंध. ₹१०, ₹२०, ₹५०, ₹६० पुड्या उपलब्ध.",
        "image_url": "/products/elaichi.jpg",
        "variants": [
            {"unit_size": "₹10 Counter Pouch", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 200},
            {"unit_size": "₹20 Counter Pouch", "selling_price": 20.0, "mrp": 20.0, "stock_quantity": 150},
            {"unit_size": "₹50 Pouch", "selling_price": 50.0, "mrp": 50.0, "stock_quantity": 100},
            {"unit_size": "₹60 Pouch", "selling_price": 60.0, "mrp": 60.0, "stock_quantity": 80},
            {"unit_size": "25g", "selling_price": 85.0, "mrp": 105.0, "stock_quantity": 50},
            {"unit_size": "50g", "selling_price": 165.0, "mrp": 200.0, "stock_quantity": 40},
            {"unit_size": "100g", "selling_price": 320.0, "mrp": 390.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Desi Khada Garam Masala (मिश्र खडा गरम मसाला)",
        "name_hi": "मिश्र खडा गरम मसाला (सर्व खडे मसाले एकत्रित)",
        "category_slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "description": "दालचिनी, लवंग, तमालपत्र, काळी मिरी, मोठी वेलची आणि चक्रफूल यांचे परिपूर्ण मिश्रण. पुलाव आणि नॉन-व्हेजसाठी.",
        "image_url": "/products/everest-garam-masala.jpg",
        "variants": [
            {"unit_size": "₹10 Counter Pouch", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 200},
            {"unit_size": "₹20 Counter Pouch", "selling_price": 20.0, "mrp": 20.0, "stock_quantity": 150},
            {"unit_size": "₹50 Pouch", "selling_price": 50.0, "mrp": 50.0, "stock_quantity": 100},
            {"unit_size": "100g", "selling_price": 65.0, "mrp": 80.0, "stock_quantity": 60},
            {"unit_size": "250g", "selling_price": 155.0, "mrp": 190.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Pure Haldi Powder (Turmeric - Loose)",
        "name_hi": "हळद पावडर (शुद्ध गावरान हळद)",
        "category_slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "description": "सांगली-नांदेडची शुद्ध पिवळीधमक हळद. भेसळमुक्त, औषधी आणि नैसर्गिक रंग देणारी.",
        "image_url": "/products/haldi-powder.jpg",
        "variants": [
            {"unit_size": "100g", "selling_price": 28.0, "mrp": 35.0, "stock_quantity": 100},
            {"unit_size": "250g", "selling_price": 65.0, "mrp": 78.0, "stock_quantity": 80},
            {"unit_size": "500g", "selling_price": 125.0, "mrp": 150.0, "stock_quantity": 50},
            {"unit_size": "1kg", "selling_price": 240.0, "mrp": 285.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Teja Lal Mirch Powder (Spicy Red Chilli - Loose)",
        "name_hi": "लाल तिखट (झणझणीत मिरची पावडर)",
        "category_slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "description": "गुंटूर-तेजा तिखट मिरची पावडर. झणझणीत चव आणि नैसर्गिक लाल रंग.",
        "image_url": "/products/mirch-powder.jpg",
        "variants": [
            {"unit_size": "100g", "selling_price": 38.0, "mrp": 46.0, "stock_quantity": 100},
            {"unit_size": "250g", "selling_price": 90.0, "mrp": 110.0, "stock_quantity": 80},
            {"unit_size": "500g", "selling_price": 175.0, "mrp": 210.0, "stock_quantity": 50},
            {"unit_size": "1kg", "selling_price": 340.0, "mrp": 400.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Everest Garam Masala",
        "name_hi": "एव्हरेस्ट गरम मसाला (पॅकेट)",
        "category_slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "description": "एव्हरेस्ट गरम मसाला. १३ मसाल्यांचे परिपूर्ण संतुलन.",
        "image_url": "/products/everest-garam-masala.jpg",
        "variants": [
            {"unit_size": "50g Pkt", "selling_price": 46.0, "mrp": 50.0, "stock_quantity": 60},
            {"unit_size": "100g Pkt", "selling_price": 88.0, "mrp": 96.0, "stock_quantity": 50}
        ]
    },
    {
        "name": "Everest Dhaniya Powder (Coriander)",
        "name_hi": "एव्हरेस्ट धने पावडर (पॅकेट)",
        "category_slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "description": "एव्हरेस्ट शुद्ध सुगंधी धने पावडर. दाट ग्रेव्ही आणि सुगंधासाठी.",
        "image_url": "/products/dhaniya-powder.jpg",
        "variants": [
            {"unit_size": "100g Pkt", "selling_price": 36.0, "mrp": 40.0, "stock_quantity": 60},
            {"unit_size": "200g Pkt", "selling_price": 68.0, "mrp": 76.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Everest Meat Masala",
        "name_hi": "एव्हरेस्ट मीट मसाला (मटन व सुक्का स्पेशल)",
        "category_slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "description": "एव्हरेस्ट मीट मसाला. मटन, सुक्का आणि मसालेदार मांसाहारी रस्स्यासाठी अस्सल चव.",
        "image_url": "/products/meat-masala.jpg",
        "variants": [
            {"unit_size": "50g Pkt", "selling_price": 48.0, "mrp": 52.0, "stock_quantity": 50},
            {"unit_size": "100g Pkt", "selling_price": 92.0, "mrp": 100.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Everest Chicken Masala",
        "name_hi": "एव्हरेस्ट चिकन मसाला (चिकन रस्सा स्पेशल)",
        "category_slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "description": "एव्हरेस्ट चिकन मसाला. रेस्टॉरंटसारखी दाट आणि मसालेदार चिकन करी घरीच.",
        "image_url": "/products/chicken-masala.jpg",
        "variants": [
            {"unit_size": "50g Pkt", "selling_price": 48.0, "mrp": 52.0, "stock_quantity": 50},
            {"unit_size": "100g Pkt", "selling_price": 92.0, "mrp": 100.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Suhana Mutton Masala",
        "name_hi": "सुहाना मटन मसाला (महाराष्ट्रीयन काळा रस्सा)",
        "category_slug": "spices-masalas",
        "brand": "Suhana",
        "is_loose": False,
        "description": "सुहाना मटन मसाला. अस्सल महाराष्ट्रीयन पद्धतीचा काळा रस्सा आणि मटन फ्राय.",
        "image_url": "/products/suhana-mutton-masala.jpg",
        "variants": [
            {"unit_size": "50g Pkt", "selling_price": 42.0, "mrp": 46.0, "stock_quantity": 50},
            {"unit_size": "100g Pkt", "selling_price": 82.0, "mrp": 90.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Everest Pav Bhaji Masala",
        "name_hi": "एव्हरेस्ट पाव भाजी मसाला (मुंबई स्पेशल)",
        "category_slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "description": "मुंबई स्ट्रीट स्टाईल चटकदार पाव भाजी मसाला.",
        "image_url": "/products/pav-bhaji-masala.jpg",
        "variants": [
            {"unit_size": "50g Pkt", "selling_price": 44.0, "mrp": 48.0, "stock_quantity": 50},
            {"unit_size": "100g Pkt", "selling_price": 85.0, "mrp": 92.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Everest Kitchen King Masala",
        "name_hi": "एव्हरेस्ट किचन किंग मसाला",
        "category_slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "description": "कोणत्याही भाजीला स्वादिष्ट बनवणारा ऑल-इन-वन किचन किंग मसाला.",
        "image_url": "/products/kitchen-king.jpg",
        "variants": [
            {"unit_size": "50g Pkt", "selling_price": 46.0, "mrp": 50.0, "stock_quantity": 50},
            {"unit_size": "100g Pkt", "selling_price": 88.0, "mrp": 96.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Tata Salt (Desh Ka Namak)",
        "name_hi": "टाटा मीठ (देश का नमक - १ किलो)",
        "category_slug": "spices-masalas",
        "brand": "Tata Salt",
        "is_loose": False,
        "description": "टाटा व्हॅक्यूम इव्हॅपोरेटेड आयोडाईज्ड मीठ. १००% शुद्ध आणि सुरक्षित.",
        "image_url": "/products/tata-salt.jpg",
        "variants": [
            {"unit_size": "1kg Pkt", "selling_price": 28.0, "mrp": 30.0, "stock_quantity": 120}
        ]
    },
    {
        "name": "Sendha Namak (Rock Salt - Fasting)",
        "name_hi": "सेंधा मीठ (उपवासाचे खडे/बारीक मीठ)",
        "category_slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "description": "नैसर्गिक हिमालयन गुलाबी सेंधा मीठ. उपवासासाठी आणि रक्तदाब नियंत्रणासाठी उत्तम.",
        "image_url": "/products/tata-salt.jpg",
        "variants": [
            {"unit_size": "500g Pkt", "selling_price": 32.0, "mrp": 38.0, "stock_quantity": 60},
            {"unit_size": "1kg Pkt", "selling_price": 60.0, "mrp": 70.0, "stock_quantity": 50}
        ]
    },
    {
        "name": "Bandhani / Ramdev Pure Hing",
        "name_hi": "बांधणी शुद्ध हिंग (खमंग फोडणी)",
        "category_slug": "spices-masalas",
        "brand": "Bandhani",
        "is_loose": False,
        "description": "तीव्र सुगंधी हिंग. वरण, कढी आणि भाज्यांच्या खमंग फोडणीसाठी.",
        "image_url": "/products/hing.jpg",
        "variants": [
            {"unit_size": "50g Dibbi", "selling_price": 65.0, "mrp": 75.0, "stock_quantity": 50}
        ]
    },
    {
        "name": "Kasuri Methi Leaves",
        "name_hi": "कसुरी मेथी (सुका सुगंधी मेथी पाला)",
        "category_slug": "spices-masalas",
        "brand": "Kasuri Pure",
        "is_loose": False,
        "description": "सुकवलेली सुगंधी कसुरी मेथी. पनीर आणि भाजीला हॉटेलसारखा घमघमाट देणारी.",
        "image_url": "/products/kasuri-methi.jpg",
        "variants": [
            {"unit_size": "25g Box", "selling_price": 28.0, "mrp": 32.0, "stock_quantity": 40},
            {"unit_size": "50g Box", "selling_price": 52.0, "mrp": 60.0, "stock_quantity": 30}
        ]
    },

    # ==========================================
    # 8. SUGAR, JAGGERY & SWEETENERS (साखर व गूळ)
    # ==========================================
    {
        "name": "Madhur Pure & Hygienic Sugar",
        "name_hi": "मधुर शुद्ध सल्फर-मुक्त साखर (पॅकेट)",
        "category_slug": "sugar-jaggery",
        "brand": "Madhur",
        "is_loose": False,
        "description": "मधुर १००% सल्फर-फ्री पांढरीशुभ्र दाणेदार साखर. स्वच्छतेची हमी.",
        "image_url": "/products/madhur-sugar.jpg",
        "variants": [
            {"unit_size": "1kg Pouch", "selling_price": 48.0, "mrp": 55.0, "stock_quantity": 80},
            {"unit_size": "5kg Bag", "selling_price": 235.0, "mrp": 265.0, "stock_quantity": 25}
        ]
    },
    {
        "name": "Loose White Sugar (M30 Desi Sakhar)",
        "name_hi": "खुली पांढरी साखर (M30 मध्यम दाना)",
        "category_slug": "sugar-jaggery",
        "brand": "Mandi Staples",
        "is_loose": True,
        "description": "मध्यम टपोऱ्या दाण्याची स्वच्छ पांढरी साखर. ३० किलो बोरी खरेदीवर उत्तम बचत.",
        "image_url": "/products/loose-sugar.jpg",
        "variants": [
            {"unit_size": "1kg", "selling_price": 42.0, "mrp": 46.0, "stock_quantity": 150},
            {"unit_size": "2kg", "selling_price": 84.0, "mrp": 92.0, "stock_quantity": 100},
            {"unit_size": "5kg", "selling_price": 205.0, "mrp": 225.0, "stock_quantity": 50},
            {"unit_size": "30kg Mandi Bori", "selling_price": 1220.0, "mrp": 1350.0, "stock_quantity": 10}
        ]
    },
    {
        "name": "Kolhapuri Desi Gud (Organic Block)",
        "name_hi": "कोल्हापूरी सेंद्रिय पिवळा गूळ (१ किलो ढेप)",
        "category_slug": "sugar-jaggery",
        "brand": "Kolhapuri",
        "is_loose": True,
        "description": "अस्सल कोल्हापूरी सेंद्रिय गूळ. रसायने नसलेला, चहा, पुरणपोळी व गुळाच्या लाडवांसाठी उत्तम.",
        "image_url": "/products/desi-gud.jpg",
        "variants": [
            {"unit_size": "1kg Block", "selling_price": 65.0, "mrp": 75.0, "stock_quantity": 80},
            {"unit_size": "5kg Block", "selling_price": 310.0, "mrp": 360.0, "stock_quantity": 20}
        ]
    },
    {
        "name": "Pure Jaggery Powder (Gud Shakkar)",
        "name_hi": "नैसर्गिक गूळ पावडर (साखरेचा उत्तम पर्याय)",
        "category_slug": "sugar-jaggery",
        "brand": "Desi Sweet",
        "is_loose": False,
        "description": "बारीक गाळलेली शुद्ध गूळ पावडर. चहा किंवा दुधात सहज विरघळणारी.",
        "image_url": "/products/gud-powder.jpg",
        "variants": [
            {"unit_size": "500g Pkt", "selling_price": 45.0, "mrp": 55.0, "stock_quantity": 50},
            {"unit_size": "1kg Pkt", "selling_price": 85.0, "mrp": 105.0, "stock_quantity": 40}
        ]
    },

    # ==========================================
    # 9. TEA, COFFEE & BEVERAGES (चहा व कॉफी)
    # ==========================================
    {
        "name": "Brooke Bond Red Label Tea",
        "name_hi": "रेड लेबल चहा (कडक चव व सुगंध)",
        "category_slug": "tea-beverages",
        "brand": "Red Label",
        "is_loose": False,
        "description": "ब्रोक बॉण्ड रेड लेबल. कडक चव, सुंदर रंग आणि चविष्ट चहाचा प्याला.",
        "image_url": "/products/red-label.jpg",
        "variants": [
            {"unit_size": "250g Pkt", "selling_price": 130.0, "mrp": 145.0, "stock_quantity": 60},
            {"unit_size": "500g Pkt", "selling_price": 250.0, "mrp": 280.0, "stock_quantity": 40},
            {"unit_size": "1kg Pkt", "selling_price": 480.0, "mrp": 540.0, "stock_quantity": 20}
        ]
    },
    {
        "name": "Society Leaf & CTC Tea",
        "name_hi": "सोसायटी चहा (महाराष्ट्राचा आवडता)",
        "category_slug": "tea-beverages",
        "brand": "Society",
        "is_loose": False,
        "description": "मुंबईकरांचा अत्यंत लाडका सोसायटी चहा. कडक आणि सुगंधी.",
        "image_url": "/products/ctc-tea.jpg",
        "variants": [
            {"unit_size": "250g Pkt", "selling_price": 135.0, "mrp": 150.0, "stock_quantity": 60},
            {"unit_size": "500g Pkt", "selling_price": 260.0, "mrp": 290.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Tata Tea Gold",
        "name_hi": "टाटा टी गोल्ड (लाँग लीफ चहा)",
        "category_slug": "tea-beverages",
        "brand": "Tata Tea",
        "is_loose": False,
        "description": "टाटा टी गोल्ड. असमच्या लांब पानांचा समृद्ध सुगंध आणि कडकपणा.",
        "image_url": "/products/tata-tea-gold.jpg",
        "variants": [
            {"unit_size": "250g Pkt", "selling_price": 145.0, "mrp": 165.0, "stock_quantity": 40},
            {"unit_size": "500g Pkt", "selling_price": 285.0, "mrp": 320.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Nescafe Classic Instant Coffee",
        "name_hi": "नेस्कॅफे क्लासिक इन्स्टंट कॉफी",
        "category_slug": "tea-beverages",
        "brand": "Nescafe",
        "is_loose": False,
        "description": "१००% शुद्ध इन्स्टंट कॉफी. सकाळी स्फूर्ती देणारा समृद्ध सुगंध. ₹१० पाऊच उपलब्ध.",
        "image_url": "/products/nescafe.jpg",
        "variants": [
            {"unit_size": "₹10 Pouch", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 150},
            {"unit_size": "50g Jar", "selling_price": 175.0, "mrp": 195.0, "stock_quantity": 30},
            {"unit_size": "100g Jar", "selling_price": 335.0, "mrp": 375.0, "stock_quantity": 20}
        ]
    },
    {
        "name": "Bru Instant Coffee",
        "name_hi": "ब्रू इन्स्टंट कॉफी (चिकोरी मिश्रित)",
        "category_slug": "tea-beverages",
        "brand": "Bru",
        "is_loose": False,
        "description": "ब्रू इन्स्टंट कॉफी. दक्षिण भारतीय फिल्टर स्टाईल चव.",
        "image_url": "/products/bru-coffee.jpg",
        "variants": [
            {"unit_size": "₹10 Pouch", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 150},
            {"unit_size": "50g Pouch", "selling_price": 105.0, "mrp": 120.0, "stock_quantity": 40},
            {"unit_size": "100g Pouch", "selling_price": 205.0, "mrp": 235.0, "stock_quantity": 30}
        ]
    },

    # ==========================================
    # 10. BISCUITS & BAKERY (बिस्किटे व टोस्ट — नो चिप्स/चॉकलेट)
    # ==========================================
    {
        "name": "Parle-G Gluco Biscuits",
        "name_hi": "पारले-जी ग्लुको बिस्किट (देश का चहा बिस्किट)",
        "category_slug": "biscuits-bakery",
        "brand": "Parle",
        "is_loose": False,
        "description": "भारताचे लाडके ग्लुकोज बिस्किट. गरमागरम चहासोबत बुडवून खाण्याचा आनंद.",
        "image_url": "/products/parle-g.jpg",
        "variants": [
            {"unit_size": "₹5 Mini Pack", "selling_price": 5.0, "mrp": 5.0, "stock_quantity": 200},
            {"unit_size": "₹10 Regular Pack", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 150},
            {"unit_size": "₹30 Family Pack", "selling_price": 30.0, "mrp": 30.0, "stock_quantity": 80},
            {"unit_size": "800g Super Saver", "selling_price": 75.0, "mrp": 85.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Britannia Good Day Butter Cookies",
        "name_hi": "ब्रिटानिया गुड डे बटर कुकीज (स्माईल पॅक)",
        "category_slug": "biscuits-bakery",
        "brand": "Britannia",
        "is_loose": False,
        "description": "लोण्याने मढलेली कुरकुरीत गोड बिस्किटे. प्रत्येक चाव्यात आनंद.",
        "image_url": "/products/good-day.jpg",
        "variants": [
            {"unit_size": "₹10 Pack", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 150},
            {"unit_size": "₹30 Pack", "selling_price": 30.0, "mrp": 30.0, "stock_quantity": 80}
        ]
    },
    {
        "name": "Britannia Marie Gold",
        "name_hi": "ब्रिटानिया मेरी गोल्ड (हलके चहा बिस्किट)",
        "category_slug": "biscuits-bakery",
        "brand": "Britannia",
        "is_loose": False,
        "description": "हलके, कुरकुरीत आणि कमी गोड असलेले चहासाठी उत्तम बिस्किट.",
        "image_url": "/products/marie-gold.jpg",
        "variants": [
            {"unit_size": "₹10 Pack", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 120},
            {"unit_size": "₹35 Family Pack", "selling_price": 35.0, "mrp": 35.0, "stock_quantity": 70}
        ]
    },
    {
        "name": "Parle Krackjack Crackers",
        "name_hi": "पारले क्रॅकजॅक (गोड व खारट क्रॅकर्स)",
        "category_slug": "biscuits-bakery",
        "brand": "Parle",
        "is_loose": False,
        "description": "गोड आणि खारट चवीचे मूळ क्लासिक क्रॅकर बिस्किट.",
        "image_url": "/products/krackjack.jpg",
        "variants": [
            {"unit_size": "₹10 Pack", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 120},
            {"unit_size": "₹30 Pack", "selling_price": 30.0, "mrp": 30.0, "stock_quantity": 60}
        ]
    },
    {
        "name": "Parle Monaco Classic Salted",
        "name_hi": "पारले मोनाको क्लासिक सॉल्टेड बिस्किट",
        "category_slug": "biscuits-bakery",
        "brand": "Parle",
        "is_loose": False,
        "description": "हलकी खारट कुरकुरीत बिस्किटे. टोमॅटो आणि चीज टॉपिंगसाठी उत्तम.",
        "image_url": "/products/monaco.jpg",
        "variants": [
            {"unit_size": "₹10 Pack", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 120},
            {"unit_size": "₹30 Pack", "selling_price": 30.0, "mrp": 30.0, "stock_quantity": 60}
        ]
    },
    {
        "name": "Britannia Bourbon Sandwich",
        "name_hi": "ब्रिटानिया बॉर्बन चॉकलेट क्रीम बिस्किट",
        "category_slug": "biscuits-bakery",
        "brand": "Britannia",
        "is_loose": False,
        "description": "साखरेचे दाणे आणि भरपूर चॉकलेट क्रीम असलेले प्रसिद्ध सँडविच बिस्किट.",
        "image_url": "/products/bourbon.jpg",
        "variants": [
            {"unit_size": "₹10 Pack", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 100},
            {"unit_size": "₹30 Pack", "selling_price": 30.0, "mrp": 30.0, "stock_quantity": 60}
        ]
    },
    {
        "name": "Britannia Premium Toast / Rusk (Elaichi)",
        "name_hi": "ब्रिटानिया टोस्ट / रस्क (वेलची फ्लेव्हर)",
        "category_slug": "biscuits-bakery",
        "brand": "Britannia",
        "is_loose": False,
        "description": "सकाळच्या चहासाठी अतिशय कुरकुरीत गव्हाचा वेलची टोस्ट.",
        "image_url": "/products/britannia-toast.jpg",
        "variants": [
            {"unit_size": "200g Pack", "selling_price": 35.0, "mrp": 40.0, "stock_quantity": 60},
            {"unit_size": "400g Family Pack", "selling_price": 65.0, "mrp": 75.0, "stock_quantity": 40}
        ]
    },

    # ==========================================
    # 11. COLD DRINKS & BOTTLED WATER (शीतपेये व मिनरल वॉटर)
    # ==========================================
    {
        "name": "Thums Up Toofani Carbonated Drink",
        "name_hi": "थम्स अप तुफानी (चिल्ड शीतपेय)",
        "category_slug": "cold-drinks",
        "brand": "Coca-Cola Co.",
        "is_loose": False,
        "description": "कडक आणि स्ट्राँग चवीचे थम्स अप. टेस्ट द थंडर.",
        "image_url": "/products/thums-up.jpg",
        "variants": [
            {"unit_size": "750ml Bottle", "selling_price": 40.0, "mrp": 40.0, "stock_quantity": 80},
            {"unit_size": "2L Party Bottle", "selling_price": 95.0, "mrp": 100.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Sprite Clear Lime Soft Drink",
        "name_hi": "स्प्राइट लेमन क्लिअर कोल्ड ड्रिंक",
        "category_slug": "cold-drinks",
        "brand": "Coca-Cola Co.",
        "is_loose": False,
        "description": "उन्हाळ्यात ताजेतवाने करणारे लिंबू-फ्लेव्हर क्लिअर शीतपेय.",
        "image_url": "/products/sprite.jpg",
        "variants": [
            {"unit_size": "750ml Bottle", "selling_price": 40.0, "mrp": 40.0, "stock_quantity": 80},
            {"unit_size": "2L Party Bottle", "selling_price": 95.0, "mrp": 100.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Coca-Cola Original Taste",
        "name_hi": "कोका-कोला ओरिजिनल टेस्ट",
        "category_slug": "cold-drinks",
        "brand": "Coca-Cola Co.",
        "is_loose": False,
        "description": "जगातील सर्वाधिक पसंतीचे ओरिजिनल टेस्ट कोका-कोला.",
        "image_url": "/products/coca-cola.jpg",
        "variants": [
            {"unit_size": "750ml Bottle", "selling_price": 40.0, "mrp": 40.0, "stock_quantity": 60},
            {"unit_size": "2L Party Bottle", "selling_price": 95.0, "mrp": 100.0, "stock_quantity": 25}
        ]
    },
    {
        "name": "Maaza Asli Mango Juice",
        "name_hi": "माझा अस्सल आंबा ज्यूस",
        "category_slug": "cold-drinks",
        "brand": "Coca-Cola Co.",
        "is_loose": False,
        "description": "अल्फोन्सो आंब्याच्या गरापासून बनवलेला घट्ट आणि गोड माझा रस.",
        "image_url": "/products/maaza.jpg",
        "variants": [
            {"unit_size": "600ml Bottle", "selling_price": 42.0, "mrp": 45.0, "stock_quantity": 60},
            {"unit_size": "1.2L Family Bottle", "selling_price": 78.0, "mrp": 85.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Bisleri Packaged Mineral Water",
        "name_hi": "बिसलेरी शुद्ध मिनरल वॉटर",
        "category_slug": "cold-drinks",
        "brand": "Bisleri",
        "is_loose": False,
        "description": "खनिजांनी समृद्ध १००% सुरक्षित आणि स्वच्छ बिसलेरी पिण्याचे पाणी.",
        "image_url": "/products/bisleri.jpg",
        "variants": [
            {"unit_size": "1L Bottle", "selling_price": 20.0, "mrp": 20.0, "stock_quantity": 120},
            {"unit_size": "20L Big Water Can", "selling_price": 90.0, "mrp": 100.0, "stock_quantity": 20}
        ]
    },

    # ==========================================
    # 12. CLEANING & DETERGENTS (स्वच्छता व डिटर्जंट)
    # ==========================================
    {
        "name": "Surf Excel Easy Wash Detergent Powder",
        "name_hi": "सर्फ एक्सेल ईझी वॉश पावडर",
        "category_slug": "household-cleaning",
        "brand": "Surf Excel",
        "is_loose": False,
        "description": "सर्फ एक्सेल ईझी वॉश. हट्टी डाग सहज काढणारी कपड्यांची वॉशिंग पावडर.",
        "image_url": "/products/surf-excel.jpg",
        "variants": [
            {"unit_size": "₹10 Pouch", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 150},
            {"unit_size": "500g Pkt", "selling_price": 75.0, "mrp": 82.0, "stock_quantity": 60},
            {"unit_size": "1kg Pkt", "selling_price": 140.0, "mrp": 155.0, "stock_quantity": 60},
            {"unit_size": "3kg Bag", "selling_price": 410.0, "mrp": 460.0, "stock_quantity": 25}
        ]
    },
    {
        "name": "Wheel 2-in-1 Detergent Powder",
        "name_hi": "व्हील २-इन-१ लेमन व चमेली वॉशिंग पावडर",
        "category_slug": "household-cleaning",
        "brand": "Wheel",
        "is_loose": False,
        "description": "लिंबू आणि चमेलीच्या सुगंधासह व्हील डिटर्जंट पावडर. बजेट फ्रेंडली.",
        "image_url": "/products/wheel-powder.jpg",
        "variants": [
            {"unit_size": "1kg Pkt", "selling_price": 68.0, "mrp": 75.0, "stock_quantity": 60}
        ]
    },
    {
        "name": "Rin Detergent Bar (Supreme Clean)",
        "name_hi": "रिन साबण (कपडे धुण्याचा पांढरा साबण)",
        "category_slug": "household-cleaning",
        "brand": "Rin",
        "is_loose": False,
        "description": "रिन डिटर्जंट बार. कपड्यांवर चकाकणारा पांढरेपणा देणारा विश्वासू साबण.",
        "image_url": "/products/rin-bar.jpg",
        "variants": [
            {"unit_size": "₹10 Small Bar", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 150},
            {"unit_size": "250g Regular Bar", "selling_price": 20.0, "mrp": 20.0, "stock_quantity": 120}
        ]
    },
    {
        "name": "Vim Lemon Dishwash Bar",
        "name_hi": "व्हिम लेमन भांडी घासण्याचा साबण",
        "category_slug": "household-cleaning",
        "brand": "Vim",
        "is_loose": False,
        "description": "१०० लिंबांची ताकद. तेलकट भांड्यांवरील तेल व दुर्गंधी एका क्षणात नाहीशी करणारा.",
        "image_url": "/products/vim-bar.jpg",
        "variants": [
            {"unit_size": "₹5 Mini Bar", "selling_price": 5.0, "mrp": 5.0, "stock_quantity": 200},
            {"unit_size": "₹10 Bar", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 150},
            {"unit_size": "300g Big Bar", "selling_price": 25.0, "mrp": 26.0, "stock_quantity": 80}
        ]
    },
    {
        "name": "Harpic Power Plus Toilet Cleaner",
        "name_hi": "हार्पिक पॉवर प्लस टॉयलेट क्लिनर",
        "category_slug": "household-cleaning",
        "brand": "Harpic",
        "is_loose": False,
        "description": "हार्पिक १०X डाग काढणारा जंतुनाशक टॉयलेट क्लिनर.",
        "image_url": "/products/harpic.jpg",
        "variants": [
            {"unit_size": "500ml Bottle", "selling_price": 98.0, "mrp": 108.0, "stock_quantity": 50},
            {"unit_size": "1L Bottle", "selling_price": 185.0, "mrp": 205.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Lizol Disinfectant Floor Cleaner (Pine)",
        "name_hi": "लायझॉल फरशी पुसण्याचे जंतुनाशक लिक्विड",
        "category_slug": "household-cleaning",
        "brand": "Lizol",
        "is_loose": False,
        "description": "९९.९% जंतूंचा खात्मा करणारे आणि घरात सुगंध पसरवणारे फरशी क्लिनर.",
        "image_url": "/products/lizol.jpg",
        "variants": [
            {"unit_size": "500ml Bottle", "selling_price": 95.0, "mrp": 105.0, "stock_quantity": 40},
            {"unit_size": "1L Bottle", "selling_price": 180.0, "mrp": 200.0, "stock_quantity": 25}
        ]
    },
    {
        "name": "Colin Glass Cleaner Spray",
        "name_hi": "कॉलिन काच क्लिनर स्प्रे",
        "category_slug": "household-cleaning",
        "brand": "Colin",
        "is_loose": False,
        "description": "काच, टेबल आणि आरशांना चमकावणारा कॉलिन स्प्रे.",
        "image_url": "/products/colin.jpg",
        "variants": [
            {"unit_size": "500ml Spray", "selling_price": 95.0, "mrp": 105.0, "stock_quantity": 35}
        ]
    },

    # ==========================================
    # 13. PERSONAL CARE & POOJA (पर्सनल केअर व पूजा साहित्य)
    # ==========================================
    {
        "name": "Dettol Original Bathing Soap",
        "name_hi": "डेटॉल ओरिजिनल आंघोळीचा साबण",
        "category_slug": "pooja-samagri",
        "brand": "Dettol",
        "is_loose": False,
        "description": "डेटॉल १००% जंतू संरक्षण देणारा संपूर्ण कुटुंबाचा आवडता साबण.",
        "image_url": "/products/dettol-soap.jpg",
        "variants": [
            {"unit_size": "₹10 Small Bar", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 150},
            {"unit_size": "75g Bar", "selling_price": 40.0, "mrp": 42.0, "stock_quantity": 80},
            {"unit_size": "Pack of 4 (75g each)", "selling_price": 155.0, "mrp": 168.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Lifebuoy Total Germ Protection Soap",
        "name_hi": "लाईफबॉय टोटल साबण (जंतू संरक्षण)",
        "category_slug": "pooja-samagri",
        "brand": "Lifebuoy",
        "is_loose": False,
        "description": "लाईफबॉय १००% जंतूनाशक साबण. रोजच्या स्वच्छतेसाठी.",
        "image_url": "/products/lifebuoy-soap.jpg",
        "variants": [
            {"unit_size": "₹10 Small Bar", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 150},
            {"unit_size": "100g Bar", "selling_price": 36.0, "mrp": 38.0, "stock_quantity": 80}
        ]
    },
    {
        "name": "Lux Soft Glow Rose Soap",
        "name_hi": "लक्स सॉफ्ट ग्लो गुलाबाचा साबण",
        "category_slug": "pooja-samagri",
        "brand": "Lux",
        "is_loose": False,
        "description": "गुलाबाचा सुगंध आणि व्हिटॅमिन ई सह मऊ त्वचेसाठी लक्स साबण.",
        "image_url": "/products/lux-soap.jpg",
        "variants": [
            {"unit_size": "₹10 Small Bar", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 150},
            {"unit_size": "100g Bar", "selling_price": 38.0, "mrp": 40.0, "stock_quantity": 80}
        ]
    },
    {
        "name": "Parachute 100% Pure Coconut Hair Oil",
        "name_hi": "पॅराशूट १००% शुद्ध खोबरेल तेल",
        "category_slug": "pooja-samagri",
        "brand": "Parachute",
        "is_loose": False,
        "description": "भारताचे नंबर १ खात्रीशीर पॅराशूट शुद्ध खोबरेल तेल. केसांच्या मुळांना पोषण.",
        "image_url": "/products/parachute-coconut-oil.jpg",
        "variants": [
            {"unit_size": "100ml Bottle", "selling_price": 42.0, "mrp": 45.0, "stock_quantity": 80},
            {"unit_size": "200ml Bottle", "selling_price": 82.0, "mrp": 90.0, "stock_quantity": 60},
            {"unit_size": "500ml Bottle", "selling_price": 195.0, "mrp": 215.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Bajaj Almond Drops Hair Oil",
        "name_hi": "बजाज बदाम ड्रॉप्स तेल (चिपचिपीत नसलेले)",
        "category_slug": "pooja-samagri",
        "brand": "Bajaj",
        "is_loose": False,
        "description": "६ पट व्हिटॅमिन ई सह हलके आणि चिपचिपीत नसलेले बदाम हेअर ऑईल.",
        "image_url": "/products/bajaj-almond-oil.jpg",
        "variants": [
            {"unit_size": "100ml Bottle", "selling_price": 68.0, "mrp": 75.0, "stock_quantity": 50},
            {"unit_size": "200ml Bottle", "selling_price": 132.0, "mrp": 145.0, "stock_quantity": 30}
        ]
    },
    {
        "name": "Colgate Strong Teeth Toothpaste",
        "name_hi": "कोलगेट स्ट्रॉंग टीथ (कॅल्शियम युक्त टूथपेस्ट)",
        "category_slug": "pooja-samagri",
        "brand": "Colgate",
        "is_loose": False,
        "description": "कोलगेट स्ट्रॉंग टीथ टूथपेस्ट. दात मजबूत आणि कीडमुक्त ठेवणारी.",
        "image_url": "/products/colgate-strong.jpg",
        "variants": [
            {"unit_size": "₹10 Tube", "selling_price": 10.0, "mrp": 10.0, "stock_quantity": 150},
            {"unit_size": "100g Tube", "selling_price": 58.0, "mrp": 65.0, "stock_quantity": 80},
            {"unit_size": "200g Tube", "selling_price": 108.0, "mrp": 120.0, "stock_quantity": 50}
        ]
    },
    {
        "name": "Colgate MaxFresh Peppermint Ice",
        "name_hi": "कोलगेट मॅक्सफ्रेश (कूलिंग क्रिस्टल्स टूथपेस्ट)",
        "category_slug": "pooja-samagri",
        "brand": "Colgate",
        "is_loose": False,
        "description": "कूलिंग क्रिस्टल्ससह १० पट ताजेतवाना श्वास देणारी टूथपेस्ट.",
        "image_url": "/products/colgate-maxfresh.jpg",
        "variants": [
            {"unit_size": "150g Tube", "selling_price": 105.0, "mrp": 115.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Dabur Red Ayurvedic Toothpaste",
        "name_hi": "डाबर लाल आयुर्वेदिक दंत मंजन/पेस्ट",
        "category_slug": "pooja-samagri",
        "brand": "Dabur",
        "is_loose": False,
        "description": "लवंग, पुदिना आणि तोमरच्या १३ आयुर्वेदिक घटकांनी युक्त दातदुखी दूर करणारी पेस्ट.",
        "image_url": "/products/dabur-red.jpg",
        "variants": [
            {"unit_size": "100g Tube", "selling_price": 60.0, "mrp": 65.0, "stock_quantity": 60},
            {"unit_size": "200g Tube", "selling_price": 115.0, "mrp": 125.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Patanjali Dant Kanti Natural",
        "name_hi": "पतंजली दंत कांति नॅचरल टूथपेस्ट",
        "category_slug": "pooja-samagri",
        "brand": "Patanjali",
        "is_loose": False,
        "description": "अकुरकरा, बबूल व कडुलिंबाच्या अर्काने बनलेली नैसर्गिक दंत कांति.",
        "image_url": "/products/dant-kanti.jpg",
        "variants": [
            {"unit_size": "100g Tube", "selling_price": 50.0, "mrp": 55.0, "stock_quantity": 60},
            {"unit_size": "200g Tube", "selling_price": 95.0, "mrp": 105.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Sensodyne Rapid Relief Toothpaste",
        "name_hi": "सेन्सॉडीन रॅपिड रिलीफ (सळसळणाऱ्या दातांसाठी)",
        "category_slug": "pooja-samagri",
        "brand": "Sensodyne",
        "is_loose": False,
        "description": "थंड-गरम खाताना दातांमध्ये होणारी सळसळ ६० सेकंदात थांबवणारी सेन्सॉडीन पेस्ट.",
        "image_url": "/products/sensodyne.jpg",
        "variants": [
            {"unit_size": "80g Tube", "selling_price": 175.0, "mrp": 195.0, "stock_quantity": 30}
        ]
    },
    # Pooja Samagri
    {
        "name": "Cycle Pure Agarbatti (Three-in-One)",
        "name_hi": "सायकल शुद्ध अगरबत्ती (थ्री-इन-वन)",
        "category_slug": "pooja-samagri",
        "brand": "Cycle Pure",
        "is_loose": False,
        "description": "सकाळ-संध्याकाळच्या देवपूजेसाठी शांत आणि प्रसन्न सुगंध देणारी सायकल अगरबत्ती.",
        "image_url": "/products/agarbatti.jpg",
        "variants": [
            {"unit_size": "₹50 Pack", "selling_price": 50.0, "mrp": 50.0, "stock_quantity": 80},
            {"unit_size": "₹100 Big Box", "selling_price": 95.0, "mrp": 100.0, "stock_quantity": 40}
        ]
    },
    {
        "name": "Mangaldeep Temple Agarbatti",
        "name_hi": "मंगलदीप मंदिर अगरबत्ती",
        "category_slug": "pooja-samagri",
        "brand": "Mangaldeep",
        "is_loose": False,
        "description": "आयटीसी मंगलदीप धूप-अगरबत्ती. दीर्घकाळ टिकणारा भक्तिमय सुगंध.",
        "image_url": "/products/agarbatti.jpg",
        "variants": [
            {"unit_size": "₹20 Regular Pack", "selling_price": 20.0, "mrp": 20.0, "stock_quantity": 100},
            {"unit_size": "₹50 Box", "selling_price": 50.0, "mrp": 50.0, "stock_quantity": 60}
        ]
    },
    {
        "name": "Mangalam Bhimseni Pure Camphor (Kapoor)",
        "name_hi": "मंगलम भीमसेनी शुद्ध कापूर (आरती स्पेशल)",
        "category_slug": "pooja-samagri",
        "brand": "Mangalam",
        "is_loose": False,
        "description": "१००% शुद्ध भीमसेनी कापूर. आरतीमध्ये काळा धूर न सोडणारा आणि हवेत विरघळणारा नैसर्गिक कापूर.",
        "image_url": "/products/kapoor.jpg",
        "variants": [
            {"unit_size": "50g Jar", "selling_price": 55.0, "mrp": 65.0, "stock_quantity": 70},
            {"unit_size": "100g Jar", "selling_price": 105.0, "mrp": 120.0, "stock_quantity": 50}
        ]
    },
    {
        "name": "Pure Cow Ghee Diya Phool Batti (Ready Wicks)",
        "name_hi": "शुद्ध गाईच्या तुपाची तयार वात (फुलवात डबी)",
        "category_slug": "pooja-samagri",
        "brand": "Pooja Staples",
        "is_loose": False,
        "description": "गाईच्या तुपात भिजवलेली तयार फुलवात. दिव्यामध्ये ठेवून लगेच प्रज्वलित करता येते.",
        "image_url": "/products/kapoor.jpg",
        "variants": [
            {"unit_size": "50 Pcs Box", "selling_price": 50.0, "mrp": 60.0, "stock_quantity": 60}
        ]
    },
    {
        "name": "Pooja Supari (Round Betel Nuts)",
        "name_hi": "पूजेची अखंड गोल सुपारी",
        "category_slug": "pooja-samagri",
        "brand": "Pooja Staples",
        "is_loose": True,
        "description": "सत्यनारायण पूजा आणि कलश स्थापनेसाठी गोल लाल पूजा सुपारी.",
        "image_url": "/products/kala-chana.jpg",
        "variants": [
            {"unit_size": "100g Pkt", "selling_price": 35.0, "mrp": 42.0, "stock_quantity": 50}
        ]
    }
]
