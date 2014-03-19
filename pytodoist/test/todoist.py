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

    def test_update_label_name(self):
        label_name = "Label 1"
        self.t.add_label(self.user.token, label_name)
        new_name = "Label 2"
        response = self.t.update_label_name(self.user.token,
                                            label_name,
                                            new_name)
        label_details = response.json()
        self.assertEqual(label_details['name'], new_name)

    def test_update_label_color(self):
        label_name = "Label 1"
        label_color = 0
        self.t.add_label(self.user.token, label_name, color=label_color)
        response = self.t.update_label_color(self.user.token,
                                             label_name,
                                             1)
        label_details = response.json()
        self.assertEqual(label_details['color'], 1)

    def test_delete_label(self):
        label_name = "Label 1"
        self.t.add_label(self.user.token, label_name)
        response = self.t.get_labels(self.user.token)
        labels = response.json()
        self.assertEqual(len(labels), 1)
        self.t.delete_label(self.user.token, label_name)
        response = self.t.get_labels(self.user.token)
        labels = response.json()
        self.assertEqual(len(labels), 0)

    def test_get_uncompleted_tasks_failure(self):
        response = self.t.get_uncompleted_tasks(self.user.token, 'badid')
        self.assertEqual(response.status_code, 400)

    def test_add_task_success(self):
        response = self.t.add_task(self.user.token, 'Task 1')
        inbox = self._get_inbox()
        inbox_id = inbox['id']
        response = self.t.get_uncompleted_tasks(self.user.token, inbox_id)
        uncompleted_tasks = response.json()
        self.assertEqual(len(uncompleted_tasks), 1)

    def test_add_task_failure(self):
        response = self.t.add_task(self.user.token,
                                   'Task 1',
                                   project_id='badid')
        self.assertEqual(response.status_code, 400)
        response = self.t.add_task(self.user.token, 'Task 2', date_string='d')
        self.assertEqual(response.text, '"ERROR_WRONG_DATE_SYNTAX"')

    def test_update_task_success(self):
        response = self.t.add_task(self.user.token, 'Task 1')
        task = response.json()
        task_id = task['id']
        response = self.t.update_task(self.user.token,
                                      task_id,
                                      content="Task 2")
        updated_task = response.json()
        self.assertEqual(updated_task['content'], "Task 2")
        self.assertEqual(updated_task['id'], task_id)

    def test_update_task_failure(self):
        task_id = '-1' # Bad id - won't exist.
        response = self.t.update_task(self.user.token, task_id)
        self.assertEqual(response.text, '"ERROR_ITEM_NOT_FOUND"')

    def test_get_all_completed_tasks_success(self):
        response = self.t.add_task(self.user.token, 'Task 1')
        task = response.json()
        task_id = task['id']
        self.t.complete_tasks(self.user.token, str([task_id]))
        response = self.t.get_all_completed_tasks(self.user.token)
        tasks = response.json()['items']
        self.assertEqual(len(tasks), 0) # Premium users only.

    def test_get_all_completed_tasks_failure(self):
        project_id = 'badid'
        response = self.t.get_all_completed_tasks(self.user.token,
                                                  project_id=project_id)
        self.assertEqual(response.status_code, 400)

    def test_get_tasks_by_id(self):
        response = self.t.add_task(self.user.token, 'Task 1')
        task = response.json()
        task_id = task['id']
        self.t.add_task(self.user.token, 'Task 2')
        response = self.t.get_tasks_by_id(self.user.token, str([task_id]))
        tasks = response.json()
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task['content'], 'Task 1')

    def test_complete_tasks(self):
        self.t.add_task(self.user.token, 'Task 1')
        self.t.add_task(self.user.token, 'Task 2')
        inbox = self._get_inbox()
        inbox_id = inbox['id']
        response = self.t.get_uncompleted_tasks(self.user.token, inbox_id)
        tasks = response.json()
        task_ids = [task['id'] for task in tasks]
        response = self.t.complete_tasks(self.user.token, str(task_ids))
        self.assertEqual(response.text, '"ok"')
        response = self.t.get_uncompleted_tasks(self.user.token, inbox_id)
        tasks = response.json()
        self.assertEqual(len(tasks), 0)

    def test_update_task_ordering_success(self):
        for i in range(10):
            self.t.add_task(self.user.token, 'Task 1')
        inbox = self._get_inbox()
        inbox_id = inbox['id']
        response = self.t.get_uncompleted_tasks(self.user.token, inbox_id)
        tasks = response.json()
        task_ordering = [task['id'] for task in tasks]
        rev_ordering = task_ordering[::-1]
        response = self.t.update_task_ordering(self.user.token,
                                               inbox_id,
                                               str(rev_ordering))
        self.assertEqual(response.text, '"ok"')
        response = self.t.get_uncompleted_tasks(self.user.token, inbox_id)
        tasks = response.json()
        task_ordering = [task['id'] for task in tasks]
        self.assertEqual(task_ordering, rev_ordering)

    def test_update_task_ordering_failure(self):
        response = self.t.update_task_ordering(self.user.token,
                                               'badid',
                                               str([]))
        self.assertEqual(response.status_code, 400)

    def test_move_tasks(self):
        response = self.t.add_project(self.user.token, 'Project 1')
        project = response.json()
        project_id = project['id']
        response = self.t.add_task(self.user.token, 'Task 1')
        task = response.json()
        task_id = task['id']
        inbox = self._get_inbox()
        inbox_id = inbox['id']
        task_locations = '{{"{p_id}": ["{t_id}"]}}'.format(p_id=inbox_id,
                                                           t_id=task_id)
        response = self.t.move_tasks(self.user.token,
                                     str(task_locations),
                                     project_id)
        response = self.t.get_uncompleted_tasks(self.user.token, inbox_id)
        tasks = response.json()
        self.assertEqual(len(tasks), 0)
        response = self.t.get_uncompleted_tasks(self.user.token, project_id)
        tasks = response.json()
        self.assertEqual(len(tasks), 1)

    def test_advance_recurring_dates(self):
        response = self.t.add_task(self.user.token,
                                   'Task 1',
                                   date_string='every day')
        task = response.json()
        task_id = task['id']
        task_due_date = task['due_date']
        response = self.t.advance_recurring_dates(self.user.token,
                                                       str([task_id]))
        tasks = response.json()
        task = tasks[0]
        self.assertEqual(task['id'], task_id)
        self.assertNotEqual(task['due_date'], task_due_date)

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
