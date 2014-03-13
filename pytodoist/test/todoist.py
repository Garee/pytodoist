#!/usr/bin/env python

import sys
import unittest
from pytodoist.todoist import Todoist

class TestUser(object):

    def __init__(self):
        self.full_name = 'Py Todoist'
        self.email = 'pytodoist.test.email@gmail.com'
        self.password = 'pytodoist.test.password'
        self.token = None

class TodoistTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.t = Todoist()
        self.user = TestUser()

    def setUp(self):
        response = self.t.register(self.user.email, self.user.full_name,
                                   self.user.password)
        if response.text == '"ALREADY_REGISTRED"':
            response = self.t.login(self.user.email, self.user.password)
        user_details = response.json()
        self.user.token = user_details['token']

    def tearDown(self):
        self.t.delete_user(self.user.token, self.user.password)

    def test_login(self):
        response = self.t.login(self.user.email, self.user.password)
        self.assertTrue(response.status_code == 200)
        self.assertTrue('token' in response.json())

    def test_ping(self):
        response = self.t.login(self.user.email, self.user.password)
        token = response.json()['token']
        response = self.t.ping(token)
        self.assertTrue(response.status_code == 200)

    def test_get_timezones(self):
        response = self.t.get_timezones()
        self.assertTrue(response.status_code == 200)
        timezones = response.json()
        n_timezones = len(timezones)
        self.assertTrue(n_timezones > 0)

def main():
    unittest.main()
    return 0

if __name__ == '__main__':
    sys.exit(main())
