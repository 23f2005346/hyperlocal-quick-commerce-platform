# Komal Mart (कोमल मार्ट) — Project Context & System Invariants

You are working on **Komal Mart (कोमल मार्ट)**, a production hyperlocal kirana & quick-commerce web platform operating in Wadala, Mumbai.

---

## 👤 Founder & Team Context
- **Founder:** Roushan (IIT Madras BS Data Science & Applications student, long-term AI/Robotics deeptech founder).
- **Communication Style:** Address as "bhai" in casual interactions. Strict English ONLY for all technical and instructional explanations.
- **Physical Store Operations:** Physical grocery store run by Roushan's father in Wadala, Mumbai.

---

## 📍 Repositories & System Paths
- **Local Workspace:** `C:\AI_Engineering_Projects\kirana-store`
- **Frontend Directory:** `frontend/` (Vue 3, Vite, Vanilla CSS)
- **Backend Directory:** `backend/` (Python Flask REST API, SQLite with WAL mode)
- **Live Production URL:** `https://komalmart.onrender.com`
- **GitHub Repository:** `https://github.com/23f2005346/hyperlocal-quick-commerce-platform` (Branch: `master`)

---

## 🧠 Persistent Local Memory & Disaster Recovery Keys
All detailed session logs, architecture diagrams, emergency disaster recovery keys, PINs, and historical milestones are stored securely in the **local Second Brain vault** on this machine (never exposed in public Git):

1. **Canonical Project & Architecture Note:**
   `C:\AI_Engineering_Projects\AI_Learning\Lessons\Python\Apna Desi Kirana Store Project.md`
2. **Master Engineering Log:**
   `C:\AI_Engineering_Projects\AI_Learning\log.md`
3. **Master Knowledge Index:**
   `C:\AI_Engineering_Projects\AI_Learning\index.md`

> **Note for AI Assistant:** Whenever you start a fresh session or need exact emergency recovery PINs, historical context, or state details, inspect the canonical note above before asking the user.

---

## 🔐 Core Architecture & Operating Invariants

1. **Admin 2FA & Emergency Access:**
   - Admin 2FA is verified in `backend/app.py`.
   - Disaster recovery fallback keys are managed via environment variables (`MASTER_ADMIN_PIN`) and documented in the local Second Brain vault.
   - Render free tier blocks outbound TCP on ports 25, 465, and 587. Production transactional emails use HTTPS APIs over Port 443.

2. **Paytm QR & Soundbox Integration:**
   - Active customer UPI QR code and soundbox matching are decoupled from third-party webhook costs.
   - Whole-rupee orders receive dynamic unique paise offsets (`.11` to `.99`) via `assign_unique_soundbox_paise` in `backend/app.py` to prevent collisions on the store's physical Paytm Soundbox.
   - Active QR code transitions are governed by the physical store protocol documented in the Second Brain note.

3. **Authentic Kirana Pricing (No Strikethroughs):**
   - No marketplace strikethrough cut-prices (`~~₹250~~ ₹190`).
   - All retail items sell at standard MRP. Wholesale bulk discount tiers (`🏷️ 5kg+ Wholesale Rate`) apply only to bulk purchases.

4. **Daily Z-Report Payment Reconciliation:**
   - Payment method matching must always use case-insensitive substring checks (`'cash' in method.lower()`), never exact equality, because walk-in counter sales record `'Cash on Counter'` while online checkout records `'Cash on Delivery (COD)'`.

---

## 🛣️ Current Roadmap Reference
Refer to Section `## 🛣️ Active Implementation Roadmap` in `C:\AI_Engineering_Projects\AI_Learning\Lessons\Python\Apna Desi Kirana Store Project.md` for the prioritized sprint items.
