import os
import random
from functools import wraps
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from models import db, User, Category, Product, ProductVariant, Order, OrderItem
from seed_data import CATEGORIES_DATA, PRODUCTS_DATA

SECRET_KEY = 'apna-desi-kirana-store-secret-key-2026'
serializer = URLSafeTimedSerializer(SECRET_KEY)

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
        db.create_all()
        # Seed default admin and inventory if empty
        if Category.query.count() == 0:
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
            return User.query.get(user_id)
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
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '').strip()
        password = data.get('password', '').strip()
        address = data.get('address', '').strip()

        if not name or not email or not password or not phone:
            return jsonify({'error': 'Name, email, phone, and password are required'}), 400

        import re
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return jsonify({'error': 'कृपया सही ईमेल आईडी दर्ज करें (Invalid Email Format)'}), 400

        if not re.match(r'^[6-9]\d{9}$', phone):
            return jsonify({'error': 'कृपया 10 अंकों का सही मोबाइल नंबर दर्ज करें (Must be valid 10-digit Indian number starting with 6-9)'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'इस ईमेल से खाता पहले से मौजूद है (Account already exists)'}), 400

        user = User(
            name=name,
            email=email,
            phone=phone,
            address=address,
            role='customer' # Strict role enforcement: customers can NEVER register as admin
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = serializer.dumps({'user_id': user.id, 'role': user.role})
        return jsonify({
            'message': 'Registration successful! Welcome to Apna Kirana Store.',
            'token': token,
            'user': user.to_dict()
        }), 201

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json() or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'इस ईमेल से कोई खाता नहीं मिला। कृपया पहले नया खाता बनाएं (No account found. Please register first).'}), 404

        if not user.check_password(password):
            return jsonify({'error': 'गलत पासवर्ड। कृपया सही पासवर्ड दर्ज करें (Incorrect password).'}), 401

        token = serializer.dumps({'user_id': user.id, 'role': user.role})
        return jsonify({
            'message': 'Login successful!',
            'token': token,
            'user': user.to_dict()
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
            user.phone = data['phone'].strip()
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

        # Precise search: only matches product name, hindi name, brand, or category
        if search_query:
            term = f"%{search_query.strip()}%"
            query = query.join(Category).filter(
                (Product.name.ilike(term)) |
                (Product.name_hi.ilike(term)) |
                (Product.brand.ilike(term)) |
                (Category.name.ilike(term)) |
                (Category.name_hi.ilike(term))
            )

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

        order_number = f"KRN-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        total_mrp = 0.0
        final_amount = 0.0
        order_items = []

        for item in data['items']:
            # Support both standard variant and custom loose weight items
            if item.get('is_custom_weight'):
                prod_id = item.get('product_id')
                product = Product.query.get(prod_id)
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

                variant = ProductVariant.query.get(variant_id)
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

        new_order = Order(
            order_number=order_number,
            user_id=user.id if user else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            total_mrp=round(total_mrp, 2),
            final_amount=round(final_amount, 2),
            total_savings=savings,
            payment_method=payment_method,
            payment_status=payment_status,
            status='Placed'
        )
        new_order.items = order_items

        db.session.add(new_order)
        db.session.commit()

        return jsonify({
            'message': 'Order placed successfully! Bill generated.',
            'order': new_order.to_dict()
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

    @app.route('/api/products', methods=['POST'])
    @admin_required
    def add_product():
        data = request.get_json() or {}
        if not data.get('name') or not data.get('category_id'):
            return jsonify({'error': 'Name and Category ID are required'}), 400

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
            category_id=data['category_id'],
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
    
    # Create Default Store Owner / Admin Account
    admin_user = User.query.filter_by(email='admin@kirana.com').first()
    if not admin_user:
        admin_user = User(
            name='Storekeeper (दुकानदार / Owner)',
            email='admin@kirana.com',
            phone='9876543210',
            address='Apna Kirana Store, Main Bazaar, Mumbai',
            role='admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()

    # Create Sample Customer Account for testing
    cust_user = User.query.filter_by(email='roushan@example.com').first()
    if not cust_user:
        cust_user = User(
            name='Roushan Kumar',
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
    print("Starting Apna Desi Kirana Store Backend API on http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=True)
