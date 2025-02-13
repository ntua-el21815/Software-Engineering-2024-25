import unittest
from unittest.mock import patch, Mock
from api_wrapper import User, getOpNames

class TestApiWrapper(unittest.TestCase):

    @patch('api_wrapper.requests.get')
    def test_getOpNames_success(self, mock_get):
        mock_response = Mock()
        expected_data = {"MO": "OperatorName"}
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_get.return_value = mock_response

        result = getOpNames()
        self.assertEqual(result, expected_data)

    @patch('api_wrapper.requests.get')
    def test_getOpNames_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        result = getOpNames()
        self.assertEqual(result, -1)

    @patch('api_wrapper.requests.post')
    @patch('api_wrapper.getOpNames', return_value={"MO": "OperatorName"})
    def test_user_authenticate_success(self, mock_getOpNames, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "fake_token"}
        mock_post.return_value = mock_response

        user = User("MO")
        result = user.authenticate("password")
        self.assertEqual(result, 1)
        self.assertTrue(user.authenticated)
        self.assertEqual(user.token, "fake_token")

    @patch('api_wrapper.requests.post')
    @patch('api_wrapper.getOpNames', return_value={"MO": "OperatorName"})
    def test_user_authenticate_failure(self, mock_getOpNames, mock_post):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        user = User("MO")
        result = user.authenticate("wrong_password")
        self.assertEqual(result, -1)
        self.assertFalse(user.authenticated)
        self.assertIsNone(user.token)

    @patch('api_wrapper.requests.post')
    @patch('api_wrapper.getOpNames', return_value={"MO": "OperatorName"})
    def test_user_logout_success(self, mock_getOpNames, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        user = User("MO")
        user.token = "fake_token"
        user.authenticated = True
        result = user.logout()
        self.assertEqual(result, 1)
        self.assertFalse(user.authenticated)
        self.assertIsNone(user.token)
        self.assertIsNone(user.username)

    @patch('api_wrapper.requests.post')
    @patch('api_wrapper.getOpNames', return_value={"MO": "OperatorName"})
    def test_user_logout_failure(self, mock_getOpNames, mock_post):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        user = User("MO")
        user.token = "fake_token"
        user.authenticated = True
        result = user.logout()
        self.assertEqual(result, 400)
        self.assertTrue(user.authenticated)
        self.assertEqual(user.token, "fake_token")

    @patch('api_wrapper.requests.get')
    @patch('api_wrapper.getOpNames', return_value={"MO": "OperatorName"})
    def test_calcCharges_success(self, mock_getOpNames, mock_get):
        mock_response = Mock()
        expected_data = {"vOpList": [{"visitingOpID": "OtherOp", "passesCost": 100}]}
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_get.return_value = mock_response

        user = User("MO")
        user.token = "fake_token"
        user.authenticated = True
        result = user.calcCharges("20220101", "20220131")
        self.assertEqual(result, expected_data)

    @patch('api_wrapper.requests.get')
    @patch('api_wrapper.getOpNames', return_value={"MO": "OperatorName"})
    def test_calcCharges_failure(self, mock_getOpNames, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response

        user = User("MO")
        user.token = "fake_token"
        user.authenticated = True
        result = user.calcCharges("20220101", "20220131")
        self.assertEqual(result, -1)

    @patch('api_wrapper.requests.get')
    @patch('api_wrapper.getOpNames', return_value={"MO": "OperatorName"})
    def test_calcStats_success(self, mock_getOpNames, mock_get):
        mock_response = Mock()
        expected_data = {"vOpList": [{"visitingOpID": "OtherOp", "passesCost": 100}]}
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_get.return_value = mock_response

        user = User("MO")
        user.token = "fake_token"
        user.authenticated = True
        result = user.calcStats("20220101", "20220131")
        self.assertEqual(result, expected_data)

    @patch('api_wrapper.requests.get')
    @patch('api_wrapper.getOpNames', return_value={"MO": "OperatorName"})
    def test_calcStats_failure(self, mock_getOpNames, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response

        user = User("MO")
        user.token = "fake_token"
        user.authenticated = True
        result = user.calcStats("20220101", "20220131")
        self.assertEqual(result, -1)

    @patch('api_wrapper.requests.get')
    @patch('api_wrapper.getOpNames', return_value={"MO": "OperatorName"})
    def test_getStations_success(self, mock_getOpNames, mock_get):
        mock_response = Mock()
        expected_data = {"stations": ["Station1", "Station2"]}
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_get.return_value = mock_response

        user = User("MO")
        user.token = "fake_token"
        user.authenticated = True
        result = user.getStations()
        self.assertEqual(result, expected_data)

    @patch('api_wrapper.requests.get')
    @patch('api_wrapper.getOpNames', return_value={"MO": "OperatorName"})
    def test_getStations_failure(self, mock_getOpNames, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response

        user = User("MO")
        user.token = "fake_token"
        user.authenticated = True
        result = user.getStations()
        self.assertEqual(result, -1)

if __name__ == '__main__':
    unittest.main()