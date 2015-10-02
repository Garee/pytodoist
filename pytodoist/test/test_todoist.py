#!/usr/bin/env python

"""This module contains the unit tests for the pytodoist.todoist module."""
import unittest
from pytodoist import todoist
from pytodoist.test.util import create_user

# Sometimes Todoist changes this which will cause tests to fail.
N_DEFAULT_PROJECTS = 6

_INBOX_PROJECT_NAME = 'Inbox'
_PROJECT_NAME = 'Test Project'
_TASK = 'Test Task'
_LABEL = 'Test Label'
_NOTE = 'Test Note'
_FILTER = 'Test Filter'


class UserTest(unittest.TestCase):

    def setUp(self):
        self.user = create_user()

    def tearDown(self):
        self.user.delete()

    def test_login_success(self):
        todoist.login(self.user.email, self.user.password)

    def test_login_failure(self):
        with self.assertRaises(todoist.RequestError):
            todoist.login(self.user.email, '')

    def test_login_with_google_success(self):
        pass  # TODO

    def test_login_with_google_failure(self):
        with self.assertRaises(todoist.RequestError):
            todoist.login_with_google(self.user.email, '')

    def test_login_with_api_token_success(self):
        todoist.login_with_api_token(self.user.api_token)

    def test_login_with_api_token_failure(self):
        with self.assertRaises(todoist.RequestError):
            todoist.login_with_api_token('')

    def test_register_success(self):
        try:
            user = create_user()
            user.delete()
        except todoist.RequestError:
            self.fail("register(...) raised an exception")

    def test_register_failure(self):
        with self.assertRaises(todoist.RequestError):
            todoist.register('', '', '')

    def test_register_already_registered(self):
        with self.assertRaises(todoist.RequestError):
            todoist.register(self.user.full_name, self.user.email,
                             self.user.password)

    def test_register_with_google_success(self):
        pass  # TODO

    def test_register_with_google_failure(self):
        with self.assertRaises(todoist.RequestError):
            todoist.register_with_google('', '', '')

    def test_get_redirect_link(self):
        link = self.user.get_redirect_link()
        self.assertIsNotNone(link)

    def test_update(self):
        new_name = self.user.full_name + ' Jnr'
        self.user.full_name = new_name
        self.user.update()
        self.user = todoist.login(self.user.email, self.user.password)
        self.assertEqual(self.user.full_name, new_name)

    def test_add_project(self):
        self.user.add_project(_PROJECT_NAME)
        projects = self.user.get_projects()
        self.assertEqual(len(projects), N_DEFAULT_PROJECTS + 1)
        project = self.user.get_project(_PROJECT_NAME)
        self.assertIsNotNone(project)
        self.assertEqual(project.name, _PROJECT_NAME)

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
        project = self.user.get_project('')
        self.assertIsNone(project)

    def test_get_archived_projects(self):
        n_arch_projects = len(self.user.get_archived_projects())
        self.assertEqual(n_arch_projects, 0)
        project = self.user.add_project(_PROJECT_NAME)
        project.archive()
        n_arch_projects = len(self.user.get_archived_projects())
        self.assertEqual(n_arch_projects, 1)

    def test_get_uncompleted_tasks(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        inbox.add_task(_TASK)
        with self.assertRaises(todoist.RequestError):  # Premium only.
            tasks = self.user.get_uncompleted_tasks()
            self.assertEqual(len(tasks), 1)

    def test_get_completed_tasks(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        task = inbox.add_task(_TASK)
        task.complete()
        with self.assertRaises(todoist.RequestError):
            completed_tasks = self.user.get_completed_tasks()  # Premium only.
            self.assertEqual(len(completed_tasks), 1)

    def test_get_tasks(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        inbox.add_task(_TASK)
        inbox.add_task(_TASK + '2')
        tasks = self.user.get_tasks()
        self.assertEqual(len(tasks), 2)
        for task in tasks:
            self.assertIsNotNone(task)

    def test_add_label(self):
        self.user.add_label(_LABEL)
        labels = self.user.get_labels()
        self.assertEqual(len(labels), 1)
        label = labels[0]
        self.assertEqual(label.name, _LABEL)
        self.assertEqual(label.color, todoist.Color.GRAY)

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

    def test_add_filter(self):
        with self.assertRaises(todoist.RequestError):
            self.user.add_filter(_FILTER, 'today')  # Premium only
            flters = self.user.get_filters()
            self.assertEqual(len(flters), 1)
            flter = flters[0]
            self.assertEqual(flter.name, _FILTER)
            self.assertEqual(flter.query, 'today')

    def test_get_filter(self):
        with self.assertRaises(todoist.RequestError):
            self.user.add_filter(_FILTER, 'today')  # Premium only.
            flter = self.user.get_filter(_FILTER)
            self.assertIsNotNone(flter)
            self.assertEqual(flter.name, _FILTER)

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
        inbox.add_task(_TASK, date='today')
        inbox.add_task(_TASK + '2', date='1 Jan 2000')
        tasks = self.user.search_tasks(todoist.Query.OVERDUE)
        self.assertEqual(len(tasks), 1)

    def test_get_productivity_stats(self):
        stats = self.user.get_productivity_stats()
        self.assertIsNotNone(stats)
        self.assertIn('karma', stats)

    def test_enable_disable_karma(self):
        # Just make sure we don't throw any exceptions.
        self.user.disable_karma()
        self.user.enable_karma()

    def test_enable_disable_vacation(self):
        # Just make sure we don't throw any exceptions.
        self.user.disable_vacation()
        self.user.enable_vacation()

    def test_update_goals(self):
        # Just make sure we don't throw any exceptions.
        self.user.update_daily_karma_goal(10)
        self.user.update_weekly_karma_goal(100)

    def test_clear_reminder_locations(self):
        # Just make sure we don't throw any exceptions.
        self.user.clear_reminder_locations()


class ProjectTest(unittest.TestCase):

    def setUp(self):
        self.user = create_user()
        self.project = self.user.add_project(_PROJECT_NAME)

    def tearDown(self):
        self.user.delete()

    def test_delete(self):
        self.project.delete()
        projects = [p for p in self.user.get_projects() if not p.is_deleted]
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
        tasks = self.project.get_tasks()
        self.assertEqual(len(tasks), 1)

    def test_get_tasks(self):
        for i in range(5):
            self.project.add_task(_TASK + str(i))
        tasks = self.project.get_tasks()
        self.assertEqual(len(tasks), 5)

    def test_get_uncompleted_tasks(self):
        for i in range(5):
            self.project.add_task(_TASK + str(i))
        with self.assertRaises(todoist.RequestError):
            tasks = self.project.get_uncompleted_tasks()  # Premium only.
            self.assertEqual(len(tasks), 5)

    def test_get_completed_tasks(self):
        with self.assertRaises(todoist.RequestError):
            self.project.get_completed_tasks()  # Premium only.

    def test_share(self):
        self.project.share('test@gmail.com')

    def test_delete_collaborator(self):
        self.project.share('test@gmail.com')
        self.project.delete_collaborator('test@gmail.com')

    def test_take_ownership(self):
        self.project.share('test@gmail.com')
        self.project.take_ownership()


class TaskTest(unittest.TestCase):

    def setUp(self):
        self.user = create_user()
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
        tasks = [t for t in self.project.get_tasks() if not t.is_deleted]
        self.assertEqual(len(tasks), 0)

    def test_complete(self):
        self.task.complete()
        with self.assertRaises(todoist.RequestError):
            tasks = self.project.get_completed_tasks()  # Premium only.
            self.assertEqual(len(tasks), 1)

    def test_uncomplete(self):
        self.task.complete()
        self.task.uncomplete()
        with self.assertRaises(todoist.RequestError):
            tasks = self.project.get_uncompleted_tasks()  # Premium only.
            self.assertEqual(len(tasks), 1)

    def test_add_note(self):
        with self.assertRaises(todoist.RequestError):
            self.task.add_note(_NOTE)    # Premium only.
            notes = self.task.get_notes()
            self.assertEqual(len(notes), 1)
            self.assertEqual(notes[0].content, _NOTE)

    def test_get_notes(self):
        with self.assertRaises(todoist.RequestError):
            for i in range(5):
                self.task.add_note(_NOTE + str(i))  # Premium only.
            notes = self.task.get_notes()
            self.assertEqual(len(notes), 5)

    def test_move(self):
        inbox = self.user.get_project(_INBOX_PROJECT_NAME)
        self.task.move(inbox)
        tasks = inbox.get_tasks()
        self.assertEqual(len(tasks), 1)

    def test_add_date_reminder(self):
        self.task.add_date_reminder('email', '2050-3-24T23:59')

    def test_add_location_reminder(self):
        self.task.add_location_reminder('email', 'Leave Glasgow',
                                        55.8580, 4.2590, 'on_leave',
                                        100)


if __name__ == '__main__':
    unittest.main()
