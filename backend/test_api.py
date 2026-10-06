from app import create_app, prune_in_memory_stores, ADMIN_2FA_STORE, CUSTOMER_RESET_STORE, RESET_COOLDOWN_STORE, RESET_RATE_LIMIT_STORE, LOGIN_ATTEMPTS_STORE, AI_SCAN_RATE_LIMIT_STORE
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

app = create_app()
client = app.test_client()

# 1. Health
h = client.get('/api/health')
print("Health:", h.status_code, h.get_json()['status'])
assert h.status_code == 200

# 2. Customer Registration / Login with Phone & Username Rules
reg_res = client.post('/api/auth/register', json={
    'name': 'Pooja Sharma',
    'username': 'poojasharma2026',
    'email': 'pooja@test.com',
    'phone': '9876543299',
    'password': 'password123',
    'address': 'B-302, Gokuldham Society, Mumbai'
})
if reg_res.status_code == 201:
    print("Customer Registration:", reg_res.status_code, reg_res.get_json().get('user', {}).get('role'))
    cust_token = reg_res.get_json()['token']
else:
    # User exists, login instead (try password123 or newpassword456)
    login_res = client.post('/api/auth/login', json={'identifier': '9876543299', 'password': 'password123'})
    if login_res.status_code != 200:
        login_res = client.post('/api/auth/login', json={'identifier': '9876543299', 'password': 'newpassword456'})
    print("Customer Re-Login with Phone:", login_res.status_code, login_res.get_json().get('user', {}).get('role'))
    cust_token = login_res.get_json()['token']

# 3. Security: Dummy phone, duplicate phone, and missing email rejection
dummy_phone_res = client.post('/api/auth/register', json={
    'name': 'Fake Tester',
    'email': 'faketester@test.com',
    'phone': '1234567890',
    'password': 'pass'
})
print("Dummy Phone Rejection Test:", dummy_phone_res.status_code, "(Should be 400)")
assert dummy_phone_res.status_code == 400

dup_phone_res = client.post('/api/auth/register', json={
    'name': 'Another User',
    'email': 'anotheruser@test.com',
    'phone': '9876543299', # duplicate phone
    'password': 'pass'
})
print("Duplicate Phone Rejection Test:", dup_phone_res.status_code, "(Should be 400)")
assert dup_phone_res.status_code == 400

missing_email_res = client.post('/api/auth/register', json={
    'name': 'No Email User',
    'phone': '9876543211',
    'password': 'pass'
})
print("Missing Email Rejection Test:", missing_email_res.status_code, "(Should be 400)")
assert missing_email_res.status_code == 400

# 4. Security Check: Customer attempts to change price (Should be REJECTED 403)
patch_as_customer = client.patch(
    '/api/variants/1',
    headers={'Authorization': f'Bearer {cust_token}'},
    json={'selling_price': 199.0}
)
print("Customer Price Tamper Attempt:", patch_as_customer.status_code, "(Should be 403)")
assert patch_as_customer.status_code == 403

# 5. Admin Login & 2-Step Verification (2FA)
# 5a. Non-whitelisted email rejection
bad_admin = client.post('/api/auth/login', json={
    'identifier': 'admin@kirana.com',
    'password': 'admin123'
})
print("Unauthorized Admin Email Rejected:", bad_admin.status_code, "(Should be 403 or customer login)")

# 5b. Whitelisted Admin Login Step 1 (Requests 2FA OTP)
admin_res = client.post('/api/auth/login', json={
    'identifier': 'thisisroushan01@gmail.com',
    'password': 'admin123'
})
print("Admin Login Step 1 (2FA Required):", admin_res.status_code, admin_res.get_json().get('require_2fa'))
assert admin_res.status_code == 200
assert admin_res.get_json().get('require_2fa') is True
assert 'otp_preview' not in admin_res.get_json(), "Security leak: OTP preview must not exist in API response"
temp_token = admin_res.get_json()['temp_token']
otp = ADMIN_2FA_STORE['thisisroushan01@gmail.com']['otp']

# 5c. Admin Login Step 2 (Verify OTP)
verify_res = client.post('/api/auth/verify-admin-2fa', json={
    'temp_token': temp_token,
    'otp': otp
})
print("Admin 2FA Verification:", verify_res.status_code, verify_res.get_json().get('user', {}).get('role'))
assert verify_res.status_code == 200
admin_token = verify_res.get_json()['token']

# 6. Admin Authorized Price Update
patch_as_admin = client.patch(
    '/api/variants/1',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={'selling_price': 80.0}
)
print("Admin Authorized Price Update:", patch_as_admin.status_code, patch_as_admin.get_json().get('variant', {}).get('selling_price'))
assert patch_as_admin.status_code == 200

# Revert variant 1 back to standard authentic retail MRP to prevent test mutation
revert_patch = client.patch(
    '/api/variants/1',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={'selling_price': 95.0}
)
assert revert_patch.status_code == 200

# 7. On-The-Fly Custom Category Creation & Product Assignment
new_prod_res = client.post(
    '/api/products',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={
        'name': 'Premium California Almonds (बदाम)',
        'name_hi': 'कॅलिफोर्निया बदाम',
        'brand': 'Mandi Fresh',
        'is_loose': True,
        'new_category_name': 'Dry Fruits & Nuts',
        'new_category_name_hi': 'सुका मेवा व नट्स',
        'variants': [
            {'unit_size': '250g', 'mrp': 280, 'selling_price': 240, 'stock_quantity': 30},
            {'unit_size': '1kg', 'mrp': 1100, 'selling_price': 920, 'stock_quantity': 20}
        ]
    }
)
print("Admin Dynamic Category & Product Creation:", new_prod_res.status_code)
assert new_prod_res.status_code == 201
created_prod = new_prod_res.get_json()['product']
print(f"Created Product in Category: {created_prod['category_name']}, Variants: {len(created_prod['variants'])}")
assert created_prod['category_name'] == 'Dry Fruits & Nuts'

# Clean up dynamically created test product so it doesn't pollute live catalog
del_test_prod = client.delete(
    f"/api/products/{created_prod['id']}",
    headers={'Authorization': f'Bearer {admin_token}'}
)
assert del_test_prod.status_code == 200

