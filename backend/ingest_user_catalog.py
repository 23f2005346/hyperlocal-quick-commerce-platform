"""
Komal Mart (कोमल मार्ट) — Master Catalog Ingestion & Image Processing
Processes 162 high-quality product images from Products.images,
normalizes and enhances them to 600x600 square packshots on white canvas,
updates frontend/public/products & frontend/dist/products,
wipes old trial products from kirana.db, seeds genuine catalog with authentic
Mumbai retail kirana pricing, variants, and wholesale tiers.
Preserves user and admin accounts.
"""
import os
import sys
import sqlite3
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\AI_Engineering_Projects\kirana-store"
SRC_IMAGES_DIR = os.path.join(BASE_DIR, "Products.images")
PUB_DIR = os.path.join(BASE_DIR, "frontend", "public", "products")
DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist", "products")
DB_PATH = os.path.join(BASE_DIR, "backend", "kirana.db")

os.makedirs(PUB_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)

CATALOG_MAPPING = {
    # 1. Dals & Pulses
    "toor.daal.jpg": {
        "name": "Toor Dal / Arhar Dal (Gavran Unpolished Loose)",
        "name_hi": "तूर डाळ (गावरान मोकळी)",
        "slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "toor-daal-gavran.jpg",
        "description": "अस्सल गावरान अनपॉलिश्ड तूर डाळ. चवदार, लवकर शिजणारी आणि पचनास हलकी.",
        "variants": [
            {"unit_size": "500g", "price": 95.0, "mrp": 95.0, "stock": 100},
            {"unit_size": "1kg", "price": 190.0, "mrp": 190.0, "stock": 150},
            {"unit_size": "2kg", "price": 380.0, "mrp": 380.0, "stock": 50},
            {"unit_size": "5kg", "price": 930.0, "mrp": 950.0, "stock": 25}
        ],
        "tiered": [{"min_qty": 5, "tier_price": 186.0, "label": "🏷️ 5kg+ Wholesale Rate (₹186/kg)"}]
    },
    "chana.daal.png": {
        "name": "Chana Dal (Bengal Gram Split Loose)",
        "name_hi": "चना डाळ (हरभरा डाळ मोकळी)",
        "slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "chana-daal-loose.jpg",
        "description": "स्वच्छ आणि निवडलेली चना डाळ. पुरणपोळी आणि बेसनासाठी उत्तम दर्जा.",
        "variants": [
            {"unit_size": "500g", "price": 45.0, "mrp": 45.0, "stock": 100},
            {"unit_size": "1kg", "price": 90.0, "mrp": 90.0, "stock": 150},
            {"unit_size": "2kg", "price": 180.0, "mrp": 180.0, "stock": 50}
        ]
    },
    "moong.daal.jpg": {
        "name": "Moong Dal Dhuli (Yellow Split Loose)",
        "name_hi": "धुली मूंग डाळ (पिवळी मोकळी)",
        "slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "moong-daal-yellow.jpg",
        "description": "पिवळी मूंग डाळ. हलकी, पचायला सोपी, आजारी व्यक्ती व मुलांसाठी खिचडी स्पेशल.",
        "variants": [
            {"unit_size": "500g", "price": 60.0, "mrp": 60.0, "stock": 80},
            {"unit_size": "1kg", "price": 120.0, "mrp": 120.0, "stock": 100},
            {"unit_size": "2kg", "price": 240.0, "mrp": 240.0, "stock": 40}
        ]
    },
    "Moong-Dal-Chilka.jpg": {
        "name": "Moong Dal Chilka (Green Split Loose)",
        "name_hi": "मूंग डाळ छिलका (हिरवी टूक मोकळी)",
        "slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "moong-daal-chilka.jpg",
        "description": "हिरवी सालीची मूंग डाळ. फायबरयुक्त, पौष्टिक आणि खिचडी स्पेशल.",
        "variants": [
            {"unit_size": "500g", "price": 58.0, "mrp": 58.0, "stock": 60},
            {"unit_size": "1kg", "price": 115.0, "mrp": 115.0, "stock": 80}
        ]
    },
    "moong-sabut.jpg": {
        "name": "Moong Sabut (Whole Green Moong Loose)",
        "name_hi": "अखंड हिरवे मूग (गावरान मोकळे)",
        "slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "moong-sabut.jpg",
        "description": "मोड आणण्यासाठी आणि उसळीसाठी अस्सल गावरान हिरवे मूग.",
        "variants": [
            {"unit_size": "500g", "price": 55.0, "mrp": 55.0, "stock": 60},
            {"unit_size": "1kg", "price": 110.0, "mrp": 110.0, "stock": 80},
            {"unit_size": "2kg", "price": 220.0, "mrp": 220.0, "stock": 30}
        ]
    },
    "urad.daal.jpeg": {
        "name": "Urad Dal Dhuli (White Split Idli Dal Loose)",
        "name_hi": "धुली उडीद डाळ (सफेद - इडली/डोसा मोकळी)",
        "slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "urad-daal-dhuli.jpg",
        "description": "इडली, डोसा आणि मेदू वड्यासाठी पांढरी शुभ्र उडीद डाळ. उत्तम आंबवणे (fermentation).",
        "variants": [
            {"unit_size": "500g", "price": 65.0, "mrp": 65.0, "stock": 80},
            {"unit_size": "1kg", "price": 130.0, "mrp": 130.0, "stock": 100},
            {"unit_size": "2kg", "price": 260.0, "mrp": 260.0, "stock": 40}
        ]
    },
    "black-urad-dal.webp": {
        "name": "Kali Urad Dal (Split Black Gram Loose)",
        "name_hi": "काळी उडीद डाळ (छिलका मोकळी)",
        "slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "urad-daal-black.jpg",
        "description": "काळी सालीची उडीद डाळ. दाल मखनी आणि पौष्टिक डाळीसाठी उत्तम.",
        "variants": [
            {"unit_size": "500g", "price": 60.0, "mrp": 60.0, "stock": 50},
            {"unit_size": "1kg", "price": 120.0, "mrp": 120.0, "stock": 70}
        ]
    },
    "masoor.daal.webp": {
        "name": "Masoor Dal Lal (Split Red Lentils Loose)",
        "name_hi": "लाल मसूर डाळ (मोकळी)",
        "slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "masoor-daal-red.jpg",
        "description": "लाल मसूर डाळ. झटपट शिजणारी आणि दैनंदिन जेवणासाठी चवदार.",
        "variants": [
            {"unit_size": "500g", "price": 45.0, "mrp": 45.0, "stock": 60},
            {"unit_size": "1kg", "price": 90.0, "mrp": 90.0, "stock": 80}
        ]
    },
    "akha.masoor.webp": {
        "name": "Akha Masoor (Whole Brown Lentils Loose)",
        "name_hi": "अख्खा मसूर (मोकळा उसळ स्पेशल)",
        "slug": "dals-pulses",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "akha-masoor.jpg",
        "description": "अख्खा तपकिरी मसूर. अस्सल कोल्हापुरी व मालवणी उसळीसाठी अप्रतिम.",
        "variants": [
            {"unit_size": "500g", "price": 45.0, "mrp": 45.0, "stock": 60},
            {"unit_size": "1kg", "price": 90.0, "mrp": 90.0, "stock": 80}
        ]
    },

    # 2. Atta, Flours & Whole Grains
    "atta.webp": {
        "name": "Chakki Fresh Whole Wheat Atta (Fresh Ground Loose)",
        "name_hi": "चक्की फ्रेश गव्हाचे पीठ (ताज्या चक्कीचे मोकळे)",
        "slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "chakki-atta-loose.jpg",
        "description": "१००% शुद्ध गव्हाचे ताजे दळलेले चक्की पीठ. मऊ लुसलुशीत पोळ्या होतात.",
        "variants": [
            {"unit_size": "1kg", "price": 38.0, "mrp": 38.0, "stock": 100},
            {"unit_size": "2kg", "price": 76.0, "mrp": 76.0, "stock": 80},
            {"unit_size": "5kg", "price": 190.0, "mrp": 190.0, "stock": 60},
            {"unit_size": "10kg", "price": 375.0, "mrp": 380.0, "stock": 30}
        ],
        "tiered": [{"min_qty": 10, "tier_price": 37.5, "label": "🏷️ 10kg+ Bulk Rate (₹37.50/kg)"}]
    },
    "aashirvaad.atta.jpg": {
        "name": "Aashirvaad Shudh Chakki Atta (5kg / 10kg)",
        "name_hi": "आशीर्वाद शुद्ध चक्की आटा (५ किलो / १० किलो)",
        "slug": "atta-flours",
        "brand": "Aashirvaad",
        "is_loose": False,
        "clean_filename": "aashirvaad-atta.jpg",
        "description": "आशीर्वाद १००% संपूर्ण गव्हाचे चक्की पीठ. नैसर्गिक फायबरयुक्त.",
        "variants": [
            {"unit_size": "5kg Bag", "price": 245.0, "mrp": 245.0, "stock": 30},
            {"unit_size": "10kg Bag", "price": 480.0, "mrp": 480.0, "stock": 20}
        ]
    },
    "fortune.atta.jpg": {
        "name": "Fortune Chakki Fresh Atta (5kg / 10kg)",
        "name_hi": "फॉर्च्युन चक्की फ्रेश आटा (५ किलो / १० किलो)",
        "slug": "atta-flours",
        "brand": "Fortune",
        "is_loose": False,
        "clean_filename": "fortune-atta.jpg",
        "description": "फॉर्च्युन चक्की फ्रेश आटा. पारंपरिक चक्की पद्धतीने दळलेले मऊ पोळ्यांचे पीठ.",
        "variants": [
            {"unit_size": "5kg Bag", "price": 230.0, "mrp": 230.0, "stock": 25},
            {"unit_size": "10kg Bag", "price": 450.0, "mrp": 450.0, "stock": 15}
        ]
    },
    "lokwan.wheat.jpg": {
        "name": "MP Lokwan Wheat Grain (Desi Gehu Loose)",
        "name_hi": "मध्य प्रदेश लोकवान गहू (मोकळा व ३० किलो बोरी)",
        "slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "mp-lokwan-wheat.jpg",
        "description": "मध्य प्रदेशचा अस्सल लोकवान गहू. मोठा टपोरा दाणा, गोडवा आणि चवदार पोळ्यांसाठी.",
        "variants": [
            {"unit_size": "1kg", "price": 42.0, "mrp": 42.0, "stock": 100},
            {"unit_size": "5kg", "price": 210.0, "mrp": 210.0, "stock": 80},
            {"unit_size": "10kg", "price": 420.0, "mrp": 420.0, "stock": 50},
            {"unit_size": "30kg Bori", "price": 1230.0, "mrp": 1260.0, "stock": 20}
        ],
        "tiered": [{"min_qty": 30, "tier_price": 41.0, "label": "🏷️ 30kg Bori Rate (₹41/kg)"}]
    },
    "wheat_lokvan.jpg": {
        "name": "MP Sharbati Premium Wheat Grain (Loose)",
        "name_hi": "मध्य प्रदेश शरबती प्रीमियम गहू (मोकळा व ३० किलो बोरी)",
        "slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "mp-sharbati-wheat.jpg",
        "description": "प्रीमियम सीहोर शरबती गहू. सोनेरी चकचकीत दाणा, सर्वाधिक मऊ पोळ्या आणि अप्रतिम चव.",
        "variants": [
            {"unit_size": "1kg", "price": 48.0, "mrp": 48.0, "stock": 80},
            {"unit_size": "5kg", "price": 240.0, "mrp": 240.0, "stock": 60},
            {"unit_size": "10kg", "price": 480.0, "mrp": 480.0, "stock": 40},
            {"unit_size": "30kg Bori", "price": 1410.0, "mrp": 1440.0, "stock": 15}
        ],
        "tiered": [{"min_qty": 30, "tier_price": 47.0, "label": "🏷️ 30kg Bori Rate (₹47/kg)"}]
    },
    "whole_wheat.webp": {
        "name": "Desi Gavran Whole Wheat Grain (Loose)",
        "name_hi": "देशी गावरान गहू (मोकळा व ३० किलो बोरी)",
        "slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "desi-gavran-wheat.jpg",
        "description": "अस्सल देशी गावरान गहू. नैसर्गिक, पौष्टिक आणि दैनंदिन दळणासाठी उत्कृष्ट निवड.",
        "variants": [
            {"unit_size": "1kg", "price": 40.0, "mrp": 40.0, "stock": 100},
            {"unit_size": "5kg", "price": 200.0, "mrp": 200.0, "stock": 80},
            {"unit_size": "10kg", "price": 400.0, "mrp": 400.0, "stock": 50},
            {"unit_size": "30kg Bori", "price": 1170.0, "mrp": 1200.0, "stock": 25}
        ],
        "tiered": [{"min_qty": 30, "tier_price": 39.0, "label": "🏷️ 30kg Bori Rate (₹39/kg)"}]
    },
    "maida.jpeg": {
        "name": "Premium Maida (Refined All-Purpose Flour Loose)",
        "name_hi": "प्रीमियम मैदा (मोकळा)",
        "slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "maida-loose.jpg",
        "description": "बारीक पांढरा शुभ्र मैदा. समोसा, भटुरे, केक व खारी-बिस्किटांसाठी उत्तम.",
        "variants": [
            {"unit_size": "500g", "price": 22.0, "mrp": 22.0, "stock": 60},
            {"unit_size": "1kg", "price": 44.0, "mrp": 44.0, "stock": 80}
        ]
    },
    "besan.jpg": {
        "name": "Pure Chana Dal Besan (Gram Flour Loose)",
        "name_hi": "शुद्ध हरभरा डाळीचे बेसन (मोकळे)",
        "slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "besan-loose.jpg",
        "description": "१००% शुद्ध हरभरा डाळीचे बारीक दळलेले ताजे बेसन. भजी, लाडू व पिठल्यासाठी.",
        "variants": [
            {"unit_size": "500g", "price": 45.0, "mrp": 45.0, "stock": 80},
            {"unit_size": "1kg", "price": 90.0, "mrp": 90.0, "stock": 100}
        ]
    },
    "loose-besan-flour.jpg": {
        "name": "Fresh Chakki Besan (Coarse Motu Besan Loose)",
        "name_hi": "ताज्या चक्कीचे जाडे बेसन (लाडू स्पेशल)",
        "slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "fresh-chakki-besan.jpg",
        "description": "चक्कीवर खास दळलेले दाणेदार बेसन. बेसन लाडू, ढोकळा व चकलीसाठी दाणेदार चव.",
        "variants": [
            {"unit_size": "500g", "price": 45.0, "mrp": 45.0, "stock": 60},
            {"unit_size": "1kg", "price": 90.0, "mrp": 90.0, "stock": 80}
        ]
    },
    "nimraj.besan.webp": {
        "name": "Nimraj Pure Chana Besan (500g Pack)",
        "name_hi": "निमराज शुद्ध चक्की बेसन (५०० ग्रॅम पॅक)",
        "slug": "atta-flours",
        "brand": "Nimraj",
        "is_loose": False,
        "clean_filename": "nimraj-besan-500g.jpg",
        "description": "निमराज ब्रँडेड सीलबंद चक्की फ्रेश चणा बेसन. हमखास स्वच्छता आणि गुणवत्ता.",
        "variants": [
            {"unit_size": "500g Pack", "price": 50.0, "mrp": 50.0, "stock": 40}
        ]
    },
    "rawa.webp": {
        "name": "Sooji / Rawa (Semolina Loose)",
        "name_hi": "सुजी / रवा (मोकळा)",
        "slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "sooji-rawa-loose.jpg",
        "description": "बारीक स्वच्छ रवा. शिरा, उपमा आणि रव्याचा डोसा बनवण्यासाठी ताजा.",
        "variants": [
            {"unit_size": "500g", "price": 22.0, "mrp": 22.0, "stock": 80},
            {"unit_size": "1kg", "price": 44.0, "mrp": 44.0, "stock": 100}
        ]
    },
    "rice.flour.jpg": {
        "name": "Fresh Rice Flour / Chawal Ka Atta (Loose)",
        "name_hi": "तांदळाचे पीठ (मोकळे घावणे/भाकरी स्पेशल)",
        "slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "rice-flour-loose.jpg",
        "description": "बारीक पांढरे तांदळाचे पीठ. मऊ तांदळाची भाकरी, घावणे व मोदकाची उकड यासाठी.",
        "variants": [
            {"unit_size": "500g", "price": 25.0, "mrp": 25.0, "stock": 60},
            {"unit_size": "1kg", "price": 50.0, "mrp": 50.0, "stock": 80}
        ]
    },
    "Jowar.webp": {
        "name": "Jowar Grain (White Sorghum Loose)",
        "name_hi": "शाळू ज्वारी अखंड (मोकळी व ३० किलो बोरी)",
        "slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "jowar-grain-loose.jpg",
        "description": "पांढरी शुभ्र शाळू ज्वारी. उत्तम पौष्टिक भाकरीसाठी चवदार दाणा.",
        "variants": [
            {"unit_size": "1kg", "price": 45.0, "mrp": 45.0, "stock": 80},
            {"unit_size": "5kg", "price": 225.0, "mrp": 225.0, "stock": 50},
            {"unit_size": "30kg Bori", "price": 1320.0, "mrp": 1350.0, "stock": 15}
        ]
    },
    "bajra.jpg": {
        "name": "Bajra Grain (Pearl Millet Loose)",
        "name_hi": "बाजरी अखंड (मोकळी व ३० किलो बोरी)",
        "slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "bajra-grain-loose.jpg",
        "description": "गावरान बाजरी. हिवाळा आणि वर्षभर उष्ण व पौष्टिक बाजरीच्या भाकरीसाठी.",
        "variants": [
            {"unit_size": "1kg", "price": 35.0, "mrp": 35.0, "stock": 80},
            {"unit_size": "5kg", "price": 175.0, "mrp": 175.0, "stock": 50},
            {"unit_size": "30kg Bori", "price": 1020.0, "mrp": 1050.0, "stock": 15}
        ]
    },
    "nachani.jpg": {
        "name": "Nachni Grain (Ragi / Finger Millet Loose)",
        "name_hi": "नाचणी अखंड (मोकळी पौष्टिक)",
        "slug": "atta-flours",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "nachni-ragi-loose.jpg",
        "description": "कॅल्शियम आणि आयर्नयुक्त लाल नाचणी. सत्त्व, भाकरी व लहान मुलांच्या पेजसाठी उत्तम.",
        "variants": [
            {"unit_size": "500g", "price": 25.0, "mrp": 25.0, "stock": 50},
            {"unit_size": "1kg", "price": 50.0, "mrp": 50.0, "stock": 60}
        ]
    },

    # 3. Rice & Mandi Staples
    "kolam_rice.jpg": {
        "name": "Wada Kolam Rice (Daily Mandi Loose Rice)",
        "name_hi": "वाडा कोलम तांदूळ (मोकळा व ३० किलो बोरी)",
        "slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "wada-kolam-rice.jpg",
        "description": "मुंबईकरांचा आवडता वाडा कोलम तांदूळ. मऊ, सुटसुटीत आणि रोजच्या जेवणासाठी चवदार.",
        "variants": [
            {"unit_size": "1kg", "price": 62.0, "mrp": 62.0, "stock": 150},
            {"unit_size": "5kg", "price": 310.0, "mrp": 310.0, "stock": 100},
            {"unit_size": "10kg", "price": 620.0, "mrp": 620.0, "stock": 60},
            {"unit_size": "30kg Bori", "price": 1800.0, "mrp": 1860.0, "stock": 25}
        ],
        "tiered": [{"min_qty": 30, "tier_price": 60.0, "label": "🏷️ 30kg Bori Rate (₹60/kg)"}]
    },
    "basmati.rice.jpeg": {
        "name": "Premium Long Grain Basmati Rice (Loose)",
        "name_hi": "प्रीमियम बासमती तांदूळ (अखंड लांब दाणा मोकळा)",
        "slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "basmati-rice-long.jpg",
        "description": "सुवासिक लांब दाण्याचा अस्सल बासमती तांदूळ. पुलाव, बिर्याणी व सणासुदीच्या जेवणासाठी.",
        "variants": [
            {"unit_size": "1kg", "price": 120.0, "mrp": 120.0, "stock": 80},
            {"unit_size": "5kg", "price": 600.0, "mrp": 600.0, "stock": 40}
        ]
    },
    "BASMATI-TUKDA.webp": {
        "name": "Basmati Rice Tukda / Tibar (Mandi Loose)",
        "name_hi": "बासमती तुकडा तांदूळ (मोकळा सुगंधित)",
        "slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "basmati-tukda-rice.jpg",
        "description": "किफायतशीर बासमती तुकडा. अप्रतिम सुगंध आणि रोजच्या स्वादिष्ट भातासाठी उत्तम.",
        "variants": [
            {"unit_size": "1kg", "price": 65.0, "mrp": 65.0, "stock": 100},
            {"unit_size": "5kg", "price": 325.0, "mrp": 325.0, "stock": 60},
            {"unit_size": "10kg", "price": 650.0, "mrp": 650.0, "stock": 30}
        ]
    },
    "thick.poha.jpg": {
        "name": "Thick Poha / Jada Poha for Kanda Poha (Loose)",
        "name_hi": "जाडा पोहा (कांदा पोहा स्पेशल मोकळा)",
        "slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "thick-jada-poha.jpg",
        "description": "मध्य प्रदेश स्पेशल जाडा पोहा. सकाळी गरमागरम आणि मऊ कांदा पोहे बनवण्यासाठी उत्तम.",
        "variants": [
            {"unit_size": "500g", "price": 25.0, "mrp": 25.0, "stock": 80},
            {"unit_size": "1kg", "price": 50.0, "mrp": 50.0, "stock": 100}
        ]
    },
    "thin.poha.jpg": {
        "name": "Thin Poha / Patla Poha for Chivda (Loose)",
        "name_hi": "पातळ पोहा (कुरकुरीत चिवडा स्पेशल मोकळा)",
        "slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "thin-patla-poha.jpg",
        "description": "बारीक कागदी पातळ पोहा. दिवाळी व घरगुती कुरकुरीत भाजका चिवडा बनवण्यासाठी.",
        "variants": [
            {"unit_size": "500g", "price": 28.0, "mrp": 28.0, "stock": 60},
            {"unit_size": "1kg", "price": 55.0, "mrp": 55.0, "stock": 80}
        ]
    },
    "sabudana.jpg": {
        "name": "Nylon Sabudana / Sago Pearls (Loose)",
        "name_hi": "नायलॉन साबुदाणा (उपवास स्पेशल मोकळा)",
        "slug": "rice-grains",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "sabudana-sago.jpg",
        "description": "मोतीसारखा चकचकीत साबुदाणा. उपवासाची मोकळी खिचडी आणि कुरकुरीत वड्यासाठी.",
        "variants": [
            {"unit_size": "250g", "price": 20.0, "mrp": 20.0, "stock": 80},
            {"unit_size": "500g", "price": 38.0, "mrp": 38.0, "stock": 80},
            {"unit_size": "1kg", "price": 75.0, "mrp": 75.0, "stock": 100}
        ]
    },

    # 4. Beans & Legumes
    "chana.jpg": {
        "name": "Desi Kala Chana (Brown Chickpeas Loose)",
        "name_hi": "देशी काळा चणा (उसळ स्पेशल मोकळा)",
        "slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "desi-kala-chana.jpg",
        "description": "देशी काळा चणा. मोड आणून उसळ व काळा मसाला भाजीसाठी प्रथिनयुक्त.",
        "variants": [
            {"unit_size": "500g", "price": 42.0, "mrp": 42.0, "stock": 80},
            {"unit_size": "1kg", "price": 84.0, "mrp": 84.0, "stock": 100}
        ]
    },
    "kabuli.chana.jpg": {
        "name": "Kabuli Chana / White Chickpeas (Loose Mandi)",
        "name_hi": "काबुली चणा / छोले (मोठे पांढरे मोकळे)",
        "slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "kabuli-chana-chhole.jpg",
        "description": "मोठ्या आकाराचे पांढरे काबुली चणे. अमृतसर छोले-भटुरे व चाटसाठी उत्कृष्ट.",
        "variants": [
            {"unit_size": "500g", "price": 75.0, "mrp": 75.0, "stock": 60},
            {"unit_size": "1kg", "price": 150.0, "mrp": 150.0, "stock": 80}
        ]
    },
    "rajma.webp": {
        "name": "Kashmiri Red Rajma (Kidney Beans Loose)",
        "name_hi": "काश्मिरी लाल राजमा (मोकळा)",
        "slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "kashmiri-red-rajma.jpg",
        "description": "अस्सल लहान काश्मिरी लाल राजमा. चवदार रस्सा आणि राजमा-चावल स्पेशल.",
        "variants": [
            {"unit_size": "500g", "price": 75.0, "mrp": 75.0, "stock": 60},
            {"unit_size": "1kg", "price": 150.0, "mrp": 150.0, "stock": 80}
        ]
    },
    "safed.vatana.jpg": {
        "name": "Safed Vatana / White Dried Peas (Ragda Special)",
        "name_hi": "सफेद वाटाणा (रगडा पॅटिस स्पेशल मोकळा)",
        "slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "safed-vatana.jpg",
        "description": "निवडलेला पांढरा वाटाणा. मुंबईचा रगडा-पॅटिस आणि पाणीपुरीचा रगडा बनवण्यासाठी.",
        "variants": [
            {"unit_size": "500g", "price": 40.0, "mrp": 40.0, "stock": 80},
            {"unit_size": "1kg", "price": 80.0, "mrp": 80.0, "stock": 100}
        ]
    },
    "green.vatana.jpg": {
        "name": "Green Vatana / Dried Green Peas (Loose Mandi)",
        "name_hi": "हिरवा सुका वाटाणा (मोकळा उसळ स्पेशल)",
        "slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "green-vatana.jpg",
        "description": "गोडसर हिरवा वाटाणा. मिसळ, उसळ आणि भाजीसाठी चवदार.",
        "variants": [
            {"unit_size": "500g", "price": 55.0, "mrp": 55.0, "stock": 60},
            {"unit_size": "1kg", "price": 110.0, "mrp": 110.0, "stock": 80}
        ]
    },
    "black-vatana-peas.jpg": {
        "name": "Kala Vatana / Black Dried Peas (Mandi Loose)",
        "name_hi": "काळा वाटाणा (मालवणी उसळ व सांबार स्पेशल)",
        "slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "black-vatana.jpg",
        "description": "कोकण स्पेशल काळा वाटाणा. अस्सल मालवणी काळ्या वाटाण्याची उसळ व सांबारासाठी.",
        "variants": [
            {"unit_size": "500g", "price": 45.0, "mrp": 45.0, "stock": 50},
            {"unit_size": "1kg", "price": 90.0, "mrp": 90.0, "stock": 70}
        ]
    },
    "chavli.jpg": {
        "name": "Chavli / Black-Eyed Peas (Lobia Loose)",
        "name_hi": "चवळी (मोकळी उसळ स्पेशल)",
        "slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "chavli-lobia.jpg",
        "description": "पांढरी चवळी. मऊ शिजणारी आणि रसरशीत भाजीसाठी पौष्टिक कडधान्य.",
        "variants": [
            {"unit_size": "500g", "price": 45.0, "mrp": 45.0, "stock": 60},
            {"unit_size": "1kg", "price": 90.0, "mrp": 90.0, "stock": 80}
        ]
    },
    "matki.png": {
        "name": "Matki / Moth Beans Whole (Sprouting Lentils)",
        "name_hi": "मटकी अखंड (मोड स्पेशल मोकळी)",
        "slug": "beans-legumes",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "matki-beans.jpg",
        "description": "अस्सल गावरान मटकी. झणझणीत मिसळ आणि मोड आलेल्या पौष्टिक उसळीसाठी.",
        "variants": [
            {"unit_size": "500g", "price": 55.0, "mrp": 55.0, "stock": 60},
            {"unit_size": "1kg", "price": 110.0, "mrp": 110.0, "stock": 80}
        ]
    },

    # 5. Dry Fruits & Nuts
    "california.almonds.webp": {
        "name": "Premium California Almonds (Badam Giri Loose)",
        "name_hi": "कॅलिफोर्निया बदाम (मोकळे व ५ किलो घाऊक)",
        "slug": "dry-fruits-nuts",
        "brand": "Mandi Dryfruits",
        "is_loose": True,
        "clean_filename": "california-almonds.jpg",
        "description": "१००% गोड कॅलिफोर्निया बदाम गिरी. कुरकुरीत, तेलाने समृद्ध आणि बुद्धिवर्धक.",
        "variants": [
            {"unit_size": "50g Pouch", "price": 50.0, "mrp": 50.0, "stock": 100},
            {"unit_size": "250g", "price": 225.0, "mrp": 225.0, "stock": 80},
            {"unit_size": "500g", "price": 440.0, "mrp": 440.0, "stock": 50},
            {"unit_size": "1kg", "price": 860.0, "mrp": 860.0, "stock": 40}
        ],
        "tiered": [{"min_qty": 5, "tier_price": 810.0, "label": "🏷️ 5kg+ Wholesale Rate (₹810/kg)"}]
    },
    "cashew.jpg": {
        "name": "Premium Whole Cashews (Kaju W320 Loose)",
        "name_hi": "प्रीमियम काजू डब्ल्यू ३२० (मोकळा व ५ किलो घाऊक)",
        "slug": "dry-fruits-nuts",
        "brand": "Mandi Dryfruits",
        "is_loose": True,
        "clean_filename": "cashew-kaju-w320.jpg",
        "description": "प्रीमियम संपूर्ण काजू गर (W320). गोडसर, बिनकिडीचा आणि मिठायांसाठी उत्कृष्ट.",
        "variants": [
            {"unit_size": "50g Pouch", "price": 50.0, "mrp": 50.0, "stock": 100},
            {"unit_size": "250g", "price": 240.0, "mrp": 240.0, "stock": 80},
            {"unit_size": "500g", "price": 470.0, "mrp": 470.0, "stock": 50},
            {"unit_size": "1kg", "price": 920.0, "mrp": 920.0, "stock": 40}
        ],
        "tiered": [{"min_qty": 5, "tier_price": 870.0, "label": "🏷️ 5kg+ Wholesale Rate (₹870/kg)"}]
    },
    "kishmish.webp": {
        "name": "Indian Golden Raisins / Kishmish (Loose)",
        "name_hi": "गोल्डन बेदाणे / मनुका (मोकळे व ५ किलो घाऊक)",
        "slug": "dry-fruits-nuts",
        "brand": "Mandi Dryfruits",
        "is_loose": True,
        "clean_filename": "golden-kishmish.jpg",
        "description": "सांगली-तासगावचे अस्सल पिवळेधमक गोड बेदाणे. खीर, शिरा व आरोग्यासाठी उत्तम.",
        "variants": [
            {"unit_size": "100g", "price": 35.0, "mrp": 35.0, "stock": 80},
            {"unit_size": "250g", "price": 85.0, "mrp": 85.0, "stock": 60},
            {"unit_size": "500g", "price": 160.0, "mrp": 160.0, "stock": 40},
            {"unit_size": "1kg", "price": 310.0, "mrp": 310.0, "stock": 30}
        ],
        "tiered": [{"min_qty": 5, "tier_price": 280.0, "label": "🏷️ 5kg+ Wholesale Rate (₹280/kg)"}]
    },
    "makhana.jpg": {
        "name": "Phool Makhana / Lotus Seeds (Fox Nuts Loose)",
        "name_hi": "फुल मखाना / कमळ गट्टा (मोकळा)",
        "slug": "dry-fruits-nuts",
        "brand": "Mandi Dryfruits",
        "is_loose": True,
        "clean_filename": "phool-makhana.jpg",
        "description": "बिहारचे पांढरे स्वच्छ फुल मखाना. तुपात भाजून खाण्यासाठी कॅल्शियमयुक्त हलका स्नॅक.",
        "variants": [
            {"unit_size": "100g", "price": 95.0, "mrp": 95.0, "stock": 60},
            {"unit_size": "250g", "price": 235.0, "mrp": 235.0, "stock": 40},
            {"unit_size": "500g", "price": 460.0, "mrp": 460.0, "stock": 25},
            {"unit_size": "1kg", "price": 900.0, "mrp": 900.0, "stock": 20}
        ]
    },
    "dry.coconut.jpg": {
        "name": "Sukha Khobra / Dry Coconut Copra (Whole Loose)",
        "name_hi": "सुके खोबरे / वाटी (मोकळे व १ किलो)",
        "slug": "dry-fruits-nuts",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "sukha-khobra-copra.jpg",
        "description": "गोडसर तेलाने भरलेली सुक्या खोबऱ्याची वाटी. मसाला वाटण व मोदकाच्या सारणासाठी.",
        "variants": [
            {"unit_size": "250g", "price": 65.0, "mrp": 65.0, "stock": 80},
            {"unit_size": "500g", "price": 130.0, "mrp": 130.0, "stock": 60},
            {"unit_size": "1kg", "price": 250.0, "mrp": 250.0, "stock": 40}
        ]
    },
    "dry.dates.jpg": {
        "name": "Kharik / Dry Dates (Loose Yellow/Black)",
        "name_hi": "सुकी खारीक (पिवळी मोकळी)",
        "slug": "dry-fruits-nuts",
        "brand": "Mandi Dryfruits",
        "is_loose": True,
        "clean_filename": "kharik-dry-dates.jpg",
        "description": "गोड निवडलेली पिवळी खारीक. डिंकाचे लाडू, खारीक पावडर व आरोग्यासाठी पौष्टिक.",
        "variants": [
            {"unit_size": "250g", "price": 75.0, "mrp": 75.0, "stock": 60},
            {"unit_size": "500g", "price": 150.0, "mrp": 150.0, "stock": 40},
            {"unit_size": "1kg", "price": 290.0, "mrp": 290.0, "stock": 30}
        ]
    },

    # 6. Edible Oils & Desi Ghee
    "fortune.oil.1L.jpg": {
        "name": "Fortune Sunlite Refined Sunflower Oil (1L Pouch)",
        "name_hi": "फॉर्च्युन सनलाईट सूर्यफूल तेल (१ लिटर पाउच)",
        "slug": "oils-ghee",
        "brand": "Fortune",
        "is_loose": False,
        "clean_filename": "fortune-sunflower-oil-1l.jpg",
        "description": "फॉर्च्युन सनलाईट रिफाइंड सूर्यफूल तेल. हलके, पचायला सोपे आणि व्हिटॅमिनयुक्त.",
        "variants": [
            {"unit_size": "1L Pouch", "price": 145.0, "mrp": 145.0, "stock": 50}
        ]
    },
    "fortune.oil.5L.webp": {
        "name": "Fortune Sunlite Refined Sunflower Oil (5L Can / Dibba)",
        "name_hi": "फॉर्च्युन सूर्यफूल तेल (५ लिटर कॅन / डब्बा)",
        "slug": "oils-ghee",
        "brand": "Fortune",
        "is_loose": False,
        "clean_filename": "fortune-sunflower-oil-5l.jpg",
        "description": "फॉर्च्युन सनलाईट ५ लिटर जार/कॅन. कौटुंबिक वापरासाठी किफायतशीर आणि स्वच्छ.",
        "variants": [
            {"unit_size": "5L Can", "price": 710.0, "mrp": 710.0, "stock": 25}
        ]
    },
    "Fortune.oil.1L.mustard.oil.png": {
        "name": "Fortune Kachi Ghani Mustard Oil (1L Pouch)",
        "name_hi": "फॉर्च्युन कच्ची घानी मोहरीचे तेल (१ लिटर पाउच)",
        "slug": "oils-ghee",
        "brand": "Fortune",
        "is_loose": False,
        "clean_filename": "fortune-mustard-oil-1l.jpg",
        "description": "फॉर्च्युन अस्सल कच्ची घानी शुद्ध मोहरीचे तेल. तिखट झणझणीत स्वाद आणि शुद्धता.",
        "variants": [
            {"unit_size": "1L Pouch", "price": 155.0, "mrp": 155.0, "stock": 40}
        ]
    },
    "gemini.oil.1l.jpg": {
        "name": "Gemini Pure Refined Sunflower Oil (1L Pouch)",
        "name_hi": "जेमिनी शुद्ध सूर्यफूल तेल (१ लिटर पाउच)",
        "slug": "oils-ghee",
        "brand": "Gemini",
        "is_loose": False,
        "clean_filename": "gemini-sunflower-oil-1l.jpg",
        "description": "महाराष्ट्राचा नंबर १ विश्वास - जेमिनी शुद्ध सूर्यफूल तेल.",
        "variants": [
            {"unit_size": "1L Pouch", "price": 145.0, "mrp": 145.0, "stock": 50}
        ]
    },
    "gemini.oil.5L.webp": {
        "name": "Gemini Pure Refined Sunflower Oil (5L Can / Dibba)",
        "name_hi": "जेमिनी सूर्यफूल तेल (५ लिटर डब्बा / कॅन)",
        "slug": "oils-ghee",
        "brand": "Gemini",
        "is_loose": False,
        "clean_filename": "gemini-sunflower-oil-5l.jpg",
        "description": "जेमिनी शुद्ध सूर्यफूल तेल ५ लिटर फॅमिली पॅक कॅन.",
        "variants": [
            {"unit_size": "5L Dibba", "price": 710.0, "mrp": 710.0, "stock": 25}
        ]
    },
    "1l-sun-white-refined-sunflower-oil.jpg": {
        "name": "Sun White Refined Sunflower Oil (1L Pouch)",
        "name_hi": "सन व्हाईट सूर्यफूल तेल (१ लिटर पाउच)",
        "slug": "oils-ghee",
        "brand": "Sun White",
        "is_loose": False,
        "clean_filename": "sun-white-sunflower-oil-1l.jpg",
        "description": "सन व्हाईट रिफाइंड सूर्यफूल तेल. खिशाला परवडणारे आणि शुद्ध स्वयंपाकाचे तेल.",
        "variants": [
            {"unit_size": "1L Pouch", "price": 135.0, "mrp": 135.0, "stock": 40}
        ]
    },
    "priya-sunflower-oil.jpg": {
        "name": "Priya Gold Refined Sunflower Oil (1L Pouch)",
        "name_hi": "प्रिया गोल्ड सूर्यफूल तेल (१ लिटर पाउच)",
        "slug": "oils-ghee",
        "brand": "Priya",
        "is_loose": False,
        "clean_filename": "priya-sunflower-oil-1l.jpg",
        "description": "प्रिया गोल्ड रिफाइंड सूर्यफूल तेल. दैनंदिन स्वयंपाक व तळणासाठी उत्तम.",
        "variants": [
            {"unit_size": "1L Pouch", "price": 135.0, "mrp": 135.0, "stock": 40}
        ]
    },
    "sunpure.kachi.ghani.1L.jpg": {
        "name": "Sunpure Kachi Ghani Mustard Oil (1L Pouch)",
        "name_hi": "सनप्युअर कच्ची घानी मोहरीचे तेल (१ लिटर पाउच)",
        "slug": "oils-ghee",
        "brand": "Sunpure",
        "is_loose": False,
        "clean_filename": "sunpure-mustard-oil-1l.jpg",
        "description": "सनप्युअर कच्ची घानी शुद्ध मोहरीचे तेल. पारंपरिक घाणी पद्धतीने काढलेले.",
        "variants": [
            {"unit_size": "1L Pouch", "price": 150.0, "mrp": 150.0, "stock": 35}
        ]
    },
    "engine.kachi,ghani,mustard.oil.jpg": {
        "name": "Engine Brand Kachi Ghani Mustard Oil (1L Bottle)",
        "name_hi": "इंजिन ब्रँड कच्ची घानी मोहरीचे तेल (१ लिटर बाटली)",
        "slug": "oils-ghee",
        "brand": "Engine Brand",
        "is_loose": False,
        "clean_filename": "engine-mustard-oil-1l.jpg",
        "description": "अस्सल आग्रा इंजिन ब्रँड मोहरीचे तेल. अतिशय तीव्र आणि पारंपरिक स्वाद.",
        "variants": [
            {"unit_size": "1L Bottle", "price": 175.0, "mrp": 175.0, "stock": 30}
        ]
    },
    "mastard.oil.jpg": {
        "name": "Pure Mustard Oil / Sarson Tel (Loose Mandi)",
        "name_hi": "शुद्ध मोहरीचे तेल (मोकळे १ लिटर / ५ लिटर)",
        "slug": "oils-ghee",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "pure-mustard-oil-loose.jpg",
        "description": "घाणीवर काढलेले शुद्ध मोहरीचे तेल. लोणचे आणि स्वयंपाकासाठी मोकळे तेल.",
        "variants": [
            {"unit_size": "1L Bottle", "price": 140.0, "mrp": 140.0, "stock": 40},
            {"unit_size": "5L Can", "price": 680.0, "mrp": 680.0, "stock": 15}
        ]
    },
    "palmolein.oil.jpg": {
        "name": "Refined Palmolein Cooking Oil (1L Pouch)",
        "name_hi": "पामोलिन तेल (१ लिटर पाउच तळण स्पेशल)",
        "slug": "oils-ghee",
        "brand": "Palmolein",
        "is_loose": False,
        "clean_filename": "palmolein-oil-1l.jpg",
        "description": "रिफाइंड पामोलिन तेल. भजी, वडे व फरसाण तळण्यासाठी उत्तम आणि किफायतशीर.",
        "variants": [
            {"unit_size": "1L Pouch", "price": 110.0, "mrp": 110.0, "stock": 50}
        ]
    },
    "Gowardha.ghee.200ml.jpg": {
        "name": "Gowardhan Pure Cow Ghee (200ml Pouch)",
        "name_hi": "गोवर्धन शुद्ध गायीचे तूप (२०० मिली पाउच)",
        "slug": "oils-ghee",
        "brand": "Gowardhan",
        "is_loose": False,
        "clean_filename": "gowardhan-ghee-200ml.jpg",
        "description": "गोवर्धन १००% शुद्ध गायीचे तूप. सुवर्ण पिवळा रंग आणि अस्सल सुगंध.",
        "variants": [
            {"unit_size": "200ml Pouch", "price": 145.0, "mrp": 145.0, "stock": 30}
        ]
    },
    "gowardhan.ghee.500ml.jpg": {
        "name": "Gowardhan Pure Cow Ghee (500ml Jar)",
        "name_hi": "गोवर्धन शुद्ध गायीचे तूप (५०० मिली जार)",
        "slug": "oils-ghee",
        "brand": "Gowardhan",
        "is_loose": False,
        "clean_filename": "gowardhan-ghee-500ml.jpg",
        "description": "गोवर्धन शुद्ध गायीचे तूप ५०० मिली सोयीस्कर जार पॅक.",
        "variants": [
            {"unit_size": "500ml Jar", "price": 360.0, "mrp": 360.0, "stock": 25}
        ]
    },
    "gowardha.ghee.1kg.jpg": {
        "name": "Gowardhan Pure Cow Ghee (1kg Tin / Jar)",
        "name_hi": "गोवर्धन शुद्ध गायीचे तूप (१ किलो टिन / जार)",
        "slug": "oils-ghee",
        "brand": "Gowardhan",
        "is_loose": False,
        "clean_filename": "gowardhan-ghee-1kg.jpg",
        "description": "गोवर्धन शुद्ध गायीचे दाणेदार तूप १ किलो पॅक.",
        "variants": [
            {"unit_size": "1kg Tin", "price": 695.0, "mrp": 695.0, "stock": 20}
        ]
    },
    "amul.ghee.pouch.avif": {
        "name": "Amul Pure Ghee (1L Refill Pouch)",
        "name_hi": "अमूल शुद्ध तूप (१ लिटर रीफिल पाउच)",
        "slug": "oils-ghee",
        "brand": "Amul",
        "is_loose": False,
        "clean_filename": "amul-ghee-pouch-1l.jpg",
        "description": "अमूल १००% शुद्ध दाणेदार तूप. भारतातील घराघरांचा विश्वास.",
        "variants": [
            {"unit_size": "1L Pouch", "price": 610.0, "mrp": 610.0, "stock": 30}
        ]
    },
    "amul.ghee.jar.jpg": {
        "name": "Amul Pure Ghee (1L Tin / Jar)",
        "name_hi": "अमूल शुद्ध तूप (१ लिटर डबा / जार)",
        "slug": "oils-ghee",
        "brand": "Amul",
        "is_loose": False,
        "clean_filename": "amul-ghee-jar-1l.jpg",
        "description": "अमूल शुद्ध तूप १ लिटर धातूचा डबा/जार. साठवणीसाठी सुरक्षित आणि ताजे.",
        "variants": [
            {"unit_size": "1L Tin", "price": 630.0, "mrp": 630.0, "stock": 25}
        ]
    },
    "dalda.jpg": {
        "name": "Dalda Vanaspati Ghee (1kg Pouch)",
        "name_hi": "डालडा वनस्पती तूप (१ किलो पाउच)",
        "slug": "oils-ghee",
        "brand": "Dalda",
        "is_loose": False,
        "clean_filename": "dalda-vanaspati-1kg.jpg",
        "description": "अस्सल डालडा वनस्पती. खस्ता समोसे, कचोरी व दिवाळी फराळासाठी उत्तम.",
        "variants": [
            {"unit_size": "500g", "price": 75.0, "mrp": 75.0, "stock": 40},
            {"unit_size": "1kg", "price": 145.0, "mrp": 145.0, "stock": 35}
        ]
    },

    # 7. Spices & Salt (Masale)
    "Everest-Garam-Masala-100gm.jpg": {
        "name": "Everest Garam Masala (100g Box)",
        "name_hi": "एव्हरेस्ट गरम मसाला (१०० ग्रॅम बॉक्स)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-garam-masala-100g.jpg",
        "description": "एव्हरेस्ट गरम मसाला. १३ मसाल्यांचे परिपूर्ण मिश्रण जेवणाचा स्वाद द्विगुणित करते.",
        "variants": [
            {"unit_size": "100g Box", "price": 92.0, "mrp": 92.0, "stock": 60}
        ]
    },
    "everest-garam-masala.5Rs.jpg": {
        "name": "Everest Garam Masala (₹5 Pouch)",
        "name_hi": "एव्हरेस्ट गरम मसाला (५ रुपये पुडी)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-garam-masala-5rs.jpg",
        "description": "एव्हरेस्ट गरम मसाला ५ रुपयांची छोटी सोयीस्कर पुडी.",
        "variants": [
            {"unit_size": "₹5 Pouch", "price": 5.0, "mrp": 5.0, "stock": 200}
        ]
    },
    "Everest-Chicken-Masala-100gm.jpg": {
        "name": "Everest Chicken Masala (100g Box)",
        "name_hi": "एव्हरेस्ट चिकन मसाला (१०० ग्रॅम बॉक्स)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-chicken-masala-100g.jpg",
        "description": "एव्हरेस्ट चिकन मसाला. झणझणीत रस्सा आणि सुका चिकनसाठी अस्सल मसालेदार चव.",
        "variants": [
            {"unit_size": "100g Box", "price": 88.0, "mrp": 88.0, "stock": 50}
        ]
    },
    "everest.chicken.masala.5Rs.jpg": {
        "name": "Everest Chicken Masala (₹5 Pouch)",
        "name_hi": "एव्हरेस्ट चिकन मसाला (५ रुपये पुडी)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-chicken-masala-5rs.jpg",
        "description": "एव्हरेस्ट चिकन मसाला ५ रुपयांची छोटी पुडी.",
        "variants": [
            {"unit_size": "₹5 Pouch", "price": 5.0, "mrp": 5.0, "stock": 200}
        ]
    },
    "Everest-Pav-Bhaji-Masala-100gm.jpg": {
        "name": "Everest Pav Bhaji Masala (100g Box)",
        "name_hi": "एव्हरेस्ट पावभाजी मसाला (१०० ग्रॅम बॉक्स)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-pav-bhaji-masala-100g.jpg",
        "description": "मुंबई स्पेशल चौपाटी स्टाईल चवदार पावभाजी बनवण्यासाठी एव्हरेस्ट पावभाजी मसाला.",
        "variants": [
            {"unit_size": "100g Box", "price": 82.0, "mrp": 82.0, "stock": 60}
        ]
    },
    "Everest-Chhole-Masala-100gm.jpg": {
        "name": "Everest Chhole Masala (100g Box)",
        "name_hi": "एव्हरेस्ट छोले मसाला (१०० ग्रॅम बॉक्स)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-chhole-masala-100g.jpg",
        "description": "पंजाबी स्टाईल पिंडी छोले बनवण्यासाठी खास एव्हरेस्ट छोले मसाला.",
        "variants": [
            {"unit_size": "100g Box", "price": 82.0, "mrp": 82.0, "stock": 50}
        ]
    },
    "Everest-Sambhar-Masala-100gm.jpg": {
        "name": "Everest Sambhar Masala (100g Box)",
        "name_hi": "एव्हरेस्ट सांबार मसाला (१०० ग्रॅम बॉक्स)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-sambhar-masala-100g.jpg",
        "description": "अस्सल उडुपि स्टाईल सांबारासाठी सुवासिक एव्हरेस्ट सांबार मसाला.",
        "variants": [
            {"unit_size": "100g Box", "price": 80.0, "mrp": 80.0, "stock": 50}
        ]
    },
    "Everest-Kitchen-King-Masala-100gm.jpg": {
        "name": "Everest Kitchen King Masala (100g Box)",
        "name_hi": "एव्हरेस्ट किचन किंग मसाला (१०० ग्रॅम बॉक्स)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-kitchen-king-masala-100g.jpg",
        "description": "सर्व प्रकारच्या भाज्यांमध्ये शाही स्वाद आणणारा एव्हरेस्ट किचन किंग मसाला.",
        "variants": [
            {"unit_size": "100g Box", "price": 90.0, "mrp": 90.0, "stock": 60}
        ]
    },
    "Everest-Chaat-Masala-100gm.jpg": {
        "name": "Everest Chaat Masala (100g Box)",
        "name_hi": "एव्हरेस्ट चाट मसाला (१०० ग्रॅम बॉक्स)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-chaat-masala-100g.jpg",
        "description": "सलाड, फळे व चाटवर भुरभुरण्यासाठी आंबट-गोड-खारट चटपटीत चाट मसाला.",
        "variants": [
            {"unit_size": "100g Box", "price": 75.0, "mrp": 75.0, "stock": 50}
        ]
    },
    "Everest-Sabji-Masala-100gm.jpg": {
        "name": "Everest Sabji Masala (100g Box)",
        "name_hi": "एव्हरेस्ट भाजी मसाला (१०० ग्रॅम बॉक्स)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-sabji-masala-100g.jpg",
        "description": "रोजच्या साध्या भाज्यांना अप्रतिम चव देणारा एव्हरेस्ट भाजी मसाला.",
        "variants": [
            {"unit_size": "100g Box", "price": 65.0, "mrp": 65.0, "stock": 50}
        ]
    },
    "Everest-Shahi-Biryani-Masala-100gm.jpg": {
        "name": "Everest Shahi Biryani Masala (100g Box)",
        "name_hi": "एव्हरेस्ट शाही बिर्याणी मसाला (१०० ग्रॅम बॉक्स)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-shahi-biryani-masala-100g.jpg",
        "description": "दम बिर्याणीसाठी केशर व खड्या मसाल्यांचे शाही मिश्रण.",
        "variants": [
            {"unit_size": "100g Box", "price": 95.0, "mrp": 95.0, "stock": 40}
        ]
    },
    "Everest-Shahi-Paneer-Masala-100gm.jpg": {
        "name": "Everest Shahi Paneer Masala (100g Box)",
        "name_hi": "एव्हरेस्ट शाही पनीर मसाला (१०० ग्रॅम बॉक्स)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-shahi-paneer-masala-100g.jpg",
        "description": "हॉटेलसारखी शाही पनीर व पनीर बटर मसाला बनवण्यासाठी खास मसाला.",
        "variants": [
            {"unit_size": "100g Box", "price": 85.0, "mrp": 85.0, "stock": 40}
        ]
    },
    "Everest-Turmeric-Powder-jar.png": {
        "name": "Everest Turmeric Powder Jar (500g Jar)",
        "name_hi": "एव्हरेस्ट हळद पावडर जार (५०० ग्रॅम)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-turmeric-jar-500g.jpg",
        "description": "एव्हरेस्ट शुद्ध हळद पावडर ५०० ग्रॅम सोयीस्कर प्लास्टिक जार पॅक.",
        "variants": [
            {"unit_size": "500g Jar", "price": 180.0, "mrp": 180.0, "stock": 30}
        ]
    },
    "everest.haldi.powder.webp": {
        "name": "Everest Turmeric / Haldi Powder (100g Pack)",
        "name_hi": "एव्हरेस्ट हळद पावडर (१०० ग्रॅम / २०० ग्रॅम)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-haldi-pack-100g.jpg",
        "description": "उच्च करक्युमिनयुक्त एव्हरेस्ट शुद्ध हळद पावडर.",
        "variants": [
            {"unit_size": "100g Pack", "price": 38.0, "mrp": 38.0, "stock": 60},
            {"unit_size": "200g Pack", "price": 74.0, "mrp": 74.0, "stock": 40}
        ]
    },
    "suhana.haldi.powder.webp": {
        "name": "Suhana Turmeric Powder (100g Pack)",
        "name_hi": "सुहाना हळद पावडर (१०० ग्रॅम)",
        "slug": "spices-masalas",
        "brand": "Suhana",
        "is_loose": False,
        "clean_filename": "suhana-haldi-pack-100g.jpg",
        "description": "सुहाना अस्सल निवडलेली हळद पावडर.",
        "variants": [
            {"unit_size": "100g Pack", "price": 36.0, "mrp": 36.0, "stock": 50}
        ]
    },
    "100-pure-turmeric-powder-for-cooking.jpg": {
        "name": "Pure Haldi Powder (Loose Mandi Turmeric)",
        "name_hi": "शुद्ध हळद पावडर (मोकळी अस्सल राजापुरी)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "pure-haldi-powder-loose.jpg",
        "description": "राजापुरी हळकुंडातून दळलेली अस्सल पिवळीधमक हळद. कोणतीही भेसळ नाही.",
        "variants": [
            {"unit_size": "100g", "price": 25.0, "mrp": 25.0, "stock": 80},
            {"unit_size": "250g", "price": 60.0, "mrp": 60.0, "stock": 60},
            {"unit_size": "500g", "price": 120.0, "mrp": 120.0, "stock": 40}
        ]
    },
    "100-pure-and-organic-red-chilli-powder.jpg": {
        "name": "Pure Lal Mirch Powder (Loose Red Chilli Powder)",
        "name_hi": "शुद्ध लाल मिरची पावडर (तिखट मोकळी)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "pure-lal-mirch-loose.jpg",
        "description": "बेडगी व गुंटूर मिरचीचे अस्सल मिश्रण. सुरेख लाल रंग आणि मध्यम तिखटपणा.",
        "variants": [
            {"unit_size": "100g", "price": 35.0, "mrp": 35.0, "stock": 80},
            {"unit_size": "250g", "price": 85.0, "mrp": 85.0, "stock": 60},
            {"unit_size": "500g", "price": 170.0, "mrp": 170.0, "stock": 40},
            {"unit_size": "1kg", "price": 330.0, "mrp": 330.0, "stock": 30}
        ]
    },
    "Coriander-Powder.jpg": {
        "name": "Dhaniya Powder (Loose Coriander Powder)",
        "name_hi": "धने पावडर (मोकळी सुगंधित)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "dhaniya-powder-loose.jpg",
        "description": "हिरव्या ताज्या धन्यापासून बनवलेली ताजी धने पूड. रस्सा घट्ट व सुवासिक करण्यासाठी.",
        "variants": [
            {"unit_size": "100g", "price": 25.0, "mrp": 25.0, "stock": 80},
            {"unit_size": "250g", "price": 60.0, "mrp": 60.0, "stock": 60},
            {"unit_size": "500g", "price": 120.0, "mrp": 120.0, "stock": 40}
        ]
    },
    "cumin.jeera.jpg": {
        "name": "Sabut Jeera (Cumin Seeds Loose Mandi)",
        "name_hi": "अखंड जिरे (मोकळे व ₹१० पुडी)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "cumin-jeera-seeds.jpg",
        "description": "स्वच्छ आणि निवडलेले अखंड जिरे. फोडणी आणि जिराराइससाठी सुगंधित.",
        "variants": [
            {"unit_size": "₹10 Pouch", "price": 10.0, "mrp": 10.0, "stock": 150},
            {"unit_size": "100g", "price": 35.0, "mrp": 35.0, "stock": 80},
            {"unit_size": "250g", "price": 85.0, "mrp": 85.0, "stock": 60},
            {"unit_size": "500g", "price": 170.0, "mrp": 170.0, "stock": 40}
        ]
    },
    "rai-black.mustard.jpg": {
        "name": "Kali Rai (Black Mustard Seeds Loose)",
        "name_hi": "काळी मोहरी (मोकळी व ₹१० पुडी)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "black-mustard-rai.jpg",
        "description": "बारीक काळी मोहरी. खमंग फोडणी, सांबार व लोणच्यासाठी अतिशय आवश्यक.",
        "variants": [
            {"unit_size": "₹10 Pouch", "price": 10.0, "mrp": 10.0, "stock": 150},
            {"unit_size": "100g", "price": 15.0, "mrp": 15.0, "stock": 80},
            {"unit_size": "250g", "price": 35.0, "mrp": 35.0, "stock": 60},
            {"unit_size": "500g", "price": 70.0, "mrp": 70.0, "stock": 40}
        ]
    },
    "dhaniya-seed.jpg": {
        "name": "Sabut Dhaniya (Whole Coriander Seeds Loose)",
        "name_hi": "अखे धने (मोकळे फोडणी व मसाला स्पेशल)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "dhaniya-seeds-whole.jpg",
        "description": "सुवासिक अखंड धने. घरगुती गरम मसाला व भाज्यांच्या फोडणीसाठी.",
        "variants": [
            {"unit_size": "100g", "price": 18.0, "mrp": 18.0, "stock": 80},
            {"unit_size": "250g", "price": 42.0, "mrp": 42.0, "stock": 60},
            {"unit_size": "500g", "price": 80.0, "mrp": 80.0, "stock": 40}
        ]
    },
    "fennel.saunf.jpg": {
        "name": "Badi Saunf (Fennel Seeds Loose)",
        "name_hi": "बडीशेप (मोकळी मुखवास व मसाला)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "badi-saunf-fennel.jpg",
        "description": "गोडसर हिरवी बडीशेप. जेवणानंतर मुखवास म्हणून आणि मसाल्यांसाठी पाचक.",
        "variants": [
            {"unit_size": "100g", "price": 25.0, "mrp": 25.0, "stock": 80},
            {"unit_size": "250g", "price": 60.0, "mrp": 60.0, "stock": 60},
            {"unit_size": "500g", "price": 120.0, "mrp": 120.0, "stock": 40}
        ]
    },
    "kali.mirch.jpg": {
        "name": "Sabut Kali Mirch (Black Pepper Loose Mandi)",
        "name_hi": "काळी मिरी (अखंड मोकळी व ₹१० पुडी)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "kali-mirch-pepper.jpg",
        "description": "मलबारची अस्सल काळी मिरी. तिखट, सुवासिक आणि औषधी गुणांनी युक्त.",
        "variants": [
            {"unit_size": "₹10 Pouch", "price": 10.0, "mrp": 10.0, "stock": 150},
            {"unit_size": "50g", "price": 55.0, "mrp": 55.0, "stock": 60},
            {"unit_size": "100g", "price": 105.0, "mrp": 105.0, "stock": 50},
            {"unit_size": "250g", "price": 250.0, "mrp": 250.0, "stock": 30}
        ]
    },
    "dalchini.jpg": {
        "name": "Dalchini (Cinnamon Sticks Loose)",
        "name_hi": "दालचिनी (अखंड काड्या मोकळी व ₹१० पुडी)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "dalchini-cinnamon.jpg",
        "description": "गोडसर सुवासिक दालचिनीच्या काड्या. चहा, पुलाव व बिर्याणीसाठी उत्तम.",
        "variants": [
            {"unit_size": "₹10 Pouch", "price": 10.0, "mrp": 10.0, "stock": 150},
            {"unit_size": "50g", "price": 35.0, "mrp": 35.0, "stock": 60},
            {"unit_size": "100g", "price": 70.0, "mrp": 70.0, "stock": 40}
        ]
    },
    "cardomon.small.jpg": {
        "name": "Chhoti Elaichi (Green Cardamom Loose)",
        "name_hi": "हिरवी वेलची (मोकळी व ₹१०/₹२० पुडी)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "green-elaichi-small.jpg",
        "description": "सुवासिक हिरवी वेलची. चहा, शिरा, खीर आणि मोदकाच्या सारणासाठी खास.",
        "variants": [
            {"unit_size": "₹10 Pouch", "price": 10.0, "mrp": 10.0, "stock": 150},
            {"unit_size": "₹20 Pouch", "price": 20.0, "mrp": 20.0, "stock": 100},
            {"unit_size": "50g", "price": 190.0, "mrp": 190.0, "stock": 40},
            {"unit_size": "100g", "price": 370.0, "mrp": 370.0, "stock": 30}
        ]
    },
    "black.cardamom.jpg": {
        "name": "Badi Elaichi (Black Cardamom Loose)",
        "name_hi": "काळी मोठी वेलची (मोकळी व ₹१० पुडी)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "black-cardamom-badi.jpg",
        "description": "मसाल्याची मोठी काळी वेलची. बिर्याणी, पुलाव व छोलेसाठी विशिष्ट खमंग चव.",
        "variants": [
            {"unit_size": "₹10 Pouch", "price": 10.0, "mrp": 10.0, "stock": 150},
            {"unit_size": "50g", "price": 95.0, "mrp": 95.0, "stock": 40},
            {"unit_size": "100g", "price": 180.0, "mrp": 180.0, "stock": 30}
        ]
    },
    "starfool.jpg": {
        "name": "Star Anise / Chakra Phool (Loose Mandi)",
        "name_hi": "चक्रफूल (मोकळे व ₹१० पुडी)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "star-anise-chakra-phool.jpg",
        "description": "ताराफूल / चक्रफूल. शाही पुलाव आणि गरम मसाल्यासाठी आवश्यक खडा मसाला.",
        "variants": [
            {"unit_size": "₹10 Pouch", "price": 10.0, "mrp": 10.0, "stock": 150},
            {"unit_size": "50g", "price": 50.0, "mrp": 50.0, "stock": 50},
            {"unit_size": "100g", "price": 95.0, "mrp": 95.0, "stock": 30}
        ]
    },
    "kasuri.methi.everest.avif": {
        "name": "Everest Kasuri Methi (Fenugreek Leaves 25g Box)",
        "name_hi": "एव्हरेस्ट कसुरी मेथी (२५ ग्रॅम बॉक्स)",
        "slug": "spices-masalas",
        "brand": "Everest",
        "is_loose": False,
        "clean_filename": "everest-kasuri-methi-25g.jpg",
        "description": "एव्हरेस्ट वाळवलेली सुवासिक मेथी. पनीर भाजी व पराठ्यांवर चुरा करून घालण्यासाठी.",
        "variants": [
            {"unit_size": "25g Box", "price": 26.0, "mrp": 26.0, "stock": 50}
        ]
    },
    "hing.vandevi.jpg": {
        "name": "Vandevi Compounded Hing (Asafoetida 100g Tub)",
        "name_hi": "वानदेवी हिंग डबी (५० ग्रॅम / १०० ग्रॅम)",
        "slug": "spices-masalas",
        "brand": "Vandevi",
        "is_loose": False,
        "clean_filename": "vandevi-hing-tub.jpg",
        "description": "वानदेवी पिवळा हिंग. डाळ व भाजीच्या खमंग फोडणीसाठी आणि पचनासाठी सर्वोत्तम.",
        "variants": [
            {"unit_size": "50g Tub", "price": 45.0, "mrp": 45.0, "stock": 50},
            {"unit_size": "100g Tub", "price": 85.0, "mrp": 85.0, "stock": 40}
        ]
    },
    "methi-powder.jpg": {
        "name": "Methi Dana Powder (Fenugreek Seed Powder Loose)",
        "name_hi": "मेथी दाणा पावडर (मोकळी)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "methi-dana-powder.jpg",
        "description": "कडवट औषधी मेथी पावडर. पचन, मधुमेह नियंत्रण व लोणच्याच्या मसाल्यासाठी.",
        "variants": [
            {"unit_size": "100g", "price": 20.0, "mrp": 20.0, "stock": 60},
            {"unit_size": "250g", "price": 45.0, "mrp": 45.0, "stock": 40}
        ]
    },
    "Khada-Masala.jpg": {
        "name": "Sabut Khada Garam Masala Mix (Loose Mandi)",
        "name_hi": "अखंड खडा गरम मसाला मिक्स (मोकळा व पुडी)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "khada-garam-masala-mix.jpg",
        "description": "तमालपत्र, लवंग, मिरी, दालचिनी, वेलची व चक्रफूल यांचे परिपूर्ण खडा मसाला मिश्रण.",
        "variants": [
            {"unit_size": "₹10 Pouch", "price": 10.0, "mrp": 10.0, "stock": 150},
            {"unit_size": "₹20 Pouch", "price": 20.0, "mrp": 20.0, "stock": 100},
            {"unit_size": "100g", "price": 65.0, "mrp": 65.0, "stock": 60},
            {"unit_size": "250g", "price": 160.0, "mrp": 160.0, "stock": 40}
        ]
    },
    "tata.salt.jpg": {
        "name": "Tata Salt Vacuum Evaporated Iodized Salt (1kg Pack)",
        "name_hi": "टाटा मीठ (१ किलो पॅक देश का नमक)",
        "slug": "spices-masalas",
        "brand": "Tata Salt",
        "is_loose": False,
        "clean_filename": "tata-salt-1kg.jpg",
        "description": "देश का नमक टाटा सॉल्ट. व्हॅक्यूम बाष्पीभवन पद्धतीने शुद्ध केलेले आयोडीनयुक्त मीठ.",
        "variants": [
            {"unit_size": "1kg Pack", "price": 28.0, "mrp": 28.0, "stock": 100}
        ]
    },
    "black.salt.jpg": {
        "name": "Kala Namak (Black Salt Powder Loose)",
        "name_hi": "काळे मीठ पावडर (मोकळे पाचक)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "black-salt-kala-namak.jpg",
        "description": "पाचक काळे मीठ. रायता, ताक, पाणीपुरी व चाटमध्ये विशिष्ट चवीसाठी.",
        "variants": [
            {"unit_size": "200g", "price": 15.0, "mrp": 15.0, "stock": 80},
            {"unit_size": "500g", "price": 35.0, "mrp": 35.0, "stock": 60}
        ]
    },
    "himalayan.pink.salt.webp": {
        "name": "Himalayan Pink Rock Salt Powder (Sendha Namak 1kg Pouch)",
        "name_hi": "हिमालयन गुलाबी सैंधव मीठ (१ किलो पाउच)",
        "slug": "spices-masalas",
        "brand": "Himalayan",
        "is_loose": False,
        "clean_filename": "himalayan-pink-salt-1kg.jpg",
        "description": "नैसर्गिक खनिजांनी युक्त गुलाबी सैंधव मीठ. रक्तदाब नियंत्रण व निरोगी आहारासाठी उत्तम.",
        "variants": [
            {"unit_size": "1kg Pouch", "price": 85.0, "mrp": 85.0, "stock": 40}
        ]
    },
    "sedha.namak.jpg": {
        "name": "Sendha Namak Khadak (Rock Salt Crystals Loose)",
        "name_hi": "सैंधव मीठ खडक / खडे (मोकळे उपवास स्पेशल)",
        "slug": "spices-masalas",
        "brand": "Mandi Spices",
        "is_loose": True,
        "clean_filename": "sendha-namak-khadak.jpg",
        "description": "उपवासाचे अखंड खडे सैंधव मीठ. १००% शुद्ध आणि उपवासाच्या फराळासाठी आवश्यक.",
        "variants": [
            {"unit_size": "250g", "price": 20.0, "mrp": 20.0, "stock": 60},
            {"unit_size": "500g", "price": 38.0, "mrp": 38.0, "stock": 50},
            {"unit_size": "1kg", "price": 70.0, "mrp": 70.0, "stock": 40}
        ]
    },

    # 8. Sugar, Jaggery & Sweeteners
    "sugar-loose.jpg": {
        "name": "Madhur Clean Sugar (Loose Mandi)",
        "name_hi": "साखर स्वच्छ (मोकळी व ५ किलो घाऊक)",
        "slug": "sugar-jaggery",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "sugar-clean-loose.jpg",
        "description": "स्वच्छ पांढरी शुभ्र दाणेदार साखर. सल्फरमुक्त, चहा व गोड पदार्थांसाठी.",
        "variants": [
            {"unit_size": "1kg", "price": 44.0, "mrp": 44.0, "stock": 150},
            {"unit_size": "2kg", "price": 88.0, "mrp": 88.0, "stock": 80},
            {"unit_size": "5kg", "price": 218.0, "mrp": 220.0, "stock": 50}
        ],
        "tiered": [{"min_qty": 5, "tier_price": 43.6, "label": "🏷️ 5kg+ Bulk Rate (₹43.60/kg)"}]
    },
    "mishri.jpg": {
        "name": "Dhaga Mishri / Rock Sugar Crystals (Loose)",
        "name_hi": "धागा खडीसाखर (मोकळी शुद्ध)",
        "slug": "sugar-jaggery",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "dhaga-mishri-loose.jpg",
        "description": "अस्सल धाग्याची आयुर्वेदिक खडीसाखर. घशाची खवखव, बडीशेपसोबत मुखवास व पूजा साहित्यासाठी.",
        "variants": [
            {"unit_size": "250g", "price": 30.0, "mrp": 30.0, "stock": 60},
            {"unit_size": "500g", "price": 55.0, "mrp": 55.0, "stock": 50},
            {"unit_size": "1kg", "price": 105.0, "mrp": 105.0, "stock": 40}
        ]
    },
    "yellow.jaggery.jpg": {
        "name": "Desi Yellow Jaggery / Pila Gud (Loose Mandi)",
        "name_hi": "देशी पिवळा गूळ (मोकळा गोड)",
        "slug": "sugar-jaggery",
        "brand": "Mandi Staples",
        "is_loose": True,
        "clean_filename": "desi-yellow-jaggery.jpg",
        "description": "देशी पिवळा गूळ. मऊ, गोड आणि चहा, लाडू व पुरणासाठी उत्कृष्ट.",
        "variants": [
            {"unit_size": "500g", "price": 35.0, "mrp": 35.0, "stock": 80},
            {"unit_size": "1kg", "price": 68.0, "mrp": 68.0, "stock": 80}
        ]
    },
    "golden.jaggery.webp": {
        "name": "Kolhapuri Golden Jaggery Block (1kg Block)",
        "name_hi": "कोल्हापुरी गोल्डन गूळ ढेप (१ किलो)",
        "slug": "sugar-jaggery",
        "brand": "Kolhapuri",
        "is_loose": False,
        "clean_filename": "kolhapuri-golden-jaggery-1kg.jpg",
        "description": "अस्सल कोल्हापुरी शुद्ध गूळ ढेप. सेंद्रिय, नैसर्गिक गोडवा आणि चहा न फाटणारा गूळ.",
        "variants": [
            {"unit_size": "1kg Block", "price": 75.0, "mrp": 75.0, "stock": 50}
        ]
    },

    # 9. Tea, Coffee & Beverages
    "society.tea.jpg": {
        "name": "Society Tea Premium CTC Blend (250g / 500g)",
        "name_hi": "सोसायटी चहा (२५० ग्रॅम / ५०० ग्रॅम)",
        "slug": "tea-beverages",
        "brand": "Society Tea",
        "is_loose": False,
        "clean_filename": "society-tea-pack.jpg",
        "description": "सोसायटी प्रीमियम चहा. मुंबईकरांची सकाळ ताजीतवानी करणारा कडक चहा.",
        "variants": [
            {"unit_size": "250g Pack", "price": 150.0, "mrp": 150.0, "stock": 50},
            {"unit_size": "500g Pack", "price": 295.0, "mrp": 295.0, "stock": 30}
        ]
    },
    "Tata_Tea_Agni.webp": {
        "name": "Tata Tea Agni (250g / 500g)",
        "name_hi": "टाटा टी अग्नी (२५० ग्रॅम / ५०० ग्रॅम)",
        "slug": "tea-beverages",
        "brand": "Tata Tea",
        "is_loose": False,
        "clean_filename": "tata-tea-agni-pack.jpg",
        "description": "टाटा टी अग्नी. कडक चव, जास्त कप आणि खिशाला परवडणारा चहा.",
        "variants": [
            {"unit_size": "250g Pack", "price": 75.0, "mrp": 75.0, "stock": 60},
            {"unit_size": "500g Pack", "price": 145.0, "mrp": 145.0, "stock": 40}
        ]
    },
    "Red-Label-Natural-Care-Tea.jpg": {
        "name": "Brooke Bond Red Label Natural Care Tea (250g / 500g)",
        "name_hi": "रेड लेबल नॅचरल केअर चहा (२५० ग्रॅम / ५०० ग्रॅम)",
        "slug": "tea-beverages",
        "brand": "Brooke Bond",
        "is_loose": False,
        "clean_filename": "red-label-natural-care-pack.jpg",
        "description": "५ आयुर्वेदिक घटकांनी युक्त - तुळस, आलं, वेलची, अश्वगंधा व मुलेठी.",
        "variants": [
            {"unit_size": "250g Pack", "price": 160.0, "mrp": 160.0, "stock": 40},
            {"unit_size": "500g Pack", "price": 315.0, "mrp": 315.0, "stock": 25}
        ]
    },
    "nescafe.instant.coffee.1Rs.jpg": {
        "name": "Nescafé Classic Instant Coffee (₹1 / ₹2 Sachet)",
        "name_hi": "नेस्कॅफे क्लासिक इन्स्टंट कॉफी (१ रुपया / २ रुपये पुडी)",
        "slug": "tea-beverages",
        "brand": "Nescafe",
        "is_loose": False,
        "clean_filename": "nescafe-sachet-1rs.jpg",
        "description": "नेस्कॅफे क्लासिक इन्स्टंट कॉफी १ रुपयाची सोयीस्कर पुडी.",
        "variants": [
            {"unit_size": "₹1 Sachet", "price": 1.0, "mrp": 1.0, "stock": 250},
            {"unit_size": "₹2 Sachet", "price": 2.0, "mrp": 2.0, "stock": 200}
        ]
    },
    "nescafe.coffee.jar.jpg": {
        "name": "Nescafé Classic Instant Coffee (50g Glass Jar)",
        "name_hi": "नेस्कॅफे क्लासिक इन्स्टंट कॉफी (५० ग्रॅम काचेची बरणी)",
        "slug": "tea-beverages",
        "brand": "Nescafe",
        "is_loose": False,
        "clean_filename": "nescafe-glass-jar-50g.jpg",
        "description": "नेस्कॅफे क्लासिक १००% शुद्ध कॉफी ५० ग्रॅम प्रीमियम काचेची बरणी.",
        "variants": [
            {"unit_size": "50g Glass Jar", "price": 195.0, "mrp": 195.0, "stock": 30}
        ]
    },
    "Bru.instant.coffee.2Rs.jpg": {
        "name": "Bru Instant Coffee (₹2 Sachet)",
        "name_hi": "ब्रू इन्स्टंट कॉफी (२ रुपये पुडी)",
        "slug": "tea-beverages",
        "brand": "Bru",
        "is_loose": False,
        "clean_filename": "bru-instant-coffee-sachet.jpg",
        "description": "ब्रू इन्स्टंट कॉफी २ रुपयांची सुलभ पुडी. कॉफी व चिकोरीचे उत्तम मिश्रण.",
        "variants": [
            {"unit_size": "₹2 Sachet", "price": 2.0, "mrp": 2.0, "stock": 200}
        ]
    },

    # 10. Biscuits & Bakery
    "parle-g.jpg": {
        "name": "Parle-G Original Gluco Biscuits (₹10 Pack)",
        "name_hi": "पारले-जी ग्लुको बिस्किटे (१० रुपये पॅक)",
        "slug": "biscuits-bakery",
        "brand": "Parle",
        "is_loose": False,
        "clean_filename": "parle-g-biscuits.jpg",
        "description": "भारताचे लाडके पारले-जी बिस्किट. चहासोबत बुडवून खाण्यासाठी सर्वांचे आवडते.",
        "variants": [
            {"unit_size": "₹5 Mini Pack", "price": 5.0, "mrp": 5.0, "stock": 100},
            {"unit_size": "₹10 Pack", "price": 10.0, "mrp": 10.0, "stock": 100}
        ]
    },
    "good day biscuit.jpg": {
        "name": "Britannia Good Day Butter Cookies (₹10 / ₹30)",
        "name_hi": "ब्रिटानिया गुड डे बटर कुकीज (१० रुपये / ३० रुपये)",
        "slug": "biscuits-bakery",
        "brand": "Britannia",
        "is_loose": False,
        "clean_filename": "good-day-butter-cookies.jpg",
        "description": "ब्रिटानिया गुड डे रिच बटर कुकीज. प्रत्येक घासात बटरचा समृद्ध स्वाद.",
        "variants": [
            {"unit_size": "₹10 Pack", "price": 10.0, "mrp": 10.0, "stock": 80},
            {"unit_size": "₹30 Pack", "price": 30.0, "mrp": 30.0, "stock": 40}
        ]
    },
    "good day biscuit.cashew.jpg": {
        "name": "Britannia Good Day Cashew Cookies (₹10 / ₹30)",
        "name_hi": "ब्रिटानिया गुड डे काजू कुकीज (१० रुपये / ३० रुपये)",
        "slug": "biscuits-bakery",
        "brand": "Britannia",
        "is_loose": False,
        "clean_filename": "good-day-cashew-cookies.jpg",
        "description": "ब्रिटानिया गुड डे क्रंची काजू कुकीज. खऱ्याखुऱ्या काजूच्या तुकड्यांनी भरलेले.",
        "variants": [
            {"unit_size": "₹10 Pack", "price": 10.0, "mrp": 10.0, "stock": 80},
            {"unit_size": "₹30 Pack", "price": 30.0, "mrp": 30.0, "stock": 40}
        ]
    },
    "Oreo.10Rs biscuit.jpeg": {
        "name": "Cadbury Oreo Vanilla Cream Biscuits (₹10 Pack)",
        "name_hi": "कॅडबरी ओरियो व्हॅनिला क्रीम बिस्किटे (१० रुपये पॅक)",
        "slug": "biscuits-bakery",
        "brand": "Cadbury",
        "is_loose": False,
        "clean_filename": "cadbury-oreo-10rs.jpg",
        "description": "ओरियो क्रंची चॉकलेट कुकीज व्हॅनिला क्रीमसह. ट्विस्ट, लिक, डंक!",
        "variants": [
            {"unit_size": "₹10 Pack", "price": 10.0, "mrp": 10.0, "stock": 80},
            {"unit_size": "₹30 Pack", "price": 30.0, "mrp": 30.0, "stock": 40}
        ]
    },
    "lijjat.papad.jpg": {
        "name": "Shri Mahila Gruha Udyog Lijjat Udad Papad (200g Pack)",
        "name_hi": "लिज्जत उडीद पापड (२०० ग्रॅम पॅक)",
        "slug": "biscuits-bakery",
        "brand": "Lijjat",
        "is_loose": False,
        "clean_filename": "lijjat-udad-papad-200g.jpg",
        "description": "अस्सल लिज्जत उडीद मिरी पापड. भाजून किंवा तळून खाण्यासाठी खमंग कुरकुरीत.",
        "variants": [
            {"unit_size": "200g Pack", "price": 75.0, "mrp": 75.0, "stock": 50}
        ]
    },
    "400-special-mix-pickles-plastic-jar-2-pickle-shree-siddhivinayak.webp": {
        "name": "Shree Siddhivinayak Special Mixed Pickle (400g Jar)",
        "name_hi": "सिद्धिविनायक स्पेशल मिक्स लोणचे (४०० ग्रॅम)",
        "slug": "biscuits-bakery",
        "brand": "Siddhivinayak",
        "is_loose": False,
        "clean_filename": "siddhivinayak-mixed-pickle-400g.jpg",
        "description": "आंबा, लिंबू, गाजर व हिरव्या मिरचीचे चटपटीत तेलयुक्त पारंपरिक लोणचे.",
        "variants": [
            {"unit_size": "400g Jar", "price": 85.0, "mrp": 85.0, "stock": 40}
        ]
    },
    "Mango_Pickle_500gm1.webp": {
        "name": "Traditional Desi Mango Pickle (Aam Ka Achar 500g Jar)",
        "name_hi": "पारंपारिक गावरान आंब्याचे लोणचे (५०० ग्रॅम बरणी)",
        "slug": "biscuits-bakery",
        "brand": "Mandi Pickles",
        "is_loose": False,
        "clean_filename": "desi-mango-pickle-500g.jpg",
        "description": "राईच्या तेलातील आणि मेथीच्या मसाल्यातील अस्सल गावरान आंब्याचे लोणचे.",
        "variants": [
            {"unit_size": "500g Jar", "price": 95.0, "mrp": 95.0, "stock": 40}
        ]
    },
    "lemon.pickle.jpg": {
        "name": "Traditional Tangy Lemon Pickle (Nimbu Achar 500g Jar)",
        "name_hi": "पारंपारिक आंबट-गोड लिंबाचे लोणचे (५०० ग्रॅम बरणी)",
        "slug": "biscuits-bakery",
        "brand": "Mandi Pickles",
        "is_loose": False,
        "clean_filename": "desi-lemon-pickle-500g.jpg",
        "description": "कागदी लिंबाचे चवदार आणि पाचक पारंपरिक लोणचे.",
        "variants": [
            {"unit_size": "500g Jar", "price": 95.0, "mrp": 95.0, "stock": 40}
        ]
    },

    # 11. Cold Drinks & Bottled Water
    "Sprite.20rS.jpg": {
        "name": "Sprite Lemon Lime Cold Drink (250ml Pet Bottle)",
        "name_hi": "स्प्राइट शीतपेय (२५० मिली २० रुपये बाटली)",
        "slug": "cold-drinks",
        "brand": "Sprite",
        "is_loose": False,
        "clean_filename": "sprite-250ml-bottle.jpg",
        "description": "थंडगार रिफ्रेशिंग स्प्राइट लेमन-लाईम फ्लेवर. क्लिअर है!",
        "variants": [
            {"unit_size": "250ml Bottle", "price": 20.0, "mrp": 20.0, "stock": 60}
        ]
    },
    "coca-cola.20Rs.jpg": {
        "name": "Coca-Cola Soft Drink (250ml Pet Bottle)",
        "name_hi": "कोका-कोला शीतपेय (२५० मिली २० रुपये बाटली)",
        "slug": "cold-drinks",
        "brand": "Coca-Cola",
        "is_loose": False,
        "clean_filename": "coca-cola-250ml-bottle.jpg",
        "description": "अस्सल थंडा कोका-कोला २५० मिली चिल्ड पेट बॉटल.",
        "variants": [
            {"unit_size": "250ml Bottle", "price": 20.0, "mrp": 20.0, "stock": 60}
        ]
    },
    "Campa.10rs.jpg": {
        "name": "Campa Cola (200ml Pet Bottle)",
        "name_hi": "कंपा कोला शीतपेय (२०० मिली १० रुपये बाटली)",
        "slug": "cold-drinks",
        "brand": "Campa",
        "is_loose": False,
        "clean_filename": "campa-cola-200ml-bottle.jpg",
        "description": "द ग्रेट इंडियन टेस्ट - कंपा कोला १० रुपयांची चिल्ड बाटली.",
        "variants": [
            {"unit_size": "200ml Bottle", "price": 10.0, "mrp": 10.0, "stock": 80}
        ]
    },

    # 12. Cleaning & Detergents
    "Fena-Superwash-Plus-Detergent-soap.png": {
        "name": "Fena Superwash Plus Detergent Soap Bar",
        "name_hi": "फेना सुपरवॉश प्लस कपड्याचा साबण",
        "slug": "household-cleaning",
        "brand": "Fena",
        "is_loose": False,
        "clean_filename": "fena-superwash-bar.jpg",
        "description": "फेना सुपरवॉश कपड्याचा साबण. हट्टी मळ काढून पांढरे कपडे लखलखीत करतो.",
        "variants": [
            {"unit_size": "200g Bar", "price": 15.0, "mrp": 15.0, "stock": 80}
        ]
    },
    "Rin.10Rs..webp": {
        "name": "Rin Detergent Soap Bar (₹10 Bar)",
        "name_hi": "रिन डिटर्जंट बार (१० रुपये साबण)",
        "slug": "household-cleaning",
        "brand": "Rin",
        "is_loose": False,
        "clean_filename": "rin-detergent-bar-10rs.jpg",
        "description": "रिन बार. कपड्यांना देतो दुप्पट चमक आणि ताजेतवाने सुगंध.",
        "variants": [
            {"unit_size": "₹10 Bar", "price": 10.0, "mrp": 10.0, "stock": 100}
        ]
    },
    "wheel.soap.bar.jpg": {
        "name": "Active Wheel Green Lemon Detergent Bar",
        "name_hi": "अॅक्टिव्ह व्हील ग्रीन लेमन कपड्याचा साबण",
        "slug": "household-cleaning",
        "brand": "Wheel",
        "is_loose": False,
        "clean_filename": "wheel-lemon-soap-bar.jpg",
        "description": "व्हील ग्रीन लेमन डिटर्जंट बार. लिंबाच्या शक्तीने स्वच्छ कपडे.",
        "variants": [
            {"unit_size": "150g Bar", "price": 12.0, "mrp": 12.0, "stock": 80}
        ]
    },
    "wheel.1kg.powder.webp": {
        "name": "Active Wheel 2 in 1 Detergent Powder (1kg Pack)",
        "name_hi": "अॅक्टिव्ह व्हील २ इन १ वॉशिंग पावडर (१ किलो)",
        "slug": "household-cleaning",
        "brand": "Wheel",
        "is_loose": False,
        "clean_filename": "wheel-detergent-powder-1kg.jpg",
        "description": "अॅक्टिव्ह व्हील २ इन १ वॉशिंग पावडर. मळ काढते आणि कपड्यांना देते सुगंध.",
        "variants": [
            {"unit_size": "1kg Pack", "price": 72.0, "mrp": 72.0, "stock": 60}
        ]
    },
    "tide.soap.bar.jpg": {
        "name": "Tide Detergent Bar (150g Bar)",
        "name_hi": "टाईड डिटर्जंट बार (१५० ग्रॅम साबण)",
        "slug": "household-cleaning",
        "brand": "Tide",
        "is_loose": False,
        "clean_filename": "tide-detergent-bar.jpg",
        "description": "टाईड बार. कॉलर आणि कफचा मळ सहज काढणारा शक्तिशाली साबण.",
        "variants": [
            {"unit_size": "150g Bar", "price": 15.0, "mrp": 15.0, "stock": 80}
        ]
    },
    "tide.10Rs.pwder.jpg": {
        "name": "Tide Plus Extra Power Detergent Powder (₹10 Pouch)",
        "name_hi": "टाईड प्लस वॉशिंग पावडर (१० रुपये पुडी)",
        "slug": "household-cleaning",
        "brand": "Tide",
        "is_loose": False,
        "clean_filename": "tide-powder-pouch-10rs.jpg",
        "description": "टाईड प्लस एक्स्ट्रा पॉवर १० रुपयांची छोटी सोयीस्कर पुडी.",
        "variants": [
            {"unit_size": "₹10 Pouch", "price": 10.0, "mrp": 10.0, "stock": 150}
        ]
    },
    "tide.1kg.powder.webp": {
        "name": "Tide Plus Extra Power Detergent Powder (1kg Pack)",
        "name_hi": "टाईड प्लस एक्स्ट्रा पॉवर वॉशिंग पावडर (१ किलो)",
        "slug": "household-cleaning",
        "brand": "Tide",
        "is_loose": False,
        "clean_filename": "tide-powder-1kg.jpg",
        "description": "टाईड प्लस एक्स्ट्रा पॉवर १ किलो फॅमिली पॅक.",
        "variants": [
            {"unit_size": "1kg Pack", "price": 135.0, "mrp": 135.0, "stock": 50}
        ]
    },
    "surf.excel.10Rs.powder.jpg": {
        "name": "Surf Excel Quick Wash Detergent Powder (₹10 Pouch)",
        "name_hi": "सर्फ एक्सेल क्विक वॉश पावडर (१० रुपये पुडी)",
        "slug": "household-cleaning",
        "brand": "Surf Excel",
        "is_loose": False,
        "clean_filename": "surf-excel-pouch-10rs.jpg",
        "description": "सर्फ एक्सेल क्विक वॉश १० रुपयांची पुडी. दाग अच्छे हैं!",
        "variants": [
            {"unit_size": "₹10 Pouch", "price": 10.0, "mrp": 10.0, "stock": 150}
        ]
    },
    "surf.excel.1kg.powder.jpg": {
        "name": "Surf Excel Easy Wash Detergent Powder (1kg Pack)",
        "name_hi": "सर्फ एक्सेल इझी वॉश डिटर्जंट पावडर (१ किलो)",
        "slug": "household-cleaning",
        "brand": "Surf Excel",
        "is_loose": False,
        "clean_filename": "surf-excel-easy-wash-1kg.jpg",
        "description": "सर्फ एक्सेल इझी वॉश १ किलो. हट्टी डागांवर प्रभावी स्वच्छता.",
        "variants": [
            {"unit_size": "1kg Pack", "price": 150.0, "mrp": 150.0, "stock": 50}
        ]
    },
    "Surf.excel.matic.liquid.jpeg": {
        "name": "Surf Excel Matic Front & Top Load Liquid Detergent (1L Bottle)",
        "name_hi": "सर्फ एक्सेल मॅटिक लिक्विड डिटर्जंट (१ लिटर)",
        "slug": "household-cleaning",
        "brand": "Surf Excel",
        "is_loose": False,
        "clean_filename": "surf-excel-matic-liquid-1l.jpg",
        "description": "वॉशिंग मशीनसाठी खास सर्फ एक्सेल मॅटिक लिक्विड. मशीनमध्ये १००% विरघळते.",
        "variants": [
            {"unit_size": "500ml Bottle", "price": 130.0, "mrp": 130.0, "stock": 30},
            {"unit_size": "1L Bottle", "price": 240.0, "mrp": 240.0, "stock": 25}
        ]
    },
    "confort.puch.4Rs.jpg": {
        "name": "Comfort After Wash Fabric Conditioner (₹4 Pouch)",
        "name_hi": "कंफर्ट फॅब्रिक कंडिशनर (४ रुपये सॅशे)",
        "slug": "household-cleaning",
        "brand": "Comfort",
        "is_loose": False,
        "clean_filename": "comfort-conditioner-sachet-4rs.jpg",
        "description": "कपड्यांना मऊपणा आणि १४ दिवस टिकणारा सुवास देणारा कंफर्ट ४ रुपयांचा सॅशे.",
        "variants": [
            {"unit_size": "₹4 Pouch", "price": 4.0, "mrp": 4.0, "stock": 200}
        ]
    },
    "confort.blue.jpg": {
        "name": "Comfort Morning Fresh Fabric Conditioner Blue (860ml Bottle)",
        "name_hi": "कंफर्ट मॉर्निंग फ्रेश फॅब्रिक कंडिशनर (८६० मिली निळा)",
        "slug": "household-cleaning",
        "brand": "Comfort",
        "is_loose": False,
        "clean_filename": "comfort-morning-fresh-blue-860ml.jpg",
        "description": "कंफर्ट मॉर्निंग फ्रेश निळा ८६० मिली बाटली. कपड्यांचे धागे मऊ ठेवतो.",
        "variants": [
            {"unit_size": "220ml Bottle", "price": 60.0, "mrp": 60.0, "stock": 30},
            {"unit_size": "860ml Bottle", "price": 220.0, "mrp": 220.0, "stock": 20}
        ]
    },
    "confort.pink.jpg": {
        "name": "Comfort Lily Fresh Fabric Conditioner Pink (860ml Bottle)",
        "name_hi": "कंफर्ट लिली फ्रेश फॅब्रिक कंडिशनर (८६० मिली गुलाबी)",
        "slug": "household-cleaning",
        "brand": "Comfort",
        "is_loose": False,
        "clean_filename": "comfort-lily-fresh-pink-860ml.jpg",
        "description": "कंफर्ट लिली फ्रेश गुलाबी ८६० मिली बाटली. सुवासिक फुलांचा सुगंध.",
        "variants": [
            {"unit_size": "220ml Bottle", "price": 60.0, "mrp": 60.0, "stock": 30},
            {"unit_size": "860ml Bottle", "price": 220.0, "mrp": 220.0, "stock": 20}
        ]
    },
    "Vim.bar.5rs.jpg": {
        "name": "Vim Dishwash Bar with Lemon (₹5 Mini Bar)",
        "name_hi": "विम डिशवॉश बार (५ रुपये छोटा साबण)",
        "slug": "household-cleaning",
        "brand": "Vim",
        "is_loose": False,
        "clean_filename": "vim-dishwash-bar-5rs.jpg",
        "description": "विम डिशवॉश बार ५ रुपयांचा छोटा साबण. लिंबाच्या शक्तीने तेलकट भांडी स्वच्छ.",
        "variants": [
            {"unit_size": "₹5 Bar", "price": 5.0, "mrp": 5.0, "stock": 200}
        ]
    },
    "Vim.bar.10Rs.jpg": {
        "name": "Vim Dishwash Bar with Lemon (₹10 Bar)",
        "name_hi": "विम डिशवॉश बार (१० रुपये साबण)",
        "slug": "household-cleaning",
        "brand": "Vim",
        "is_loose": False,
        "clean_filename": "vim-dishwash-bar-10rs.jpg",
        "description": "विम डिशवॉश बार १० रुपयांचा लोकप्रिय साबण.",
        "variants": [
            {"unit_size": "₹10 Bar", "price": 10.0, "mrp": 10.0, "stock": 150}
        ]
    },
    "VimDishwashLiquidGel-Lemon120ml.webp": {
        "name": "Vim Dishwash Liquid Gel Lemon (120ml Bottle)",
        "name_hi": "विम डिशवॉश लिक्विड जेल (१२० मिली बाटली)",
        "slug": "household-cleaning",
        "brand": "Vim",
        "is_loose": False,
        "clean_filename": "vim-dishwash-gel-120ml.jpg",
        "description": "विम जेल लिंबू १२० मिली. फक्त १ चमचा विम जेल सिंकभर भांड्यांसाठी पुरेसा.",
        "variants": [
            {"unit_size": "120ml Bottle", "price": 30.0, "mrp": 30.0, "stock": 50}
        ]
    },
    "vim.liquid.bottle.jpg": {
        "name": "Vim Dishwash Liquid Gel Lemon (250ml / 500ml Bottle)",
        "name_hi": "विम डिशवॉश जेल लिंबू (२५० मिली / ५०० मिली बाटली)",
        "slug": "household-cleaning",
        "brand": "Vim",
        "is_loose": False,
        "clean_filename": "vim-dishwash-gel-250ml.jpg",
        "description": "विम डिशवॉश लिक्विड जेल २५० मिली बाटली. भांड्यांवर पांढरे डाग पडू देत नाही.",
        "variants": [
            {"unit_size": "250ml Bottle", "price": 60.0, "mrp": 60.0, "stock": 40},
            {"unit_size": "500ml Bottle", "price": 115.0, "mrp": 115.0, "stock": 25}
        ]
    },
    "exo.soapbar.jpg": {
        "name": "Exo Touch & Shine Round Dishwash Bar (250g Tub)",
        "name_hi": "एक्सो टच अँड शाइन डिशवॉश बार (२५० ग्रॅम गोल टब)",
        "slug": "household-cleaning",
        "brand": "Exo",
        "is_loose": False,
        "clean_filename": "exo-round-dishwash-bar.jpg",
        "description": "एक्सो अँटी-बॅक्टेरियल गोल डिशवॉश बार टबसह. पाणी साचून साबण वाया जात नाही.",
        "variants": [
            {"unit_size": "250g Tub", "price": 32.0, "mrp": 32.0, "stock": 50}
        ]
    },
    "harpic.blue.png": {
        "name": "Harpic Power Plus Toilet Cleaner Blue (500ml / 1L Bottle)",
        "name_hi": "हार्पिक पॉवर प्लस टॉयलेट क्लिनर (५०० मिली निळा)",
        "slug": "household-cleaning",
        "brand": "Harpic",
        "is_loose": False,
        "clean_filename": "harpic-toilet-cleaner-blue.jpg",
        "description": "हार्पिक १० पट जास्त मळ आणि पिवळे डाग काढणारा नंबर १ टॉयलेट क्लिनर.",
        "variants": [
            {"unit_size": "500ml Bottle", "price": 99.0, "mrp": 99.0, "stock": 40},
            {"unit_size": "1L Bottle", "price": 195.0, "mrp": 195.0, "stock": 25}
        ]
    },
    "harpic.red.webp": {
        "name": "Harpic Bathroom Cleaner Red Floral (500ml Bottle)",
        "name_hi": "हार्पिक बाथरूम क्लिनर (५०० मिली लाल बाटली)",
        "slug": "household-cleaning",
        "brand": "Harpic",
        "is_loose": False,
        "clean_filename": "harpic-bathroom-cleaner-red.jpg",
        "description": "हार्पिक रेड बाथरूम क्लिनर. टाईल्स, बेसिन आणि नळ लखलखीत स्वच्छ करतो.",
        "variants": [
            {"unit_size": "500ml Bottle", "price": 99.0, "mrp": 99.0, "stock": 35}
        ]
    },
    "sunny.floor.cleaner.jpg": {
        "name": "Sunny Herbal Pine Floor Cleaner (1L Bottle)",
        "name_hi": "सन्नी हर्बल पाइन फ्लोअर क्लिनर (१ लिटर फिनाइल)",
        "slug": "household-cleaning",
        "brand": "Sunny",
        "is_loose": False,
        "clean_filename": "sunny-pine-floor-cleaner-1l.jpg",
        "description": "सन्नी हर्बल नैसर्गिक पाइन तेलाचे फिनाइल. फरशीवरील जंतू मारते आणि ताजा सुगंध देते.",
        "variants": [
            {"unit_size": "1L Bottle", "price": 75.0, "mrp": 75.0, "stock": 40}
        ]
    },

    # 13. Personal Care & Pooja
    "dettol-original-soap-quick-pantry-1.jpg": {
        "name": "Dettol Original Bathing Soap (75g Single Bar)",
        "name_hi": "डेटॉल ओरिजिनल आंघोळीचा साबण (७५ ग्रॅम एक साबण)",
        "slug": "pooja-samagri",
        "brand": "Dettol",
        "is_loose": False,
        "clean_filename": "dettol-original-soap-single.jpg",
        "description": "डेटॉल ओरिजिनल जंतूनाशक साबण. १०० आजार पसरवणाऱ्या जंतूंपासून संरक्षण.",
        "variants": [
            {"unit_size": "75g Single Bar", "price": 40.0, "mrp": 40.0, "stock": 80}
        ]
    },
    "dettol.pack.of4.jpg": {
        "name": "Dettol Original Bathing Soap (Pack of 4 x 75g)",
        "name_hi": "डेटॉल ओरिजिनल साबण (४ साबणाचा कॉम्बो पॅक)",
        "slug": "pooja-samagri",
        "brand": "Dettol",
        "is_loose": False,
        "clean_filename": "dettol-original-soap-pack4.jpg",
        "description": "डेटॉल ओरिजिनल ४ साबणांचा सुपर सेव्हर फॅमिली पॅक.",
        "variants": [
            {"unit_size": "Pack of 4 x 75g", "price": 155.0, "mrp": 155.0, "stock": 40}
        ]
    },
    "Dettol_Cool_4_x_75.webp": {
        "name": "Dettol Cool Menthol Soap (Pack of 4 x 75g)",
        "name_hi": "डेटॉल कुल मेंथॉल साबण (४ साबणाचा पॅक)",
        "slug": "pooja-samagri",
        "brand": "Dettol",
        "is_loose": False,
        "clean_filename": "dettol-cool-soap-pack4.jpg",
        "description": "डेटॉल कुल मेंथॉल साबण. उन्हाळ्यात शरीराला देतो थंडगार ताजेतवानेपणा.",
        "variants": [
            {"unit_size": "Pack of 4 x 75g", "price": 155.0, "mrp": 155.0, "stock": 40}
        ]
    },
    "dettol.liquid.handwash.jpg": {
        "name": "Dettol Liquid Handwash Original (175ml Refill Pouch)",
        "name_hi": "डेटॉल लिक्विड हँडवॉश रीफिल पाउच (१७५ मिली)",
        "slug": "pooja-samagri",
        "brand": "Dettol",
        "is_loose": False,
        "clean_filename": "dettol-handwash-refill-175ml.jpg",
        "description": "डेटॉल ओरिजिनल लिक्विड हँडवॉश रीफिल पॅक. हात स्वच्छ व जंतूमुक्त ठेवण्यासाठी.",
        "variants": [
            {"unit_size": "175ml Refill Pouch", "price": 55.0, "mrp": 55.0, "stock": 50}
        ]
    },
    "lux-soft-glow-soap-quick-pantry-1.webp": {
        "name": "Lux Soft Glow Rose Bathing Soap (100g Bar)",
        "name_hi": "लक्स रोझ सॉफ्ट ग्लो आंघोळीचा साबण (१०० ग्रॅम)",
        "slug": "pooja-samagri",
        "brand": "Lux",
        "is_loose": False,
        "clean_filename": "lux-soft-glow-rose-100g.jpg",
        "description": "लक्स रोझ आणि व्हिटॅमिन सी समृद्ध सौंदर्य साबण. त्वचेला देतो मऊपणा आणि चमक.",
        "variants": [
            {"unit_size": "100g Bar", "price": 35.0, "mrp": 35.0, "stock": 60}
        ]
    },
    "margo.soap.jpg": {
        "name": "Margo Original Neem Bathing Soap (100g Bar)",
        "name_hi": "मार्गॊ ओरिजिनल कडुलिंब साबण (१०० ग्रॅम)",
        "slug": "pooja-samagri",
        "brand": "Margo",
        "is_loose": False,
        "clean_filename": "margo-neem-soap-100g.jpg",
        "description": "१००% शुद्ध कडूनिंबाच्या तेलापासून बनवलेला नैसर्गिक अँटी-बॅक्टेरियल साबण.",
        "variants": [
            {"unit_size": "100g Bar", "price": 35.0, "mrp": 35.0, "stock": 60}
        ]
    },
    "moti.body.soap.webp": {
        "name": "Moti Luxury Sandal Bath Soap (150g Bar)",
        "name_hi": "मोती लक्झरी चंदन आंघोळीचा साबण (१५० ग्रॅम)",
        "slug": "pooja-samagri",
        "brand": "Moti",
        "is_loose": False,
        "clean_filename": "moti-luxury-sandal-soap.jpg",
        "description": "महाराष्ट्राचा पारंपरिक मोती साबण. चंदनाचा अस्सल शाही सुगंध आणि टवटवीत त्वचा.",
        "variants": [
            {"unit_size": "150g Bar", "price": 55.0, "mrp": 55.0, "stock": 40}
        ]
    },
    "Clinic.plus.1rs.jpg": {
        "name": "Clinic Plus Strong & Long Shampoo (₹1 Sachet)",
        "name_hi": "क्लिनिक प्लस शाम्पू (१ रुपया सॅशे)",
        "slug": "pooja-samagri",
        "brand": "Clinic Plus",
        "is_loose": False,
        "clean_filename": "clinic-plus-sachet-1rs.jpg",
        "description": "क्लिनिक प्लस मिल्क प्रोटीन फॉर्म्युला १ रुपयाचा सॅशे. केसांच्या मजबुतीसाठी.",
        "variants": [
            {"unit_size": "₹1 Sachet", "price": 1.0, "mrp": 1.0, "stock": 300},
            {"unit_size": "₹2 Sachet", "price": 2.0, "mrp": 2.0, "stock": 200}
        ]
    },
    "clinic-plus-strong-and-long-health-shampoo-quick-pantry-2.jpg": {
        "name": "Clinic Plus Strong & Long Shampoo (80ml / 175ml Bottle)",
        "name_hi": "क्लिनिक प्लस शाम्पू बाटली (८० मिली / १७५ मिली)",
        "slug": "pooja-samagri",
        "brand": "Clinic Plus",
        "is_loose": False,
        "clean_filename": "clinic-plus-shampoo-bottle.jpg",
        "description": "क्लिनिक प्लस मिल्क प्रोटीन शाम्पू बाटली.",
        "variants": [
            {"unit_size": "80ml Bottle", "price": 50.0, "mrp": 50.0, "stock": 40},
            {"unit_size": "175ml Bottle", "price": 120.0, "mrp": 120.0, "stock": 25}
        ]
    },
    "Dove.2Rs.webp": {
        "name": "Dove Daily Shine Shampoo (₹2 Sachet)",
        "name_hi": "डव्ह डेली शाइन शाम्पू (२ रुपये सॅशे)",
        "slug": "pooja-samagri",
        "brand": "Dove",
        "is_loose": False,
        "clean_filename": "dove-shampoo-sachet-2rs.jpg",
        "description": "डव्ह डेली शाइन न्यूट्रिटिव्ह सीरम शाम्पू २ रुपयांचा सॅशे.",
        "variants": [
            {"unit_size": "₹2 Sachet", "price": 2.0, "mrp": 2.0, "stock": 200}
        ]
    },
    "Dove.180ml.webp": {
        "name": "Dove Daily Shine Shampoo (180ml Bottle)",
        "name_hi": "डव्ह डेली शाइन शाम्पू (१८० मिली बाटली)",
        "slug": "pooja-samagri",
        "brand": "Dove",
        "is_loose": False,
        "clean_filename": "dove-shampoo-bottle-180ml.jpg",
        "description": "डव्ह डेली शाइन शाम्पू १८० मिली बाटली. केसांना देतो मऊपणा आणि नैसर्गिक चमक.",
        "variants": [
            {"unit_size": "180ml Bottle", "price": 175.0, "mrp": 175.0, "stock": 25}
        ]
    },
    "sunsilk.1rs.webp": {
        "name": "Sunsilk Black Shine Shampoo (₹1 Sachet)",
        "name_hi": "सनसिल्क ब्लॅक शाइन शाम्पू (१ रुपया सॅशे)",
        "slug": "pooja-samagri",
        "brand": "Sunsilk",
        "is_loose": False,
        "clean_filename": "sunsilk-sachet-1rs.jpg",
        "description": "सनसिल्क ब्लॅक शाइन १ रुपया सॅशे. आवळा व तेल फॉर्म्युला चकचकीत काळ्या केसांसाठी.",
        "variants": [
            {"unit_size": "₹1 Sachet", "price": 1.0, "mrp": 1.0, "stock": 300}
        ]
    },
    "sunlink.bottle.webp": {
        "name": "Sunsilk Black Shine Shampoo (180ml Bottle)",
        "name_hi": "सनसिल्क ब्लॅक शाइन शाम्पू (१८० मिली बाटली)",
        "slug": "pooja-samagri",
        "brand": "Sunsilk",
        "is_loose": False,
        "clean_filename": "sunsilk-bottle-180ml.jpg",
        "description": "सनसिल्क स्टनिंग ब्लॅक शाइन १८० मिली बाटली.",
        "variants": [
            {"unit_size": "180ml Bottle", "price": 160.0, "mrp": 160.0, "stock": 25}
        ]
    },
    "head & shoulders bottle.jpg": {
        "name": "Head & Shoulders Anti-Dandruff Smooth & Silky Shampoo (180ml)",
        "name_hi": "हेड अँड शोल्डर अँटी डँड्रफ शाम्पू (१८० मिली बाटली)",
        "slug": "pooja-samagri",
        "brand": "Head & Shoulders",
        "is_loose": False,
        "clean_filename": "head-shoulders-smooth-silky-180ml.jpg",
        "description": "हेड अँड शोल्डर डँड्रफ मुळापासून घालवणारा आणि केसांना रेशमी मऊ ठेवणारा शाम्पू.",
        "variants": [
            {"unit_size": "180ml Bottle", "price": 185.0, "mrp": 185.0, "stock": 25}
        ]
    },
    "head-and-shoulders-cool-menthol-shampoo-quick-pantry-1.webp": {
        "name": "Head & Shoulders Cool Menthol Shampoo (72ml Bottle)",
        "name_hi": "हेड अँड शोल्डर कुल मेंथॉल शाम्पू (७२ मिली बाटली)",
        "slug": "pooja-samagri",
        "brand": "Head & Shoulders",
        "is_loose": False,
        "clean_filename": "head-shoulders-cool-menthol-72ml.jpg",
        "description": "हेड अँड शोल्डर कुल मेंथॉल शाम्पू ७२ मिली बाटली. डोक्याला देतो ताजेतवाने गारवा.",
        "variants": [
            {"unit_size": "72ml Bottle", "price": 85.0, "mrp": 85.0, "stock": 30}
        ]
    },
    "dabur_vatika_henna_amla_health_shampoo-1.webp": {
        "name": "Dabur Vatika Henna & Amla Shampoo (180ml Bottle)",
        "name_hi": "डाबर वाटिका हिना व आवळा शाम्पू (१८० मिली बाटली)",
        "slug": "pooja-samagri",
        "brand": "Dabur",
        "is_loose": False,
        "clean_filename": "dabur-vatika-shampoo-180ml.jpg",
        "description": "डाबर वाटिका आयुर्वेदिक हिना व आवळा शाम्पू. केसांना नैसर्गिक पोषण आणि मजबूती देतो.",
        "variants": [
            {"unit_size": "180ml Bottle", "price": 145.0, "mrp": 145.0, "stock": 25}
        ]
    },
    "colgate.jpg": {
        "name": "Colgate Strong Teeth Dental Cream (100g / 150g)",
        "name_hi": "कोलगेट स्ट्रॉंग टीथ पेस्ट (१०० ग्रॅम / १५० ग्रॅम)",
        "slug": "pooja-samagri",
        "brand": "Colgate",
        "is_loose": False,
        "clean_filename": "colgate-strong-teeth-paste.jpg",
        "description": "कोलगेट स्ट्रॉंग टीथ कॅल्शियम व मिनरल्सयुक्त टूथपेस्ट. दातांना देतो पोलादी मजबूती.",
        "variants": [
            {"unit_size": "100g Tube", "price": 65.0, "mrp": 65.0, "stock": 60},
            {"unit_size": "150g Tube", "price": 95.0, "mrp": 95.0, "stock": 40}
        ]
    },
    "colgate.maxfresh.webp": {
        "name": "Colgate MaxFresh Peppermint Ice Toothpaste (80g / 150g)",
        "name_hi": "कोलगेट मॅक्सफ्रेश पेपरमिंट पेस्ट (८० ग्रॅम / १५० ग्रॅम)",
        "slug": "pooja-samagri",
        "brand": "Colgate",
        "is_loose": False,
        "clean_filename": "colgate-maxfresh-peppermint.jpg",
        "description": "कोलगेट मॅक्सफ्रेश कुलिंग क्रिस्टल्ससह. श्वासाला देतो दिवसभर टिकणारा ताजेतवाना सुगंध.",
        "variants": [
            {"unit_size": "80g Tube", "price": 60.0, "mrp": 60.0, "stock": 50},
            {"unit_size": "150g Tube", "price": 110.0, "mrp": 110.0, "stock": 30}
        ]
    },
    "dabur.red.webp": {
        "name": "Dabur Red Ayurvedic Toothpaste (100g / 150g)",
        "name_hi": "डाबर रेड आयुर्वेदिक टूथपेस्ट (१०० ग्रॅम / १५० ग्रॅम)",
        "slug": "pooja-samagri",
        "brand": "Dabur",
        "is_loose": False,
        "clean_filename": "dabur-red-paste.jpg",
        "description": "डाबर लाल दंतमंजन पेस्ट. लवंग व पुदिन्याने हिरड्यांच्या सर्व समस्यांवर रामबाण उपाय.",
        "variants": [
            {"unit_size": "100g Tube", "price": 60.0, "mrp": 60.0, "stock": 60},
            {"unit_size": "150g Tube", "price": 95.0, "mrp": 95.0, "stock": 40}
        ]
    },
    "patanjali.dant.kanti.webp": {
        "name": "Patanjali Dant Kanti Dental Cream (100g / 200g)",
        "name_hi": "पतंजली दंतकांती आयुर्वेदिक पेस्ट (१०० ग्रॅम / २०० ग्रॅम)",
        "slug": "pooja-samagri",
        "brand": "Patanjali",
        "is_loose": False,
        "clean_filename": "patanjali-dant-kanti-paste.jpg",
        "description": "पतंजली दंतकांती. अकर्करा, बबूल व कडूनिंबायुक्त दातांचे नैसर्गिक आयुर्वेदिक सुरक्षा कवच.",
        "variants": [
            {"unit_size": "100g Tube", "price": 55.0, "mrp": 55.0, "stock": 60},
            {"unit_size": "200g Tube", "price": 105.0, "mrp": 105.0, "stock": 40}
        ]
    },
    "pepsodent.avif": {
        "name": "Pepsodent Expert Protection Germi Check Toothpaste (100g)",
        "name_hi": "पेप्सोडंट जर्मि चेक टूथपेस्ट (१०० ग्रॅम)",
        "slug": "pooja-samagri",
        "brand": "Pepsodent",
        "is_loose": False,
        "clean_filename": "pepsodent-germi-check-100g.jpg",
        "description": "पेप्सोडंट जर्मि चेक. जेवणानंतर १२ तास दातांमधील जंतूंशी लढा देणारी टूथपेस्ट.",
        "variants": [
            {"unit_size": "100g Tube", "price": 60.0, "mrp": 60.0, "stock": 50}
        ]
    },
    "Sensodyne-Dentifrice-Daily-Care-Cool-Mint.webp": {
        "name": "Sensodyne Daily Care Cool Mint Toothpaste (75g)",
        "name_hi": "सेन्सॊडाइन डेली केअर कूल मिंट पेस्ट (७५ ग्रॅम)",
        "slug": "pooja-samagri",
        "brand": "Sensodyne",
        "is_loose": False,
        "clean_filename": "sensodyne-daily-care-75g.jpg",
        "description": "दात आंबणे आणि सेन्सिटिव्हिटीवर डॉक्टरांनी शिफारस केलेली नंबर १ टूथपेस्ट.",
        "variants": [
            {"unit_size": "75g Tube", "price": 135.0, "mrp": 135.0, "stock": 35}
        ]
    },
    "parachute.oil.webp": {
        "name": "Parachute 100% Pure Coconut Hair Oil (100ml / 200ml / 500ml)",
        "name_hi": "पॅराशूट १००% शुद्ध खोबरेल तेल (१०० मिली / २०० मिली / ५०० मिली)",
        "slug": "pooja-samagri",
        "brand": "Parachute",
        "is_loose": False,
        "clean_filename": "parachute-coconut-oil.jpg",
        "description": "पॅराशूट १००% शुद्ध खोबरेल तेल. हाताने निवडलेल्या सुक्या खोबऱ्यापासून बनवलेले खाद्य दर्जाचे तेल.",
        "variants": [
            {"unit_size": "100ml Bottle", "price": 45.0, "mrp": 45.0, "stock": 60},
            {"unit_size": "200ml Bottle", "price": 90.0, "mrp": 90.0, "stock": 40},
            {"unit_size": "500ml Bottle", "price": 210.0, "mrp": 210.0, "stock": 25}
        ]
    },
    "cycle.agarbatti.jpg": {
        "name": "Cycle Pure Three in One Agarbatti (Pooja Incense Sticks)",
        "name_hi": "सायकल थ्री इन वन अगरबत्ती (पूजा साहित्य)",
        "slug": "pooja-samagri",
        "brand": "Cycle Pure",
        "is_loose": False,
        "clean_filename": "cycle-three-in-one-agarbatti.jpg",
        "description": "सायकल थ्री इन वन अगरबत्ती. मंद आणि पवित्र सुगंधाने घर प्रसन्न करणारी अगरबत्ती.",
        "variants": [
            {"unit_size": "Standard Pack", "price": 20.0, "mrp": 20.0, "stock": 80},
            {"unit_size": "Jumbo Box", "price": 65.0, "mrp": 65.0, "stock": 40}
        ]
    }
}

