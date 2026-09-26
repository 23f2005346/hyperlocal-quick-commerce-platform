import sys
import os
import json
import sqlite3

# Ensure UTF-8 stdout encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app
MASTER_ADMIN_PIN = os.environ.get('MASTER_ADMIN_PIN', '202699')
from models import db, User, Category, Product, ProductVariant, Order, OrderItem, KhataPayment

app = create_app()

def run_stress_tests():
    client = app.test_client()
    passed = 0
    total = 0

    def assert_test(condition, label, detail=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] {label}")
        else:
            print(f"  [FAIL] {label} -> {detail}")

    print("=" * 65)
    print("KOMAL MART DEEP STRESS & VULNERABILITY TEST SUITE")
    print("=" * 65)

    # -------------------------------------------------------------
    # SUITE 1: SQL INJECTION, XSS & UNICODE FUZZING
    # -------------------------------------------------------------
    print("\n[SUITE 1: Search & Payload Fuzzing]")
    
    sqli_payloads = [
        "' OR 1=1 --",
        "'; DROP TABLE products; --",
        "admin' --",
        "1 UNION SELECT null, null, null, null, null --"
    ]
    for p in sqli_payloads:
        res = client.get(f'/api/products?search={p}')
        assert_test(res.status_code == 200, f"SQLi Search Defense: {p[:20]}")

    xss_payloads = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:void(0)"
    ]
    for p in xss_payloads:
        res = client.get(f'/api/products?search={p}')
        assert_test(res.status_code == 200, f"XSS Search Defense: {p[:20]}")

    unicode_queries = ["तांदूळ", "गहू", "चककी आटा", "🌾", "💥"]
    for q in unicode_queries:
        res = client.get(f'/api/products?search={q}')
        assert_test(res.status_code == 200, f"Unicode / Emoji Search: {q}")

    res = client.get('/api/products?category=completely-invalid-slug-99999')
    assert_test(res.status_code == 200 and len(res.json) == 0, "Invalid Category Slug returns empty list (no 500)")

    # -------------------------------------------------------------
    # SUITE 2: AUTHENTICATION, REGISTRATION & ROLE BOUNDARIES
    # -------------------------------------------------------------
    print("\n[SUITE 2: Auth & Boundary Validation]")
    
    # Invalid phone numbers in registration
    bad_phones = ["", "123", "987654321", "98765432100", "abcdefghij", "98765-43210"]
    for bp in bad_phones:
        res = client.post('/api/auth/register', json={
            'name': 'Test User',
            'phone': bp,
            'password': 'password123'
        })
        assert_test(res.status_code == 400, f"Bad Phone Rejection ({bp or 'empty'})")

    # Unauthorized access to protected admin routes
    admin_routes = [
        ('GET', '/api/admin/orders'),
        ('PATCH', '/api/admin/orders/1/status'),
        ('POST', '/api/products'),
        ('POST', '/api/products/bulk-delete'),
        ('POST', '/api/admin/orders/create'),
        ('POST', '/api/admin/backup/create'),
        ('GET', '/api/admin/reports/daily-z')
    ]
    for method, endpoint in admin_routes:
        if method == 'GET':
            res = client.get(endpoint)
        elif method == 'PATCH':
            res = client.patch(endpoint, json={'status': 'Delivered'})
        else:
            res = client.post(endpoint, json={})
        assert_test(res.status_code in [401, 403], f"Unauthorized Block on {endpoint}")

    # Forged Bearer Token test
    res = client.get('/api/admin/orders', headers={'Authorization': 'Bearer forged.fake.jwt.token'})
    assert_test(res.status_code in [401, 403], "Forged JWT Token Rejected")

    # -------------------------------------------------------------
    # SUITE 3: 2FA RESILIENCE & MASTER PIN
    # -------------------------------------------------------------
    print("\n[SUITE 3: Admin 2FA Resilience]")

    # Request 2FA for authorized admin
    res = client.post('/api/auth/login', json={
        'identifier': 'thisisroushan01@gmail.com',
        'password': 'admin123'
    })
    assert_test(res.status_code == 200 and res.json.get('require_2fa') is True, "Admin 2FA Initiated")
    temp_token = res.json.get('temp_token')

    # Brute-force resistance: wrong OTP
    res = client.post('/api/auth/verify-admin-2fa', json={
        'temp_token': temp_token,
        'otp': '000000'
    })
    assert_test(res.status_code in [400, 401], "Invalid 6-Digit OTP Rejected")

    # Emergency Master PIN Validation
    res = client.post('/api/auth/verify-admin-2fa', json={
        'temp_token': temp_token,
        'otp': MASTER_ADMIN_PIN
    })
    assert_test(res.status_code == 200 and 'token' in res.json, "Emergency Master PIN Accepted")
    admin_token = res.json.get('token')

    # -------------------------------------------------------------
    # SUITE 4: ORDER & CHECKOUT MATH BOUNDARIES
    # -------------------------------------------------------------
    print("\n[SUITE 4: Order Validation & Math Integrity]")

    # Empty cart order
    res = client.post('/api/orders', json={
        'customer_name': 'Roushan',
        'customer_phone': '9820011223',
        'delivery_type': 'home_delivery',
        'customer_address': 'Flat 101, Wadala East, Mumbai - 400037',
        'payment_method': 'Cash on Delivery (COD)',
        'items': []
    })
    assert_test(res.status_code == 400, "Empty Cart Order Rejected")

    # Negative & zero quantity
    res = client.post('/api/orders', json={
        'customer_name': 'Roushan',
        'customer_phone': '9820011223',
        'delivery_type': 'home_delivery',
        'customer_address': 'Wadala - 400037',
        'payment_method': 'Cash on Delivery',
        'items': [{'product_id': 1, 'variant_id': 1, 'quantity': -3}]
    })
    assert_test(res.status_code == 400, "Negative Quantity Rejected")

    res = client.post('/api/orders', json={
        'customer_name': 'Roushan',
        'customer_phone': '9820011223',
        'delivery_type': 'home_delivery',
        'customer_address': 'Wadala - 400037',
        'payment_method': 'Cash on Delivery',
        'items': [{'product_id': 1, 'variant_id': 1, 'quantity': 0}]
    })
    assert_test(res.status_code == 400, "Zero Quantity Rejected")

    # Non-existent product/variant
    res = client.post('/api/orders', json={
        'customer_name': 'Roushan',
        'customer_phone': '9820011223',
        'delivery_type': 'home_delivery',
        'customer_address': 'Wadala - 400037',
        'payment_method': 'Cash on Delivery',
        'items': [{'product_id': 999999, 'variant_id': 999999, 'quantity': 1}]
    })
    assert_test(res.status_code == 400, "Non-existent Variant Rejected")

    # Pincode Validation: Outside Wadala Home Delivery
    res = client.post('/api/orders', json={
        'customer_name': 'Outside User',
        'customer_phone': '9820011223',
        'delivery_type': 'home_delivery',
        'customer_address': 'Bandra West, Mumbai - 400050',
        'payment_method': 'Cash on Delivery',
        'items': [{'product_id': 1, 'variant_id': 1, 'quantity': 1}]
    })
    assert_test(res.status_code == 400, "Outside Wadala Home Delivery Rejected (400050)")

    # Store Counter Pickup with Outside Pincode allowed
    res = client.post('/api/orders', json={
        'customer_name': 'Pickup User',
        'customer_phone': '9820011223',
        'delivery_type': 'pickup',
        'customer_address': 'Bandra West - 400050',
        'payment_method': 'Cash on Delivery',
        'items': [{'product_id': 1, 'variant_id': 1, 'quantity': 1}]
    })
    assert_test(res.status_code == 201, "Store Counter Pickup Allowed for Any Address")

    # Micro-paisa Soundbox assignment on UPI orders
    res = client.post('/api/orders', json={
        'customer_name': 'UPI Customer',
        'customer_phone': '9820011223',
        'delivery_type': 'pickup',
        'customer_address': 'Wadala Counter',
        'payment_method': 'UPI (QR Code)',
        'items': [{'product_id': 1, 'variant_id': 1, 'quantity': 1}]
    })
    assert_test(res.status_code == 201, "UPI Order Placed Successfully")
    order_data = res.json.get('order', {})
    final_amount = order_data.get('final_amount', 0)
    has_paise = (round(final_amount * 100) % 100) > 0
    assert_test(has_paise, f"Micro-Paise Soundbox Assigned (Final: Rs. {final_amount})")

    # -------------------------------------------------------------
    # SUITE 5: Z-REPORT RECONCILIATION & WEEKLY DIGEST
    # -------------------------------------------------------------
    print("\n[SUITE 5: Financial Reconciliation & Reports]")

    # Check Z-Report with valid admin token
    res = client.get('/api/admin/reports/daily-z', headers={'Authorization': f'Bearer {admin_token}'})
    assert_test(res.status_code == 200, "Daily Z-Report API returns 200")
    z_data = res.json
    assert_test('total_cash_in_drawer' in z_data and 'total_upi_received' in z_data, "Z-Report Contains Liquid Cash & UPI splits")

    # Weekly Digest: unauthorized rejection
    res = client.get('/api/reports/weekly-summary')
    assert_test(res.status_code == 401, "Weekly Summary Blocked without Key")

    # Weekly Digest with valid cron key
    res = client.get('/api/reports/weekly-summary?cron_key=komalmart-sunday-cron-2026')
    assert_test(res.status_code == 200, "Weekly Summary Accessible with Secret Cron Key")

    # -------------------------------------------------------------
    # SUITE 6: SQLITE CONCURRENCY & WAL INTEGRITY
    # -------------------------------------------------------------
    print("\n[SUITE 6: SQLite Storage & Hot Backup]")

    with app.app_context():
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode;")
        mode = cursor.fetchone()[0]
        assert_test(mode.lower() == 'wal', f"SQLite Invariant: WAL Mode active ({mode})")
        conn.close()

    res = client.post('/api/admin/backup/create', headers={'Authorization': f'Bearer {admin_token}'}, json={'compress': True})
    assert_test(res.status_code == 201, "Live SQLite Hot Backup Execution")

    print("\n" + "=" * 65)
    print(f"RESULTS: {passed}/{total} TESTS PASSED ({round((passed/total)*100, 1)}%)")
    print("=" * 65)
    return passed == total

if __name__ == '__main__':
    success = run_stress_tests()
    sys.exit(0 if success else 1)
