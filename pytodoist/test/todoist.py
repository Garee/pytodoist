#!/usr/bin/env python
"""This module contains unit tests for the pytodoist.todoist module."""

import sys
import unittest
from pytodoist.todoist import Todoist

class TestUser(object):
    """A fake user to use in each unit test."""

    def __init__(self):
        self.full_name = "Py Todoist"
        self.email = "pytodoist.test.email@gmail.com"
        self.password = "pytodoist.test.password"
        self.token = None

class TodoistTest(unittest.TestCase):
    """Test the functionality of the pytodoist.Todoist class"""

    @classmethod
    def setUpClass(cls):
        cls.t = Todoist()
        cls.user = TestUser()

    def setUp(self):
        response = self.t.register(self.user.email,
                                   self.user.full_name,
                                   self.user.password)
        if response.text == '"ALREADY_REGISTRED"':
            response = self.t.login(self.user.email, self.user.password)
        user_details = response.json()
        self.user.token = user_details['token']

    def tearDown(self):
        self.t.delete_user(self.user.token, self.user.password)

    def test_login_success(self):
        response = self.t.login(self.user.email, self.user.password)
        self.assertIn('token', response.json())

    def test_login_failure(self):
        response = self.t.login(self.user.email, "badpassword")
        self.assertEqual(response.text, '"LOGIN_ERROR"')

    def test_ping_success(self):
        response = self.t.ping(self.user.token)
        self.assertEqual(response.status_code, 200)

    def test_ping_failure(self):
        response = self.t.ping('badtoken')
        self.assertEqual(response.status_code, 401)

    def test_get_timezones(self):
        response = self.t.get_timezones()
        timezones = response.json()
        self.assertTrue(len(timezones) > 0)

    def test_update_user(self):
        new_email = "todoist.updated.email@gmail.com"
        response = self.t.update_user(self.user.token, email=new_email)
        user_details = response.json()
        self.assertEqual(user_details['email'], new_email)

    def test_update_user_bad_password(self):
        new_password = "007" # Too short.
        response = self.t.update_user(self.user.token, password=new_password)
        self.assertEqual(response.status_code, 400)

    def test_update_user_bad_email(self):
        new_email = "gareeblackwood@gmail.com" # Already exists.
        response = self.t.update_user(self.user.token, email=new_email)
        self.assertEqual(response.text, '"ERROR_EMAIL_FOUND"')

    def test_update_avatar(self):
        pass

    def test_get_projects(self):
        response = self.t.get_projects(self.user.token)
        projects = response.json()
        self.assertEqual(len(projects), 1) # Inbox always exists.

    def test_get_project_success(self):
        inbox = self._get_inbox()
        project_id = inbox['id']
        response = self.t.get_project(self.user.token, project_id)
        project_details = response.json()
        self.assertEqual(project_details['name'], inbox['name'])

    def test_get_project_failure(self):
        response = self.t.get_project(self.user.token, 'badid')
        self.assertEqual(response.status_code, 400)

    def test_add_project_success(self):
        project_name = "Project 1"
        response = self.t.add_project(self.user.token, project_name)
        project_details = response.json()
        self.assertEqual(project_details['name'], project_name)

    def test_add_project_failure(self):
        project_name = ""
        response = self.t.add_project(self.user.token, project_name)
        self.assertEqual(response.text, '"ERROR_NAME_IS_EMPTY"')

    def test_update_project_success(self):
        response = self.t.add_project(self.user.token, "Project 1")
        project_details = response.json()
        project_id = project_details['id']
        new_project_name = "Project 2"
        response = self.t.update_project(self.user.token,
                                         project_id,
                                         name=new_project_name)
        project_details = response.json()
        updated_project_name = project_details['name']
        self.assertEqual(updated_project_name, new_project_name)

    def test_update_project_failure(self):
        project_id = "badid"
        new_project_name = "Project 2"
        response = self.t.update_project(self.user.token,
                                         project_id,
                                         name=new_project_name)
        self.assertEqual(response.status_code, 400)

    def test_update_project_orders(self):
        for i in range(5):
            self.t.add_project(self.user.token, "Project_" + str(i))
        response = self.t.get_projects(self.user.token)
        current_order = [project['id'] for project in response.json()]
        reverse_order = current_order[::-1]
        response = self.t.update_project_orders(self.user.token,
                                                str(reverse_order))
        response = self.t.get_projects(self.user.token)
        updated_order = [project['id'] for project in response.json()]
        self.assertEqual(updated_order, reverse_order)

    def test_delete_project(self):
        response = self.t.add_project(self.user.token, 'Project_1')
        project_id = response.json()['id']
        response = self.t.delete_project(self.user.token, project_id)
        self.assertEqual(response.status_code, 200)
        response = self.t.get_projects(self.user.token)
        self.assertTrue(len(response.json()) == 1) # Only Inbox remains.

    def test_archive_project(self):
        project_id = '1'
        response = self.t.archive_project(self.user.token, project_id)
        archived_ids = response.json()
        self.assertEqual(len(archived_ids), 0) # Premium users only.

    def test_unarchive_project(self):
        project_id = '1'
        response = self.t.unarchive_project(self.user.token, project_id)
        archived_ids = response.json()
        self.assertEqual(len(archived_ids), 0) # Premium users only.

    def test_get_labels(self):
        response = self.t.get_labels(self.user.token)
        labels = response.json()
        self.assertTrue(isinstance(labels, dict))
        response = self.t.get_labels(self.user.token, as_list=1)
        labels = response.json()
        self.assertTrue(isinstance(labels, list))

    def test_add_label(self):
        label_name = "Label 1"
        response = self.t.add_label(self.user.token, label_name)
        label_details = response.json()
        self.assertEqual(label_details['name'], label_name)
        response = self.t.get_labels(self.user.token)
        labels = response.json()
        self.assertEqual(len(labels), 1)

    def _get_inbox(self):
        response = self.t.get_projects(self.user.token)
        projects = response.json()
        for project in projects:
            if project['name'] == 'Inbox':
                return project


def main():
    unittest.main()
    return 0

if __name__ == '__main__':
    sys.exit(main())