print(f"Total defined items in CATALOG_MAPPING: {len(CATALOG_MAPPING)}")

# Check against actual files in Products.images
src_files = os.listdir(SRC_IMAGES_DIR)
missing_in_mapping = [f for f in src_files if f not in CATALOG_MAPPING]
missing_on_disk = [k for k in CATALOG_MAPPING if k not in src_files]

print(f"Files in directory: {len(src_files)}")
print(f"Missing in mapping: {len(missing_in_mapping)} -> {missing_in_mapping}")
print(f"Missing on disk: {len(missing_on_disk)} -> {missing_on_disk}")

if missing_in_mapping or missing_on_disk:
    print("ERROR: Mismatch between files on disk and catalog mapping!")
    sys.exit(1)

print("\n--- STEP 1: Processing and Standardizing Product Images (600x600 White Canvas) ---")

def process_packshot(src_path, dst_path, target_size=(600, 600)):
    with Image.open(src_path) as img:
        img = img.convert("RGBA")
        
        # Calculate aspect-ratio preserving fit inside (540, 540) to leave comfortable padding
        max_w, max_h = int(target_size[0] * 0.90), int(target_size[1] * 0.90)
        img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
        
        # Create solid white canvas
        canvas = Image.new("RGB", target_size, (255, 255, 255))
        
        # Paste centered
        offset_x = (target_size[0] - img.width) // 2
        offset_y = (target_size[1] - img.height) // 2
        
        # Use alpha channel as mask if present
        canvas.paste(img, (offset_x, offset_y), mask=img.split()[3])
        canvas.save(dst_path, "JPEG", quality=90, optimize=True)

