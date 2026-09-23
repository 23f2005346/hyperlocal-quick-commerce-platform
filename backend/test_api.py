from app import create_app, ADMIN_2FA_STORE
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

# 3. Security: Dummy phone and duplicate username rejection
dummy_phone_res = client.post('/api/auth/register', json={
    'name': 'Fake Tester',
    'phone': '1234567890',
    'password': 'pass'
})
print("Dummy Phone Rejection Test:", dummy_phone_res.status_code, "(Should be 400)")
assert dummy_phone_res.status_code == 400

dup_phone_res = client.post('/api/auth/register', json={
    'name': 'Another User',
    'phone': '9876543299', # duplicate phone
    'password': 'pass'
})
print("Duplicate Phone Rejection Test:", dup_phone_res.status_code, "(Should be 400)")
assert dup_phone_res.status_code == 400

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

# 8. Password Reset via Phone
reset_res = client.post('/api/auth/reset-password', json={
    'phone': '9876543299',
    'new_password': 'newpassword456'
})
print("Password Reset via Phone:", reset_res.status_code, reset_res.get_json()['message'])
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
assert pickup_order.status_code == 201
assert pickup_order.get_json()['order']['delivery_type'] == 'store_pickup'

print("\nALL KOMAL MART 2FA, REGISTRATION, POS, WAL, RESTOCK ALERTS, WADALA GUARD & HOT BACKUP TESTS PASSED 100%!")