# 8. Password Reset via 2-Step Email OTP Flow
# 8a. Step 1: Request OTP via Phone or Email
with app.app_context():
    from models import User, db
    u_pooja = User.query.filter_by(phone='9876543299').first()
    if u_pooja:
        u_pooja.email = 'pooja@test.com'
        db.session.commit()

step1_res = client.post('/api/auth/forgot-password', json={
    'identifier': '9876543299'
})
print("Customer Forgot Password Step 1:", step1_res.status_code, step1_res.get_json())
assert step1_res.status_code == 200
reset_token = step1_res.get_json()['reset_token']
assert 'pooja@test.com' in CUSTOMER_RESET_STORE
otp = CUSTOMER_RESET_STORE['pooja@test.com']['otp']

# 8b. Step 2: Attempt reset with wrong OTP (should fail 400)
bad_reset_res = client.post('/api/auth/reset-password', json={
    'reset_token': reset_token,
    'otp': '000000',
    'new_password': 'newpassword456'
})
assert bad_reset_res.status_code == 400

# 8c. Step 2: Complete reset with correct OTP
reset_res = client.post('/api/auth/reset-password', json={
    'reset_token': reset_token,
    'otp': otp,
    'new_password': 'newpassword456'
})
print("Password Reset via Email OTP:", reset_res.status_code, reset_res.get_json()['message'])
assert reset_res.status_code == 200

# Re-login with new password
relogin_res = client.post('/api/auth/login', json={'identifier': '9876543299', 'password': 'newpassword456'})
assert relogin_res.status_code == 200
cust_token = relogin_res.get_json()['token']

# 9. Admin Counter Bill / POS Creation Test (Walk-in / Phone Order)
pos_res = client.post(
    '/api/admin/orders/create',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={
        'customer_name': 'Ramesh Hotel (Bhai Counter)',
        'customer_phone': '9876543299',
        'customer_address': 'Shop Counter (In-Store Pickup)',
        'order_type': 'restaurant',
        'payment_method': 'Cash on Counter',
        'payment_status': 'Paid',
        'items': [
            {'product_id': 1, 'variant_id': 1, 'quantity': 5, 'unit_price': 80.0, 'mrp': 100.0},
            {'is_custom_weight': True, 'product_id': 2, 'unit_size': '4.5 kg', 'unit_price': 140.0, 'subtotal': 630.0, 'mrp': 700.0}
        ]
    }
)
print("Admin Counter POS Bill Creation:", pos_res.status_code)
assert pos_res.status_code == 201
pos_order = pos_res.get_json()['order']
print(f"Created Counter Bill: {pos_order['order_number']}, Total: Rs.{pos_order['final_amount']}, Status: {pos_order['status']}")

# 10. Admin Registered Users Directory & Khata Audit Test
users_res = client.get('/api/admin/users', headers={'Authorization': f'Bearer {admin_token}'})
print("Admin Users Directory:", users_res.status_code, "Registered Customers:", len(users_res.get_json()))
assert users_res.status_code == 200
assert len(users_res.get_json()) > 0

# 11. SQLite WAL Mode Concurrency Verification
with app.app_context():
    from models import db
    import sqlalchemy as sa
    with db.engine.connect() as conn:
        res = conn.execute(sa.text("PRAGMA journal_mode")).fetchone()
        journal_mode = res[0].lower() if res else ''
        print(f"SQLite Journal Mode: {journal_mode} (Expected: wal)")
        assert journal_mode == 'wal', f"Expected wal, got {journal_mode}"

# 12. "Notify Me" Restock Alert System Test
# Step A: Mark variant 1 as out of stock
patch_stock_zero = client.patch(
    '/api/variants/1',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={'stock_quantity': 0, 'is_available': False}
)
assert patch_stock_zero.status_code == 200

# Step B: Customer registers restock alert
notify_res = client.post('/api/products/1', json={
    'customer_name': 'Santosh Patil',
    'customer_phone': '9820011223',
    'variant_id': 1
})
# Product 1 notify-me endpoint
notify_res = client.post('/api/products/1/notify-me', json={
    'customer_name': 'Santosh Patil',
    'customer_phone': '9820011223',
    'variant_id': 1
})
print("Restock Alert Registration:", notify_res.status_code, notify_res.get_json().get('message'))
assert notify_res.status_code == 201

# Step C: Duplicate registration prevention
dup_notify = client.post('/api/products/1/notify-me', json={
    'customer_name': 'Santosh Patil',
    'customer_phone': '9820011223',
    'variant_id': 1
})
assert dup_notify.status_code == 200
assert dup_notify.get_json().get('already_registered') == True
print("Duplicate Restock Alert Prevention:", dup_notify.status_code, "Already Registered Flag: True")

# Step D: Admin views restock alerts
alerts_res = client.get('/api/admin/restock-alerts', headers={'Authorization': f'Bearer {admin_token}'})
assert alerts_res.status_code == 200
assert alerts_res.get_json()['pending_count'] >= 1
print("Admin Pending Restock Alerts Count:", alerts_res.get_json()['pending_count'])

# Step E: Admin restocks variant 1 (triggers notification)
restock_res = client.patch(
    '/api/variants/1',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={'stock_quantity': 50, 'is_available': True}
)
assert restock_res.status_code == 200
notified_count = restock_res.get_json().get('notified_count', 0)
print("Admin Restock Action:", restock_res.status_code, "Notified Customers:", notified_count)
assert notified_count >= 1

# 13. Safe SQLite Hot Backup Engine Test
backup_create_res = client.post(
    '/api/admin/backup/create',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={'compress': True}
)
print("Admin Backup Create API:", backup_create_res.status_code, backup_create_res.get_json().get('message'))
assert backup_create_res.status_code == 201
assert backup_create_res.get_json().get('integrity_ok') == True

backup_list_res = client.get('/api/admin/backup/list', headers={'Authorization': f'Bearer {admin_token}'})
print("Admin Backup List API:", backup_list_res.status_code, "Total Snapshots:", backup_list_res.get_json().get('count'))
assert backup_list_res.status_code == 200
assert backup_list_res.get_json()['count'] >= 1

