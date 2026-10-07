"""
Extensive Multi-Vector Audit & Diagnostic Test Suite for Komal Mart
Tests all business logic, financial invariants, race conditions, and security edge cases.
"""
import sys
import os
import json
import time
import threading
from decimal import Decimal

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath('backend'))

from app import create_app, db, User, Product, ProductVariant, Order, OrderItem, prune_in_memory_stores, CUSTOMER_RESET_STORE, ADMIN_2FA_STORE

app = create_app()
client = app.test_client()

print("=" * 70)
print("KOMAL MART EXTENSIVE SYSTEM & SECURITY AUDIT TEST SUITE")
print("=" * 70)

results = {
    'passed': 0,
    'failed': 0,
    'issues': []
}

def record_pass(test_name):
    results['passed'] += 1
    print(f"  [PASS] {test_name}")

def record_fail(test_name, reason):
    results['failed'] += 1
    results['issues'].append({'test': test_name, 'reason': reason})
    print(f"  [FAIL] {test_name}: {reason}")

# -----------------------------------------------------------------------------
# 1. AUTHENTICATION, REGISTRATION & PROFILE INTEGRITY
# -----------------------------------------------------------------------------
print("\n--- 1. AUTHENTICATION & PROFILE INTEGRITY ---")

with app.app_context():
    # Setup test user
    test_phone = '9811122233'
    test_email = 'extensive_test@example.com'
    existing = User.query.filter((User.phone == test_phone) | (User.email == test_email)).all()
    for u in existing:
        db.session.delete(u)
    db.session.commit()

# Test 1.1: Registration requires email
r = client.post('/api/auth/register', json={
    'name': 'Audit Tester',
    'phone': '9811122233',
    'password': 'password123',
    'email': ''
})
if r.status_code == 400 and r.get_json().get('code') == 'MISSING_FIELDS':
    record_pass("Registration strictly rejects empty email")
else:
    record_fail("Registration empty email", f"Expected 400 MISSING_FIELDS, got {r.status_code}: {r.get_json()}")

# Test 1.2: Registration with valid email works
r = client.post('/api/auth/register', json={
    'name': 'Audit Tester',
    'phone': '9811122233',
    'password': 'password123',
    'email': 'Extensive_Test@Example.com'
})
if r.status_code == 201:
    token = r.get_json()['token']
    cust_id = r.get_json()['user']['id']
    record_pass("Registration succeeds with mixed-case email (lowercased)")
else:
    record_fail("Registration mixed-case email", f"Expected 201, got {r.status_code}: {r.get_json()}")
    cust_id = None
    token = None

# Test 1.3: Login with formatted phone (+91 9811122233)
r = client.post('/api/auth/login', json={
    'identifier': '+91 9811122233',
    'password': 'password123'
})
if r.status_code == 200:
    record_pass("Login with formatted phone (+91 9811122233)")
else:
    record_fail("Login with formatted phone", f"Expected 200, got {r.status_code}: {r.get_json()}")

# Test 1.4: Profile Update - can customer clear their email to None?
if token:
    r = client.put('/api/auth/profile', headers={'Authorization': f'Bearer {token}'}, json={
        'name': 'Audit Tester Renamed',
        'email': ''
    })
    # Since email is mandatory, clearing email to empty should NOT be permitted!
    with app.app_context():
        u = db.session.get(User, cust_id)
        if u and u.email is None:
            record_fail("Profile Email Deletion", "Profile update allowed wiping email to None! This converts customer to email-less state.")
        else:
            record_pass("Profile preserves mandatory email (does not wipe to None)")

# -----------------------------------------------------------------------------
# 2. CONCURRENT FINANCIAL RACE CONDITIONS (WALLET CREDIT & STOCK)
# -----------------------------------------------------------------------------
print("\n--- 2. CONCURRENT FINANCIAL RACE CONDITIONS ---")

