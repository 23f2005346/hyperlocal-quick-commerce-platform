# 🌾 कोमल मार्ट (Komal Mart - Wholesale & Retail Supermarket)
### Fully Functional Full-Stack Indian Grocery & Supermarket Web Application

A production-ready, authentic Indian Grocery & Supermarket web application built with **Python Flask (REST API + SQLite)** on the backend and **Vue 3 (Vite + Modern Responsive Indian Mandi Aesthetic)** on the frontend.

Designed specifically around the nuances of Indian retail & wholesale operations:
- **Komal Mart Counter POS:** Storekeeper manual bill builder for walk-in counter customers, phone-in orders, and restaurant/hotel bulk supplies.
- **Customer Directory & Khata Audit:** Lifetime purchase history and payment tracking per registered customer with 1-click WhatsApp statements.
- **Khula vs Packed:** Open grain mandi staples (Chakki Atta, Loose Dals, Mustard Oil by liter) vs Branded packaged items (Aashirvaad, Fortune, Tata Sampann).
- **Weight Variants:** 250g, 500g, 1kg, 5kg, 10kg, 25kg bori with dynamic price updates.
- **Trilingual System:** Marathi default, Hindi, and English with Devanagari catalog.
- **Dukandar Mode (Admin):** Live price & stock editor in SQLite, product adder, and order ledger (बहीखाता).
- **Desi Kirana Parcha (Bill):** Realistic printable shop receipt with order number, itemized rates, discounts, and customer details.

---

## 🏗️ Architecture & Tech Stack

```
kirana-store/
├── backend/
│   ├── app.py              # Flask app factory, REST API endpoints, static SPA server
│   ├── models.py           # SQLAlchemy models (Category, Product, ProductVariant, Order, OrderItem)
│   ├── seed_data.py        # 44 realistic Indian products, 90 variants, 9 categories
│   ├── kirana.db           # SQLite persistent database
│   ├── test_api.py         # Automated verification tests
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.vue         # Main Vue 3 SPA (Catalog, Cart Drawer, Checkout, Dukandar Admin, Bill Modal)
│   │   ├── style.css       # Clean Indian grocery theme with print styles
│   │   └── main.js
│   ├── dist/               # Pre-built production bundle served directly by Flask
│   ├── package.json
│   └── vite.config.js
├── run.bat                 # 1-Click double-click launcher
└── README.md
```

---

## 🛒 Seeded Catalog (Included by Default)

| Category | Highlights & Items |
| :--- | :--- |
| **दालें एवं दलहन (Dals & Pulses)** | Toor/Arhar Dal (Loose & Tata Sampann), Moong Dal Dhuli (yellow split), Moong Dal Chilka, Sabut Moong (sprouts), Urad Dal Dhuli (idli/dosa), Urad Chilka, Urad Sabut / Kali Dal (Dal Makhani), Lal Masoor / Malka, Chana Dal. |
| **आटा, मैदा एवं सूजी (Atta & Flours)** | Chakki Fresh Atta (खुला आटा - ₹34/kg), Aashirvaad Shudh Chakki Atta (5kg, 10kg), Fortune Chakki Fresh Atta, Maida (loose & packet), Besan (pure chana pisai), Suji / Rawa. |
| **चावल एवं पोहा (Rice & Grains)** | Wada Kolam / Sona Masoori Rice (Loose 1kg, 5kg, 25kg bori), India Gate Feast Rozzana Basmati, Thick Poha for breakfast. |
| **राजमा, छोले एवं चना (Beans & Legumes)** | Kashmiri Red Rajma, Himalayan Chitra Rajma, Jumbo Kabuli Chana (Chhole), Kala Chana (Navratri / sprout special). |
| **चाय पत्ती एवं पेय (Tea & Beverages)** | Tata Tea Gold, Tata Tea Agni, Brooke Bond Red Label, Brooke Bond Taaza, Taj Mahal (Wah Taj!), Girnar Masala Tea. |
| **टूथपेस्ट (Oral Care)** | Colgate Strong Teeth (100g, 200g, 500g saver), Colgate MaxFresh Peppermint, Sensodyne Fresh Gel, Dabur Red Ayurvedic, Patanjali Dant Kanti. |
| **तेल एवं शुद्ध देसी घी (Oils & Ghee)** | Desi Mustard Oil (कच्ची घानी खुला), Fortune Mustard Oil pouch, Fortune Sunflower Oil, Amul Pure Desi Ghee (carton & tin). |
| **मसाले एवं नमक (Spices & Salt)** | Pure Chakki Haldi Powder, Teja Lal Mirch Powder, Dhaniya Powder, Tata Salt (Iodised), Everest Garam Masala. |
| **सफाई एवं डिटर्जेंट (Cleaning)** | Surf Excel Quick Wash, Rin Detergent Bar, Vim Dishwash Bar, Dettol Soap. |

