#!/usr/bin/env python
"""This module contains unit tests for the pytodoist.api module."""

import sys
import unittest
from pytodoist.api import TodoistAPI

N_DEFAULT_PROJECTS = 8


class TestUser(object):
    """A fake user to use in each unit test."""

    def __init__(self):
        self.full_name = "Py Todoist"
        self.email = "pytodoist.test.email@gmail.com"
        self.password = "pytodoist.test.password"
        self.token = None


class TodoistAPITest(unittest.TestCase):
    """Test the functionality of the pytodoist.Todoist class"""

    @classmethod
    def setUpClass(cls):
        cls.t = TodoistAPI()
        cls.user = TestUser()

    def setUp(self):
        response = self.t.register(self.user.email,
                                   self.user.full_name,
                                   self.user.password)
        if response.text == '"ALREADY_REGISTRED"':
            response = self.t.login(self.user.email, self.user.password)
        user = response.json()
        self.user.token = user['token']

    def tearDown(self):
        self.t.delete_user(self.user.token, self.user.password)

    def test_login_success(self):
        response = self.t.login(self.user.email, self.user.password)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    def test_login_failure(self):
        response = self.t.login(self.user.email, 'badpassword')
        self.assertEqual(response.text, '"LOGIN_ERROR"')

    def test_ping_success(self):
        response = self.t.ping(self.user.token)
        self.assertEqual(response.status_code, 200)

    def test_ping_failure(self):
        response = self.t.ping('badtoken')
        self.assertEqual(response.status_code, 401)

    def test_get_timezones(self):
        response = self.t.get_timezones()
        self.assertEqual(response.status_code, 200)
        timezones = response.json()
        self.assertTrue(len(timezones) > 0)

    def test_register_already_registered(self):
        response = self.t.register(self.user.email,
                                   self.user.full_name,
                                   self.user.password)
        self.assertEqual(response.text, '"ALREADY_REGISTRED"')

    def test_update_user(self):
        new_email = "todoist.updated.email@gmail.com"
        response = self.t.update_user(self.user.token, email=new_email)
        self.assertEqual(response.status_code, 200)
        user_details = response.json()
        self.assertEqual(user_details['email'], new_email)

    def test_update_user_bad_password(self):
        new_password = "007"  # Too short.
        response = self.t.update_user(self.user.token, password=new_password)
        self.assertEqual(response.status_code, 400)

    def test_update_user_bad_email(self):
        new_email = "gareeblackwood@gmail.com"  # Already exists.
        response = self.t.update_user(self.user.token, email=new_email)
        self.assertEqual(response.text, '"ERROR_EMAIL_FOUND"')

    def test_update_avatar(self):
        response = self.t.update_avatar(self.user.token, delete=1)
        self.assertEqual(response.status_code, 200)

    def test_get_redirect_link(self):
        response = self.t.get_redirect_link(self.user.token)
        self.assertEqual(response.status_code, 200)
        link = response.json()['link']
        self.assertIsNotNone(link)

    def test_get_projects(self):
        response = self.t.get_projects(self.user.token)
        self.assertEqual(response.status_code, 200)
        projects = response.json()
        self.assertEqual(len(projects), N_DEFAULT_PROJECTS)

    def test_get_project_success(self):
        project_id = self._get_inbox_id()
        response = self.t.get_project(self.user.token, project_id)
        self.assertEqual(response.status_code, 200)
        project_details = response.json()
        self.assertEqual(project_details['name'], 'Inbox')

    def test_get_project_failure(self):
        response = self.t.get_project(self.user.token, 'badid')
        self.assertEqual(response.status_code, 400)

    def test_add_project_success(self):
        project_name = 'Project 1'
        response = self.t.add_project(self.user.token, project_name)
        self.assertEqual(response.status_code, 200)
        project_details = response.json()
        self.assertEqual(project_details['name'], project_name)

    def test_add_project_failure(self):
        project_name = ""
        response = self.t.add_project(self.user.token, project_name)
        self.assertEqual(response.text, '"ERROR_NAME_IS_EMPTY"')

    def test_update_project_success(self):
        project = self._add_project()
        response = self.t.update_project(self.user.token, project['id'],
                                         name='Update')
        self.assertEqual(response.status_code, 200)
        updated_project = response.json()
        self.assertEqual(updated_project['name'], 'Update')

    def test_update_project_failure(self):
        response = self.t.update_project(self.user.token, 'badid',
                                         name='Update')
        self.assertEqual(response.status_code, 400)

    def test_update_project_orders_success(self):
        for i in range(5):
            self.t.add_project(self.user.token, 'Project_' + str(i))
        response = self.t.get_projects(self.user.token)
        current_order = [project['id'] for project in response.json()]
        reverse_order = current_order[::-1]
        self.t.update_project_orders(self.user.token, str(reverse_order))
        response = self.t.get_projects(self.user.token)
        updated_order = [project['id'] for project in response.json()]
        self.assertEqual(updated_order, reverse_order)

    def test_update_project_orders_failure(self):
        bad_ids = ['1', '2']
        response = self.t.update_project_orders(self.user.token, str(bad_ids))
        self.assertEqual(response.status_code, 400)

    def test_delete_project(self):
        project = self._add_project()
        response = self.t.delete_project(self.user.token, project['id'])
        self.assertEqual(response.status_code, 200)
        response = self.t.get_projects(self.user.token)
        self.assertTrue(len(response.json()) == N_DEFAULT_PROJECTS)

    def test_archive_project(self):
        project = self._add_project()
        response = self.t.archive_project(self.user.token, project['id'])
        self.assertEqual(response.status_code, 200)
        archived_ids = response.json()
        self.assertEqual(len(archived_ids), 1)

    def test_get_archived_projects(self):
        project = self._add_project()
        self.t.archive_project(self.user.token, project['id'])
        response = self.t.archive_project(self.user.token, project['id'])
        archived_projects = response.json()
        self.assertEqual(len(archived_projects), 1)

    def test_unarchive_project(self):
        project = self._add_project()
        response = self.t.unarchive_project(self.user.token, project['id'])
        self.assertEqual(response.status_code, 200)
        unarchived_ids = response.json()
        self.assertEqual(len(unarchived_ids), 1)

    def test_get_labels(self):
        self.t.add_label(self.user.token, 'Label 1')
        response = self.t.get_labels(self.user.token)
        self.assertEqual(response.status_code, 200)
        labels = response.json()
        self.assertTrue(isinstance(labels, dict))
        self.assertEqual(len(labels), 1)
        response = self.t.get_labels(self.user.token, as_list=1)
        self.assertEqual(response.status_code, 200)
        labels = response.json()
        self.assertTrue(isinstance(labels, list))
        self.assertEqual(len(labels), 1)

    def test_add_label(self):
        label_name = 'Label 1'
        response = self.t.add_label(self.user.token, label_name)
        self.assertEqual(response.status_code, 200)
        label = response.json()
        self.assertEqual(label['name'], label_name)
        response = self.t.get_labels(self.user.token)
        labels = response.json()
        self.assertEqual(len(labels), 1)

    def test_update_label_name(self):
        label_name = "Label 1"
        new_name = "Updated"
        self.t.add_label(self.user.token, label_name)
        response = self.t.update_label_name(self.user.token, label_name,
                                            new_name)
        self.assertEqual(response.status_code, 200)
        label = response.json()
        self.assertEqual(label['name'], new_name)

    def test_update_label_color(self):
        label_name = "Label 1"
        label_color = 0
        self.t.add_label(self.user.token, label_name, color=label_color)
        response = self.t.update_label_color(self.user.token, label_name, 1)
        self.assertEqual(response.status_code, 200)
        label = response.json()
        self.assertEqual(label['color'], 1)

    def test_delete_label(self):
        label_name = "Label 1"
        self.t.add_label(self.user.token, label_name)
        response = self.t.get_labels(self.user.token)
        labels = response.json()
        self.assertEqual(len(labels), 1)
        response = self.t.delete_label(self.user.token, label_name)
        self.assertEqual(response.status_code, 200)
        response = self.t.get_labels(self.user.token)
        labels = response.json()
        self.assertEqual(len(labels), 0)

    def test_get_uncompleted_tasks_failure(self):
        response = self.t.get_uncompleted_tasks(self.user.token, 'badid')
        self.assertEqual(response.status_code, 400)

    def test_add_task_success(self):
        response = self.t.add_task(self.user.token, 'Task 1')
        self.assertEqual(response.status_code, 200)
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
        self.assertEqual(response.status_code, 200)
        updated_task = response.json()
        self.assertEqual(updated_task['content'], "Task 2")
        self.assertEqual(updated_task['id'], task_id)

    def test_update_task_failure(self):
        task_id = '-1'  # Bad id - won't exist.
        response = self.t.update_task(self.user.token, task_id)
        self.assertEqual(response.text, '"ERROR_ITEM_NOT_FOUND"')

    def test_get_all_completed_tasks_success(self):
        response = self.t.add_task(self.user.token, 'Task 1')
        task = response.json()
        task_id = task['id']
        self.t.complete_tasks(self.user.token, str([task_id]))
        response = self.t.get_all_completed_tasks(self.user.token)
        self.assertEqual(response.status_code, 200)
        tasks = response.json()['items']
        self.assertEqual(len(tasks), 0)  # Premium users only.

    def test_get_completed_tasks_failure(self):
        project_id = 'badid'
        response = self.t.get_completed_tasks(self.user.token, project_id)
        self.assertEqual(response.status_code, 400)

    def test_get_tasks_by_id(self):
        response = self.t.add_task(self.user.token, 'Task 1')
        task = response.json()
        task_id = task['id']
        self.t.add_task(self.user.token, 'Task 2')
        response = self.t.get_tasks_by_id(self.user.token, str([task_id]))
        self.assertEqual(response.status_code, 200)
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
        self.assertEqual(response.status_code, 200)
        response = self.t.get_uncompleted_tasks(self.user.token, inbox_id)
        tasks = response.json()
        self.assertEqual(len(tasks), 0)

    def test_update_task_ordering_success(self):
        for i in range(10):
            self.t.add_task(self.user.token, 'Task_' + str(i))
        inbox = self._get_inbox()
        inbox_id = inbox['id']
        response = self.t.get_uncompleted_tasks(self.user.token, inbox_id)
        tasks = response.json()
        task_ordering = [task['id'] for task in tasks]
        rev_ordering = task_ordering[::-1]
        response = self.t.update_task_ordering(self.user.token,
                                               inbox_id,
                                               str(rev_ordering))
        self.assertEqual(response.status_code, 200)
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
        self.assertEqual(response.status_code, 200)
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
        self.assertEqual(response.status_code, 200)
        tasks = response.json()
        task = tasks[0]
        self.assertEqual(task['id'], task_id)
        self.assertNotEqual(task['due_date'], task_due_date)

    def test_delete_tasks(self):
        for i in range(3):
            self.t.add_task(self.user.token, 'Task_' + str(i))
        inbox = self._get_inbox()
        inbox_id = inbox['id']
        response = self.t.get_uncompleted_tasks(self.user.token, inbox_id)
        tasks = response.json()
        task_ids = [task['id'] for task in tasks]
        response = self.t.delete_tasks(self.user.token, str(task_ids))
        self.assertEqual(response.status_code, 200)
        response = self.t.get_uncompleted_tasks(self.user.token, inbox_id)
        tasks = response.json()
        self.assertEqual(len(tasks), 0)

    def test_uncomplete_tasks(self):
        response = self.t.add_task(self.user.token, 'Task 1')
        task = response.json()
        task_id = task['id']
        self.t.complete_tasks(self.user.token, str([task_id]))
        response = self.t.uncomplete_tasks(self.user.token, str([task_id]))
        self.assertEqual(response.status_code, 200)
        inbox = self._get_inbox()
        inbox_id = inbox['id']
        response = self.t.get_uncompleted_tasks(self.user.token, inbox_id)
        tasks = response.json()
        self.assertEqual(len(tasks), 1)

    def test_add_note(self):
        response = self.t.add_task(self.user.token, 'Task 1')
        task = response.json()
        task_id = task['id']
        response = self.t.add_note(self.user.token, task_id, 'Note 1')
        self.assertEqual(response.status_code, 200)
        note = response.json()
        self.assertEqual(note['content'], 'Note 1')

    def test_update_note(self):
        response = self.t.add_task(self.user.token, 'Task 1')
        task = response.json()
        task_id = task['id']
        response = self.t.add_note(self.user.token, task_id, 'Note 1')
        note = response.json()
        note_id = note['id']
        response = self.t.update_note(self.user.token, note_id, 'Note 2')
        self.assertEqual(response.status_code, 200)
        response = self.t.get_notes(self.user.token, task_id)
        notes = response.json()
        note = notes[0]
        self.assertEqual(note['content'], 'Note 2')

    def test_delete_note(self):
        response = self.t.add_task(self.user.token, 'Task 1')
        task = response.json()
        task_id = task['id']
        response = self.t.add_note(self.user.token, task_id, 'Note 1')
        note = response.json()
        note_id = note['id']
        response = self.t.delete_note(self.user.token, task_id, note_id)
        self.assertEqual(response.status_code, 200)
        response = self.t.get_notes(self.user.token, task_id)
        notes = response.json()
        self.assertEqual(len(notes), 0)

    def test_get_notes(self):
        response = self.t.add_task(self.user.token, 'Task 1')
        task = response.json()
        task_id = task['id']
        response = self.t.add_note(self.user.token, task_id, 'Note 1')
        note = response.json()
        note_id = note['id']
        response = self.t.get_notes(self.user.token, task_id)
        self.assertEqual(response.status_code, 200)
        notes = response.json()
        self.assertTrue(len(notes) > 0)
        note = notes[0]
        self.assertEqual(note['id'], note_id)
        self.assertEqual(note['content'], 'Note 1')

    def test_get_notes_and_task(self):
        response = self.t.add_task(self.user.token, 'Task 1')
        task = response.json()
        task_id = task['id']
        self.t.add_note(self.user.token, task_id, 'Note 1')
        response = self.t.get_notes_and_task(self.user.token, task_id)
        self.assertEqual(response.status_code, 200)
        notes_and_task = response.json()
        self.assertEqual(len(notes_and_task), 3)

    def test_search_tasks(self):
        response = self.t.add_task(self.user.token,
                                   'Task 1',
                                   date_string='tomorrow')
        task = response.json()
        task_id = task['id']
        queries = '["tomorrow"]'
        response = self.t.search_tasks(self.user.token, queries)
        self.assertEqual(response.status_code, 200)
        tasks = []
        for entry in response.json():
            if entry['query'] == 'tomorrow':
                tasks = entry['data']
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task['id'], task_id)

    def test_get_notification_settings(self):
        response = self.t.get_notification_settings(self.user.token)
        self.assertEqual(response.status_code, 200)
        settings = response.json()
        self.assertTrue(len(settings) > 0)

    def test_update_notification_settings(self):
        response = self.t.update_notification_settings(self.user.token,
                                                       'user_left_project',
                                                       'push',
                                                       1)
        self.assertEqual(response.status_code, 200)
        response = self.t.get_notification_settings(self.user.token)
        settings = response.json()
        setting = settings['user_left_project']
        self.assertEqual(setting['notify_email'], 1)

    def _add_project(self):
        response = self.t.add_project(self.user.token, 'Project')
        return response.json()

    def _add_task(self):
        response = self.t.add_task(self.user.token, 'Task')
        return response.json()

    def _add_label(self):
        response = self.t.add_label(self.user.token, 'Label')
        return response.json()

    def _get_inbox(self):
        response = self.t.get_projects(self.user.token)
        projects = response.json()
        for project in projects:
            if project['name'] == 'Inbox':
                return project

    def _get_inbox_id(self):
        inbox = self._get_inbox()
        return inbox['id']


def main():
    unittest.main()
    return 0

if __name__ == '__main__':
    sys.exit(main())
