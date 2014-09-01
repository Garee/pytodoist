#!/usr/bin/env python

import sys
import unittest
from pytodoist import todoist

N_DEFAULT_PROJECTS = 8

full_name = "Py Todoist"
email = "pytodoist.test.email@gmail.com"
password = "pytodoist.test.password"


def _get_user():
    try:
        user = todoist.register(full_name, email, password)
    except todoist.RequestError:
        user = todoist.login(email, password)
        user.delete()
        user = todoist.register(full_name, email, password)
    return user


class UserTest(unittest.TestCase):

    def setUp(self):
        self.user = _get_user()

    def tearDown(self):
        self.user.delete()

    def test_login_success(self):
        self.assertTrue(self.user.is_logged_in())

    def test_login_failure(self):
        with self.assertRaises(todoist.RequestError):
            user = todoist.login('', '')

    def test_login_with_token(self):
        user = todoist.login_with_token(self.user.token)
        self.assertTrue(user.is_logged_in())

    def test_registration_failure(self):
        with self.assertRaises(todoist.RequestError):
            user = todoist.register('', '', '')

    def test_update(self):
        self.user.full_name = 'Todoist Py'
        self.user.update()
        self.user = todoist.login(email, password)
        self.assertEqual(self.user.full_name, 'Todoist Py')

    def test_get_redirect_link(self):
        link = self.user.get_redirect_link()
        self.assertIsNotNone(link)
        self.assertTrue(len(link) > 0)

    def test_add_project(self):
        project = self.user.add_project('Project 1')
        projects = self.user.get_projects()
        self.assertEqual(len(projects), N_DEFAULT_PROJECTS + 1)
        project = self.user.get_project('Project 1')
        self.assertIsNotNone(project)

    def test_add_project_failure(self):
        with self.assertRaises(todoist.RequestError):
            self.user.add_project('')

    def test_get_projects(self):
        for i in range(5):
            self.user.add_project('Project ' + str(i))
        projects = self.user.get_projects()
        self.assertEqual(len(projects), N_DEFAULT_PROJECTS + 5)

    def test_get_project(self):
        inbox = self.user.get_project('Inbox')
        self.assertEqual(inbox.name, 'Inbox')

    def test_get_archived_projects(self):
        n_arch_projects = len(self.user.get_archived_projects())
        self.assertEqual(n_arch_projects, 0)
        self.user.add_project('Project 1')
        n_projects = len(self.user.get_projects())
        project = self.user.get_project('Project 1')
        project.archive()
        n_arch_projects = len(self.user.get_archived_projects())
        self.assertEqual(n_arch_projects, 1)

    def test_get_project_with_id(self):
        inbox = self.user.get_project('Inbox')
        project = self.user.get_project_with_id(inbox.id)
        self.assertEqual(project.name, inbox.name)

    def test_update_project_orders(self):
        for i in range(5):
            self.user.add_project('Project_' + str(i))
        projects = self.user.get_projects()
        rev_projects = projects[::-1]
        self.user.update_project_orders(rev_projects)
        projects = self.user.get_projects()
        for i, project in enumerate(projects):
            self.assertEqual(project.name, rev_projects[i].name)

    def test_get_uncompleted_tasks(self):
        inbox = self.user.get_project('Inbox')
        inbox.add_task('Task 1')
        tasks = self.user.get_uncompleted_tasks()
        self.assertEqual(len(tasks), 1)

    def test_get_completed_tasks(self):
        inbox = self.user.get_project('Inbox')
        task = inbox.add_task('Task 1')
        task.complete()
        completed_tasks = self.user.get_completed_tasks()
        self.assertEqual(len(completed_tasks), 1)

    def test_search_completed_tasks(self):
        inbox = self.user.get_project('Inbox')
        task = inbox.add_task('Task 1 @homework')
        task.complete()
        tasks = self.user.search_completed_tasks(label_name='homework')
        # self.assertEqual(len(tasks), 1)
        self.assertEqual(len(tasks), 0)  # Requires premium.

    def test_get_tasks(self):
        inbox = self.user.get_project('Inbox')
        task = inbox.add_task('Task 1')
        task = inbox.add_task('Task 2')
        task.complete()
        tasks = self.user.get_tasks()
        self.assertEqual(len(tasks), 2)

    def test_add_label(self):
        self.user.add_label('Label 1', color=1)
        labels = self.user.get_labels()
        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0].name, 'Label 1')

    def test_get_label(self):
        self.user.add_label('homework')
        label = self.user.get_label('homework')
        self.assertIsNotNone(label)

    def test_get_labels(self):
        for i in range(5):
            self.user.add_label('Label_' + str(i))
        labels = self.user.get_labels()
        self.assertEqual(len(labels), 5)

    def test_add_label(self):
        label = self.user.add_label('homework')
        labels = self.user.get_labels()
        self.assertEqual(len(labels), 1)

    def test_search_tasks(self):
        inbox = self.user.get_project('Inbox')
        inbox.add_task('Task Red')
        inbox.add_task('Task Blue')
        queries = ['view all']
        tasks = self.user.search_tasks(queries)
        self.assertEqual(len(tasks), 2)

    def test_search_tasks_today(self):
        inbox = self.user.get_project('Inbox')
        inbox.add_task('Task Red', date='today')
        inbox.add_task('Task Blue', date='today')
        queries = ['today']
        tasks = self.user.search_tasks(queries)
        self.assertEqual(len(tasks), 2)

    def test_is_email_notified_when(self):
        self.user.disable_email_notifications(todoist.Event.NOTE_ADDED)
        is_recv = self.user.is_email_notified_when(todoist.Event.NOTE_ADDED)
        self.assertFalse(is_recv)

    def test_enable_email_notifications(self):
        self.user.enable_email_notifications(todoist.Event.NOTE_ADDED)
        is_recv = self.user.is_email_notified_when(todoist.Event.NOTE_ADDED)
        self.assertTrue(is_recv)