backup_dl_res = client.get('/api/admin/backup/download?compress=true', headers={'Authorization': f'Bearer {admin_token}'})
print("Admin 1-Click Backup Download API:", backup_dl_res.status_code, "Content-Length:", len(backup_dl_res.data), "bytes")
assert backup_dl_res.status_code == 200
# 14. Wadala Local Delivery Pincode Guard Tests
# 14a. Rejection: Home Delivery with outside pincode (e.g., 400050 Bandra)
out_zone_order = client.post('/api/orders', json={
    'customer_name': 'Bandra Customer',
    'customer_phone': '9820099887',
    'customer_address': 'Hill Road, Bandra West, Mumbai 400050',
    'delivery_type': 'home_delivery',
    'pincode': '400050',
    'items': [{'variant_id': 1, 'quantity': 1}]
})
print("Outside Wadala Home Delivery Rejection:", out_zone_order.status_code, "(Should be 400)")
assert out_zone_order.status_code == 400
assert 'Wadala' in out_zone_order.get_json()['error']

# 14b. Rejection: Home Delivery with outside pincode in address string even if pincode field is omitted
out_zone_addr_order = client.post('/api/orders', json={
    'customer_name': 'Andheri Customer',
    'customer_phone': '9820099887',
    'customer_address': 'Lokhandwala Complex, Andheri 400053',
    'delivery_type': 'home_delivery',
    'items': [{'variant_id': 1, 'quantity': 1}]
})
print("Outside Wadala Address Pincode Rejection:", out_zone_addr_order.status_code, "(Should be 400)")
assert out_zone_addr_order.status_code == 400

# 14c. Acceptance: Home Delivery within Wadala (400031)
wadala_order = client.post('/api/orders', json={
    'customer_name': 'Wadala Resident',
    'customer_phone': '9820099887',
    'customer_address': 'Katrak Road, Wadala West, Mumbai - 400031',
    'delivery_type': 'home_delivery',
    'pincode': '400031',
    'items': [{'variant_id': 1, 'quantity': 1}]
})
print("Wadala Home Delivery Acceptance:", wadala_order.status_code, "(Should be 201)")
assert wadala_order.status_code == 201
assert wadala_order.get_json()['order']['delivery_type'] == 'home_delivery'
assert wadala_order.get_json()['order']['pincode'] == '400031'

# 14d. Acceptance: Store Counter Pickup (Free, accepted from any customer/area)
pickup_order = client.post('/api/orders', json={
    'customer_name': 'Pickup Visitor',
    'customer_phone': '9820099887',
    'customer_address': 'Komal Mart Shop Counter [STORE PICKUP]',
    'delivery_type': 'store_pickup',
    'pincode': '400050',
    'items': [{'variant_id': 1, 'quantity': 1}]
})
print("Store Counter Pickup Acceptance (Any Pincode):", pickup_order.status_code, "(Should be 201)")
# 15. Anti-Fraud UPI Verification Protocol Test
# 15a. Customer placing UPI QR order gets 'Pending Verification' (NOT instant 'Paid')
upi_order_res = client.post('/api/orders', headers={'Authorization': f'Bearer {cust_token}'}, json={
    'customer_name': 'Santosh Patil',
    'customer_phone': '9876543299',
    'customer_address': 'Dosti Acres, Wadala East, Mumbai 400037',
    'delivery_type': 'home_delivery',
    'pincode': '400037',
    'payment_method': 'UPI / QR Code',
    'utr_number': '426899123456',
    'items': [{'variant_id': 1, 'quantity': 2}]
})
assert upi_order_res.status_code == 201
upi_order = upi_order_res.get_json()['order']
print("UPI Order Placed Payment Status:", upi_order['payment_status'], "(Should be 'Pending Verification')")
assert upi_order['payment_status'] == 'Pending Verification'
assert 'UPI UTR: 426899123456' in upi_order['customer_address']

# 15b. Store Owner verifies bank receipt and marks order as 'Paid'
admin_verify_res = client.patch(
    f"/api/admin/orders/{upi_order['id']}/status",
    headers={'Authorization': f'Bearer {admin_token}'},
    json={'payment_status': 'Paid'}
)
assert admin_verify_res.status_code == 200
verified_order = admin_verify_res.get_json()['order']
print("Admin Verified Payment Status:", verified_order['payment_status'], "(Should be 'Paid')")
assert verified_order['payment_status'] == 'Paid'

# 16. Stock Clearance Sale Tests (Authentic Kirana Discounting)
clearance_patch = client.patch(
    '/api/variants/1',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={
        'is_clearance': True,
        'clearance_price': 55.0
    }
)
assert clearance_patch.status_code == 200
v1_data = clearance_patch.get_json()['variant']
print("Variant Clearance Mode Active:", v1_data['is_clearance'], "Price:", v1_data['clearance_price'])
assert v1_data['is_clearance'] is True
assert v1_data['clearance_price'] == 55.0

# Place order with clearance variant
clearance_order_res = client.post('/api/orders', json={
    'customer_name': 'Clearance Tester',
    'customer_phone': '9820011988',
    'delivery_type': 'counter_pickup',
    'payment_method': 'Cash on Delivery',
    'items': [{'variant_id': 1, 'quantity': 2}]
})
assert clearance_order_res.status_code == 201
clearance_order = clearance_order_res.get_json()['order']
print("Clearance Order Final Amount:", clearance_order['final_amount'], "(Expected: 110.0)")
assert clearance_order['final_amount'] == 110.0

# Revert clearance mode so test does not pollute production/staging database
client.patch(
    '/api/admin/products/variants/1',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={'is_clearance': False, 'clearance_price': None, 'selling_price': 95.0, 'mrp': 95.0}
)

# 17. Weekly Summary Report Tests
# 17a. Unauthorized rejection without cron key or token
unauth_weekly = client.get('/api/reports/weekly-summary')
assert unauth_weekly.status_code == 401
print("Weekly Report Unauthorized Rejection:", unauth_weekly.status_code)

# 17b. Authorized with cron key (without sending email for fast test)
cron_weekly = client.get('/api/reports/weekly-summary?cron_key=komalmart-sunday-cron-2026&send_email=false')
assert cron_weekly.status_code == 200
weekly_data = cron_weekly.get_json()['report']
print("Weekly Report via Cron Key: Total Orders:", weekly_data['total_orders_count'], "Net Sales: Rs.", weekly_data['net_sales'])
assert weekly_data['total_orders_count'] >= 1

