import unittest
from client import create_presense, process_answ
from common.variables import TIME, ACTION, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, ERROR


class TestClient(unittest.TestCase):
    test_dict = create_presense()
    test_dict[TIME] = 1.1

    def test_create_presense_ok(self):
        self.assertEqual(self.test_dict, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_process_answer_200(self):
        self.assertEqual(process_answ({RESPONSE: 200}), '200: Ok')

    def test_process_answer_400(self):
        self.assertEqual(process_answ({RESPONSE: 400, ERROR: 'Bad request'}), '400: Bad request')

    def test_process_answer_no_response(self):
        self.assertRaises(ValueError, process_answ, 'Bad request')


if __name__ == '__main__':
    unittest.main()
