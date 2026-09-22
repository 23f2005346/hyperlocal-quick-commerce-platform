from app import create_app
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

app = create_app()
client = app.test_client()

# 1. Health
h = client.get('/api/health')
print("Health:", h.status_code, h.get_json()['status'])

# 2. Customer Registration / Login
reg_res = client.post('/api/auth/register', json={
    'name': 'Pooja Sharma',
    'email': 'pooja@test.com',
    'phone': '9876543299',
    'password': 'password123',
    'address': 'B-302, Gokuldham Society, Mumbai'
})
if reg_res.status_code == 201:
    print("Customer Registration:", reg_res.status_code, reg_res.get_json().get('user', {}).get('role'))
    cust_token = reg_res.get_json()['token']
else:
    # User exists, login instead
    login_res = client.post('/api/auth/login', json={'email': 'pooja@test.com', 'password': 'password123'})
    print("Customer Re-Login:", login_res.status_code, login_res.get_json().get('user', {}).get('role'))
    cust_token = login_res.get_json()['token']

# 3. Security Check: Customer attempts to change price (Should be REJECTED 403)
patch_as_customer = client.patch(
    '/api/variants/1',
    headers={'Authorization': f'Bearer {cust_token}'},
    json={'selling_price': 199.0}
)
print("Customer Price Tamper Attempt:", patch_as_customer.status_code, "(Should be 403)")
assert patch_as_customer.status_code == 403, "Security violation: customer was able to change price!"

# 4. Admin Login & Authorized Price Update
admin_res = client.post('/api/auth/login', json={
    'email': 'admin@kirana.com',
    'password': 'admin123'
})
print("Admin Login:", admin_res.status_code, admin_res.get_json().get('user', {}).get('role'))
admin_token = admin_res.get_json()['token']

patch_as_admin = client.patch(
    '/api/variants/1',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={'selling_price': 80.0}
)
print("Admin Authorized Price Update:", patch_as_admin.status_code, patch_as_admin.get_json().get('variant', {}).get('selling_price'))

# 5. Customer Place Order
order_res = client.post(
    '/api/orders',
    headers={'Authorization': f'Bearer {cust_token}'},
    json={
        'payment_method': 'Kirana Khata (Pay Later)',
        'items': [{'variant_id': 1, 'quantity': 2}]
    }
)
print("Customer Placed Order:", order_res.status_code)
order_data = order_res.get_json()['order']
order_id = order_data['id']
print(f"Order: {order_data['order_number']}, Status: {order_data['status']}, Payment: {order_data['payment_status']}")

# 6. Customer Checks Their Own Orders
cust_orders = client.get('/api/customer/orders', headers={'Authorization': f'Bearer {cust_token}'})
print("Customer Order History Count:", len(cust_orders.get_json()))

# 7. Customer Pays for the Order
pay_res = client.post(f'/api/customer/orders/{order_id}/pay', headers={'Authorization': f'Bearer {cust_token}'})
print("Customer Paid Khata Bill:", pay_res.status_code, pay_res.get_json()['order']['payment_status'])

# 8. Admin Registered Users Directory & Khata Audit Test
users_res = client.get('/api/admin/users', headers={'Authorization': f'Bearer {admin_token}'})
print("Admin Users Directory:", users_res.status_code, "Registered Customers:", len(users_res.get_json()))
assert users_res.status_code == 200
assert len(users_res.get_json()) > 0
customer_entry = [u for u in users_res.get_json() if u['email'] == 'pooja@test.com'][0]
print(f"Customer Audit for Pooja: {customer_entry['name']}, Orders: {customer_entry['total_orders']}, Spent: Rs.{customer_entry['total_spent']}, Unpaid: Rs.{customer_entry['unpaid_balance']}")

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
print(f"Created Counter Bill: {pos_order['order_number']}, Total: Rs.{pos_order['final_amount']}, Status: {pos_order['status']}, Payment: {pos_order['payment_status']}")

# 10. Re-verify Customer Ledger after new order
users_res2 = client.get('/api/admin/users', headers={'Authorization': f'Bearer {admin_token}'})
customer_entry2 = [u for u in users_res2.get_json() if u['email'] == 'pooja@test.com'][0]
print(f"Pooja Updated Total Orders: {customer_entry2['total_orders']}, Total Spent: Rs.{customer_entry2['total_spent']}")
assert customer_entry2['total_orders'] == 2

print("\nALL KOMAL MART SECURITY, POS & CUSTOMER DIRECTORY TESTS PASSED 100%!")