# 17c. Authorized with Admin token
# 18. Batch Photo Ingestion Pipeline API Test
batch_res = client.post(
    '/api/admin/batch-ingest-photos',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={'dry_run': True}
)
assert batch_res.status_code == 200
assert batch_res.get_json()['success'] is True
print("Admin Batch Photo Ingest API: 200 Success: True")

# 19. Add to Active Delivery Integration Test (Plugs Margin Leak)
from models import Order, ProductVariant, Product, db
with app.app_context():
    test_ord = Order.query.first()
    test_var = ProductVariant.query.filter(ProductVariant.stock_quantity > 5).first()
    if test_ord and test_var:
        # 19a. Unauthorized check
        addon_unauth = client.post(f'/api/orders/{test_ord.order_number}/add-item', json={'variant_id': test_var.id, 'quantity': 1})
        assert addon_unauth.status_code == 403
        print("Add-Item Unauthorized Rejection: 403 (Should be 403)")

        # 19b. Authorized check when Placed
        orig_st = test_ord.status
        test_ord.status = 'Placed'
        db.session.commit()

        addon_ok = client.post(f'/api/orders/{test_ord.order_number}/add-item', json={
            'variant_id': test_var.id,
            'quantity': 1,
            'token': test_ord.tracking_token
        })
        assert addon_ok.status_code == 200
        print("Add-Item Authorized Appending: 200 Success:", addon_ok.get_json()['added_item']['name'])

        # 19c. Dispatch window closed when Out for Delivery
        test_ord.status = 'Out for Delivery'
        db.session.commit()

        addon_closed = client.post(f'/api/orders/{test_ord.order_number}/add-item', json={
            'variant_id': test_var.id,
            'quantity': 1,
            'token': test_ord.tracking_token
        })
        assert addon_closed.status_code == 400
        assert addon_closed.get_json()['code'] == 'DISPATCH_WINDOW_CLOSED'
        print("Add-Item Dispatch Window Closed: 400 DISPATCH_WINDOW_CLOSED")

        # Restore status
        test_ord.status = orig_st
        db.session.commit()

# 20. Paid Order Add-on Partial Payment & Balance Reconciliation Test
with app.app_context():
    test_ord = Order.query.first()
    test_var = ProductVariant.query.filter(ProductVariant.stock_quantity > 5).first()
    if test_ord and test_var:
        test_ord.status = 'Placed'
        test_ord.payment_status = 'Paid'
        test_ord.amount_paid = float(test_ord.final_amount or 0.0)
        orig_amount_paid = test_ord.amount_paid
        db.session.commit()

        addon_res = client.post(f'/api/orders/{test_ord.order_number}/add-item', json={
            'variant_id': test_var.id,
            'quantity': 1,
            'token': test_ord.tracking_token
        })
        assert addon_res.status_code == 200
        ord_payload = addon_res.get_json()['order']
        assert ord_payload['payment_status'] == 'Partially Paid'
        assert ord_payload['amount_paid'] == orig_amount_paid
        assert ord_payload['balance_due'] > 0
        assert round(ord_payload['amount_paid'] + ord_payload['balance_due'], 2) == round(ord_payload['final_amount'], 2)
        print("Paid Order Add-on Partial Reconciliation: 200 (payment_status: Partially Paid, balance_due:", ord_payload['balance_due'], ")")

        admin_settle = client.patch(
            f'/api/admin/orders/{test_ord.id}/status',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'payment_status': 'Paid'}
        )
        assert admin_settle.status_code == 200
        settled_ord = admin_settle.get_json()['order']
        assert settled_ord['payment_status'] == 'Paid'
        assert settled_ord['balance_due'] == 0.0
        assert settled_ord['amount_paid'] == settled_ord['final_amount']
        print("Admin Full Balance Settlement: 200 (payment_status: Paid, balance_due: 0.0)")

# 21. Custom-Weight Price Manipulation Defense Test (Audit Issue #1)
with app.app_context():
    loose_prod = Product.query.filter_by(is_loose=True).first()
    if loose_prod and loose_prod.variants:
        real_var = loose_prod.variants[0]
        tamper_res = client.post('/api/orders', json={
            'customer_name': 'Audit Tester',
            'customer_phone': '9876543210',
            'customer_address': 'Vitthal Rukhmai CHS, Wadala 400031',
            'delivery_type': 'store_pickup',
            'pincode': '400031',
            'payment_method': 'Cash on Counter',
            'items': [{
                'product_id': loose_prod.id,
                'variant_id': real_var.id,
                'is_custom_weight': True,
                'custom_weight': 1.0,
                'unit_price': 2.0, # Attacker attempts to buy at ₹2
                'subtotal': 2.0,   # Attacker attempts to pay ₹2
                'mrp': 2.0
            }]
        })
        assert tamper_res.status_code == 201
        created_ord = tamper_res.get_json()['order']
        item_unit_price = created_ord['items'][0]['unit_price']
        assert item_unit_price > 2.0, f"Vulnerability detected! Unit price was manipulated: {item_unit_price}"
        print(f"Custom-Weight Tamper Defense: Server computed genuine rate ₹{item_unit_price} (attacker's ₹2 ignored)")

# 22. Support Ticket PII Protection Test (Audit Issue #3)
with app.app_context():
    # Unauthenticated ticket listing must be rejected with 401
    anon_tickets = client.get('/api/support/my-tickets?phone=9876543210')
    assert anon_tickets.status_code == 401
    print("Support Ticket PII Guard: Anonymous ticket listing blocked with 401")

    # Create a test ticket to verify token-based privacy
    post_ticket = client.post('/api/support/ticket', json={
        'customer_name': 'Privacy Test User',
        'customer_phone': '9820123456',
        'ticket_type': 'complaint',
        'category': 'Delivery Delay',
        'message': 'My grocery delivery was delayed by more than an hour.'
    })
    assert post_ticket.status_code == 201
    tk_data = post_ticket.get_json()
    tk_num = tk_data['ticket']['ticket_number']
    tk_token = tk_data['ticket_token']

    # Access without token (anonymous) -> 403
    unauth_tk = client.get(f'/api/support/ticket/{tk_num}')
    assert unauth_tk.status_code == 403

    # Access with invalid/tampered token -> 403
    bad_token_tk = client.get(f'/api/support/ticket/{tk_num}?token=tampered_fake_token')
    assert bad_token_tk.status_code == 403

    # Access with valid cryptographic token -> 200
    valid_token_tk = client.get(f'/api/support/ticket/{tk_num}?token={tk_token}')
    assert valid_token_tk.status_code == 200
    print("Support Ticket Guest Token Guard: Unauthenticated lookup blocked (403), valid signed token allowed (200)")

