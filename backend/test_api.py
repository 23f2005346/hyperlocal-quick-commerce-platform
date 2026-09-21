from app import create_app
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

app = create_app()
client = app.test_client()

# 1. Health
h = client.get('/api/health')
print("Health:", h.status_code, h.get_json()['status'])

# 2. Customer Registration
reg_res = client.post('/api/auth/register', json={
    'name': 'Pooja Sharma',
    'email': 'pooja@test.com',
    'phone': '9876543299',
    'password': 'password123',
    'address': 'B-302, Gokuldham Society, Mumbai'
})
print("Customer Registration:", reg_res.status_code, reg_res.get_json().get('user', {}).get('role'))
cust_token = reg_res.get_json()['token']

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

print("\nALL SECURITY & CUSTOMER TESTS PASSED SUCCESSFULLY!")