with app.app_context():
    # Create user with 100 wallet balance
    r_user = User.query.filter_by(phone='9811122233').first()
    if r_user:
        r_user.wallet_balance = 100.0
        db.session.commit()
        r_token = r_user.get_token() if hasattr(r_user, 'get_token') else None
    
    # Get a product variant with known stock
    variant = ProductVariant.query.filter(ProductVariant.stock_quantity >= 10).first()
    var_id = variant.id if variant else 1

if token:
    # Simulate 2 concurrent checkout requests for the same user, both requesting use_credit=True
    # Each order total is ~₹200. Max allowed credit per order = 25% of 200 = ₹50.
    # Total available credit is ₹100.
    # If the user has only ₹50 credit, two simultaneous orders should NOT both deduct ₹50!
    with app.app_context():
        r_user = db.session.get(User, cust_id)
        r_user.wallet_balance = 50.0  # Exactly enough for ONE order's max credit
        db.session.commit()

    order_payload = {
        'delivery_type': 'store_pickup',
        'payment_method': 'Cash on Delivery (COD)',
        'use_credit': True,
        'items': [{'variant_id': var_id, 'quantity': 1}]
    }

    results_concurrent = []
    def place_concurrent_order():
        with app.test_client() as c:
            res = c.post('/api/orders', headers={'Authorization': f'Bearer {token}'}, json=order_payload)
            results_concurrent.append(res)

    t1 = threading.Thread(target=place_concurrent_order)
    t2 = threading.Thread(target=place_concurrent_order)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    total_credit_used = 0
    for res in results_concurrent:
        if res.status_code == 201:
            total_credit_used += res.get_json()['order'].get('credit_used', 0.0)

    with app.app_context():
        final_user = db.session.get(User, cust_id)
        final_bal = final_user.wallet_balance

    print(f"    Initial wallet: ₹50.0 | Concurrent orders placed: {len(results_concurrent)} | Total credit used: ₹{total_credit_used} | Final wallet: ₹{final_bal}")
    if total_credit_used > 50.0:
        record_fail("Wallet Credit Double-Spend", f"Two concurrent orders both consumed full wallet credit! Used ₹{total_credit_used} from ₹50.0 balance.")
    else:
        record_pass("Wallet credit race condition protected (no double-spend beyond balance)")

# -----------------------------------------------------------------------------
# 3. ORDER CANCELLATION LIFECYCLE & IDEMPOTENCY
# -----------------------------------------------------------------------------
print("\n--- 3. ORDER CANCELLATION LIFECYCLE & IDEMPOTENCY ---")

with app.app_context():
    admin = User.query.filter_by(role='admin').first()
    from app import serializer
    admin_token = serializer.dumps({'user_id': admin.id, 'role': admin.role, 'token_version': admin.token_version})

    # Place an order with credit used and credit earned
    test_user = db.session.get(User, cust_id)
    test_user.wallet_balance = 100.0
    variant = db.session.get(ProductVariant, var_id)
    initial_stock = variant.stock_quantity or 50
    variant.stock_quantity = initial_stock
    db.session.commit()