---

## 🚀 How to Run

### Method 1: Single Command (Runs Both API + UI via Flask)
Open PowerShell or Terminal in the project root:
```bash
cd C:\AI_Engineering_Projects\kirana-store\backend
python app.py
```
Open your browser at:
👉 **`http://127.0.0.1:5000`**

*(The Flask backend is configured to serve both the REST API on `/api/*` and the pre-built Vue SPA on `/`!)*

---

### Method 2: Full Dev Mode (Flask API + Vite Hot-Reload)
For active development with instant code updates:

**Terminal 1 (Backend):**
```bash
cd C:\AI_Engineering_Projects\kirana-store\backend
python app.py
```

**Terminal 2 (Frontend with Vite Hot Reload):**
```bash
cd C:\AI_Engineering_Projects\kirana-store\frontend
npm run dev
```
Open your browser at:
👉 **`http://localhost:5173`**

---

## 🎓 Learning Guide: How You Can Change Prices & Add Products

You asked: *"learning in a way like changing price and all"*. Here are the 3 ways you can experiment with full-stack data flow:

### 1. Directly in the Web UI (Dukandar Dashboard Mode)
1. Click the **"⚙️ दुकानदार मोड (Admin)"** button in the top right header.
2. In the **"📋 पूरा सामान व कीमत सूची (Live Price Editor)"** table, you will see all 90 items.
3. Change any value:
   - For example, change Toor Dal 1kg price from `145` to `150`.
   - Change MRP or stock units.
4. Click **"💾 सेव करें"**.
5. The frontend sends a `PATCH /api/variants/<id>` request to Flask, which immediately commits the update to `kirana.db` in SQLite!

### 2. Via REST API (cURL / Postman / Python)
You can test API calls directly:
```bash
# Update price of variant ID 1 to ₹160
curl -X PATCH http://127.0.0.1:5000/api/variants/1 \
     -H "Content-Type: application/json" \
     -d "{\"selling_price\": 160.0}"
```

### 3. In the Python Seed File (`backend/seed_data.py`)
Open `backend/seed_data.py`:
- Add any new Indian grocery item under `PRODUCTS_DATA`.
- Edit prices, variants, or Hindi names.
- In the Dukandar dashboard, click **"🔄 रीसेट डिफ़ॉल्ट सामान"** or call `POST /api/reset-seed` to rebuild the database with your new items in 1 second!

---

## 🖼️ How to Add or Change Product Pictures

All product photos are served locally from:
`frontend/public/products/`

1. **Add new image:** Copy your `.jpg` or `.png` into `frontend/public/products/` (e.g. `my-dal.jpg`).
2. **Link to product:** In `backend/seed_data.py`, set `"image_url": "/products/my-dal.jpg"`.
3. **Re-build frontend:**
   ```powershell
   cd frontend
   npm run build
   ```
4. Reset seed via UI (`http://127.0.0.1:5000/#admin`) or terminal.

---

## 🔐 Default Access Accounts

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Store Owner (Dukandar)** | `admin@kirana.com` | `admin123` | Inventory price editor, order ledger, 1-click Paid status, product add/delete. (No shopping cart). |
| **Customer** | `roushan@example.com` | `customer123` | Shopping catalog, custom weight picker, cart, checkout, UPI QR, order history & khata book. |

