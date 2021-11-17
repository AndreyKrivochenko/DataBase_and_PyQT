import json
import unittest
from common.utils import send_message, get_message
from common.variables import ENCODING, ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR


class SocketTest:
    def __init__(self, dict_for_test):
        self.dict_for_test = dict_for_test
        self.encoded_message = None
        self.receved_message = None

    def send(self, message_for_send):
        json_test_message = json.dumps(self.dict_for_test)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.receved_message = message_for_send

    def recv(self):
        json_test_message = json.dumps(self.dict_for_test)
        return json_test_message.encode(ENCODING)


class TestUtils(unittest.TestCase):
    test_dict_for_send = {
        ACTION: PRESENCE,
        TIME: 123.123,
        USER: {
            ACCOUNT_NAME: 'user'
        }
    }
    test_dict_recv_err = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }
    test_dict_recv_ok = {
        RESPONSE: 200
    }

    def test_send_message(self):
        socket_for_test = SocketTest(self.test_dict_for_send)
        send_message(socket_for_test, self.test_dict_for_send)
        self.assertEqual(socket_for_test.encoded_message, socket_for_test.receved_message)
        with self.assertRaises(Exception):
            send_message(socket_for_test, socket_for_test)

    def test_get_message(self):
        test_sock_err = SocketTest(self.test_dict_recv_err)
        test_sock_ok = SocketTest(self.test_dict_recv_ok)
        self.assertEqual(get_message(test_sock_err), self.test_dict_recv_err)
        self.assertEqual(get_message(test_sock_ok), self.test_dict_recv_ok)


if __name__ == '__main__':
    unittest.main()