class ProjectTest(unittest.TestCase):

    def setUp(self):
        self.user = _get_user()
        self.project = self.user.add_project('Project_1')

    def tearDown(self):
        self.user.delete()

    def test_delete(self):
        self.project.delete()
        projects = self.user.get_projects()
        self.assertEqual(len(projects), N_DEFAULT_PROJECTS)

    def test_update(self):
        self.project.name = 'Project_2'
        self.project.update()
        project = self.user.get_project('Project_2')
        self.assertEqual(project.name, 'Project_2')

    def test_archive(self):
        self.project.archive()  # Premium only.

    def test_unarchive(self):
        self.project.unarchive()  # Premium only.

    def test_add_task(self):
        self.project.add_task('Task_1')
        tasks = self.project.get_uncompleted_tasks()
        self.assertEqual(len(tasks), 1)

    def test_get_uncompleted_tasks(self):
        for i in range(5):
            self.project.add_task('Task_' + str(i))
        tasks = self.project.get_uncompleted_tasks()
        self.assertEqual(len(tasks), 5)

    def test_get_completed_tasks(self):
        for i in range(5):
            task = self.project.add_task('Task_' + str(i))
            task.complete()
        tasks = self.project.get_completed_tasks()
        self.assertEqual(len(tasks), 5)

    def test_update_task_orders(self):
        for i in range(5):
            self.project.add_task('Task_' + str(i))
        tasks = self.project.get_tasks()
        rev_tasks = tasks[::-1]
        self.project.update_task_orders(rev_tasks)
        tasks = self.project.get_tasks()
        for i, task in enumerate(tasks):
            self.assertEqual(task.id, rev_tasks[i].id)


class TaskTest(unittest.TestCase):

    def setUp(self):
        self.user = _get_user()
        self.project = self.user.add_project('Project_1')
        self.task = self.project.add_task('Task_1', date='every day')

    def tearDown(self):
        self.user.delete()

    def test_update(self):
        self.task.content = 'Task_2'
        self.task.update()
        tasks = self.project.get_tasks()
        for task in tasks:
            if task.id == self.task.id:
                self.assertEqual(task.content, 'Task_2')

    def test_delete(self):
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
        self.task.add_note('Note_1')
        notes = self.task.get_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].content, 'Note_1')

    def test_get_notes(self):
        for i in range(5):
            self.task.add_note('Note_' + str(i))
        notes = self.task.get_notes()
        self.assertEqual(len(notes), 5)

    def test_advance_recurring_date(self):
        date_before = self.task.due_date
        self.task.advance_recurring_date()
        date_after = self.task.due_date
        self.assertNotEqual(date_before, date_after)

    def test_move(self):
        inbox = self.user.get_project('Inbox')
        self.task.move(inbox)
        tasks = inbox.get_uncompleted_tasks()
        self.assertEqual(len(tasks), 1)


class NoteTest(unittest.TestCase):

    def setUp(self):
        self.user = _get_user()
        self.project = self.user.add_project('Project_1')
        self.task = self.project.add_task('Task_1')
        self.note = self.task.add_note('Note_1')

    def tearDown(self):
        self.user.delete()

    def test_update(self):
        self.note.content = 'Note_2'
        self.note.update()
        for note in self.task.get_notes():
            if note.id == self.note.id:
                self.assertEqual(note.content, 'Note_2')

    def test_delete(self):
        self.note.delete()
        notes = self.task.get_notes()
        self.assertEqual(len(notes), 0)


class LabelTest(unittest.TestCase):

    def setUp(self):
        self.user = _get_user()
        self.label = self.user.add_label('Label_1')

    def tearDown(self):
        self.user.delete()

    def test_update(self):
        self.label.name = 'Label_2'
        self.label.update()
        label = self.user.get_label('Label_2')
        self.assertIsNotNone(label)

    def test_delete(self):
        self.label.delete()
        labels = self.user.get_labels()
        self.assertEqual(len(labels), 0)


def main():
    unittest.main()
    return 0

if __name__ == '__main__':
    sys.exit(main())
