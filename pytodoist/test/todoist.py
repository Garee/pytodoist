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

    def test_update(self):
        self.user.full_name = 'Todoist Py'
        self.user.update()
        self.user = todoist.login(email, password)
        print self.user
        self.assertEqual(self.user.full_name, 'Todoist Py')

    def test_add_project(self):
        project = self.user.add_project('Project 1')
        projects = self.user.get_projects()
        self.assertEqual(len(projects), 2) # Project 1 + Inbox.
        project = self.user.get_project('Project 1')
        self.assertIsNotNone(project)

    def test_get_projects(self):
        for i in range(5):
            project = self.user.add_project('Project ' + str(i))
        projects = self.user.get_projects()
        self.assertEqual(len(projects), 6) # 5 + Inbox

    def test_update_project_orders(self):
        for i in range(5):
            self.user.add_project('Project_' + str(i))
        projects = self.user.get_projects()
        rev_projects = projects[::-1]
        self.user.update_project_orders(rev_projects)
        projects = self.user.get_projects()
        for i, p in enumerate(projects):
            self.assertEqual(p.name, rev_projects[i].name)

    def test_get_completed_tasks(self):
        pass

    def test_add_label(self):
        self.user.add_label('Label 1', color=1)
        labels = self.user.get_labels()
        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0].name, 'Label 1')

    def test_get_labels(self):
        for i in range(5):
            self.user.add_label('Label_' + str(i))
        labels = self.user.get_labels()
        self.assertEqual(len(labels), 5)

    def test_search(self):
        inbox = self.user.get_project('Inbox')
        inbox.add_task('Task Red')
        inbox.add_task('Task Blue')
        queries = '["view all"]'
        tasks = self.user.search(queries)
        self.assertEqual(len(tasks), 2)


def main():
    unittest.main()
    return 0

if __name__ == '__main__':
    sys.exit(main())
