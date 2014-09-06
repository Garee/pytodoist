#!/usr/bin/env python

import unittest
from pytodoist import todoist

N_DEFAULT_PROJECTS = 8

_USER_NAME = "Py Todoist"
_USER_EMAIL = "pytodoist.test.email@gmail.com"
_USER_PASSWORD = "pytodoist.test.password"

_INBOX_PROJECT_NAME = 'Inbox'
_PROJECT_NAME = 'Project'
_TASK = 'Task'
_LABEL = 'Homework'
_NOTE = 'Note'


def _get_user():
    try:
        user = todoist.register(_USER_NAME, _USER_EMAIL, _USER_PASSWORD)
    except todoist.RequestError:
        user = todoist.login(_USER_EMAIL, _USER_PASSWORD)
        user.delete()
        user = todoist.register(_USER_NAME, _USER_EMAIL, _USER_PASSWORD)
    return user


class TodoistTest(unittest.TestCase):

    def test_get_timezones(self):
        timezones = todoist.get_timezones()
        self.assertTrue(len(timezones) > 0)
        self.assertTrue('GMT' in timezones)


class UserTest(unittest.TestCase):

    def setUp(self):
        self.user = _get_user()

    def tearDown(self):
        self.user.delete()

    def test_login_success(self):
        self.user = todoist.login(_USER_EMAIL, _USER_PASSWORD)
        self.assertTrue(self.user.is_logged_in())

    def test_login_failure(self):
        with self.assertRaises(todoist.RequestError):
            todoist.login('', '')

    def test_login_with_token_success(self):
        user = todoist.login_with_token(self.user.token)
        self.assertTrue(user.is_logged_in())

    def test_login_with_token_failure(self):
        with self.assertRaises(todoist.RequestError):
            todoist.login_with_token('')

    def test_is_logged_in(self):
        self.user.token = None
        self.assertFalse(self.user.is_logged_in())
        self.user = todoist.login(_USER_EMAIL, _USER_PASSWORD)
        self.assertTrue(self.user.is_logged_in())

    def test_register(self):
        email = 'unused.todoist.email@gmail.com'
        user = todoist.register(_USER_NAME, email, _USER_PASSWORD)
        self.assertTrue(user.is_logged_in())
        user.delete()

    def test_register_failure(self):
        with self.assertRaises(todoist.RequestError):
            todoist.register('', '', '')

    def test_register_failure_already_registered(self):
        with self.assertRaises(todoist.RequestError):
            todoist.register(_USER_NAME, _USER_EMAIL, _USER_PASSWORD)

    def test_update(self):
        new_name = _USER_NAME + 'Jnr'
        self.user.full_name = new_name
        self.user.update()
        self.user = todoist.login(_USER_EMAIL, _USER_PASSWORD)
        self.assertEqual(self.user.full_name, new_name)

    def test_get_redirect_link(self):
        link = self.user.get_redirect_link()
        self.assertIsNotNone(link)

    def test_add_project(self):
        self.user.add_project(_PROJECT_NAME)
        projects = self.user.get_projects()
        self.assertEqual(len(projects), N_DEFAULT_PROJECTS + 1)
        project = self.user.get_project(_PROJECT_NAME)
        self.assertIsNotNone(project)
        self.assertEqual(project.name, _PROJECT_NAME)

    def test_add_project_failure(self):
        with self.assertRaises(todoist.RequestError):
            self.user.add_project('')

    def test_get_projects(self):
        for i in range(5):
            self.user.add_project(_PROJECT_NAME + str(i))
        projects = self.user.get_projects()
        self.assertEqual(len(projects), N_DEFAULT_PROJECTS + 5)
        for project in projects:
            self.assertIsNotNone(project)

    def test_get_project_success(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        self.assertIsNotNone(inbox)
        self.assertEqual(inbox.name, _INBOX_PROJECT_NAME)

    def test_get_project_failure(self):
        project = self.user.get_project(None)
        self.assertIsNone(project)

    def test_get_archived_projects(self):
        n_arch_projects = len(self.user.get_archived_projects())
        self.assertEqual(n_arch_projects, 0)
        project = self.user.add_project(_PROJECT_NAME)
        project.archive()
        n_arch_projects = len(self.user.get_archived_projects())
        self.assertEqual(n_arch_projects, 1)

    def test_get_project_with_id(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        project = self.user.get_project_with_id(inbox.id)
        self.assertEqual(project.name, inbox.name)

    def test_update_project_orders(self):
        for i in range(5):
            self.user.add_project(_PROJECT_NAME + str(i))
        projects = self.user.get_projects()
        rev_projects = projects[::-1]
        self.user.update_project_orders(rev_projects)
        projects = self.user.get_projects()
        for i, project in enumerate(projects):
            self.assertEqual(project.name, rev_projects[i].name)

    def test_get_uncompleted_tasks(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        inbox.add_task(_TASK)
        tasks = self.user.get_uncompleted_tasks()
        self.assertEqual(len(tasks), 1)

    def test_get_completed_tasks(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        task = inbox.add_task(_TASK)
        task.complete()
        completed_tasks = self.user.get_completed_tasks()
        self.assertEqual(len(completed_tasks), 1)

    def test_search_completed_tasks(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        task = inbox.add_task(_TASK + ' @' + _LABEL)
        task.complete()
        tasks = self.user.search_completed_tasks(label_name=_LABEL)
        # self.assertEqual(len(tasks), 1)  # Requires premium.
        self.assertEqual(len(tasks), 0)

    def test_get_tasks(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        inbox.add_task(_TASK)
        inbox.add_task(_TASK + '2')
        tasks = self.user.get_tasks()
        self.assertEqual(len(tasks), 2)
        for task in tasks:
            self.assertIsNotNone(task)

    def test_add_label(self):
        self.user.add_label(_LABEL, color=todoist.Color.PINK)
        labels = self.user.get_labels()
        self.assertEqual(len(labels), 1)
        label = labels[0]
        self.assertEqual(label.name, _LABEL)
        self.assertEqual(label.color, todoist.Color.PINK)

    def test_get_label(self):
        self.user.add_label(_LABEL)
        label = self.user.get_label(_LABEL)
        self.assertIsNotNone(label)
        self.assertEqual(label.name, _LABEL)

    def test_get_labels(self):
        for i in range(5):
            self.user.add_label(_LABEL + str(i))
        labels = self.user.get_labels()
        self.assertEqual(len(labels), 5)
        for label in labels:
            self.assertIsNotNone(label)

    def test_search_tasks(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        inbox.add_task(_TASK)
        inbox.add_task(_TASK + '2')
        tasks = self.user.search_tasks(todoist.Query.ALL)
        self.assertEqual(len(tasks), 2)

    def test_search_tasks_no_results(self):
        tasks = self.user.search_tasks(todoist.Query.ALL)
        self.assertEqual(len(tasks), 0)

    def test_search_tasks_today(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        inbox.add_task(_TASK, date='today')
        inbox.add_task(_TASK + '2', date='today')
        tasks = self.user.search_tasks(todoist.Query.TODAY)
        self.assertEqual(len(tasks), 2)

    def test_search_tasks_overdue(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        inbox.add_task(_TASK, date='yesterday')
        inbox.add_task(_TASK + '2', date='today')
        tasks = self.user.search_tasks(todoist.Query.OVERDUE)
        self.assertEqual(len(tasks), 1)

    def test_is_email_notified_when(self):
        self.user.disable_email_notifications(todoist.Event.NOTE_ADDED)
        is_recv = self.user.is_email_notified_when(todoist.Event.NOTE_ADDED)
        self.assertFalse(is_recv)

    def test_enable_email_notifications(self):
        self.user.enable_email_notifications(todoist.Event.NOTE_ADDED)
        is_recv = self.user.is_email_notified_when(todoist.Event.NOTE_ADDED)
        self.assertTrue(is_recv)

    def test_is_push_notified_when(self):
        self.user.disable_push_notifications(todoist.Event.NOTE_ADDED)
        is_recv = self.user.is_push_notified_when(todoist.Event.NOTE_ADDED)
        self.assertFalse(is_recv)

    def test_enable_push_notifications(self):
        self.user.enable_push_notifications(todoist.Event.NOTE_ADDED)
        is_recv = self.user.is_push_notified_when(todoist.Event.NOTE_ADDED)
        self.assertTrue(is_recv)


class ProjectTest(unittest.TestCase):

    def setUp(self):
        self.user = _get_user()
        self.project = self.user.add_project(_PROJECT_NAME)

    def tearDown(self):
        self.user.delete()

    def test_delete(self):
        self.project.delete()
        projects = self.user.get_projects()
        self.assertEqual(len(projects), N_DEFAULT_PROJECTS)

    def test_update(self):
        new_name = _PROJECT_NAME + '2'
        self.project.name = new_name
        self.project.update()
        project = self.user.get_project(new_name)
        self.assertEqual(project.name, new_name)

    def test_archive(self):
        self.project.archive()
        for project in self.user.get_archived_projects():
            if project.id == self.project.id:
                self.assertTrue(project.is_archived)

    def test_unarchive(self):
        self.project.archive()
        for project in self.user.get_archived_projects():
            if project.id == self.project.id:
                self.assertTrue(project.is_archived)
        self.project.unarchive()
        self.project = self.user.get_project(self.project.name)
        self.assertFalse(self.project.is_archived)

    def test_collapse(self):
        self.assertFalse(self.project.collapsed)
        self.project.collapse()
        self.project = self.user.get_project(self.project.name)
        self.assertTrue(self.project.collapsed)

    def test_add_task(self):
        self.project.add_task(_TASK)
        tasks = self.project.get_uncompleted_tasks()
        self.assertEqual(len(tasks), 1)

    def test_get_tasks(self):
        for i in range(5):
            self.project.add_task(_TASK + str(i))
        tasks = self.project.get_tasks()
        self.assertEqual(len(tasks), 5)

    def test_get_uncompleted_tasks(self):
        for i in range(5):
            self.project.add_task(_TASK + str(i))
        tasks = self.project.get_uncompleted_tasks()
        self.assertEqual(len(tasks), 5)

    def test_get_completed_tasks(self):
        for i in range(5):
            task = self.project.add_task(_TASK + str(i))
            task.complete()
        tasks = self.project.get_completed_tasks()
        self.assertEqual(len(tasks), 5)

    def test_update_task_orders(self):
        for i in range(5):
            self.project.add_task(_TASK + str(i))
        tasks = self.project.get_tasks()
        rev_tasks = tasks[::-1]
        self.project.update_task_orders(rev_tasks)
        tasks = self.project.get_tasks()
        for i, task in enumerate(tasks):
            self.assertEqual(task.id, rev_tasks[i].id)


class TaskTest(unittest.TestCase):

    def setUp(self):
        self.user = _get_user()
        self.project = self.user.add_project(_PROJECT_NAME)
        self.task = self.project.add_task(_TASK, date='every day')

    def tearDown(self):
        self.user.delete()

    def test_update(self):
        new_content = _TASK + '2'
        self.task.content = new_content
        self.task.update()
        tasks = self.project.get_tasks()
        for task in tasks:
            if task.id == self.task.id:
                self.assertEqual(task.content, new_content)

    def test_delete(self):
        tasks = self.project.get_tasks()
        self.assertEqual(len(tasks), 1)
        self.task.delete()
        tasks = self.project.get_tasks()
        self.assertEqual(len(tasks), 0)

    def test_complete(self):
        self.task.complete()
        tasks = self.project.get_completed_tasks()
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task.id, self.task.id)

    def test_uncomplete(self):
        self.task.complete()
        tasks = self.project.get_completed_tasks()
        self.assertEqual(len(tasks), 1)
        self.task.uncomplete()
        tasks = self.project.get_completed_tasks()
        self.assertEqual(len(tasks), 0)
        tasks = self.project.get_uncompleted_tasks()
        self.assertEqual(len(tasks), 1)

    def test_add_note(self):
        self.task.add_note(_NOTE)
        notes = self.task.get_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].content, _NOTE)

    def test_get_notes(self):
        for i in range(5):
            self.task.add_note(_NOTE + str(i))
        notes = self.task.get_notes()
        self.assertEqual(len(notes), 5)

    def test_advance_recurring_date(self):
        date_before = self.task.due_date
        self.task.advance_recurring_date()
        date_after = self.task.due_date
        self.assertNotEqual(date_before, date_after)

    def test_move(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        self.task.move(inbox)
        tasks = inbox.get_uncompleted_tasks()
        self.assertEqual(len(tasks), 1)


class NoteTest(unittest.TestCase):

    def setUp(self):
        self.user = _get_user()
        self.project = self.user.add_project(_PROJECT_NAME)
        self.task = self.project.add_task(_TASK)
        self.note = self.task.add_note(_NOTE)

    def tearDown(self):
        self.user.delete()

    def test_update(self):
        new_content = _NOTE + '2'
        self.note.content = new_content
        self.note.update()
        for note in self.task.get_notes():
            if note.id == self.note.id:
                self.assertEqual(note.content, new_content)

    def test_delete(self):
        self.note.delete()
        notes = self.task.get_notes()
        self.assertEqual(len(notes), 0)


class LabelTest(unittest.TestCase):

    def setUp(self):
        self.user = _get_user()
        self.label = self.user.add_label(_LABEL)

    def tearDown(self):
        self.user.delete()

    def test_update(self):
        new_name = _LABEL + '2'
        self.label.name = new_name
        self.label.update()
        label = self.user.get_label(new_name)
        self.assertIsNotNone(label)
        self.assertEqual(label.id, self.label.id)

    def test_delete(self):
        labels = self.user.get_labels()
        self.assertEqual(len(labels), 1)
        self.label.delete()
        labels = self.user.get_labels()
        self.assertEqual(len(labels), 0)


if __name__ == '__main__':
    unittest.main()
