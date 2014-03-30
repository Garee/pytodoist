#!/usr/bin/env python

import sys
import unittest
from pytodoist import todoist

full_name = "Py Todoist"
email = "pytodoist.test.email@gmail.com"
password = "pytodoist.test.password"

class UserTest(unittest.TestCase):

    def setUp(self):
        try:
            self.user = todoist.register(full_name, email, password)
        except todoist.TodoistException, e:
            if e.response.text == '"ALREADY_REGISTRED"':
                self.user = todoist.login(email, password)
                self.user.delete()
                self.user = todoist.register(full_name, email, password)

    def tearDown(self):
        self.user.delete()

    def test_login_success(self):
        self.assertTrue(self.user.is_logged_in())

    def test_change_avatar(self):
        pass

    def test_use_default_avatar(self):
        pass

    def test_add_project(self):
        project = self.user.add_project('Project 1')
        projects = self.user.get_projects()
        self.assertEqual(len(projects), 2) # Project 1 + Inbox.

    def test_get_projects(self):
        for i in range(5):
            project = self.user.add_project('Project ' + str(i))
        projects = self.user.get_projects()
        self.assertEqual(len(projects), 6) # 5 + Inbox

    def test_update_project_orders(self):
        pass

    def test_update(self):
        self.user.full_name = 'Todoist Py'
        self.user.update()
        self.user = todoist.login(email, password)
        self.assertEqual(self.user.full_name, 'Todoist Py')

    def test_get_completed_tasks(self):
        pass

    def test_get_labels(self):
        pass

    def test_search(self):
        pass


def main():
    unittest.main()
    return 0

if __name__ == '__main__':
    sys.exit(main())
