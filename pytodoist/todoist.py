from pytodoist.api import TodoistAPI

API = TodoistAPI()

def login(email, password):
    user = _login(API.login, email, password)
    user.password = password
    return user

def login_with_google(email, oauth2_token):
    return _login(API.login_with_google, email, oauth2_token)

def _login(login_func, *args):
    response = login_func(*args)
    _fail_if_contains_errors(response)
    user_as_json = response.json()
    return User(user_as_json)

def register(full_name, email, password, lang=None, timezone=None):
    response = API.register(email, full_name, password,
                            lang=lang, timezone=timezone)
    _fail_if_contains_errors(response)
    user_as_json = response.json()
    user = User(user_as_json)
    user.password = password
    return user

def get_timezones():
    response = API.get_timezones()
    _fail_if_contains_errors(response)
    timezones_as_json = response.json()
    return [timezone for timezone in timezones_as_json]

class TodoistObject(object):

    def __init__(self, json):
        for attr in json:
            setattr(self, attr, json[attr])

    def __repr__(self):
        return self.__dict__


class User(TodoistObject):

    def __init__(self, json):
        self.token = None
        self.password = None
        super(User, self).__init__(json)

    def is_logged_in(self):
        if not self.token:
            return False
        response = API.ping(self.token)
        return not _contains_errors(response)

    def delete(self, reason=None):
        if not hasattr(self, 'password'):
            raise Exception("You cannot delete a Google-linked account.")
        response = API.delete_user(self.token, self.password,
                                   reason=reason, in_background=0)
        _fail_if_contains_errors(response)

    def update(self):
        response = API.update_user(**self.__dict__)
        _fail_if_contains_errors(response)

    def change_avatar(self, image):
        response = API.update_avatar(self.token, image=image)
        _fail_if_contains_errors(response)

    def use_default_avatar(self):
        response = API.update_avatar(self.token, delete=1)
        _fail_if_contains_errors(response)

    def add_project(self, name, color=None, indent=None, order=None):
        response = API.add_project(self.token, name,
                                   color=color, indent=indent, order=order)
        _fail_if_contains_errors(response)
        project_as_json = response.json()
        return Project(project_as_json, self)

    def get_projects(self):
        response = API.get_projects(self.token)
        _fail_if_contains_errors(response)
        projects_as_json = response.json()
        return [Project(json, self) for json in projects_as_json]

    def get_project(self, name):
        projects = self.get_projects()
        for project in projects:
            if project.name == name:
                return project

    def get_project_with_id(self, project_id):
        response = API.get_project(self.token, project_id)
        _fail_if_contains_errors(response)
        project_as_json = response.json()
        return Project(project_as_json, self)

    def update_project_orders(self, projects):
        project_ids = str([project.id for project in projects])
        response = API.update_project_orders(self.token, project_ids)
        _fail_if_contains_errors(response)

    def get_completed_tasks(self, label=None, interval=None):
        response = API.get_all_completed_tasks(self.token, label=label,
                                               interval=interval)
        _fail_if_contains_errors(response)
        tasks_as_json = response.json()['items']
        tasks = []
        for json in tasks_as_json:
            project_id = json['project_id']
            project = self.get_project_with_id(project_id)
            tasks.append(Task(json, project))
        return tasks

    def get_label(self, label_name):
        for label in self.get_labels():
            if label.name == label_name:
                return label

    def get_labels(self):
        response = API.get_labels(self.token)
        _fail_if_contains_errors(response)
        labels_as_json = response.json().values()
        return [Label(json, self) for json in labels_as_json]

    def add_label(self, name, color=None):
        response = API.add_label(self.token, name, color=color)
        _fail_if_contains_errors(response)
        label_as_json = response.json()
        return Label(label_as_json, self)

    def search(self, queries):
        response = API.search_tasks(self.token, queries)
        _fail_if_contains_errors(response)
        query_results = response.json()
        tasks = []
        for query in query_results:
            projects_with_results = query['data']
            for project in projects_with_results:
                uncompleted_tasks = project.get('uncompleted', [])
                completed_tasks = project.get('completed', [])
                found_tasks = uncompleted_tasks + completed_tasks
                for task_as_json in found_tasks:
                    project_id = task_as_json['project_id']
                    project = self.get_project_with_id(project_id)
                    task = Task(task_as_json, project)
                    tasks.append(task)
        return tasks

    def get_notification_settings(self):
        response = API.get_notification_settings(self.token)
        _fail_if_contains_errors(response)
        return response.json()

    def get_notification_types(self):
        return self.get_notification_settings().values()

    def is_receiving_email_notifications(self, notification_type):
        notification_settings = self.get_notification_settings()
        return notification_settings[notification_type]['notify_email']

    def is_receiving_push_notifications(self, notification_type):
        notification_settings = self.get_notification_settings()
        return notification_settings[notification_type]['notify_push']

    def enable_push_notifications(self, notification_type):
        self.update_notification_settings(notification_type, 'push', 0)

    def disable_push_notifications(self, notification_type):
        self.update_notification_settings(notification_type, 'push', 1)

    def enable_email_notifications(self, notification_type):
        self.update_notification_settings(notification_type, 'email', 0)

    def disable_email_notifications(self, notification_type):
        self.update_notification_settings(notification_type, 'email', 1)

    def update_notification_settings(self, notification_type, service,
                                         should_notify):
        response = API.update_notification_settings(self.token,
                                                    notification_type,
                                                    service,
                                                    should_notify)
        _fail_if_contains_errors(response)