processed_count = 0
for orig_name, meta in CATALOG_MAPPING.items():
    src_file = os.path.join(SRC_IMAGES_DIR, orig_name)
    clean_name = meta["clean_filename"]
    pub_file = os.path.join(PUB_DIR, clean_name)
    dist_file = os.path.join(DIST_DIR, clean_name)
    
    process_packshot(src_file, pub_file)
    process_packshot(src_file, dist_file)
    processed_count += 1

print(f"Successfully processed and deployed {processed_count} packshots to public/products and dist/products!")

print("\n--- STEP 2: Updating Database (kirana.db) ---")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get category id mapping
cursor.execute("SELECT slug, id FROM categories;")
cat_map = dict(cursor.fetchall())
print(f"Categories in DB: {len(cat_map)} categories -> {cat_map}")

# Check current user count
cursor.execute("SELECT COUNT(*) FROM users;")
user_count = cursor.fetchone()[0]
print(f"Existing Users (will be preserved): {user_count}")

# Clear old products, variants, tiered_pricing, restock_alerts
cursor.execute("DELETE FROM restock_alerts;")
cursor.execute("DELETE FROM tiered_pricing;")
cursor.execute("DELETE FROM product_variants;")
cursor.execute("DELETE FROM products;")
conn.commit()

# Reset auto-increment sequence for products and variants
cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('products', 'product_variants', 'tiered_pricing');")
conn.commit()

