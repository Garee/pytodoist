#!/usr/bin/env python

import sys
import unittest
from pytodoist import todoist

class UserTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        full_name = "Py Todoist"
        email = "pytodoist.test.email@gmail.com"
        password = "pytodoist.test.password"
        cls.user = todoist.User(email, full_name, password)

    def setUp(self):
        if not self.user.is_registered():
            self.user.register()
        self.user.login()

    def tearDown(self):
        self.user.delete()

    def test_login_success(self):
        self.assertTrue(self.user.is_logged_in())

    def test_add_project(self):
        project = todoist.Project('Project 1')
        self.user.add_project(project)
        projects = self.user.get_projects()
        self.assertEqual(len(projects), 2) # Project 1 + Inbox.

    def test_get_projects(self):
        for i in range(5):
            project = todoist.Project('Project_' + str(i))
            self.user.add_project(project)
        projects = self.user.get_projects()
        self.assertEqual(len(projects), 6) # 5 + Inbox

def main():
    unittest.main()
    return 0

if __name__ == '__main__':
    sys.exit(main())
