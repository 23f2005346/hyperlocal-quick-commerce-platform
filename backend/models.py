from datetime import datetime, timezone, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Indian Standard Time (IST = UTC + 05:30)
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_time():
    return datetime.now(IST).replace(tzinfo=None)

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=True)
    role = db.Column(db.String(20), default='customer') # 'customer' or 'admin'
    wallet_balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=get_ist_time)

    orders = db.relationship('Order', backref='customer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'role': self.role,
            'wallet_balance': round(self.wallet_balance or 0.0, 2),
            'created_at': self.created_at.strftime('%d %b %Y')
        }


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    name_hi = db.Column(db.String(100), nullable=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), nullable=True, default='package')
    display_order = db.Column(db.Integer, default=0)

    products = db.relationship('Product', backref='category', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_hi': self.name_hi,
            'slug': self.slug,
            'icon': self.icon,
            'product_count': len(self.products)
        }


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    name_hi = db.Column(db.String(150), nullable=True)
    brand = db.Column(db.String(100), nullable=True, default='Loose / Local')
    is_loose = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_ist_time)

    variants = db.relationship('ProductVariant', backref='product', lazy=True, cascade="all, delete-orphan")
    tiered_prices = db.relationship('TieredPricing', backref='product', lazy=True, cascade="all, delete-orphan", order_by="TieredPricing.min_qty.asc()")
    restock_alerts = db.relationship('RestockAlert', backref='product', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        raw_img = self.image_url or ''
        images = [u.strip() for u in raw_img.split('||') if u.strip()]
        primary_image = images[0] if images else '/products/chakki-atta.jpg'
        if not images:
            images = [primary_image]

        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else '',
            'name': self.name,
            'name_hi': self.name_hi,
            'brand': self.brand,
            'is_loose': self.is_loose,
            'description': self.description,
            'image_url': primary_image,
            'images': images,
            'variants': [v.to_dict() for v in self.variants],
            'tiered_prices': [tp.to_dict() for tp in self.tiered_prices]
        }


class ProductVariant(db.Model):
    __tablename__ = 'product_variants'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    unit_size = db.Column(db.String(50), nullable=False)
    mrp = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=50)
    is_available = db.Column(db.Boolean, default=True)

    restock_alerts = db.relationship('RestockAlert', backref='variant', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        discount_pct = 0
        if self.mrp > self.selling_price:
            discount_pct = round(((self.mrp - self.selling_price) / self.mrp) * 100)
        return {
            'id': self.id,
            'product_id': self.product_id,
            'unit_size': self.unit_size,
            'mrp': self.mrp,
            'selling_price': self.selling_price,
            'discount_pct': discount_pct,
            'stock_quantity': self.stock_quantity,
            'is_available': bool(self.is_available and (self.stock_quantity is None or self.stock_quantity > 0)),
            'is_in_stock': bool(self.is_available)
        }


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(30), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Linked to registered customer
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.Text, nullable=True)
    delivery_type = db.Column(db.String(30), default='home_delivery')
    pincode = db.Column(db.String(10), default='400031')
    total_mrp = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, nullable=False)
    total_savings = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(50), default='Cash on Delivery')
    payment_status = db.Column(db.String(30), default='Unpaid') # 'Paid' or 'Unpaid / Khata'
    status = db.Column(db.String(30), default='Placed') # Placed, Packed, Out for Delivery, Delivered
    credit_used = db.Column(db.Float, default=0.0)
    credit_earned = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=get_ist_time)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_address': self.customer_address,
            'delivery_type': self.delivery_type or 'home_delivery',
            'pincode': self.pincode or '400031',
            'total_mrp': self.total_mrp,
            'final_amount': self.final_amount,
            'total_savings': self.total_savings,
            'credit_used': round(self.credit_used or 0.0, 2),
            'credit_earned': round(self.credit_earned or 0.0, 2),
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'status': self.status,
            'created_at': self.created_at.strftime('%d %b %Y, %I:%M %p'),
            'items': [item.to_dict() for item in self.items]
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=True)
    variant_id = db.Column(db.Integer, nullable=True)
    product_name = db.Column(db.String(150), nullable=False)
    variant_label = db.Column(db.String(50), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    subtotal = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'variant_label': self.variant_label,
            'unit_price': self.unit_price,
            'quantity': self.quantity,
            'subtotal': self.subtotal
        }


class KhataPayment(db.Model):
    __tablename__ = 'khata_payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='Cash') # Cash, UPI, Bank Transfer, Cheque
    note = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=get_ist_time)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'amount': round(self.amount, 2),
            'payment_method': self.payment_method,
            'note': self.note or '',
            'created_at': self.created_at.strftime('%d %b %Y, %I:%M %p')
        }


class TieredPricing(db.Model):
    __tablename__ = 'tiered_pricing'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    min_qty = db.Column(db.Float, nullable=False)
    max_qty = db.Column(db.Float, nullable=True)
    unit_price = db.Column(db.Float, nullable=False)
    tier_label = db.Column(db.String(100), nullable=True)
    tier_label_hi = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=get_ist_time)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'min_qty': self.min_qty,
            'max_qty': self.max_qty,
            'unit_price': round(self.unit_price, 2),
            'tier_label': self.tier_label or f"होलसेल ({self.min_qty}+)",
            'tier_label_hi': self.tier_label_hi or f"होलसेल ({self.min_qty}+)"
        }


class RestockAlert(db.Model):
    __tablename__ = 'restock_alerts'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    is_notified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_ist_time)
    notified_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else '',
            'variant_id': self.variant_id,
            'variant_label': self.variant.unit_size if self.variant else '',
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'is_notified': self.is_notified,
            'created_at': self.created_at.strftime('%d %b %Y, %I:%M %p') if self.created_at else '',
            'notified_at': self.notified_at.strftime('%d %b %Y, %I:%M %p') if self.notified_at else None
        }