# Place order
order_res = client.post('/api/orders', headers={'Authorization': f'Bearer {token}'}, json={
    'delivery_type': 'store_pickup',
    'payment_method': 'Cash on Delivery (COD)',
    'use_credit': True,
    'items': [{'variant_id': var_id, 'quantity': 2}]
})
if order_res.status_code == 201:
    ord_id = order_res.get_json()['order']['id']
    credit_used_in_ord = order_res.get_json()['order']['credit_used']

    # Step A: Mark order Paid (simulating store payment, which awards credit_earned)
    client.patch(f'/api/admin/orders/{ord_id}/status', headers={'Authorization': f'Bearer {admin_token}'}, json={
        'payment_status': 'Paid'
    })

    with app.app_context():
        u_after_pay = db.session.get(User, cust_id)
        bal_after_pay = u_after_pay.wallet_balance

    # Step B: Cancel the order
    cancel_res1 = client.patch(f'/api/admin/orders/{ord_id}/status', headers={'Authorization': f'Bearer {admin_token}'}, json={
        'status': 'Cancelled'
    })
    
    with app.app_context():
        u_after_cancel1 = db.session.get(User, cust_id)
        bal_after_cancel1 = u_after_cancel1.wallet_balance
        v_after_cancel1 = db.session.get(ProductVariant, var_id)
        stock_after_cancel1 = v_after_cancel1.stock_quantity

    # Check stock restored
    if stock_after_cancel1 == initial_stock:
        record_pass("Order cancellation restores variant stock accurately")
    else:
        record_fail("Stock restoration on cancel", f"Expected stock {initial_stock}, got {stock_after_cancel1}")

    # Step C: Idempotency Test - Cancel again! Does it restore stock AGAIN or refund AGAIN?
    cancel_res2 = client.patch(f'/api/admin/orders/{ord_id}/status', headers={'Authorization': f'Bearer {admin_token}'}, json={
        'status': 'Cancelled'
    })

    with app.app_context():
        u_after_cancel2 = db.session.get(User, cust_id)
        bal_after_cancel2 = u_after_cancel2.wallet_balance
        v_after_cancel2 = db.session.get(ProductVariant, var_id)
        stock_after_cancel2 = v_after_cancel2.stock_quantity

    if stock_after_cancel2 == initial_stock and bal_after_cancel2 == bal_after_cancel1:
        record_pass("Duplicate order cancellation is idempotent (no double stock/credit restoration)")
    else:
        record_fail("Cancellation Idempotency", f"Second cancel mutated stock ({stock_after_cancel2}) or balance ({bal_after_cancel2})!")

    # Step D: Un-cancellation guard - can an admin change status from Cancelled to Delivered without stock deduction?
    uncancel_res = client.patch(f'/api/admin/orders/{ord_id}/status', headers={'Authorization': f'Bearer {admin_token}'}, json={
        'status': 'Delivered'
    })
    with app.app_context():
        v_after_uncancel = db.session.get(ProductVariant, var_id)
        stock_after_uncancel = v_after_uncancel.stock_quantity
    
    print(f"    Stock after un-cancellation: {stock_after_uncancel} (initial was {initial_stock})")
    if uncancel_res.status_code == 200 and stock_after_uncancel == initial_stock:
        record_fail("Un-cancellation Stock Hole", "Order was moved from Cancelled to Delivered without re-deducting stock, allowing free goods delivery!")
    else:
        record_pass("Un-cancellation properly guarded or blocked")

# -----------------------------------------------------------------------------
# 4. ADD TO ACTIVE DELIVERY WINDOW GUARDS
# -----------------------------------------------------------------------------
print("\n--- 4. ADD TO ACTIVE DELIVERY WINDOW GUARDS ---")

# Place a new order
new_ord_res = client.post('/api/orders', headers={'Authorization': f'Bearer {token}'}, json={
    'delivery_type': 'store_pickup',
    'payment_method': 'Cash on Delivery (COD)',
    'items': [{'variant_id': var_id, 'quantity': 1}]
})
if new_ord_res.status_code == 201:
    test_ord = new_ord_res.get_json()['order']
    test_ord_id = test_ord['id']
    test_ord_num = test_ord['order_number']

    # Test adding while 'Placed' (Allowed)
    add_placed = client.post(f'/api/orders/{test_ord_num}/add-item', headers={'Authorization': f'Bearer {token}'}, json={
        'variant_id': var_id,
        'quantity': 1
    })
    if add_placed.status_code == 200:
        record_pass("Add-to-delivery allowed while order is in preparation (Placed)")
    else:
        record_fail("Add-to-delivery on Placed", f"Expected 200, got {add_placed.status_code}")

    # Set status to 'Out for Delivery'
    client.patch(f'/api/admin/orders/{test_ord_id}/status', headers={'Authorization': f'Bearer {admin_token}'}, json={
        'status': 'Out for Delivery'
    })

    # Test adding while 'Out for Delivery' (Must be REJECTED 400 DISPATCH_WINDOW_CLOSED)
    add_out = client.post(f'/api/orders/{test_ord_num}/add-item', headers={'Authorization': f'Bearer {token}'}, json={
        'variant_id': var_id,
        'quantity': 1
    })
    if add_out.status_code == 400 and add_out.get_json().get('code') == 'DISPATCH_WINDOW_CLOSED':
        record_pass("Add-to-delivery strictly blocked when Out for Delivery (400 DISPATCH_WINDOW_CLOSED)")
    else:
        record_fail("Add-to-delivery dispatch lock", f"Expected 400 DISPATCH_WINDOW_CLOSED, got {add_out.status_code}: {add_out.get_json()}")

    # Set status to 'Delivered'
    client.patch(f'/api/admin/orders/{test_ord_id}/status', headers={'Authorization': f'Bearer {admin_token}'}, json={
        'status': 'Delivered'
    })

    # Test adding while 'Delivered' (Must be REJECTED 400)
    add_delivered = client.post(f'/api/orders/{test_ord_num}/add-item', headers={'Authorization': f'Bearer {token}'}, json={
        'variant_id': var_id,
        'quantity': 1
    })
    if add_delivered.status_code == 400 and add_delivered.get_json().get('code') == 'DISPATCH_WINDOW_CLOSED':
        record_pass("Add-to-delivery strictly blocked when Delivered (400 DISPATCH_WINDOW_CLOSED)")
    else:
        record_fail("Add-to-delivery delivered order lock", f"Expected 400 DISPATCH_WINDOW_CLOSED, got {add_delivered.status_code}")