# 23. Admin 2FA Brute-Force Rate Limiting Test (Audit Issue #4)
with app.app_context():
    admin_login_step1 = client.post('/api/auth/login', json={
        'identifier': 'thisisroushan01@gmail.com',
        'password': 'admin123'
    })
    assert admin_login_step1.status_code == 200
    temp_token = admin_login_step1.get_json()['temp_token']

    # Send 4 invalid attempts -> all should return 400 INVALID_OTP with remaining attempts count
    for i in range(1, 5):
        bad_attempt = client.post('/api/auth/verify-admin-2fa', json={
            'temp_token': temp_token,
            'otp': '000000'
        })
        assert bad_attempt.status_code == 400
        assert bad_attempt.get_json()['code'] == 'INVALID_OTP'
        assert bad_attempt.get_json()['remaining_attempts'] == (5 - i)

    # 5th invalid attempt -> must trigger 429 TOO_MANY_ATTEMPTS
    lockout_attempt = client.post('/api/auth/verify-admin-2fa', json={
        'temp_token': temp_token,
        'otp': '000000'
    })
    assert lockout_attempt.status_code == 429
    assert lockout_attempt.get_json()['code'] == 'TOO_MANY_ATTEMPTS'
    print("Admin 2FA Brute-Force Lockout: 5 failed attempts triggered 429 TOO_MANY_ATTEMPTS")

# 24. Area Delivery Hold Backend Enforcement Test (Audit Issue #5)
with app.app_context():
    hold_test_var = ProductVariant.query.filter(ProductVariant.stock_quantity > 5).first()
    assert hold_test_var is not None

    try:
        # Admin holds pincode 400031
        hold_toggle = client.post(
            '/api/admin/delivery-areas/toggle-hold',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'pincode': '400031', 'is_held': True, 'reason': 'Heavy Rain Test Hold', 'resume': 'Tomorrow 9am'}
        )
        assert hold_toggle.status_code == 200

        # Customer attempts home delivery to held pincode -> must be rejected with 400 AREA_DELIVERY_HELD
        held_order = client.post('/api/orders', json={
            'customer_name': 'Hold Test User',
            'customer_phone': '9876543210',
            'customer_address': 'Vitthal Rukhmai CHS, Wadala 400031',
            'delivery_type': 'home_delivery',
            'pincode': '400031',
            'payment_method': 'Cash on Delivery (COD)',
            'items': [{'variant_id': hold_test_var.id, 'quantity': 1}]
        })
        assert held_order.status_code == 400
        assert held_order.get_json()['code'] == 'AREA_DELIVERY_HELD'
        print("Area Delivery Hold Enforcement: Home delivery to held pincode blocked with 400 AREA_DELIVERY_HELD")

        # Store Counter pickup for held area must succeed
        pickup_order = client.post('/api/orders', json={
            'customer_name': 'Hold Test User',
            'customer_phone': '9876543210',
            'customer_address': 'Vitthal Rukhmai CHS, Wadala 400031',
            'delivery_type': 'store_pickup',
            'pincode': '400031',
            'payment_method': 'Cash on Counter',
            'items': [{'variant_id': hold_test_var.id, 'quantity': 1}]
        })
        assert pickup_order.status_code == 201
        print("Area Delivery Hold Bypass for Pickup: Store Counter pickup allowed during hold (201)")
    finally:
        # Resume delivery for 400031 guaranteed
        resume_toggle = client.post(
            '/api/admin/delivery-areas/toggle-hold',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'pincode': '400031', 'is_held': False}
        )
        assert resume_toggle.status_code == 200
        print("Area Delivery Hold Resumed: Pincode 400031 unheld successfully")

# 25. CSV Export UTF-8 BOM Test (Audit Issue #11)
with app.app_context():
    csv_orders = client.get('/api/admin/export/orders.csv', headers={'Authorization': f'Bearer {admin_token}'})
    assert csv_orders.status_code == 200
    assert csv_orders.data.startswith(b'\xef\xbb\xbf'), "Orders CSV missing UTF-8 BOM"

    csv_cust = client.get('/api/admin/export/customers.csv', headers={'Authorization': f'Bearer {admin_token}'})
    assert csv_cust.status_code == 200
    assert csv_cust.data.startswith(b'\xef\xbb\xbf'), "Customers CSV missing UTF-8 BOM"
    print("CSV Export UTF-8 BOM: Orders & Customers CSV exports properly prepend \\ufeff BOM (no Devanagari mojibake)")

