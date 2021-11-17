import unittest
from server import process_client_message
from common.variables import ACTION, ACCOUNT_NAME, PRESENCE, USER, RESPONSE, ERROR, TIME


class TestServer(unittest.TestCase):

    error_dict = {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }

    ok_dict = {
        RESPONSE: 200
    }

    def test_client_message_no_action(self):
        self.assertEqual(process_client_message({TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.error_dict)

    def test_client_message_wrong_action(self):
        self.assertEqual(process_client_message({ACTION: 'Wrong', TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}),
                         self.error_dict)

    def test_client_message_no_time(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.error_dict)

    def test_client_message_no_user(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1}), self.error_dict)

    def test_client_message_user_not_guest(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'User'}}),
                         self.error_dict)

    def test_client_message_ok(self):
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}),
                         self.ok_dict)


if __name__ == '__main__':
    unittest.main()