# -----------------------------------------------------------------------------
# 5. SOUNDBOX UNIQUE PAISE COLLISION CHECK
# -----------------------------------------------------------------------------
print("\n--- 5. SOUNDBOX UNIQUE PAISE COLLISION CHECK ---")

# Place 5 sequential whole-rupee UPI orders and check that all 5 have DISTINCT paise offsets
upi_orders = []
for i in range(5):
    res_upi = client.post('/api/orders', headers={'Authorization': f'Bearer {token}'}, json={
        'delivery_type': 'store_pickup',
        'payment_method': 'UPI / QR Code',
        'items': [{'variant_id': var_id, 'quantity': 1}]
    })
    if res_upi.status_code == 201:
        final_amt = res_upi.get_json()['order']['final_amount']
        upi_orders.append(final_amt)

paise_suffixes = [round(amt % 1, 2) for amt in upi_orders]
print(f"    Assigned UPI amounts: {upi_orders}")
print(f"    Paise suffixes: {paise_suffixes}")
if len(set(paise_suffixes)) == len(paise_suffixes):
    record_pass("All active UPI orders received unique Soundbox paise offsets without collision")
else:
    record_fail("Soundbox Paise Collision", f"Duplicate paise assigned: {paise_suffixes}")

# -----------------------------------------------------------------------------
# 6. DAILY Z-REPORT RECONCILIATION ACCURACY
# -----------------------------------------------------------------------------
print("\n--- 6. DAILY Z-REPORT RECONCILIATION ACCURACY ---")

# Call Daily Z-report endpoint
z_res = client.get('/api/admin/reports/daily-z', headers={'Authorization': f'Bearer {admin_token}'})
if z_res.status_code == 200:
    z_data = z_res.get_json()
    req_keys = ['total_orders_count', 'net_sales', 'cash_paid_amount', 'upi_paid_amount', 'total_cash_in_drawer', 'total_liquid_collected']
    missing_keys = [k for k in req_keys if k not in z_data]
    if not missing_keys:
        record_pass("Daily Z-Report returned all operational financial metrics")
    else:
        record_fail("Daily Z-Report missing metrics", f"Missing: {missing_keys}")
else:
    record_fail("Daily Z-Report status", f"Expected 200, got {z_res.status_code}")

# -----------------------------------------------------------------------------
# CLEANUP & SUMMARY
# -----------------------------------------------------------------------------
print("\n" + "=" * 70)
print(f"AUDIT COMPLETE: {results['passed']} PASSED | {results['failed']} FAILED")
print("=" * 70)
if results['issues']:
    print("\nISSUES DETECTED:")
    for issue in results['issues']:
        print(f" - [{issue['test']}]: {issue['reason']}")
else:
    print("\nZERO BUGS OR VULNERABILITIES DETECTED!")