# 26. JWT Token Revocation on Password Change Test (Audit Issue #7)
with app.app_context():
    from models import db, ProductVariant, Product, User, Order

    # 26a. Login as customer and obtain active token
    login_step = client.post('/api/auth/login', json={'identifier': '9876543299', 'password': 'newpassword456'})
    if login_step.status_code != 200:
        login_step = client.post('/api/auth/login', json={'identifier': '9876543299', 'password': 'password123'})
    assert login_step.status_code == 200
    stale_token = login_step.get_json()['token']

    # Confirm token currently grants authenticated access
    me_valid = client.get('/api/auth/me', headers={'Authorization': f'Bearer {stale_token}'})
    assert me_valid.status_code == 200
    assert me_valid.get_json()['user']['phone'] == '9876543299'
    orders_valid_pre = client.get('/api/customer/orders', headers={'Authorization': f'Bearer {stale_token}'})
    assert orders_valid_pre.status_code == 200

    # 26b. Customer resets password via forgot-password email OTP flow
    RESET_COOLDOWN_STORE.clear()
    RESET_RATE_LIMIT_STORE.clear()

    fp_res = client.post('/api/auth/forgot-password', json={'identifier': '9876543299'})
    assert fp_res.status_code == 200
    r_token = fp_res.get_json()['reset_token']
    r_otp = CUSTOMER_RESET_STORE['pooja@test.com']['otp']

    rp_res = client.post('/api/auth/reset-password', json={
        'reset_token': r_token,
        'otp': r_otp,
        'new_password': 'password123'
    })
    assert rp_res.status_code == 200

    # 26c. Stale JWT token MUST now be rejected on all protected endpoints
    me_revoked = client.get('/api/auth/me', headers={'Authorization': f'Bearer {stale_token}'})
    assert me_revoked.get_json().get('user') is None, "Stale token was not invalidated by customer password change!"

    orders_revoked = client.get('/api/customer/orders', headers={'Authorization': f'Bearer {stale_token}'})
    assert orders_revoked.status_code == 401, "Stale token bypassed authentication after customer password change!"

    profile_revoked = client.put('/api/auth/profile', headers={'Authorization': f'Bearer {stale_token}'}, json={'name': 'Hacker'})
    assert profile_revoked.status_code == 401, "Stale token bypassed profile update authorization!"
    print("JWT Token Revocation: Customer password reset immediately invalidated old session token (401)")

    # 26d. Login with new password gives fresh token
    login_fresh = client.post('/api/auth/login', json={'identifier': '9876543299', 'password': 'password123'})
    assert login_fresh.status_code == 200
    fresh_token = login_fresh.get_json()['token']

    orders_fresh = client.get('/api/customer/orders', headers={'Authorization': f'Bearer {fresh_token}'})
    assert orders_fresh.status_code == 200

    # 26e. Admin-triggered password reset also invalidates active sessions
    test_user = User.query.filter_by(phone='9876543299').first()
    assert test_user is not None
    admin_reset = client.post(
        f'/api/admin/customers/{test_user.id}/reset-password',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'new_password': 'newpassword456'}
    )
    assert admin_reset.status_code == 200

    # That fresh_token must now also be rejected
    orders_admin_revoked = client.get('/api/customer/orders', headers={'Authorization': f'Bearer {fresh_token}'})
    assert orders_admin_revoked.status_code == 401, "Admin reset did not invalidate customer session token!"
    print("JWT Token Revocation: Admin password reset immediately invalidated customer session token (401)")

    # Clean up customer password back to password123 for idempotent runs
    test_user.set_password('password123')
    db.session.commit()

# 27. Zero-Stock & Inactive Item Checkout Defense Test (Audit Issue #6)
with app.app_context():
    from models import db, ProductVariant, Product, User, Order

    stock_test_var = ProductVariant.query.filter(ProductVariant.stock_quantity > 0).first()
    assert stock_test_var is not None
    original_stock = stock_test_var.stock_quantity
    original_avail = stock_test_var.is_available

    try:
        # 27a. Insufficient stock on online checkout: Requesting 5 when only 2 in stock -> 400 INSUFFICIENT_STOCK
        stock_test_var.stock_quantity = 2
        stock_test_var.is_available = True
        db.session.commit()

        excess_order = client.post('/api/orders', json={
            'customer_name': 'Stock Tester',
            'customer_phone': '9876543210',
            'customer_address': 'Shop Counter, Wadala 400031',
            'delivery_type': 'store_pickup',
            'pincode': '400031',
            'payment_method': 'Cash on Counter',
            'items': [{'variant_id': stock_test_var.id, 'quantity': 5}]
        })
        assert excess_order.status_code == 400
        assert excess_order.get_json()['code'] == 'INSUFFICIENT_STOCK'
        assert excess_order.get_json()['available_quantity'] == 2
        assert excess_order.get_json()['requested_quantity'] == 5
        print("Zero-Stock Defense: Order exceeding stock rejected with 400 INSUFFICIENT_STOCK")

        # 27b. Inactive / out-of-stock item (is_available=False) -> 400 ITEM_OUT_OF_STOCK
        stock_test_var.is_available = False
        db.session.commit()

        inactive_order = client.post('/api/orders', json={
            'customer_name': 'Stock Tester',
            'customer_phone': '9876543210',
            'customer_address': 'Shop Counter, Wadala 400031',
            'delivery_type': 'store_pickup',
            'pincode': '400031',
            'payment_method': 'Cash on Counter',
            'items': [{'variant_id': stock_test_var.id, 'quantity': 1}]
        })
        assert inactive_order.status_code == 400
        assert inactive_order.get_json()['code'] == 'ITEM_OUT_OF_STOCK'
        print("Zero-Stock Defense: Inactive/out-of-stock item rejected with 400 ITEM_OUT_OF_STOCK")

        # 27c. Loose staple item when all base variants are inactive -> 400 ITEM_OUT_OF_STOCK
        loose_prod = Product.query.filter_by(is_loose=True).first()
        if loose_prod and loose_prod.variants:
            orig_states = {v.id: v.is_available for v in loose_prod.variants}
            try:
                for v in loose_prod.variants:
                    v.is_available = False
                db.session.commit()

                loose_order = client.post('/api/orders', json={
                    'customer_name': 'Stock Tester',
                    'customer_phone': '9876543210',
                    'customer_address': 'Shop Counter, Wadala 400031',
                    'delivery_type': 'store_pickup',
                    'pincode': '400031',
                    'payment_method': 'Cash on Counter',
                    'items': [{'is_custom_weight': True, 'product_id': loose_prod.id, 'unit_size': '500g', 'quantity': 1}]
                })
                assert loose_order.status_code == 400
                assert loose_order.get_json()['code'] == 'ITEM_OUT_OF_STOCK'
                print("Zero-Stock Defense: Loose staple with inactive variants rejected with 400 ITEM_OUT_OF_STOCK")
            finally:
                for v in loose_prod.variants:
                    v.is_available = orig_states[v.id]
                db.session.commit()

        # 27d. Add-to-delivery route (/api/orders/<order_number>/add-item) enforces stock & availability
        # Restore stock for placing a base order
        stock_test_var.is_available = True
        stock_test_var.stock_quantity = 10
        db.session.commit()

        base_order_res = client.post('/api/orders', json={
            'customer_name': 'Add-Item Tester',
            'customer_phone': '9876543210',
            'customer_address': 'Shop Counter, Wadala 400031',
            'delivery_type': 'home_delivery',
            'pincode': '400031',
            'payment_method': 'Cash on Delivery (COD)',
            'items': [{'variant_id': stock_test_var.id, 'quantity': 1}]
        })
        assert base_order_res.status_code == 201
        base_order_num = base_order_res.get_json()['order']['order_number']
        base_track_token = base_order_res.get_json()['order']['tracking_token']

        # Now set variant unavailable and try adding to order
        stock_test_var.is_available = False
        db.session.commit()

        add_unavail = client.post(
            f'/api/orders/{base_order_num}/add-item?token={base_track_token}',
            json={'variant_id': stock_test_var.id, 'quantity': 1}
        )
        assert add_unavail.status_code == 400
        assert add_unavail.get_json()['code'] == 'ITEM_OUT_OF_STOCK'
        print("Zero-Stock Defense: Add-to-delivery rejected inactive variant with 400 ITEM_OUT_OF_STOCK")

        # Now set variant available but stock = 1 and try adding quantity = 5
        stock_test_var.is_available = True
        stock_test_var.stock_quantity = 1
        db.session.commit()

        add_excess = client.post(
            f'/api/orders/{base_order_num}/add-item?token={base_track_token}',
            json={'variant_id': stock_test_var.id, 'quantity': 5}
        )
        assert add_excess.status_code == 400
        assert add_excess.get_json()['code'] == 'INSUFFICIENT_STOCK'
        print("Zero-Stock Defense: Add-to-delivery rejected excess quantity with 400 INSUFFICIENT_STOCK")

    finally:
        # Restore original variant state
        stock_test_var.stock_quantity = original_stock
        stock_test_var.is_available = original_avail
        db.session.commit()

