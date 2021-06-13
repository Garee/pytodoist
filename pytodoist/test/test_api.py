#!/usr/bin/env python

"""This module contains unit tests for the pytodoist.api module."""
import json
import time
import unittest
from pytodoist.api import TodoistAPI
from pytodoist.test.util import TestUser

# No magic numbers
_HTTP_OK = 200


class TodoistAPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = TodoistAPI()

    def setUp(self):
        self.user = TestUser()
        time.sleep(10)  # Rate limit ourselves to avoid a server rate limit.
        response = self.api.register(self.user.email, self.user.full_name,
                                     self.user.password)
        if response.status_code != _HTTP_OK:  # Assume already registered.
            response = self.api.login(self.user.email, self.user.password)
        user_json = response.json()
        self.user.token = user_json['token']

    def tearDown(self):
        self.api.delete_user(self.user.token, self.user.password)

    def test_class_variables(self):
        self.assertEqual(self.api.VERSION, '8')
        self.assertEqual(self.api.URL, 'https://api.todoist.com/API/v8/')

    def test_login_success(self):
        response = self.api.login(self.user.email, self.user.password)
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertIn('token', response.json())

    def test_login_failure(self):
        response = self.api.login(self.user.email, '')
        self.assertNotEqual(response.status_code, _HTTP_OK)
        self.assertIn('error', response.json())

    def test_login_with_google_failure(self):
        response = self.api.login_with_google(self.user.email, '')
        self.assertNotEqual(response.status_code, _HTTP_OK)

    def test_register_success(self):
        self.api.delete_user(self.user.token, self.user.password)
        response = self.api.register(self.user.email, self.user.full_name,
                                     self.user.password)
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertIn('token', response.json())

    def test_register_failure(self):
        response = self.api.register(self.user.email, self.user.full_name,
                                     self.user.password)
        self.assertNotEqual(response.status_code, _HTTP_OK)
        self.assertIn('error', response.json())

    def test_delete_user_success(self):
        response = self.api.delete_user(self.user.token,
                                        self.user.password)
        self.assertEqual(response.status_code, _HTTP_OK)
        response = self.api.login(self.user.email, self.user.password)
        self.assertNotEqual(response.status_code, _HTTP_OK)
        self.assertIn('error', response.json())

    def test_delete_user_failure(self):
        self.api.delete_user(self.user.token, '')
        response = self.api.login(self.user.email, self.user.password)
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertNotIn('error', response.json())

    def test_sync_all(self):
        response = self.api.sync(self.user.token, self.user.sync_token)
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertIn('sync_token', response.json())

    def test_query(self):
        queries = ['tomorrow', 'p1']
        response = self.api.query(self.user.token, json.dumps(queries))
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertEqual(len(response.json()), len(queries))

    def test_add_item_success(self):
        response = self.api.add_item(self.user.token, 'Task 1')
        self.assertEqual(response.status_code, _HTTP_OK)
        task_info = response.json()
        self.assertEqual(task_info['content'], 'Task 1')

    def test_quick_add(self):
        text = 'Buy milk #Inbox'
        response = self.api.quick_add(self.user.token, text)
        self.assertEqual(response.status_code, _HTTP_OK)
        task_info = response.json()
        self.assertEqual(task_info['content'], 'Buy milk')

    def test_get_all_completed_tasks_empty(self):
        response = self.api.get_all_completed_tasks(self.user.token)
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertIn('items', response.json())

    def test_get_redirect_link(self):
        response = self.api.get_redirect_link(self.user.token)
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertIn('link', response.json())

    def test_get_productivity_stats(self):
        response = self.api.get_productivity_stats(self.user.token)
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertIn('karma', response.json())

    def test_update_notification_settings_success(self):
        response = self.api.update_notification_settings(self.user.token,
                                                         'user_left_project',
                                                         'email',
                                                         1)  # False
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertIn('user_left_project', response.json())
        self.assertFalse(response.json()['user_left_project']['notify_email'])


if __name__ == '__main__':
    unittest.main()
