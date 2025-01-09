import unittest
from unittest.mock import patch, Mock
from APIWrapper import User

class TestUser(unittest.TestCase):
    
    @patch('APIWrapper.requests.post')
    def test_authenticate_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "fake_token"}
        mock_post.return_value = mock_response

        user = User("test_user")
        result = user.authenticate("test_password")
        self.assertEqual(result, 1)
        self.assertTrue(user.authenticated)
        self.assertEqual(user.token, "fake_token")

    @patch('APIWrapper.requests.post')
    def test_authenticate_failure(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        user = User("test_user")
        result = user.authenticate("wrong_password")
        self.assertEqual(result, -1)
        self.assertFalse(user.authenticated)
        self.assertIsNone(user.token)

    @patch('APIWrapper.requests.post')
    def test_logout_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        user = User("test_user")
        user.token = "fake_token"
        user.authenticated = True
        result = user.logout()
        self.assertEqual(result, 1)
        self.assertFalse(user.authenticated)
        self.assertIsNone(user.token)

    @patch('APIWrapper.requests.post')
    def test_logout_failure(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        user = User("test_user")
        user.token = "fake_token"
        user.authenticated = True
        result = user.logout()
        self.assertEqual(result, 400)
        self.assertTrue(user.authenticated)
        self.assertEqual(user.token, "fake_token")

    @patch('APIWrapper.requests.get')
    def test_calcCharges_authenticated(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"charges": "some_data"}
        mock_get.return_value = mock_response

        user = User("test_user")
        user.authenticated = True
        result = user.calcCharges("20220101", "20220131")
        self.assertEqual(result, {"charges": "some_data"})

    @patch('APIWrapper.requests.get')
    def test_calcCharges_not_authenticated(self, mock_get):
        user = User("test_user")
        user.authenticated = False
        result = user.calcCharges("20220101", "20220131")
        self.assertEqual(result, -1)

    @patch('APIWrapper.requests.get')
    def test_calcStats_authenticated(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "vOpList": [
                {"visitingOpID": "op1", "passesCost": 100},
                {"visitingOpID": "op2", "passesCost": 200}
            ]
        }
        mock_get.return_value = mock_response

        user = User("test_user")
        user.authenticated = True
        result = user.calcStats("20220101", "20220131")
        self.assertEqual(result, {
            "vOpList": [
                {"visitingOpID": "op1", "passesCost": 100},
                {"visitingOpID": "op2", "passesCost": 200}
            ]
        })

    @patch('APIWrapper.requests.get')
    def test_calcStats_not_authenticated(self, mock_get):
        user = User("test_user")
        user.authenticated = False
        result = user.calcStats("20220101", "20220131")
        self.assertEqual(result, -1)

if __name__ == '__main__':
    unittest.main()
