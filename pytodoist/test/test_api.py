#!/usr/bin/env python

"""This module contains unit tests for the pytodoist.api module."""
import sys
import unittest
from pytodoist.api import TodoistAPI

# No magic numbers
_N_DEFAULT_PROJECTS = 8
_N_DEFAULT_LABELS = 0

# Constants for testing invalid input
_INCORRECT_PASSWORD = None
_INCORRECT_TOKEN = None
_INVALID_ID = None
_INVALID_NAME = ''
_INVALID_NOTE = ''
_INVALID_COLOR = -1
_INVALID_DATE_STRING = 'd'

# Constants for creating objects
_PROJECT_NAME = 'Project'
_LABEL_NAME = 'Label'
_TASK = 'Task'
_NOTE = 'Note'


class TestUser(object):
    """A fake user to use in each unit test."""

    def __init__(self):
        self.full_name = "Py Todoist"
        self.email = "pytodoist.test.email@gmail.com"
        self.password = "pytodoistpassword"
        self.token = None


class TodoistAPITest(unittest.TestCase):
    """Test the functionality of the pytodoist.Todoist class"""

    @classmethod
    def setUpClass(cls):
        cls.api = TodoistAPI()
        cls.user = TestUser()

    def setUp(self):
        response = self.api.register(self.user.email, self.user.full_name, self.user.password)
        if not self.api.is_response_success(response):
            response = self.api.login(self.user.email, self.user.password)
        user_json = response.json()
        self.user.token = user_json['token']

    def tearDown(self):
        self.api.delete_user(self.user.token, self.user.password)

    def test_login_success(self):
        response = self.api.login(self.user.email, self.user.password)
        self.assertTrue(self.api.is_response_success(response))
        self.assertIn('token', response.json())

    def test_login_failure(self):
        response = self.api.login(self.user.email, _INCORRECT_PASSWORD)
        self.assertFalse(self.api.is_response_success(response))

    def test_ping_success(self):
        response = self.api.ping(self.user.token)
        self.assertTrue(self.api.is_response_success(response))

    def test_ping_failure(self):
        response = self.api.ping(_INCORRECT_TOKEN)
        self.assertFalse(self.api.is_response_success(response))

    def test_get_timezones(self):
        response = self.api.get_timezones()
        self.assertTrue(self.api.is_response_success(response))
        timezones = response.json()
        self.assertTrue(len(timezones) > 0)

    def test_register_success(self):
        self.api.delete_user(self.user.token, self.user.password)
        response = self.api.register(self.user.email, self.user.full_name, self.user.password)
        self.assertTrue(self.api.is_response_success(response))
        self.assertIn('token', response.json())

    def test_register_failure(self):
        response = self.api.register(self.user.email, self.user.full_name, self.user.password)
        self.assertFalse(self.api.is_response_success(response))

    def test_delete_user(self):
        response = self.api.delete_user(self.user.token, self.user.password)
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.add_task(self.user.token, _TASK)
        self.assertFalse(self.api.is_response_success(response))

    def test_update_user_success(self):
        new_email = "updated" + self.user.email
        response = self.api.update_user(self.user.token, email=new_email)
        self.assertTrue(self.api.is_response_success(response))
        user_json = response.json()
        self.assertEqual(user_json['email'], new_email)

    def test_update_user_bad_email(self):
        other_user = TestUser()
        other_user.email = 'other.user.pytodoist.email@gmail.com'
        response = self.api.register(other_user.email, other_user.full_name, other_user.password)
        self.assertTrue(self.api.is_response_success(response))
        other_user_json = response.json()
        other_user_token = other_user_json['token']
        response = self.api.update_user(self.user.token, email=other_user.email)
        self.assertFalse(self.api.is_response_success(response))
        response = self.api.delete_user(other_user_token, other_user.password)
        self.assertTrue(self.api.is_response_success(response))

    def test_update_avatar_use_default(self):
        response = self.api.update_avatar(self.user.token, delete=1)
        self.assertTrue(self.api.is_response_success(response))

    def test_get_redirect_link(self):
        response = self.api.get_redirect_link(self.user.token)
        self.assertTrue(self.api.is_response_success(response))
        link_json = response.json()
        link = link_json['link']
        self.assertIsNotNone(link)

    def test_get_projects(self):
        n_projects = self._get_project_count()
        self.assertEqual(n_projects, _N_DEFAULT_PROJECTS)

    def test_get_projects_plus_one(self):
        self._add_project()
        n_projects = self._get_project_count()
        self.assertEqual(n_projects, _N_DEFAULT_PROJECTS + 1)

    def test_get_project_success(self):
        project_id = self._get_inbox_id()
        response = self.api.get_project(self.user.token, project_id)
        self.assertTrue(self.api.is_response_success(response))
        project_json = response.json()
        self.assertEqual(project_json['name'], 'Inbox')

    def test_get_project_failure(self):
        response = self.api.get_project(self.user.token, _INVALID_ID)
        self.assertFalse(self.api.is_response_success(response))

    def test_add_project_success(self):
        project_name = _PROJECT_NAME
        response = self.api.add_project(self.user.token, project_name)
        self.assertTrue(self.api.is_response_success(response))
        project_json = response.json()
        self.assertEqual(project_json['name'], project_name)
        n_projects = self._get_project_count()
        self.assertEqual(n_projects, _N_DEFAULT_PROJECTS + 1)

    def test_add_project_failure(self):
        response = self.api.add_project(self.user.token, _INVALID_NAME)
        self.assertFalse(self.api.is_response_success(response))
        n_projects = self._get_project_count()
        self.assertEqual(n_projects, _N_DEFAULT_PROJECTS)

    def test_update_project_success(self):
        project = self._add_project()
        new_name = 'update'
        response = self.api.update_project(self.user.token, project['id'], name=new_name)
        self.assertTrue(self.api.is_response_success(response))
        updated_project = response.json()
        self.assertEqual(updated_project['name'], new_name)

    def test_update_project_failure(self):
        response = self.api.update_project(self.user.token, _INVALID_ID, name=None)
        self.assertFalse(self.api.is_response_success(response))

    def test_update_project_orders_success(self):
        for i in range(5):
            response = self.api.add_project(self.user.token, _PROJECT_NAME + str(i))
            self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_projects(self.user.token)
        self.assertTrue(self.api.is_response_success(response))
        current_order = [project['id'] for project in response.json()]
        reverse_order = current_order[::-1]
        response = self.api.update_project_orders(self.user.token, str(reverse_order))
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_projects(self.user.token)
        self.assertTrue(self.api.is_response_success(response))
        updated_order = [project['id'] for project in response.json()]
        self.assertEqual(updated_order, reverse_order)

    def test_update_project_orders_failure(self):
        bad_ids = str([_INVALID_ID])
        response = self.api.update_project_orders(self.user.token, bad_ids)
        self.assertFalse(self.api.is_response_success(response))

    def test_delete_project_success(self):
        project = self._add_project()
        n_projects = self._get_project_count()
        self.assertTrue(n_projects == _N_DEFAULT_PROJECTS + 1)
        response = self.api.delete_project(self.user.token, project['id'])
        self.assertTrue(self.api.is_response_success(response))
        n_projects = self._get_project_count()
        self.assertTrue(n_projects == _N_DEFAULT_PROJECTS)

    def test_delete_project_failure(self):
        response = self.api.delete_project(self.user.token, _INVALID_ID)
        self.assertFalse(self.api.is_response_success(response))

    def test_archive_project_success(self):
        project = self._add_project()
        response = self.api.archive_project(self.user.token, project['id'])
        self.assertTrue(self.api.is_response_success(response))
        archived_ids = response.json()
        self.assertEqual(len(archived_ids), 1)

    def test_archive_project_failure(self):
        response = self.api.archive_project(self.user.token, _INVALID_ID)
        self.assertFalse(self.api.is_response_success(response))

    def test_get_archived_projects(self):
        project = self._add_project()
        response = self.api.archive_project(self.user.token, project['id'])
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_archived_projects(self.user.token)
        self.assertTrue(self.api.is_response_success(response))
        archived_projects = response.json()
        self.assertEqual(len(archived_projects), 1)

    def test_unarchive_project_success(self):
        project = self._add_project()
        response = self.api.archive_project(self.user.token, project['id'])
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.unarchive_project(self.user.token, project['id'])
        self.assertTrue(self.api.is_response_success(response))
        unarchived_ids = response.json()
        self.assertEqual(len(unarchived_ids), 1)

    def test_unarchive_project_failure(self):
        project = self._add_project()
        response = self.api.archive_project(self.user.token, project['id'])
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.unarchive_project(self.user.token, _INVALID_ID)
        self.assertFalse(self.api.is_response_success(response))

    def test_get_labels(self):
        response = self.api.add_label(self.user.token, _LABEL_NAME)
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_labels(self.user.token)
        self.assertTrue(self.api.is_response_success(response))
        labels = response.json()
        self.assertTrue(isinstance(labels, dict))
        self.assertEqual(len(labels), _N_DEFAULT_LABELS + 1)

    def test_get_labels_as_list(self):
        response = self.api.add_label(self.user.token, _LABEL_NAME)
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_labels(self.user.token, as_list=1)
        self.assertTrue(self.api.is_response_success(response))
        labels = response.json()
        self.assertTrue(isinstance(labels, list))
        self.assertEqual(len(labels), _N_DEFAULT_LABELS + 1)

    def test_add_label(self):
        response = self.api.add_label(self.user.token, _LABEL_NAME)
        self.assertTrue(self.api.is_response_success(response))
        label = response.json()
        self.assertEqual(label['name'], _LABEL_NAME)
        response = self.api.get_labels(self.user.token)
        self.assertTrue(self.api.is_response_success(response))
        labels = response.json()
        self.assertEqual(len(labels), _N_DEFAULT_LABELS + 1)

    def test_update_label_name(self):
        new_name = 'update' + _LABEL_NAME
        self.api.add_label(self.user.token, _LABEL_NAME)
        response = self.api.update_label_name(self.user.token, _LABEL_NAME, new_name)
        self.assertTrue(self.api.is_response_success(response))
        label = response.json()
        self.assertEqual(label['name'], new_name)

    def test_update_label_color_success(self):
        new_color = 1
        self.api.add_label(self.user.token, _LABEL_NAME, color=0)
        response = self.api.update_label_color(self.user.token, _LABEL_NAME, new_color)
        self.assertTrue(self.api.is_response_success(response))
        label = response.json()
        self.assertEqual(label['color'], new_color)

    def test_delete_label_success(self):
        response = self.api.add_label(self.user.token, _LABEL_NAME)
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_labels(self.user.token)
        self.assertTrue(self.api.is_response_success(response))
        labels = response.json()
        self.assertEqual(len(labels), _N_DEFAULT_LABELS + 1)
        response = self.api.delete_label(self.user.token, _LABEL_NAME)
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_labels(self.user.token)
        self.assertTrue(self.api.is_response_success(response))
        labels = response.json()
        self.assertEqual(len(labels), _N_DEFAULT_LABELS)

    def test_get_uncompleted_tasks_success(self):
        self._add_task()
        response = self.api.get_uncompleted_tasks(self.user.token, self._get_inbox_id())
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        self.assertEqual(len(tasks), 1)

    def test_get_uncompleted_tasks_failure(self):
        response = self.api.get_uncompleted_tasks(self.user.token, _INVALID_ID)
        self.assertFalse(self.api.is_response_success(response))

    def test_add_task_success(self):
        response = self.api.add_task(self.user.token, _TASK)
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_uncompleted_tasks(self.user.token, self._get_inbox_id())
        self.assertTrue(self.api.is_response_success(response))
        uncompleted_tasks = response.json()
        self.assertEqual(len(uncompleted_tasks), 1)

    def test_add_task_failure(self):
        response = self.api.add_task(self.user.token, _TASK, date_string=_INVALID_DATE_STRING)
        self.assertFalse(self.api.is_response_success(response))

    def test_update_task_success(self):
        task = self._add_task()
        new_content = _TASK + '2'
        response = self.api.update_task(self.user.token, task['id'], content=new_content)
        self.assertTrue(self.api.is_response_success(response))
        updated_task = response.json()
        self.assertEqual(updated_task['content'], new_content)

    def test_update_task_failure(self):
        response = self.api.update_task(self.user.token, _INVALID_ID)
        self.assertFalse(self.api.is_response_success(response))

    def test_get_all_completed_tasks_success(self):
        task = self._add_task()
        task_ids = str([task['id']])
        response = self.api.complete_tasks(self.user.token, task_ids)
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_all_completed_tasks(self.user.token)
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()['items']
        self.assertEqual(len(tasks), 0)  # Premium users only.

    def test_get_completed_tasks(self):
        task = self._add_task()
        task_ids = str([task['id']])
        response = self.api.complete_tasks(self.user.token, task_ids)
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_completed_tasks(self.user.token, self._get_inbox_id())
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        self.assertEqual(len(tasks), 1)

    def test_get_completed_tasks_failure(self):
        response = self.api.get_completed_tasks(self.user.token, _INVALID_ID)
        self.assertFalse(self.api.is_response_success(response))

    def test_get_tasks_by_id(self):
        response = self.api.add_task(self.user.token, _TASK)
        task = response.json()
        task_id = task['id']
        self.api.add_task(self.user.token, _TASK + '2')
        response = self.api.get_tasks_by_id(self.user.token, str([task_id]))
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task['content'], _TASK)

    def test_complete_tasks(self):
        response = self.api.add_task(self.user.token, _TASK)
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.add_task(self.user.token, _TASK + '2')
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_uncompleted_tasks(self.user.token, self._get_inbox_id())
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        task_ids = str([task['id'] for task in tasks])
        response = self.api.complete_tasks(self.user.token, task_ids)
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_uncompleted_tasks(self.user.token, self._get_inbox_id())
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        self.assertEqual(len(tasks), 0)

    def test_update_task_ordering_success(self):
        for i in range(5):
            self.api.add_task(self.user.token, _TASK + str(i))
        response = self.api.get_uncompleted_tasks(self.user.token, self._get_inbox_id())
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        task_ordering = [task['id'] for task in tasks]
        rev_ordering = task_ordering[::-1]
        response = self.api.update_task_ordering(self.user.token, self._get_inbox_id(), str(rev_ordering))
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_uncompleted_tasks(self.user.token, self._get_inbox_id())
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        task_ordering = [task['id'] for task in tasks]
        self.assertEqual(task_ordering, rev_ordering)

    def test_update_task_ordering_failure(self):
        response = self.api.update_task_ordering(self.user.token, _INVALID_ID, '')
        self.assertFalse(self.api.is_response_success(response))

    def test_move_tasks(self):
        project = self._add_project()
        task = self._add_task()
        task_locations = '{{"{p_id}": ["{t_id}"]}}'.format(p_id=self._get_inbox_id(), t_id=task['id'])
        response = self.api.move_tasks(self.user.token, str(task_locations), project['id'])
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_uncompleted_tasks(self.user.token, self._get_inbox_id())
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        self.assertEqual(len(tasks), 0)
        response = self.api.get_uncompleted_tasks(self.user.token, project['id'])
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        self.assertEqual(len(tasks), 1)

    def test_advance_recurring_dates(self):
        response = self.api.add_task(self.user.token, _TASK, date_string='every day')
        self.assertTrue(self.api.is_response_success(response))
        task = response.json()
        task_id = task['id']
        task_due_date = task['due_date']
        response = self.api.advance_recurring_dates(self.user.token, str([task_id]))
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        task = tasks[0]
        self.assertNotEqual(task['due_date'], task_due_date)

    def test_advance_recurring_dates_failure(self):
        response = self.api.add_task(self.user.token, _TASK, date_string=_INVALID_DATE_STRING)
        self.assertFalse(self.api.is_response_success(response))

    def test_delete_tasks(self):
        for i in range(5):
            response = self.api.add_task(self.user.token, _TASK + str(i))
            self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_uncompleted_tasks(self.user.token, self._get_inbox_id())
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        task_ids = [task['id'] for task in tasks]
        self.assertTrue(len(tasks) > 0)
        response = self.api.delete_tasks(self.user.token, str(task_ids))
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_uncompleted_tasks(self.user.token, self._get_inbox_id())
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        self.assertEqual(len(tasks), 0)

    def test_uncomplete_tasks(self):
        task = self._add_task()
        response = self.api.complete_tasks(self.user.token, str([task['id']]))
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_uncompleted_tasks(self.user.token, self._get_inbox_id())
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        self.assertEqual(len(tasks), 0)
        response = self.api.uncomplete_tasks(self.user.token, str([task['id']]))
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_uncompleted_tasks(self.user.token, self._get_inbox_id())
        self.assertTrue(self.api.is_response_success(response))
        tasks = response.json()
        self.assertEqual(len(tasks), 1)

    def test_add_note_success(self):
        task = self._add_task()
        response = self.api.add_note(self.user.token, task['id'], _NOTE)
        self.assertTrue(self.api.is_response_success(response))
        note = response.json()
        self.assertEqual(note['content'], _NOTE)
        response = self.api.get_notes(self.user.token, task['id'])
        self.assertTrue(self.api.is_response_success(response))
        notes = response.json()
        self.assertEqual(len(notes), 1)

    def test_add_note_failure(self):
        response = self.api.add_note(self.user.token, _INVALID_ID, _NOTE)
        self.assertFalse(self.api.is_response_success(response))

    def test_update_note_success(self):
        task = self._add_task()
        response = self.api.add_note(self.user.token, task['id'], _NOTE)
        self.assertTrue(self.api.is_response_success(response))
        note = response.json()
        note_id = note['id']
        new_note = _NOTE + '2'
        response = self.api.update_note(self.user.token, note_id, new_note)
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_notes(self.user.token, task['id'])
        self.assertTrue(self.api.is_response_success(response))
        notes = response.json()
        note = notes[0]
        self.assertEqual(note['content'], new_note)

    def test_update_note_failure(self):
        response = self.api.update_note(self.user.token, _INVALID_ID, _INVALID_NOTE)
        self.assertFalse(self.api.is_response_success(response))

    def test_delete_note(self):
        task = self._add_task()
        response = self.api.add_note(self.user.token, task['id'], _NOTE)
        self.assertTrue(self.api.is_response_success(response))
        note = response.json()
        note_id = note['id']
        response = self.api.delete_note(self.user.token, task['id'], note_id)
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_notes(self.user.token, task['id'])
        self.assertTrue(self.api.is_response_success(response))
        notes = response.json()
        self.assertEqual(len(notes), 0)

    def test_get_notes(self):
        task = self._add_task()
        response = self.api.add_note(self.user.token, task['id'], _NOTE)
        self.assertTrue(self.api.is_response_success(response))
        note = response.json()
        note_id = note['id']
        response = self.api.get_notes(self.user.token, task['id'])
        self.assertTrue(self.api.is_response_success(response))
        notes = response.json()
        self.assertEqual(len(notes), 1)
        note = notes[0]
        self.assertEqual(note['id'], note_id)
        self.assertEqual(note['content'], _NOTE)

    def test_get_notes_and_task(self):
        task = self._add_task()
        self.api.add_note(self.user.token, task['id'], _NOTE)
        response = self.api.get_notes_and_task(self.user.token, task['id'])
        self.assertTrue(self.api.is_response_success(response))
        notes_and_task = response.json()
        self.assertEqual(len(notes_and_task), 3)

    def test_search_tasks(self):
        response = self.api.add_task(self.user.token, _TASK, date_string='tomorrow')
        self.assertTrue(self.api.is_response_success(response))
        task = response.json()
        task_id = task['id']
        queries = '["tomorrow"]'
        response = self.api.search_tasks(self.user.token, queries)
        self.assertTrue(self.api.is_response_success(response))
        tasks = []
        for entry in response.json():
            if entry['query'] == 'tomorrow':
                tasks = entry['data']
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task['id'], task_id)

    def test_get_notification_settings(self):
        response = self.api.get_notification_settings(self.user.token)
        self.assertTrue(self.api.is_response_success(response))
        settings = response.json()
        self.assertTrue(len(settings) > 0)

    def test_update_notification_settings(self):
        response = self.api.update_notification_settings(self.user.token, 'user_left_project', 'push', 0)
        self.assertTrue(self.api.is_response_success(response))
        response = self.api.get_notification_settings(self.user.token)
        self.assertTrue(self.api.is_response_success(response))
        settings = response.json()
        setting = settings['user_left_project']
        self.assertEqual(setting['notify_push'], True)

    def _add_project(self):
        response = self.api.add_project(self.user.token, 'Project')
        self.assertTrue(self.api.is_response_success(response))
        return response.json()

    def _add_task(self):
        response = self.api.add_task(self.user.token, 'Task')
        self.assertTrue(self.api.is_response_success(response))
        return response.json()

    def _add_label(self):
        response = self.api.add_label(self.user.token, 'Label')
        self.assertTrue(self.api.is_response_success(response))
        return response.json()

    def _get_inbox(self):
        response = self.api.get_projects(self.user.token)
        self.assertTrue(self.api.is_response_success(response))
        projects = response.json()
        for project in projects:
            if project['name'] == 'Inbox':
                return project

    def _get_inbox_id(self):
        inbox = self._get_inbox()
        return inbox['id']

    def _get_project_count(self):
        response = self.api.get_projects(self.user.token)
        self.assertTrue(self.api.is_response_success(response))
        projects = response.json()
        return len(projects)


if __name__ == '__main__':
    if sys.version_info > (3, 0):
        # Avoid the ResourceWarning spam bug.
        unittest.main(warnings='ignore')
    unittest.main()
