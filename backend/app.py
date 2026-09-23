import os
import sys
import random
import re
import time
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from models import db, User, Category, Product, ProductVariant, Order, OrderItem, get_ist_time
from seed_data import CATEGORIES_DATA, PRODUCTS_DATA

# Ensure UTF-8 stdout encoding on Windows consoles to prevent charmap crashes
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Automatically load backend/.env if present
env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_file):
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception as e:
        print(f"[ENV WARNING] Could not read .env: {e}")

SECRET_KEY = 'apna-desi-kirana-store-secret-key-2026'
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Strict Store Owner Admin Email Whitelist
ADMIN_WHITELIST = {'thisisroushan01@gmail.com', 'novaaether01@gmail.com'}
ADMIN_2FA_STORE = {} # { email: { 'otp': '123456', 'expires_at': ts, 'user_id': id } }

# SMTP configuration for real email delivery (Gmail App Password)
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', 'thisisroushan01@gmail.com').strip()
SMTP_PASS = os.environ.get('SMTP_PASS', 'emaiuwgdfqddjskg').replace(' ', '').strip()

def send_admin_otp_email(to_email, otp):
    """
    Dispatches 6-digit OTP code to the authorized admin email address.
    If SMTP credentials are provided, sends a real HTML email.
    Always logs clearly to console for local testing and server audits.
    """
    subject = f"🔐 Komal Mart Admin 2FA Code: {otp}"
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 24px; border: 1.5px solid #059669; border-radius: 12px; background-color: #fdfbf7;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #064e3b; margin: 0; font-size: 24px;">🌾 कोमल मार्ट (Komal Mart)</h1>
            <p style="color: #6b7280; font-size: 13px; margin-top: 4px;">Store Owner Security Verification</p>
        </div>
        <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; text-align: center;">
            <p style="font-size: 14px; color: #374151; margin-bottom: 12px;">Your 6-digit Store Admin Login OTP is:</p>
            <div style="font-size: 32px; font-weight: 900; letter-spacing: 6px; color: #059669; background: #ecfdf5; padding: 12px; border-radius: 8px; display: inline-block;">
                {otp}
            </div>
            <p style="font-size: 12px; color: #9ca3af; margin-top: 14px;">This code expires in 5 minutes. Do not share this code with anyone.</p>
        </div>
        <p style="font-size: 11px; color: #9ca3af; text-align: center; margin-top: 20px;">Komal Mart Kirana Store • Secure Admin Gateway</p>
    </div>
    """
    if SMTP_USER and SMTP_PASS:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"Komal Mart Admin Security <{SMTP_USER}>"
            msg['To'] = to_email
            msg.attach(MIMEText(f"Your Komal Mart Admin 2FA Code is: {otp}. Valid for 5 minutes.", 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [to_email], msg.as_string())
            server.quit()
            print(f"[EMAIL SENT] Successfully sent 2FA OTP to {to_email}")
            return True, "Email dispatched successfully"
        except Exception as e:
            print(f"[SMTP ERROR] Failed to send email to {to_email}: {e}")
            return False, str(e)
    else:
        print("[SMTP INFO] SMTP_USER/SMTP_PASS not set. Printed OTP to terminal console only.")
def is_dummy_phone(phone: str) -> bool:
    if not phone or len(phone) != 10:
        return True

    # 1. Fewer than 3 unique digits (e.g., 9999999999, 9898989898, 9191919191)
    if len(set(phone)) <= 2:
        return True

    # 2. Known sequential or ascending/descending patterns
    sequences = {
        "9876543210", "9876543211", "9876543212", "9876543213", "9876543214", "9876543215",
        "9876543216", "9876543217", "9876543218", "9876543219", "0123456789", "1234567890",
        "9123456789", "6789012345", "9876598765", "1234512345", "1122334455"
    }
    if phone in sequences:
        return True

    # 3. Repeating triplets (e.g. 9879879870 or 9879879879)
    if phone[:3] == phone[3:6] == phone[6:9]:
        return True

    # 4. Repeating pairs (e.g. 9898989898)
    if phone[:2] * 5 == phone:
        return True

    # 5. Repeating 4-digit prefix (e.g. 9876987612)
    if phone[:4] == phone[4:8]:
        return True

    # 6. Any single digit appearing 7 or more times
    for ch in set(phone):
        if phone.count(ch) >= 7:
            return True

    return False

SEARCH_ALIASES = {
    # Rice / Grains
    'rice': ['rice', 'chawal', 'chaawal', 'tandul', 'taandul', 'bhat', 'basmati', 'kolam', 'चावल', 'तांदूळ', 'भात', 'बासमती'],
    'chawal': ['rice', 'chawal', 'chaawal', 'tandul', 'bhat', 'basmati', 'चावल', 'तांदूळ'],
    'chaawal': ['rice', 'chawal', 'chaawal', 'tandul', 'bhat', 'basmati', 'चावल', 'तांदूळ'],
    'tandul': ['rice', 'tandul', 'taandul', 'chawal', 'bhat', 'kolam', 'तांदूळ', 'चावल'],
    'taandul': ['rice', 'tandul', 'taandul', 'chawal', 'bhat', 'kolam', 'तांदूळ', 'चावल'],
    'bhat': ['rice', 'chawal', 'tandul', 'भात', 'चावल'],
    'kolam': ['kolam', 'rice', 'कोलम', 'तांदूळ'],
    'basmati': ['basmati', 'rice', 'chawal', 'बासमती', 'दावत', 'daawat'],

    # Atta / Flours / Wheat
    'atta': ['atta', 'aata', 'pith', 'peeth', 'gehu', 'gehun', 'flour', 'chakki', 'wheat', 'sharbati', 'आटा', 'पीठ', 'गहू'],
    'aata': ['atta', 'aata', 'pith', 'flour', 'chakki', 'आटा', 'पीठ'],
    'pith': ['atta', 'pith', 'peeth', 'flour', 'पीठ', 'आटा'],
    'peeth': ['atta', 'pith', 'peeth', 'flour', 'पीठ', 'आटा'],
    'gehu': ['atta', 'gehu', 'gehun', 'wheat', 'chakki', 'sharbati', 'गहू', 'आटा'],
    'gehun': ['atta', 'gehu', 'gehun', 'wheat', 'chakki', 'sharbati', 'गहू', 'आटा'],
    'wheat': ['atta', 'gehu', 'wheat', 'chakki', 'aashirvaad', 'fortune', 'गहू', 'आटा'],
    'maida': ['maida', 'flour', 'मैदा'],
    'besan': ['besan', 'gram flour', 'chana', 'हरभरा', 'बेसन', 'चना'],
    'rava': ['rava', 'suji', 'sooji', 'semolina', 'रवा', 'सुजी'],
    'suji': ['rava', 'suji', 'sooji', 'रवा', 'सुजी'],
    'sooji': ['rava', 'suji', 'sooji', 'रवा', 'सुजी'],
    'semolina': ['rava', 'suji', 'sooji', 'रवा'],
    'poha': ['poha', 'pohe', 'flattened rice', 'पोहे', 'पोहा'],
    'pohe': ['poha', 'pohe', 'पोहे', 'पोहा'],

    # Dals & Pulses
    'dal': ['dal', 'daal', 'dall', 'डाळ', 'दाल', 'toor', 'arhar', 'moong', 'urad', 'masoor', 'chana'],
    'daal': ['dal', 'daal', 'डाळ', 'दाल', 'toor', 'arhar', 'moong', 'urad', 'masoor', 'chana'],
    'toor': ['toor', 'tuvar', 'arhar', 'तूर', 'अरहर', 'tur'],
    'tuvar': ['toor', 'tuvar', 'arhar', 'तूर', 'तुवर'],
    'arhar': ['toor', 'arhar', 'tuvar', 'अरहर', 'तूर'],
    'tur': ['toor', 'tuvar', 'arhar', 'तूर'],
    'moong': ['moong', 'mung', 'mug', 'मूग', 'मूँग'],
    'mung': ['moong', 'mung', 'mug', 'मूग', 'मूँग'],
    'mug': ['moong', 'mung', 'mug', 'मूग'],
    'urad': ['urad', 'udid', 'udad', 'उडीद', 'उड़द'],
    'udid': ['urad', 'udid', 'उडीद', 'उड़द'],
    'udad': ['urad', 'udid', 'उडीद', 'उड़द'],
    'masoor': ['masoor', 'masur', 'मलका', 'मसूर'],
    'masur': ['masoor', 'masur', 'मसूर'],
    'chana': ['chana', 'channa', 'harbhara', 'चना', 'हरभरा', 'छोले', 'काबुली'],
    'channa': ['chana', 'channa', 'harbhara', 'चना', 'हरभरा'],
    'harbhara': ['chana', 'harbhara', 'हरभरा', 'चना'],
    'rajma': ['rajma', 'rajmah', 'राजमा'],
    'rajmah': ['rajma', 'राजमा'],
    'chhole': ['chhole', 'chole', 'kabuli', 'chana', 'छोले', 'काबुली'],
    'chole': ['chhole', 'chole', 'kabuli', 'chana', 'छोले', 'काबुली'],
    'kabuli': ['kabuli', 'chhole', 'chana', 'काबुली', 'छोले'],

    # Oils & Ghee
    'oil': ['oil', 'tel', 'tail', 'तेल', 'mustard', 'sarson', 'ghee'],
    'tel': ['oil', 'tel', 'tail', 'तेल', 'mustard', 'sarson'],
    'tail': ['oil', 'tel', 'तेल'],
    'sarson': ['sarson', 'sarso', 'mustard', 'mohari', 'मोहरी', 'सरसों', 'oil', 'tel'],
    'sarso': ['sarson', 'sarso', 'mustard', 'सरसों', 'तेल', 'oil'],
    'mustard': ['mustard', 'sarson', 'mohari', 'मोहरी', 'सरसों', 'oil', 'tel'],
    'mohari': ['mustard', 'sarson', 'mohari', 'मोहरी', 'तेल'],
    'ghee': ['ghee', 'ghi', 'toop', 'tup', 'तूप', 'घी', 'cow ghee', 'amul'],
    'ghi': ['ghee', 'toop', 'tup', 'तूप', 'घी'],
    'toop': ['ghee', 'toop', 'tup', 'तूप', 'घी'],
    'tup': ['ghee', 'toop', 'tup', 'तूप', 'घी'],

    # Salt, Sugar, Spices
    'salt': ['salt', 'namak', 'meeth', 'mith', 'मीठ', 'नमक', 'tata salt'],
    'namak': ['salt', 'namak', 'meeth', 'मीठ', 'नमक', 'tata'],
    'meeth': ['salt', 'namak', 'meeth', 'मीठ', 'नमक', 'tata salt'],
    'mith': ['salt', 'namak', 'meeth', 'मीठ', 'नमक'],
    'sugar': ['sugar', 'cheeni', 'shakkar', 'saakhar', 'sakhar', 'साखर', 'चीनी', 'शक्कर'],
    'cheeni': ['sugar', 'cheeni', 'shakkar', 'saakhar', 'चीनी', 'साखर'],
    'chini': ['sugar', 'cheeni', 'shakkar', 'saakhar', 'चीनी', 'साखर'],
    'shakkar': ['sugar', 'shakkar', 'cheeni', 'saakhar', 'शक्कर', 'साखर'],
    'saakhar': ['sugar', 'saakhar', 'sakhar', 'cheeni', 'साखर', 'चीनी'],
    'sakhar': ['sugar', 'saakhar', 'sakhar', 'cheeni', 'साखर', 'चीनी'],
    'haldi': ['haldi', 'halad', 'turmeric', 'हळद', 'हल्दी'],
    'halad': ['haldi', 'halad', 'turmeric', 'हळद', 'हल्दी'],
    'turmeric': ['turmeric', 'haldi', 'halad', 'हळद', 'हल्दी'],
    'mirchi': ['mirch', 'mirchi', 'chilli', 'chili', 'tikhat', 'तिखट', 'मिर्च'],
    'mirch': ['mirch', 'mirchi', 'chilli', 'tikhat', 'मिर्च', 'तिखट'],
    'tikhat': ['mirch', 'mirchi', 'tikhat', 'तिखट', 'मिर्च'],
    'chilli': ['mirch', 'mirchi', 'tikhat', 'chilli', 'मिर्च'],
    'chili': ['mirch', 'mirchi', 'tikhat', 'chili', 'मिर्च'],
    'masala': ['masala', 'everest', 'garam masala', 'मसाला'],
    'dhania': ['dhania', 'dhaniya', 'coriander', 'धने', 'धनिया', 'masala'],
    'dhaniya': ['dhania', 'dhaniya', 'coriander', 'धने', 'धनिया', 'masala'],

    # Tea / Beverages
    'tea': ['tea', 'chai', 'chaha', 'चहा', 'चाय', 'tata tea', 'red label', 'wagh bakri', 'taj mahal'],
    'chai': ['tea', 'chai', 'chaha', 'चाय', 'चहा', 'tata tea', 'red label'],
    'chaha': ['tea', 'chai', 'chaha', 'चहा', 'चाय', 'tata tea'],
    'coffee': ['coffee', 'कॉफी'],

    # Cleaning & Oral Care
    'soap': ['soap', 'sabun', 'saabun', 'साबण', 'साबुन', 'dettol', 'rin'],
    'sabun': ['soap', 'sabun', 'saabun', 'साबण', 'साबुन', 'dettol', 'rin'],
    'saabun': ['soap', 'sabun', 'साबण', 'साबुन'],
    'detergent': ['detergent', 'surf', 'surf excel', 'powder', 'सर्फ', 'डिटर्जंट'],
    'surf': ['surf', 'surf excel', 'detergent', 'powder', 'सर्फ'],
    'rin': ['rin', 'bar', 'साबण', 'रिन'],
    'vim': ['vim', 'dishwash', 'व्हिम', 'विम', 'bar'],
    'paste': ['toothpaste', 'paste', 'colgate', 'sensodyne', 'dabur', 'patanjali', 'टूथपेस्ट', 'पेस्ट'],
    'toothpaste': ['toothpaste', 'paste', 'colgate', 'sensodyne', 'dabur', 'patanjali', 'टूथपेस्ट'],
    'colgate': ['colgate', 'toothpaste', 'कोलगेट'],
    'dant': ['dant', 'dantmanjan', 'dant kanti', 'दंत', 'पतंजली', 'डाबर', 'toothpaste'],
    'dettol': ['dettol', 'soap', 'डेटॉल']
}

def calculate_order_credit(items_data):
    """
    Margin-based Store Credit Earning:
    - Loose Mandi commodities (is_loose=True): Wholesale margin 15-25% -> 2.5% Store Credit
    - Packaged Branded FMCG (is_loose=False): Thin margin 3-6% -> 0.5% Store Credit
    """
    total_credit = 0.0
    for item in items_data:
        subtotal = float(item.get('subtotal') or 0.0)
        is_loose = bool(item.get('is_loose', False))

        if item.get('variant_id'):
            v = db.session.get(ProductVariant, item['variant_id'])
            if v:
                qty = int(item.get('quantity', 1))
                if subtotal <= 0:
                    subtotal = v.selling_price * qty
                if v.product and v.product.is_loose:
                    is_loose = True
        elif item.get('product_id'):
            prod = db.session.get(Product, item['product_id'])
            if prod and prod.is_loose:
                is_loose = True

        if is_loose:
            total_credit += subtotal * 0.025
        else:
            total_credit += subtotal * 0.005

    return round(total_credit, 2)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    
    # Enable CORS for frontend development
    CORS(app)

    # SQLite Database setup
    db_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(db_dir, 'kirana.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        # SQLite migration to ensure username column and unique indices
        import sqlite3
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        try:
            cur.execute("PRAGMA table_info(users)")
            cols = cur.fetchall()
            col_names = [r[1] for r in cols]
            if 'username' not in col_names:
                cur.execute("ALTER TABLE users ADD COLUMN username VARCHAR(60)")
                conn.commit()

            # Ensure email is nullable
            email_col = next((c for c in cols if c[1] == 'email'), None)
            if email_col and email_col[3] == 1:
                cur.execute("PRAGMA foreign_keys = OFF")
                cur.execute("""
                    CREATE TABLE users_migrated (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username VARCHAR(60),
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(120),
                        phone VARCHAR(20) NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        address TEXT,
                        role VARCHAR(20) DEFAULT 'customer',
                        created_at DATETIME
                    )
                """)
                cur.execute("""
                    INSERT INTO users_migrated (id, username, name, email, phone, password_hash, address, role, created_at)
                    SELECT id, username, name, email, phone, password_hash, address, role, created_at FROM users
                """)
                cur.execute("DROP TABLE users")
                cur.execute("ALTER TABLE users_migrated RENAME TO users")
                cur.execute("PRAGMA foreign_keys = ON")
                conn.commit()

            # Deduplicate any duplicate phone numbers in legacy test data
            cur.execute("SELECT phone, COUNT(*) FROM users GROUP BY phone HAVING COUNT(*) > 1")
            dups = cur.fetchall()
            for p_dup, cnt in dups:
                cur.execute("SELECT id FROM users WHERE phone = ?", (p_dup,))
                rows = cur.fetchall()
                for idx, r in enumerate(rows[1:], start=1):
                    new_p = f"{p_dup[:9]}{idx}"
                    cur.execute("UPDATE users SET phone = ? WHERE id = ?", (new_p, r[0]))
            conn.commit()

            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_users_username ON users(username) WHERE username IS NOT NULL")
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_users_phone ON users(phone)")
            conn.commit()

            # Ensure users.wallet_balance column exists
            cur.execute("PRAGMA table_info(users)")
            current_user_cols = [r[1] for r in cur.fetchall()]
            if 'wallet_balance' not in current_user_cols:
                cur.execute("ALTER TABLE users ADD COLUMN wallet_balance FLOAT DEFAULT 0.0")
                conn.commit()

            # Ensure orders.credit_used and orders.credit_earned columns exist
            cur.execute("PRAGMA table_info(orders)")
            order_cols = [r[1] for r in cur.fetchall()]
            if 'credit_used' not in order_cols:
                cur.execute("ALTER TABLE orders ADD COLUMN credit_used FLOAT DEFAULT 0.0")
                conn.commit()
            if 'credit_earned' not in order_cols:
                cur.execute("ALTER TABLE orders ADD COLUMN credit_earned FLOAT DEFAULT 0.0")
                conn.commit()
        except Exception as e:
            print("Migration warning:", e)
        finally:
            conn.close()

        db.create_all()
        # Seed default admin and inventory if empty or missing admin
        if Category.query.count() == 0 or User.query.filter_by(role='admin').count() == 0:
            seed_database()

    # --- AUTHENTICATION HELPERS ---

    def get_current_user():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        token = auth_header.split(' ')[1]
        try:
            data = serializer.loads(token, max_age=86400 * 30) # 30 days
            user_id = data.get('user_id')
            return db.session.get(User, user_id)
        except (SignatureExpired, BadSignature, Exception):
            return None

    def admin_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user or user.role != 'admin':
                return jsonify({
                    'error': 'Forbidden: Admin access required. Customers cannot modify store data.'
                }), 403
            return f(*args, **kwargs)
        return decorated

    def login_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Unauthorized: Please login to continue.'}), 401
            return f(user, *args, **kwargs)
        return decorated

    # --- AUTH ROUTES ---

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip().lower()
        phone = (data.get('phone') or '').strip()
        password = (data.get('password') or '').strip()
        address = (data.get('address') or '').strip()

        if not name or not password or not phone:
            return jsonify({'error': 'नाव, मोबाईल नंबर आणि पासवर्ड आवश्यक आहेत.', 'code': 'MISSING_FIELDS'}), 400

        # Mandatory & Strict Indian Mobile Validation (10 digits starting with 6,7,8,9)
        if not re.match(r'^[6-9]\d{9}$', phone):
            return jsonify({'error': 'कृपया १० अंकांचा वैध मोबाईल नंबर टाका (6, 7, 8 किंवा 9 ने सुरू होणारा).', 'code': 'INVALID_PHONE'}), 400

        # Reject dummy or fake phone numbers
        if is_dummy_phone(phone):
            return jsonify({'error': 'अवैध मोबाईल नंबर! डमी नंबर (उदा. 0000000000, 1234567890, 9876543210) चालणार नाही.', 'code': 'DUMMY_PHONE'}), 400

        # Enforce unique phone
        if User.query.filter_by(phone=phone).first():
            return jsonify({'error': 'हा मोबाईल नंबर आधीच नोंदणीकृत आहे. कृपया लॉगिन करा किंवा पासवर्ड रीसेट करा.', 'code': 'PHONE_EXISTS'}), 400

        # Unique username validation (if provided)
        if username:
            if not re.match(r'^[a-zA-Z0-9_.-]{3,30}$', username):
                return jsonify({'error': 'युझरनेम ३ ते ३० अक्षरांचे (फक्त अक्षरे, अंक, _, . किंवा -) असावे.', 'code': 'INVALID_USERNAME'}), 400
            if User.query.filter_by(username=username).first():
                return jsonify({'error': f'युझरनेम "{username}" आधीच वापरले गेले आहे. कृपया दुसरे नाव निवडा.', 'code': 'USERNAME_EXISTS'}), 400
        else:
            username = None

        # Optional Email Validation
        if email:
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                return jsonify({'error': 'कृपया वैध ईमेल पत्ता टाका (उदा. name@example.com)', 'code': 'INVALID_EMAIL'}), 400
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'या ईमेलवर आधीच खाते अस्तित्वात आहे.', 'code': 'EMAIL_EXISTS'}), 400
        else:
            email = None

        user = User(
            name=name,
            username=username,
            email=email,
            phone=phone,
            address=address,
            role='customer' # Strict role enforcement
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = serializer.dumps({'user_id': user.id, 'role': user.role})
        return jsonify({
            'message': 'Registration successful! Welcome to Komal Mart.',
            'token': token,
            'user': user.to_dict()
        }), 201

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json() or {}
        identifier = (data.get('identifier') or data.get('email') or data.get('phone') or data.get('username') or '').strip()
        password = data.get('password', '').strip()

        if not identifier or not password:
            return jsonify({'error': 'मोबाईल नंबर/ईमेल/युझरनेम आणि पासवर्ड आवश्यक आहे.', 'code': 'MISSING_FIELDS'}), 400

        # Find user by email, phone, or username
        user = User.query.filter(
            (User.email == identifier.lower()) |
            (User.phone == identifier) |
            (User.username == identifier)
        ).first()

        if not user:
            return jsonify({'error': 'या तपशीलांशी जुळणारे कोणतेही खाते सापडले नाही. कृपया नवीन खाते तयार करा.', 'code': 'USER_NOT_FOUND'}), 404

        if not user.check_password(password):
            return jsonify({'error': 'चुकीचा पासवर्ड! कृपया योग्य पासवर्ड टाका.', 'code': 'INVALID_CREDENTIALS'}), 401

        # Check if user is Admin -> Strict Whitelist and 2FA Verification
        if user.role == 'admin':
            if user.email not in ADMIN_WHITELIST:
                return jsonify({'error': 'अनाधिकृत प्रवेश: केवळ अधिकृत दुकान मालक ईमेलद्वारे ॲडमिन ॲक्सेस शक्य आहे.', 'code': 'UNAUTHORIZED_ADMIN'}), 403

            # Generate 6-digit OTP
            otp = f"{random.randint(100000, 999999)}"
            temp_token = serializer.dumps({'email': user.email, 'purpose': 'admin_2fa'}, salt='admin-2fa-salt')
            ADMIN_2FA_STORE[user.email] = {
                'otp': otp,
                'expires_at': time.time() + 300, # 5 minutes
                'user_id': user.id
            }

            print("\n=======================================================")
            print("[KOMAL MART ADMIN 2FA OTP] Storekeeper Login OTP")
            print(f"Admin Email: {user.email}")
            print(f"6-Digit OTP Code: {otp}")
            print("Valid for 5 minutes")
            print("=======================================================\n")

            # Dispatch email via SMTP if configured
            email_sent, _ = send_admin_otp_email(user.email, otp)

            parts = user.email.split('@')
            masked = (parts[0][:2] + '***' + parts[0][-2:] + '@' + parts[1]) if len(parts[0]) > 4 else user.email

            return jsonify({
                'require_2fa': True,
                'temp_token': temp_token,
                'masked_email': masked,
                'admin_email': user.email,
                'email_dispatched': email_sent,
                'message': f'सुरक्षा पडताळणी: ६-अंकी OTP कोड {masked} वर पाठवला आहे.'
            })

        # Regular customer login -> Direct JWT
        token = serializer.dumps({'user_id': user.id, 'role': user.role})
        return jsonify({
            'message': 'Login successful!',
            'token': token,
            'user': user.to_dict()
        })

    @app.route('/api/auth/verify-admin-2fa', methods=['POST'])
    def verify_admin_2fa():
        data = request.get_json() or {}
        temp_token = data.get('temp_token', '').strip()
        otp_input = data.get('otp', '').strip()

        if not temp_token or not otp_input:
            return jsonify({'error': 'Temp token and 6-digit OTP are required', 'code': 'MISSING_FIELDS'}), 400

        try:
            payload = serializer.loads(temp_token, salt='admin-2fa-salt', max_age=300)
            email = payload.get('email')
        except (SignatureExpired, BadSignature, Exception):
            return jsonify({'error': '२-स्टेप पडताळणी सत्र संपले आहे. कृपया पुन्हा लॉगिन करा.', 'code': 'SESSION_EXPIRED'}), 401

        record = ADMIN_2FA_STORE.get(email)
        if not record:
            return jsonify({'error': 'कोणताही सक्रिय OTP सापडला नाही. कृपया पुन्हा लॉगिन करा.', 'code': 'OTP_NOT_FOUND'}), 400

        if time.time() > record['expires_at']:
            ADMIN_2FA_STORE.pop(email, None)
            return jsonify({'error': 'OTP कोडची मुदत संपली आहे. कृपया नवीन OTP मागवा.', 'code': 'OTP_EXPIRED'}), 400

        if record['otp'] != otp_input:
            return jsonify({'error': 'चुकीचा OTP कोड! कृपया योग्य ६-अंकी कोड टाका.', 'code': 'INVALID_OTP'}), 400

        # OTP valid! Issue Admin JWT Token
        ADMIN_2FA_STORE.pop(email, None)
        user = db.session.get(User, record['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized admin account', 'code': 'UNAUTHORIZED_ADMIN'}), 403

        token = serializer.dumps({'user_id': user.id, 'role': user.role})
        return jsonify({
            'message': 'दुकानदार २-स्टेप व्हेरिफिकेशन यशस्वी! स्वागत आहे.',
            'token': token,
            'user': user.to_dict()
        })

    @app.route('/api/auth/reset-password', methods=['POST'])
    def reset_password():
        data = request.get_json() or {}
        phone = data.get('phone', '').strip()
        new_password = data.get('new_password', '').strip()

        if not phone or not new_password:
            return jsonify({'error': 'मोबाईल नंबर आणि नवीन पासवर्ड आवश्यक आहेत.', 'code': 'MISSING_FIELDS'}), 400

        if len(new_password) < 4:
            return jsonify({'error': 'नवीन पासवर्ड किमान ४ अक्षरांचा असावा.', 'code': 'PASSWORD_TOO_SHORT'}), 400

        user = User.query.filter_by(phone=phone).first()
        if not user:
            return jsonify({'error': 'या मोबाईल नंबरवर कोणतेही खाते सापडले नाही.', 'code': 'USER_NOT_FOUND'}), 404

        user.set_password(new_password)
        db.session.commit()
        return jsonify({
            'message': 'पासवर्ड यशस्वीरीत्या बदलला आहे! आता नवीन पासवर्डने लॉगिन करा.'
        })

    @app.route('/api/auth/me', methods=['GET'])
    def get_me():
        user = get_current_user()
        if not user:
            return jsonify({'user': None})
        return jsonify({'user': user.to_dict()})

    @app.route('/api/auth/profile', methods=['PUT'])
    def update_profile():
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.get_json() or {}
        if 'name' in data and data['name'].strip():
            user.name = data['name'].strip()
        if 'phone' in data and data['phone'].strip():
            new_phone = data['phone'].strip()
            if not re.match(r'^[6-9]\d{9}$', new_phone):
                return jsonify({'error': 'कृपया १० अंकांचा वैध मोबाईल नंबर टाका.', 'code': 'INVALID_PHONE'}), 400
            if is_dummy_phone(new_phone):
                return jsonify({'error': 'अवैध मोबाईल नंबर! डमी नंबर चालणार नाही.', 'code': 'DUMMY_PHONE'}), 400
            existing = User.query.filter_by(phone=new_phone).first()
            if existing and existing.id != user.id:
                return jsonify({'error': 'हा मोबाईल नंबर आधीच दुसऱ्या खात्याशी जोडलेला आहे.', 'code': 'PHONE_EXISTS'}), 400
            user.phone = new_phone
        if 'address' in data:
            user.address = data['address'].strip()

        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully!',
            'user': user.to_dict()
        })

    # --- CUSTOMER ACCOUNT & ORDER ROUTES ---

    @app.route('/api/customer/orders', methods=['GET'])
    def get_customer_orders():
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Please login to view your orders'}), 401

        orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
        return jsonify([o.to_dict() for o in orders])

    @app.route('/api/customer/orders/<int:order_id>/pay', methods=['POST'])
    def pay_customer_order(order_id):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401

        order = Order.query.filter_by(id=order_id, user_id=user.id).first_or_404()
        order.payment_status = 'Paid'
        db.session.commit()

        return jsonify({
            'message': f'Order {order.order_number} payment recorded successfully! Thank you.',
            'order': order.to_dict()
        })

    # --- PUBLIC STORE ROUTES ---

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'online',
            'store': 'Apna Desi Kirana Store API',
            'time': datetime.now().isoformat()
        })

    @app.route('/api/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.display_order.asc()).all()
        return jsonify([cat.to_dict() for cat in categories])

    @app.route('/api/products', methods=['GET'])
    def get_products():
        category_slug = request.args.get('category')
        search_query = request.args.get('search')
        loose_filter = request.args.get('loose')
        sort_by = request.args.get('sort')

        query = Product.query

        if category_slug:
            category = Category.query.filter_by(slug=category_slug).first()
            if category:
                query = query.filter_by(category_id=category.id)

        if loose_filter in ['true', 'false']:
            is_loose = (loose_filter == 'true')
            query = query.filter_by(is_loose=is_loose)

        # Smart Hinglish & Phonetic Search Aliases Matching
        if search_query:
            from sqlalchemy import or_
            raw_query = search_query.strip().lower()
            tokens = [t.strip() for t in raw_query.split() if t.strip()]

            all_terms = set()
            all_terms.add(raw_query)
            for tok in tokens:
                all_terms.add(tok)
                if tok in SEARCH_ALIASES:
                    for alias in SEARCH_ALIASES[tok]:
                        all_terms.add(alias)

            filter_clauses = []
            for t in all_terms:
                like_term = f"%{t}%"
                filter_clauses.append(Product.name.ilike(like_term))
                filter_clauses.append(Product.name_hi.ilike(like_term))
                filter_clauses.append(Product.brand.ilike(like_term))
                filter_clauses.append(Category.name.ilike(like_term))
                filter_clauses.append(Category.name_hi.ilike(like_term))

            query = query.join(Category).filter(or_(*filter_clauses)).distinct()

        products = query.all()
        result = [p.to_dict() for p in products]

        if sort_by == 'price_asc':
            result.sort(key=lambda p: p['variants'][0]['selling_price'] if p['variants'] else 0)
        elif sort_by == 'price_desc':
            result.sort(key=lambda p: p['variants'][0]['selling_price'] if p['variants'] else 0, reverse=True)
        elif sort_by == 'name':
            result.sort(key=lambda p: p['name'].lower())

        return jsonify(result)

    @app.route('/api/products/<int:product_id>', methods=['GET'])
    def get_product_detail(product_id):
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict())

    # --- ORDER PLACEMENT (CUSTOMER & GUEST) ---

    @app.route('/api/orders', methods=['POST'])
    def place_order():
        data = request.get_json() or {}
        if not data or not data.get('items'):
            return jsonify({'error': 'Cart is empty'}), 400

        user = get_current_user()
        customer_name = data.get('customer_name') or (user.name if user else 'Walk-in Customer')
        customer_phone = data.get('customer_phone') or (user.phone if user else '9876543210')
        customer_address = data.get('customer_address') or (user.address if user else 'Local Delivery')
        payment_method = data.get('payment_method', 'Cash on Delivery (COD)')

        # Only UPI QR code is paid immediately; COD and Khata are Unpaid until cash received
        if payment_method in ['UPI / QR Code', 'Paid via UPI QR']:
            payment_status = 'Paid'
        else:
            payment_status = 'Unpaid'

        order_number = f"KRN-{get_ist_time().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        total_mrp = 0.0
        final_amount = 0.0
        order_items = []

        for item in data['items']:
            # Support both standard variant and custom loose weight items
            if item.get('is_custom_weight'):
                prod_id = item.get('product_id')
                product = db.session.get(Product, prod_id) if prod_id else None
                prod_name = product.name if product else item.get('product_name', 'Kirana Item')
                unit_label = item.get('unit_size', '1kg')
                unit_price = float(item.get('unit_price', 30.0))
                subtotal = round(float(item.get('subtotal', unit_price)), 2)
                item_mrp = round(float(item.get('mrp', unit_price * 1.15)), 2)
                
                total_mrp += item_mrp
                final_amount += subtotal

                order_item = OrderItem(
                    product_id=prod_id,
                    variant_id=None,
                    product_name=prod_name,
                    variant_label=f"{unit_label} (कस्टम तोल)",
                    unit_price=unit_price,
                    quantity=1,
                    subtotal=subtotal
                )
                order_items.append(order_item)
            else:
                variant_id = item.get('variant_id')
                qty = int(item.get('quantity', 1))

                variant = db.session.get(ProductVariant, variant_id) if variant_id else None
                if not variant:
                    continue

                if variant.stock_quantity >= qty:
                    variant.stock_quantity -= qty
                else:
                    variant.stock_quantity = 0

                subtotal = round(variant.selling_price * qty, 2)
                total_mrp += round(variant.mrp * qty, 2)
                final_amount += subtotal

                order_item = OrderItem(
                    product_id=variant.product_id,
                    variant_id=variant.id,
                    product_name=variant.product.name,
                    variant_label=variant.unit_size,
                    unit_price=variant.selling_price,
                    quantity=qty,
                    subtotal=subtotal
                )
                order_items.append(order_item)

        savings = round(total_mrp - final_amount, 2) if total_mrp > final_amount else 0.0

        # Margin-based Store Credit Earning & Redemption
        credit_earned = calculate_order_credit(data['items'])
        use_credit = bool(data.get('use_credit', False))
        credit_used = 0.0

        if use_credit and user and user.wallet_balance and user.wallet_balance > 0:
            credit_available = round(float(user.wallet_balance), 2)
            credit_used = min(credit_available, final_amount)
            final_amount = round(final_amount - credit_used, 2)
            user.wallet_balance = round(user.wallet_balance - credit_used, 2)

        if user:
            user.wallet_balance = round((user.wallet_balance or 0.0) + credit_earned, 2)

        new_order = Order(
            order_number=order_number,
            user_id=user.id if user else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            total_mrp=round(total_mrp, 2),
            final_amount=round(final_amount, 2),
            total_savings=savings,
            credit_used=round(credit_used, 2),
            credit_earned=round(credit_earned, 2),
            payment_method=payment_method,
            payment_status=payment_status,
            status='Placed'
        )
        new_order.items = order_items

        db.session.add(new_order)
        db.session.commit()

        return jsonify({
            'message': 'Order placed successfully! Bill generated.',
            'order': new_order.to_dict(),
            'user': user.to_dict() if user else None
        }), 201

    @app.route('/api/orders/<string:order_number>', methods=['GET'])
    def get_order_by_number(order_number):
        order = Order.query.filter_by(order_number=order_number).first_or_404()
        return jsonify(order.to_dict())

    # --- PROTECTED STORE OWNER / ADMIN ROUTES ---

    @app.route('/api/admin/orders', methods=['GET'])
    @admin_required
    def get_admin_orders():
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return jsonify([o.to_dict() for o in orders])

    @app.route('/api/admin/orders/<int:order_id>/status', methods=['PATCH'])
    @admin_required
    def update_order_status(order_id):
        order = Order.query.get_or_404(order_id)
        data = request.get_json() or {}

        if 'status' in data:
            order.status = data['status']
        if 'payment_status' in data:
            order.payment_status = data['payment_status']

        db.session.commit()
        return jsonify({
            'message': f'Order {order.order_number} status updated to {order.status} ({order.payment_status})',
            'order': order.to_dict()
        })

    @app.route('/api/categories', methods=['POST'])
    @admin_required
    def create_category():
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        name_hi = data.get('name_hi', '').strip() or name
        if not name:
            return jsonify({'error': 'Category name is required'}), 400

        slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
        if not slug:
            slug = f"cat-{uuid.uuid4().hex[:6]}"

        cat = Category.query.filter((Category.slug == slug) | (Category.name.ilike(name))).first()
        if cat:
            return jsonify({'message': 'Category already exists', 'category': cat.to_dict()}), 200

        max_order = db.session.query(db.func.max(Category.display_order)).scalar() or 0
        cat = Category(
            name=name,
            name_hi=name_hi,
            slug=slug,
            icon=data.get('icon', 'package'),
            display_order=max_order + 1
        )
        db.session.add(cat)
        db.session.commit()
        return jsonify({'message': 'Category created successfully!', 'category': cat.to_dict()}), 201

    @app.route('/api/products', methods=['POST'])
    @admin_required
    def add_product():
        data = request.get_json() or {}
        category_id = data.get('category_id')
        new_category_name = data.get('new_category_name', '').strip()
        new_category_name_hi = data.get('new_category_name_hi', '').strip() or new_category_name

        # On-the-fly Category Creation
        if new_category_name:
            cat_slug = re.sub(r'[^a-zA-Z0-9]+', '-', new_category_name.lower()).strip('-')
            if not cat_slug:
                cat_slug = f"cat-{uuid.uuid4().hex[:6]}"
            category = Category.query.filter((Category.slug == cat_slug) | (Category.name.ilike(new_category_name))).first()
            if not category:
                max_order = db.session.query(db.func.max(Category.display_order)).scalar() or 0
                category = Category(
                    name=new_category_name,
                    name_hi=new_category_name_hi,
                    slug=cat_slug,
                    icon='package',
                    display_order=max_order + 1
                )
                db.session.add(category)
                db.session.flush()
            category_id = category.id

        if not data.get('name') or not category_id:
            return jsonify({'error': 'Product name and Category are required'}), 400

        # Multi-angle images support (Front, Back, Packaging)
        images_input = data.get('images')
        if isinstance(images_input, list) and len(images_input) > 0:
            valid_images = [img.strip() for img in images_input if isinstance(img, str) and img.strip()]
            final_image_url = '||'.join(valid_images) if valid_images else '/products/chakki-atta.jpg'
        elif data.get('image_url'):
            final_image_url = str(data['image_url']).strip()
        else:
            final_image_url = '/products/chakki-atta.jpg'

        product = Product(
            category_id=category_id,
            name=data['name'],
            name_hi=data.get('name_hi', ''),
            brand=data.get('brand', 'Local / Loose'),
            is_loose=data.get('is_loose', False),
            description=data.get('description', ''),
            image_url=final_image_url
        )
        db.session.add(product)
        db.session.flush()

        variants_data = data.get('variants', [])
        if not variants_data:
            variants_data = [{"unit_size": "1kg", "mrp": 100.0, "selling_price": 90.0, "stock_quantity": 50}]

        for v in variants_data:
            variant = ProductVariant(
                product_id=product.id,
                unit_size=v.get('unit_size', '1kg'),
                mrp=float(v.get('mrp', 100)),
                selling_price=float(v.get('selling_price', 90)),
                stock_quantity=int(v.get('stock_quantity', 50)),
                is_available=True
            )
            db.session.add(variant)

        db.session.commit()
        return jsonify({'message': 'Product added successfully!', 'product': product.to_dict()}), 201

    @app.route('/api/products/<int:product_id>', methods=['PUT', 'PATCH'])
    @admin_required
    def update_product(product_id):
        product = Product.query.get_or_404(product_id)
        data = request.get_json() or {}

        if 'name' in data and data['name'].strip():
            product.name = data['name'].strip()
        if 'name_hi' in data:
            product.name_hi = data['name_hi'].strip()
        if 'brand' in data:
            product.brand = data['brand'].strip()
        if 'is_loose' in data:
            product.is_loose = bool(data['is_loose'])
        if 'description' in data:
            product.description = data['description'].strip()
        if 'category_id' in data:
            product.category_id = int(data['category_id'])

        # Multi-angle images update
        if 'images' in data:
            images_input = data['images']
            if isinstance(images_input, list):
                valid_images = [img.strip() for img in images_input if isinstance(img, str) and img.strip()]
                product.image_url = '||'.join(valid_images) if valid_images else '/products/chakki-atta.jpg'
            elif isinstance(images_input, str):
                product.image_url = images_input.strip()
        elif 'image_url' in data:
            product.image_url = str(data['image_url']).strip()

        db.session.commit()
        return jsonify({
            'message': f'Product {product.name} updated successfully!',
            'product': product.to_dict()
        })

    @app.route('/api/variants/<int:variant_id>', methods=['PATCH'])
    @admin_required
    def update_variant(variant_id):
        variant = ProductVariant.query.get_or_404(variant_id)
        data = request.get_json() or {}

        if 'selling_price' in data:
            variant.selling_price = float(data['selling_price'])
        if 'mrp' in data:
            variant.mrp = float(data['mrp'])
        if 'stock_quantity' in data:
            variant.stock_quantity = int(data['stock_quantity'])
        if 'is_available' in data:
            variant.is_available = bool(data['is_available'])

        db.session.commit()
        return jsonify({
            'message': 'Variant updated successfully in SQLite!',
            'variant': variant.to_dict()
        })

    @app.route('/api/products/<int:product_id>', methods=['DELETE'])
    @admin_required
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': f'Product {product.name} deleted successfully!'})

    @app.route('/api/reset-seed', methods=['POST'])
    @admin_required
    def reset_seed():
        seed_database()
        return jsonify({'message': 'Database re-seeded successfully with authentic Kirana inventory!'})

    # --- STORE OWNER: REGISTERED CUSTOMERS DIRECTORY & AUDIT ---
    @app.route('/api/admin/users', methods=['GET'])
    @admin_required
    def get_admin_users():
        users = User.query.filter_by(role='customer').order_by(User.created_at.desc()).all()
        result = []
        for u in users:
            # Query all orders linked to this user (by user_id or matching phone)
            user_orders = Order.query.filter(
                (Order.user_id == u.id) | (Order.customer_phone == u.phone)
            ).order_by(Order.created_at.desc()).all()

            total_spent = sum(o.final_amount for o in user_orders)
            unpaid_balance = sum(o.final_amount for o in user_orders if o.payment_status != 'Paid')

            result.append({
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'phone': u.phone,
                'address': u.address or '',
                'created_at': u.created_at.strftime('%d %b %Y'),
                'total_orders': len(user_orders),
                'total_spent': round(total_spent, 2),
                'unpaid_balance': round(unpaid_balance, 2),
                'orders': [o.to_dict() for o in user_orders]
            })
        return jsonify(result)

    # --- STORE OWNER: COUNTER POS / WALK-IN / PHONE ORDER CREATOR ---
    @app.route('/api/admin/orders/create', methods=['POST'])
    @admin_required
    def create_admin_order():
        data = request.get_json() or {}
        items_data = data.get('items', [])
        if not items_data:
            return jsonify({'error': 'कम से कम एक सामान जोड़ना आवश्यक है (Order items cannot be empty)'}), 400

        customer_name = data.get('customer_name', 'काउंटर ग्राहक (Walk-in)').strip()
        customer_phone = data.get('customer_phone', '9999999999').strip()
        customer_address = data.get('customer_address', 'दुकान से काउंटर पिकअप (In-Store Pickup)').strip()
        payment_method = data.get('payment_method', 'Cash on Counter')
        payment_status = data.get('payment_status', 'Paid')
        order_status = data.get('status', 'Delivered')

        # Link to customer account if user_id given or phone matches
        linked_user = None
        if data.get('user_id'):
            linked_user = db.session.get(User, data['user_id'])
        elif customer_phone and customer_phone != '9999999999':
            linked_user = User.query.filter_by(phone=customer_phone).first()

        order_number = f"KRN-{get_ist_time().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        total_mrp = 0.0
        final_amount = 0.0
        order_items = []

        for item in items_data:
            is_custom = item.get('is_custom_weight', False)
            if is_custom:
                prod_id = item.get('product_id')
                product = db.session.get(Product, prod_id) if prod_id else None
                prod_name = product.name if product else item.get('product_name', 'किराना सामान')
                unit_label = item.get('unit_size', '1kg')
                unit_price = float(item.get('unit_price', 30.0))
                subtotal = round(float(item.get('subtotal', unit_price)), 2)
                item_mrp = round(float(item.get('mrp', unit_price * 1.15)), 2)

                total_mrp += item_mrp
                final_amount += subtotal

                order_item = OrderItem(
                    product_id=prod_id,
                    variant_id=None,
                    product_name=prod_name,
                    variant_label=f"{unit_label} (कस्टम तोल)",
                    unit_price=unit_price,
                    quantity=1,
                    subtotal=subtotal
                )
                order_items.append(order_item)
            else:
                variant_id = item.get('variant_id')
                qty = int(item.get('quantity', 1))

                variant = db.session.get(ProductVariant, variant_id) if variant_id else None
                if variant:
                    if variant.stock_quantity >= qty:
                        variant.stock_quantity -= qty
                    else:
                        variant.stock_quantity = 0

                    unit_price = float(item.get('unit_price', variant.selling_price))
                    subtotal = round(unit_price * qty, 2)
                    mrp = float(item.get('mrp', variant.mrp))
                    total_mrp += round(mrp * qty, 2)
                    final_amount += subtotal

                    order_item = OrderItem(
                        product_id=variant.product_id,
                        variant_id=variant.id,
                        product_name=variant.product.name,
                        variant_label=variant.unit_size,
                        unit_price=unit_price,
                        quantity=qty,
                        subtotal=subtotal
                    )
                    order_items.append(order_item)
                else:
                    p_name = item.get('product_name', 'सामान')
                    p_unit = item.get('unit_size', '1 Unit')
                    p_price = float(item.get('unit_price', 10.0))
                    p_mrp = float(item.get('mrp', p_price))
                    subtotal = round(p_price * qty, 2)
                    total_mrp += round(p_mrp * qty, 2)
                    final_amount += subtotal

                    order_item = OrderItem(
                        product_id=item.get('product_id'),
                        variant_id=None,
                        product_name=p_name,
                        variant_label=p_unit,
                        unit_price=p_price,
                        quantity=qty,
                        subtotal=subtotal
                    )
                    order_items.append(order_item)

        savings = round(total_mrp - final_amount, 2) if total_mrp > final_amount else 0.0

        # Margin-based Store Credit Earning & Redemption for Counter POS
        credit_earned = calculate_order_credit(items_data)
        use_credit = bool(data.get('use_credit', False))
        credit_used = 0.0

        if use_credit and linked_user and linked_user.wallet_balance and linked_user.wallet_balance > 0:
            credit_available = round(float(linked_user.wallet_balance), 2)
            credit_used = min(credit_available, final_amount)
            final_amount = round(final_amount - credit_used, 2)
            linked_user.wallet_balance = round(linked_user.wallet_balance - credit_used, 2)

        if linked_user:
            linked_user.wallet_balance = round((linked_user.wallet_balance or 0.0) + credit_earned, 2)

        new_order = Order(
            order_number=order_number,
            user_id=linked_user.id if linked_user else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            total_mrp=round(total_mrp, 2),
            final_amount=round(final_amount, 2),
            total_savings=savings,
            credit_used=round(credit_used, 2),
            credit_earned=round(credit_earned, 2),
            payment_method=payment_method,
            payment_status=payment_status,
            status=order_status
        )
        new_order.items = order_items

        db.session.add(new_order)
        db.session.commit()

        return jsonify({
            'message': f'बिल #{order_number} सफलतापूर्वक दर्ज हुआ!',
            'order': new_order.to_dict(),
            'customer': linked_user.to_dict() if linked_user else None
        }), 201

    # --- DEVICE PHOTO / CAMERA UPLOADS ---
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'public', 'uploads')
    dist_uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(dist_uploads_dir, exist_ok=True)

    @app.route('/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        if os.path.exists(os.path.join(uploads_dir, filename)):
            return send_from_directory(uploads_dir, filename)
        return send_from_directory(dist_uploads_dir, filename)

    @app.route('/api/upload', methods=['POST'])
    @admin_required
    def upload_product_image():
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty file selected'}), 400

        allowed_exts = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp'}
        raw_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
        if raw_ext not in allowed_exts:
            raw_ext = 'jpg'

        unique_name = f"kirana_{uuid.uuid4().hex[:10]}.{raw_ext}"
        file_bytes = file.read()

        # Save to both frontend/public/uploads and frontend/dist/uploads
        path1 = os.path.join(uploads_dir, unique_name)
        path2 = os.path.join(dist_uploads_dir, unique_name)
        with open(path1, 'wb') as f:
            f.write(file_bytes)
        with open(path2, 'wb') as f:
            f.write(file_bytes)

        return jsonify({
            'message': 'Image uploaded successfully!',
            'url': f'/uploads/{unique_name}'
        })

    # --- STATIC FILE SERVING FOR PRODUCTION / SINGLE-PORT RUN ---
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(frontend_dist, path)):
            return send_from_directory(frontend_dist, path)
        elif os.path.exists(os.path.join(frontend_dist, 'index.html')):
            return send_from_directory(frontend_dist, 'index.html')
        else:
            return jsonify({
                'store': 'Apna Desi Kirana Store Backend API',
                'status': 'Backend running.'
            })

    return app


def seed_database():
    """Populates database with authentic Indian Kirana categories, products, and default accounts."""
    OrderItem.query.delete()
    Order.query.delete()
    ProductVariant.query.delete()
    Product.query.delete()
    Category.query.delete()
    
    # Create Whitelisted Store Owner / Admin Accounts
    admin_primary = User.query.filter_by(email='thisisroushan01@gmail.com').first()
    if not admin_primary:
        admin_primary = User(
            name='Roushan (दुकान मालक / Store Owner)',
            username='roushan_admin',
            email='thisisroushan01@gmail.com',
            phone='9820011223',
            address='कोमल मार्ट (Komal Mart), मुख्य बाजार, स्टेशन रोड, मुंबई',
            role='admin'
        )
        admin_primary.set_password('admin123')
        db.session.add(admin_primary)

    admin_sec = User.query.filter_by(email='novaaether01@gmail.com').first()
    if not admin_sec:
        admin_sec = User(
            name='Nova Aether (दुकानदार / Partner)',
            username='novaaether_admin',
            email='novaaether01@gmail.com',
            phone='9820011224',
            address='कोमल मार्ट (Komal Mart), मुख्य बाजार, स्टेशन रोड, मुंबई',
            role='admin'
        )
        admin_sec.set_password('admin123')
        db.session.add(admin_sec)

    # Legacy admin account update if present
    legacy_admin = User.query.filter_by(email='admin@kirana.com').first()
    if legacy_admin:
        legacy_admin.role = 'customer' # demote legacy admin
        legacy_admin.phone = '9820011299'

    # Create Sample Customer Account for testing
    cust_user = User.query.filter_by(email='roushan@example.com').first()
    if not cust_user:
        cust_user = User(
            name='Roushan Kumar',
            username='roushancust',
            email='roushan@example.com',
            phone='9876543210',
            address='Flat 402, Shiv Shakti Apts, Mumbai',
            role='customer'
        )
        cust_user.set_password('customer123')
        db.session.add(cust_user)

    db.session.commit()

    cat_map = {}
    for cat_info in CATEGORIES_DATA:
        category = Category(
            name=cat_info['name'],
            name_hi=cat_info['name_hi'],
            slug=cat_info['slug'],
            icon=cat_info['icon'],
            display_order=cat_info['display_order']
        )
        db.session.add(category)
        db.session.flush()
        cat_map[cat_info['slug']] = category.id

    for prod_info in PRODUCTS_DATA:
        cat_id = cat_map.get(prod_info['category_slug'])
        if not cat_id:
            continue

        product = Product(
            category_id=cat_id,
            name=prod_info['name'],
            name_hi=prod_info['name_hi'],
            brand=prod_info['brand'],
            is_loose=prod_info['is_loose'],
            description=prod_info['description'],
            image_url=prod_info['image_url']
        )
        db.session.add(product)
        db.session.flush()

        for var_info in prod_info['variants']:
            variant = ProductVariant(
                product_id=product.id,
                unit_size=var_info['unit_size'],
                mrp=var_info['mrp'],
                selling_price=var_info['selling_price'],
                stock_quantity=var_info['stock_quantity'],
                is_available=True
            )
            db.session.add(variant)

    db.session.commit()
    print("Database successfully seeded with authentic Indian Kirana inventory & default accounts!")


if __name__ == '__main__':
    app = create_app()
    print("Starting Apna Desi Kirana Store Backend API on http://0.0.0.0:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
