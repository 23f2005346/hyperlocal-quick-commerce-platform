import os
import sys
import unittest
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, serializer
from models import db, SupportTicket, User

class TestSupportTicketAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def test_01_validation_rejects_missing_fields(self):
        resp = self.client.post('/api/support/ticket', json={
            'ticket_type': 'complaint'
        })
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.data)
        self.assertIn('error', data)

    def test_02_validation_rejects_dummy_phone(self):
        # Invalid format (not 10 digits starting with 6-9)
        resp1 = self.client.post('/api/support/ticket', json={
            'ticket_type': 'complaint',
            'category': 'डिलिव्हरीला उशीर',
            'message': 'सामान अद्याप आले नाही, १ तास झाला आहे.',
            'customer_name': 'Test User',
            'customer_phone': '0000000000'
        })
        self.assertEqual(resp1.status_code, 400)
        self.assertIn('वैध मोबाईल नंबर', json.loads(resp1.data).get('error', ''))

        # Dummy 10-digit number (9876543210)
        resp2 = self.client.post('/api/support/ticket', json={
            'ticket_type': 'complaint',
            'category': 'डिलिव्हरीला उशीर',
            'message': 'सामान अद्याप आले नाही, १ तास झाला आहे.',
            'customer_name': 'Test User',
            'customer_phone': '9876543210'
        })
        self.assertEqual(resp2.status_code, 400)
        self.assertIn('अवैध मोबाईल नंबर', json.loads(resp2.data).get('error', ''))

    def test_03_create_complaint_ticket_success(self):
        resp = self.client.post('/api/support/ticket', json={
            'ticket_type': 'complaint',
            'category': 'चुकीचे किंवा न आलेले सामान',
            'order_number': 'KRN-TEST-9999',
            'message': 'मी २ किलो साखर मागवली होती, पण पार्सलमध्ये १ किलोच निघाली.',
            'customer_name': 'Roushan Test',
            'customer_phone': '9142052967',
            'customer_email': 'test@komalmart.com'
        })
        self.assertEqual(resp.status_code, 201)
        data = json.loads(resp.data)
        self.assertIn('ticket', data)
        self.assertTrue(data['ticket']['ticket_number'].startswith('TKT-'))
        self.assertEqual(data['ticket']['ticket_type'], 'complaint')
        self.assertEqual(data['ticket']['status'], 'Open')
        self.assertEqual(data['ticket']['customer_phone'], '9142052967')

    def test_04_create_feedback_ticket_success(self):
        resp = self.client.post('/api/support/ticket', json={
            'ticket_type': 'feedback',
            'category': 'नवीन मालाची मागणी',
            'message': 'कृपया दुकानात खारीक व बदाम पावडर देखील उपलब्ध करून द्यावी.',
            'customer_name': 'Roushan Customer',
            'customer_phone': '9820011223'
        })
        self.assertEqual(resp.status_code, 201)
        data = json.loads(resp.data)
        self.assertIn('ticket', data)
        self.assertEqual(data['ticket']['ticket_type'], 'feedback')
        self.assertEqual(data['ticket']['status'], 'Open')

    def test_05_get_my_tickets_by_phone(self):
        resp = self.client.get('/api/support/my-tickets?phone=9142052967')
        self.assertEqual(resp.status_code, 200)
        tickets = json.loads(resp.data)
        self.assertTrue(len(tickets) >= 1)
        self.assertEqual(tickets[0]['customer_phone'], '9142052967')

    def test_06_admin_support_tickets_access_control(self):
        # Without token
        resp = self.client.get('/api/admin/support/tickets')
        self.assertEqual(resp.status_code, 403)

    def test_07_admin_view_and_resolve_ticket(self):
        with self.app.app_context():
            admin_user = User.query.filter_by(role='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin_test',
                    name='Admin Master',
                    phone='9999999999',
                    role='admin'
                )
                admin_user.set_password('Admin@123')
                db.session.add(admin_user)
                db.session.commit()
            token = serializer.dumps({'user_id': admin_user.id})

            # Create ticket to resolve
            import uuid
            unique_tkt_num = f'TKT-RESOLVE-{uuid.uuid4().hex[:6]}'
            t = SupportTicket(
                ticket_number=unique_tkt_num,
                ticket_type='complaint',
                category='बिलात चूक',
                customer_name='Anil Kumar',
                customer_phone='9819922334',
                message='सुटे पैसे मिळाले नाहीत.',
                status='Open'
            )
            db.session.add(t)
            db.session.commit()
            t_id = t.id

        headers = {'Authorization': f'Bearer {token}'}

        # Admin gets tickets
        resp = self.client.get('/api/admin/support/tickets', headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn('tickets', data)
        self.assertIn('open_complaints_count', data)

        # Admin marks ticket as 'In Review'
        resp = self.client.patch(f'/api/admin/support/tickets/{t_id}/status',
            headers=headers,
            json={'status': 'In Review', 'admin_notes': 'ग्राहकाला फोन करून चौकशी केली.'}
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data['ticket']['status'], 'In Review')
        self.assertEqual(data['ticket']['admin_notes'], 'ग्राहकाला फोन करून चौकशी केली.')

        # Admin marks ticket as 'Resolved'
        resp = self.client.patch(f'/api/admin/support/tickets/{t_id}/status',
            headers=headers,
            json={'status': 'Resolved', 'admin_notes': 'सुटे पैसे गुगल पे द्वारे परत पाठवले. समस्या निवारण पूर्ण.'}
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data['ticket']['status'], 'Resolved')
        self.assertIsNotNone(data['ticket']['resolved_at'])

if __name__ == '__main__':
    unittest.main()