# 28. Trilingual Profile Localization & Admin Email Collision Defense
with app.app_context():
    from models import db, User

    # Log in as test customer
    cust_login = client.post('/api/auth/login', json={'identifier': '9876543299', 'password': 'password123'})
    assert cust_login.status_code == 200, "Customer login failed for profile test"
    cust_token = cust_login.get_json()['token']
    cust_auth_header = {'Authorization': f'Bearer {cust_token}'}

    # 28a. Attempt to claim secondary admin email (novaaether01@gmail.com) -> 400 EMAIL_EXISTS
    # Test English localization
    res_en = client.put('/api/auth/profile', headers=cust_auth_header, json={
        'email': 'novaaether01@gmail.com',
        'lang': 'en'
    })
    assert res_en.status_code == 400
    assert res_en.get_json()['code'] == 'EMAIL_EXISTS'
    assert res_en.get_json()['error'] == 'This email address is already registered to another account.'
    print("Profile Defense: Secondary admin email collision rejected with localized English 400")

    # Test Hindi localization
    res_hi = client.put('/api/auth/profile', headers=cust_auth_header, json={
        'email': 'novaaether01@gmail.com',
        'lang': 'hi'
    })
    assert res_hi.status_code == 400
    assert res_hi.get_json()['code'] == 'EMAIL_EXISTS'
    assert res_hi.get_json()['error'] == 'यह ईमेल पता पहले से दूसरे खाते से जुड़ा हुआ है।'
    print("Profile Defense: Secondary admin email collision rejected with localized Hindi 400")

    # Test Marathi localization (default)
    res_mr = client.put('/api/auth/profile', headers=cust_auth_header, json={
        'email': 'novaaether01@gmail.com',
        'lang': 'mr'
    })
    assert res_mr.status_code == 400
    assert res_mr.get_json()['code'] == 'EMAIL_EXISTS'
    assert res_mr.get_json()['error'] == 'हा ईमेल पत्ता आधीच दुसऱ्या खात्याशी जोडलेला आहे.'
    print("Profile Defense: Secondary admin email collision rejected with localized Marathi 400")

    # 28b. Attempt to claim primary admin email (thisisroushan01@gmail.com) -> 400 EMAIL_EXISTS
    res_admin1 = client.put('/api/auth/profile', headers=cust_auth_header, json={
        'email': 'thisisroushan01@gmail.com',
        'lang': 'en'
    })
    assert res_admin1.status_code == 400
    assert res_admin1.get_json()['code'] == 'EMAIL_EXISTS'
    print("Profile Defense: Primary admin email collision rejected with 400 EMAIL_EXISTS")

    # 28c. Invalid email format -> 400 INVALID_EMAIL (English)
    res_invalid = client.put('/api/auth/profile', headers=cust_auth_header, json={
        'email': 'not-a-valid-email',
        'lang': 'en'
    })
    assert res_invalid.status_code == 400
    assert res_invalid.get_json()['code'] == 'INVALID_EMAIL'
    assert res_invalid.get_json()['error'] == 'Please enter a valid email address (e.g. name@gmail.com).'
    print("Profile Defense: Invalid email rejected with localized English 400")

    # 28d. Valid unique customer email update succeeds
    res_valid = client.put('/api/auth/profile', headers=cust_auth_header, json={
        'email': 'customer_test_unique@example.com'
    })
    assert res_valid.status_code == 200
    assert res_valid.get_json()['user']['email'] == 'customer_test_unique@example.com'
    print("Profile Defense: Valid unique customer email update succeeded (200)")

    # Clean up test customer email back to pooja@test.com
    client.put('/api/auth/profile', headers=cust_auth_header, json={'email': 'pooja@test.com'})

# 29. Truthful Email Dispatch & Instant WhatsApp Failover Guard
with app.app_context():
    from unittest.mock import patch

    RESET_COOLDOWN_STORE.clear()
    RESET_RATE_LIMIT_STORE.clear()

    with patch('app.send_customer_otp_email', return_value=(False, 'Resend sandbox restricted: custom domain required')):
        failover_res = client.post('/api/auth/forgot-password', json={
            'identifier': '9876543299',
            'lang': 'en'
        })
        assert failover_res.status_code == 200
        data = failover_res.get_json()
        assert data['channel'] == 'whatsapp', "Failed email dispatch did not failover to WhatsApp channel!"
        assert data['sent_ok'] == False, "System falsely claimed sent_ok=True on failed email delivery!"
        assert data['email_failed'] == True
        assert 'wa_link' in data and 'wa.me/919142052967' in data['wa_link']
        assert 'Email delivery is currently unavailable' in data['message']
        print("Truthful Email Guard: Failed email delivery gracefully failed over to 1-tap WhatsApp support (channel='whatsapp', sent_ok=False)")

