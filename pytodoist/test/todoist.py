#!/usr/bin/env python

import sys
import unittest
from pytodoist.todoist import Todoist

class TestUser(object):

    def __init__(self):
        self.full_name = 'Py Todoist'
        self.email = 'pytodoist.test.email@gmail.com'
        self.password = 'pytodoist.test.password'
        self.token = None

class TodoistTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.t = Todoist()
        self.user = TestUser()

    def setUp(self):
        response = self.t.register(self.user.email, self.user.full_name,
                                   self.user.password)
        if response.text == '"ALREADY_REGISTRED"':
            response = self.t.login(self.user.email, self.user.password)
        user_details = response.json()
        self.user.token = user_details['token']

    def tearDown(self):
        self.t.delete_user(self.user.token, self.user.password)

    def test_login(self):
        response = self.t.login(self.user.email, self.user.password)
        self.assertTrue(response.status_code == 200)
        self.assertTrue('token' in response.json())

    def test_ping(self):
        response = self.t.login(self.user.email, self.user.password)
        token = response.json()['token']
        response = self.t.ping(token)
        self.assertTrue(response.status_code == 200)

    def test_get_timezones(self):
        response = self.t.get_timezones()
        self.assertTrue(response.status_code == 200)
        timezones = response.json()
        n_timezones = len(timezones)
        self.assertTrue(n_timezones > 0)

    def test_update_user(self):
        params = {'email': 'todoist.updated.email@gmail.com'}
        response = self.t.update_user(self.user.token, **params)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['email'] == params['email'])

    def test_update_avatar(self):
        response = self.t.update_avatar(self.user.token)
        self.assertTrue(response.status_code == 200)

    def test_get_projects(self):
        response = self.t.get_projects(self.user.token)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.json()) == 1) # Inbox is a default project.

    def test_get_project(self):
        response = self.t.get_projects(self.user.token)
        projects = response.json()
        inbox = projects[0]
        response = self.t.get_project(self.user.token, inbox['id'])
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['name'] == inbox['name'])

    def test_add_project(self):
        response = self.t.add_project(self.user.token, 'Project_1')
        self.assertTrue(response.status_code == 200)
        response = self.t.get_projects(self.user.token)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.json()) == 2)
        response = self.t.add_project(self.user.token, 'Project_2')
        self.assertTrue(response.status_code == 200)
        response = self.t.get_projects(self.user.token)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.json()) == 3)

    def test_update_project(self):
        response = self.t.add_project(self.user.token, 'Project_1')
        project_id = response.json()['id']
        params = {'name': 'Project_1_Updated'}
        response = self.t.update_project(self.user.token, project_id, **params)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()['name'] == params['name'])

    def test_update_project_orders(self):
        for i in range(10):
            response = self.t.add_project(self.user.token, 'Project_' + str(i))
        response = self.t.get_projects(self.user.token)
        project_ids = [project['id'] for project in response.json()]
        rev_project_ids = project_ids[::-1]
        response = self.t.update_project_orders(self.user.token, rev_project_ids)
        self.assertTrue(response.status_code == 200)
        response = self.t.get_projects(self.user.token)
        project_ids_2 = [project['id'] for project in response.json()]
        self.assertTrue(project_ids_2 == rev_project_ids)

    def test_delete_project(self):
        response = self.t.add_project(self.user.token, 'Project_1')
        project_id = response.json()['id']
        response = self.t.delete_project(self.user.token, project_id)
        self.assertTrue(response.status_code == 200)
        response = self.t.get_projects(self.user.token)
        self.assertTrue(len(response.json()) == 1)

    def test_archive_project(self):
        for i in range(3):
            response = self.t.add_project(self.user.token, 'Project_' + str(i))
        response = self.t.get_projects(self.user.token)
        project_ids = [project['id'] for project in response.json() if project['name'] != 'Inbox']
        response = self.t.archive_project(self.user.token, project_ids[0])
        self.assertTrue(response.status_code == 200)
        archived_ids = response.json()
        self.assertTrue(len(archived_ids) == 0) # Only works if you are a premium user.

    def test_unarchive_project(self):
        for i in range(3):
            response = self.t.add_project(self.user.token, 'Project_' + str(i))
        response = self.t.get_projects(self.user.token)
        project_ids = [project['id'] for project in response.json() if project['name'] != 'Inbox']
        response = self.t.unarchive_project(self.user.token, project_ids[0])
        self.assertTrue(response.status_code == 200)
        archived_ids = response.json()
        self.assertTrue(len(archived_ids) == 0) # Only works if you are a premium user.

def main():
    unittest.main()
    return 0

if __name__ == '__main__':
    sys.exit(main())
