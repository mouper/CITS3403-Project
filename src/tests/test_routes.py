import unittest
import json
from app import application, db
from models import User

class RoutesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure app for testing
        application.config['TESTING'] = True
        application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        application.config['WTF_CSRF_ENABLED'] = False
        # Keep login enabled to test redirect logic
        application.config['LOGIN_DISABLED'] = False
        cls.app = application
        with cls.app.app_context():
            db.create_all()
            # Create a test user
            user = User(username='testuser', email='test@example.com', first_name='Test', last_name='User')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            cls.test_user_id = user.id

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.drop_all()

    def setUp(self):
        self.client = self.app.test_client()
        # Simulate user login for protected routes
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.test_user_id)
            sess['_fresh'] = True

    def test_landing_authenticated_redirect(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.headers.get('Location', ''))

    def test_login_get_authenticated_redirect(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.headers.get('Location', ''))

    def test_signup_get_authenticated_redirect(self):
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.headers.get('Location', ''))

    def test_dashboard_get(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'dashboard', response.data.lower())

    def test_analytics_get(self):
        response = self.client.get('/analytics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'analytics', response.data.lower())

    def test_requests_get(self):
        response = self.client.get('/requests')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'requests', response.data.lower())

    def test_account_get(self):
        response = self.client.get('/account')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'my account', response.data.lower())

    def test_search_players_empty_query(self):
        response = self.client.get('/search_players?query=')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        self.assertIn('players', data)
        self.assertEqual(data['players'], [])

    def test_send_friend_request_no_data(self):
        response = self.client.post('/friends/request', json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'No user selected')

    def test_get_friends_empty(self):
        response = self.client.get('/get_friends')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['friends'], list)
        self.assertEqual(len(data['friends']), 0)

if __name__ == '__main__':
    unittest.main()