# 30. Strict Packaged Item Quantity Validation & Decimal Truncation Guard (Audit Issue #10)
with app.app_context():
    # 30a. Decimal float quantity (2.9) rejected with 400 INVALID_QUANTITY
    res_dec = client.post('/api/orders', json={
        'items': [{'variant_id': 1, 'quantity': 2.9}],
        'delivery_type': 'store_pickup',
        'customer_name': 'Quantity Tester',
        'customer_phone': '9876543210',
        'lang': 'en'
    })
    assert res_dec.status_code == 400
    assert res_dec.get_json()['code'] == 'INVALID_QUANTITY'
    assert 'whole integer' in res_dec.get_json()['error']
    print("Quantity Defense: Decimal float quantity 2.9 rejected with 400 INVALID_QUANTITY (no silent truncation)")

    # 30b. Decimal string quantity ("2.5") rejected with 400 INVALID_QUANTITY
    res_dec_str = client.post('/api/orders', json={
        'items': [{'variant_id': 1, 'quantity': '2.5'}],
        'delivery_type': 'store_pickup',
        'customer_name': 'Quantity Tester',
        'customer_phone': '9876543210',
        'lang': 'hi'
    })
    assert res_dec_str.status_code == 400
    assert res_dec_str.get_json()['code'] == 'INVALID_QUANTITY'
    print("Quantity Defense: Decimal string quantity '2.5' rejected with localized Hindi 400")

    # 30c. Negative and zero quantities rejected
    res_zero = client.post('/api/orders', json={
        'items': [{'variant_id': 1, 'quantity': 0}],
        'delivery_type': 'store_pickup',
        'customer_name': 'Quantity Tester',
        'customer_phone': '9876543210'
    })
    assert res_zero.status_code == 400
    assert res_zero.get_json()['code'] == 'INVALID_QUANTITY'
    print("Quantity Defense: Zero quantity rejected with 400 INVALID_QUANTITY")

    # 30d. Boolean quantity rejected
    res_bool = client.post('/api/orders', json={
        'items': [{'variant_id': 1, 'quantity': True}],
        'delivery_type': 'store_pickup',
        'customer_name': 'Quantity Tester',
        'customer_phone': '9876543210'
    })
    assert res_bool.status_code == 400
    assert res_bool.get_json()['code'] == 'INVALID_QUANTITY'
    print("Quantity Defense: Boolean quantity True rejected with 400 INVALID_QUANTITY")

# 31. In-Memory Store Periodic Pruning & Memory Leak Defense (Audit Issue #12)
with app.app_context():
    import time
    now_ts = time.time()

    # Populate dummy expired and active records across all 6 stores
    ADMIN_2FA_STORE['audit_expired@admin.com'] = {'otp': '111111', 'expires_at': now_ts - 500, 'locked_until': now_ts - 100}
    ADMIN_2FA_STORE['audit_active@admin.com'] = {'otp': '222222', 'expires_at': now_ts + 500, 'locked_until': now_ts + 100}

    CUSTOMER_RESET_STORE['audit_expired_reset'] = {'otp': '333333', 'expires_at': now_ts - 200}
    CUSTOMER_RESET_STORE['audit_active_reset'] = {'otp': '444444', 'expires_at': now_ts + 200}

    RESET_RATE_LIMIT_STORE['audit_expired_ip'] = [now_ts - 4000]
    RESET_RATE_LIMIT_STORE['audit_active_ip'] = [now_ts - 100]

    RESET_COOLDOWN_STORE['audit_expired_cooldown'] = now_ts - 70
    RESET_COOLDOWN_STORE['audit_active_cooldown'] = now_ts - 10

    LOGIN_ATTEMPTS_STORE['audit_expired_login'] = {'first_attempt': now_ts - 1000, 'locked_until': now_ts - 10}
    LOGIN_ATTEMPTS_STORE['audit_active_login'] = {'first_attempt': now_ts - 100, 'locked_until': now_ts + 500}

    AI_SCAN_RATE_LIMIT_STORE['audit_expired_ai'] = [now_ts - 4000]
    AI_SCAN_RATE_LIMIT_STORE['audit_active_ai'] = [now_ts - 100]

    # Force sweep
    sweep_res = prune_in_memory_stores(force=True)
    assert 'audit_expired@admin.com' not in ADMIN_2FA_STORE and 'audit_active@admin.com' in ADMIN_2FA_STORE
    assert 'audit_expired_reset' not in CUSTOMER_RESET_STORE and 'audit_active_reset' in CUSTOMER_RESET_STORE
    assert 'audit_expired_ip' not in RESET_RATE_LIMIT_STORE and 'audit_active_ip' in RESET_RATE_LIMIT_STORE
    assert 'audit_expired_cooldown' not in RESET_COOLDOWN_STORE and 'audit_active_cooldown' in RESET_COOLDOWN_STORE
    assert 'audit_expired_login' not in LOGIN_ATTEMPTS_STORE and 'audit_active_login' in LOGIN_ATTEMPTS_STORE
    assert 'audit_expired_ai' not in AI_SCAN_RATE_LIMIT_STORE and 'audit_active_ai' in AI_SCAN_RATE_LIMIT_STORE

    # Clean up active test records
    ADMIN_2FA_STORE.pop('audit_active@admin.com', None)
    CUSTOMER_RESET_STORE.pop('audit_active_reset', None)
    RESET_RATE_LIMIT_STORE.pop('audit_active_ip', None)
    RESET_COOLDOWN_STORE.pop('audit_active_cooldown', None)
    LOGIN_ATTEMPTS_STORE.pop('audit_active_login', None)
    AI_SCAN_RATE_LIMIT_STORE.pop('audit_active_ai', None)

    print("Memory Leak Defense: All expired entries across all 6 rate-limiter, lockout & OTP stores purged cleanly")

print("\nALL KOMAL MART 2FA, REGISTRATION, POS, WAL, RESTOCK ALERTS, WADALA GUARD, HOT BACKUP, ANTI-FRAUD UPI, CLEARANCE SALE, WEEKLY REPORT, BATCH INGEST, ADD-TO-DELIVERY & SECURITY AUDIT DEFENSE TESTS PASSED 100%!")