print("Old products, variants, and tiers cleared successfully.")

# Insert new products and variants
inserted_prods = 0
inserted_vars = 0
inserted_tiers = 0

for orig_name, meta in CATALOG_MAPPING.items():
    cat_id = cat_map[meta["slug"]]
    img_url = f"/products/{meta['clean_filename']}"
    
    cursor.execute("""
        INSERT INTO products (category_id, name, name_hi, brand, is_loose, description, image_url, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (cat_id, meta["name"], meta["name_hi"], meta["brand"], 1 if meta["is_loose"] else 0, meta["description"], img_url))
    
    prod_id = cursor.lastrowid
    inserted_prods += 1
    
    for v in meta["variants"]:
        cursor.execute("""
            INSERT INTO product_variants (product_id, unit_size, mrp, selling_price, stock_quantity, is_available, is_clearance)
            VALUES (?, ?, ?, ?, ?, 1, 0)
        """, (prod_id, v["unit_size"], float(v["mrp"]), float(v["price"]), v["stock"]))
        inserted_vars += 1
        
    for t in meta.get("tiered", []):
        cursor.execute("""
            INSERT INTO tiered_pricing (product_id, min_qty, unit_price, tier_label, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (prod_id, t["min_qty"], float(t["tier_price"]), t["label"]))
        inserted_tiers += 1

conn.commit()
conn.close()

print(f"\n--- Database Seeding Complete ---")
print(f"Products Inserted: {inserted_prods}")
print(f"Variants Inserted: {inserted_vars}")
print(f"Tiered Pricing Slabs: {inserted_tiers}")