class Project(TodoistObject):

    def __init__(self, json, owner):
        self.id = None
        self.owner = owner
        super(Project, self).__init__(json)

    def delete(self):
        response = API.delete_project(self.owner.token, self.id)
        _fail_if_contains_errors(response)

    def update(self):
        response = API.update_project(self.owner.token, self.id,
                                      **self.__dict__)
        _fail_if_contains_errors(response)

    def archive(self):
        response = API.archive_project(self.owner.token, self.id)
        _fail_if_contains_errors(response)

    def unarchive(self):
        response = API.unarchive_project(self.owner.token, self.id)
        _fail_if_contains_errors(response)

    def add_task(self, content, date=None, priority=None):
        response = API.add_task(self.owner.token, content, project_id=self.id,
                                date_string=date, priority=priority)
        _fail_if_contains_errors(response)
        task_as_json = response.json()
        return Task(task_as_json, self)

    def get_tasks(self):
        return self.get_uncompleted_tasks() + self.get_completed_tasks()

    def get_task(self, task_id):
        for task in self.get_tasks():
            if task.id == task_id:
                return task

    def get_uncompleted_tasks(self):
        response = API.get_uncompleted_tasks(self.owner.token, self.id)
        _fail_if_contains_errors(response)
        tasks_as_json = response.json()
        return [Task(json, self) for json in tasks_as_json]

    def get_completed_tasks(self):
        response = API.get_completed_tasks(self.owner.token, self.id)
        _fail_if_contains_errors(response)
        tasks_as_json = response.json()
        return [Task(json, self) for json in tasks_as_json]

    def update_task_orders(self, tasks):
        task_ids = str([task.id for task in tasks])
        response = API.update_task_ordering(self.owner.token, self.id, task_ids)
        _fail_if_contains_errors(response)


class Task(TodoistObject):

    def __init__(self, json, project):
        self.id = None
        self.project = project
        super(Task, self).__init__(json)

    def update(self):
        response = API.update_task(self.project.owner.token, self.id,
                                   **self.__dict__)
        _fail_if_contains_errors(response)

    def delete(self):
        task_ids = '[{id}]'.format(id=self.id)
        response = API.delete_tasks(self.project.owner.token, task_ids)
        _fail_if_contains_errors(response)

    def complete(self):
        task_ids = '[{id}]'.format(id=self.id)
        response = API.complete_tasks(self.project.owner.token, task_ids)
        _fail_if_contains_errors(response)

    def uncomplete(self):
        task_ids = '[{id}]'.format(id=self.id)
        response = API.uncomplete_tasks(self.project.owner.token, task_ids)
        _fail_if_contains_errors(response)

    def add_note(self, content):
        response = API.add_note(self.project.owner.token, self.id, content)
        _fail_if_contains_errors(response)
        note_as_json = response.json()
        return Note(note_as_json, self)

    def get_note(self, note_id):
        for note in self.get_notes():
            if note.id == note_id:
                return note

    def get_notes(self):
        response = API.get_notes(self.project.owner.token, self.id)
        _fail_if_contains_errors(response)
        notes_as_json = response.json()
        return [Note(json, self) for json in notes_as_json]

    def advance_recurring_date(self):
        task_ids = '[{id}]'.format(id=self.id)
        response = API.advance_recurring_dates(self.project.owner.token,
                                               task_ids)
        _fail_if_contains_errors(response)
        task_as_json = response.json()[0]
        self.__init__(task_as_json, self.project)

    def move(self, project):
        current_pos = '{{"{p_id}":["{t_id}"]}}'.format(p_id=self.project.id,
                                                       t_id=self.id)
        response = API.move_tasks(self.project.owner.token, current_pos,
                                  project.id)
        _fail_if_contains_errors(response)
        self.project = project


class Note(TodoistObject):

    def __init__(self, json, task):
        self.id = None
        self.content = None
        self.task = task
        super(Note, self).__init__(json)

    def update(self):
        response = API.update_note(self.task.project.owner.token, self.id,
                                   self.content)
        _fail_if_contains_errors(response)

    def delete(self):
        response = API.delete_note(self.task.project.owner.token,
                                   self.task.id, self.id)
        _fail_if_contains_errors(response)


class Label(TodoistObject):

    def __init__(self, json, owner):
        self.name = None
        self.color = None
        self.owner = owner
        super(Label, self).__init__(json)
        self.id = self.name

    def update(self):
        response = API.update_label_name(self.owner.token, self.id, self.name)
        _fail_if_contains_errors(response)
        self.id = self.name
        response = API.update_label_color(self.owner.token, self.id, self.color)
        _fail_if_contains_errors(response)

    def delete(self):
        response = API.delete_label(self.owner.token, self.id)
        _fail_if_contains_errors(response)


class TodoistException(Exception):
    def __init__(self, response):
        self.response = response
        super(TodoistException, self).__init__(response.text)


def _fail_if_contains_errors(response):
    if _contains_errors(response):
        raise TodoistException(response)

def _contains_errors(response):
    return response.status_code != 200 or response.text in API.ERRORS
