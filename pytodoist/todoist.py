import itertools
from pytodoist.api import TodoistAPI

API = TodoistAPI()

def login(email, password):
    """Login to Todoist.

    :param email: A Todoist user's email address.
    :type email: string
    :param password: A Todoist user's password.
    :type password: string
    :return: The Todoist user.
    :rtype: :mod:`pytodoist.todoist.User`
    :raises AuthError: If the login credentials are incorrect.

    >>> from pytodoist import todoist
    >>> user = todoist.login('john.doe@gmail.com', 'passwd')
    >>> user.full_name
    u'John Doe'
    >>> user.join_date
    u'Sun 09 Mar 2014 19:54:01 +0000'
    """
    user = _login(API.login, email, password)
    user.password = password
    return user

def login_with_google(email, oauth2_token):
    """Login to Todoist using Google oauth2 authentication.

    :param email: A Todoist user's email address.
    :type email: string
    :param oauth2_token: The oauth2 token associated with the email.
    :type oauth2_token: string
    :return: The Todoist user.
    :rtype: :mod:`pytodoist.todoist.User`
    :raises AuthError: If Google has refused to accept the token.
    :raises InternalError: If a server error occurs. Try again later.
    :raises BadValueError: If the token is valid but doesn't match the email.

    .. note:: It is up to you to obtain the valid oauth2 token.

    >>> from pytodoist import todoist
    ... # Get the oauth2 token.
    >>> user = todoist.login_with_google('john.doe@gmail.com', oauth2_token)
    >>> user.full_name
    u'John Doe'
    >>> user.join_date
    u'Sun 09 Mar 2014 19:54:01 +0000'
    """
    return _login(API.login_with_google, email, oauth2_token)

def _login(login_func, *args):
    """A helper function for logging in.

    It's purpose is to avoid duplicate code in login and login_with_google.
    """
    response = login_func(*args)
    _fail_if_contains_errors(response)
    user_as_json = response.json()
    return User(user_as_json)

def register(full_name, email, password, lang=None, timezone=None):
    """Register a new Todoist account.

    :param full_name: The user's full name.
    :type full_name: string
    :param email: The user's email address.
    :type email: string
    :param password: The user's password.
    :type password: string
    :param lang: The user's language.
    :type lang: string
    :param timezone: The user's timezone.
    :type timezone: string
    :return: The Todoist user.
    :rtype: :mod:`pytodoist.todoist.User`
    :raises RegistrationError: If an account with the given details exists.

    >>> from pytodoist import todoist
    >>> user = todoist.register('John Doe', 'john.doe@gmail.com', 'passwd')
    >>> user.full_name
    u'John Doe'
    >>> user.join_date
    u'Sun 09 Mar 2014 19:54:01 +0000'
    """
    response = API.register(email, full_name, password,
                            lang=lang, timezone=timezone)
    _fail_if_contains_errors(response)
    user_as_json = response.json()
    user = User(user_as_json)
    user.password = password
    return user

def register_with_google(full_name, email, oauth2_token,
                         lang=None, timezone=None):
    """Register a new Todoist account by linking a Google account.

    :param full_name: The user's full name.
    :type full_name: string
    :param email: The user's email address.
    :type email: string
    :param oauth2_token: The oauth2 token associated with the email.
    :type oauth2_token: string
    :param lang: The user's language.
    :type lang: string
    :param timezone: The user's timezone.
    :type timezone: string
    :return: The Todoist user.
    :rtype: :mod:`pytodoist.todoist.User`
    :raises AuthError: If Google has refused to accept the token.
    :raises InternalError: If a server error occurs. Try again later.
    :raises BadValueError: If the token is valid but doesn't match the email.

    .. note:: It is up to you to obtain the valid oauth2 token.

    >>> from pytodoist import todoist
    ... # Get the oauth2 token.
    >>> user = todoist.register_with_google('John Doe', 'john.doe@gmail.com',
    ...                                      oauth2_token)
    >>> user.full_name
    u'John Doe'
    >>> user.join_date
    u'Sun 09 Mar 2014 19:54:01 +0000'
    """
    response = API.login_with_google(email, oauth2_token, auto_signup=1,
                                     lang=lang, timezone=timezone)
    _fail_if_contains_errors(response)
    user_as_json = response.json()
    user = User(user_as_json)
    user.password = password
    return user

def get_timezones():
    """Return a list of Todoist supported timezones.

    :return: A list of timezones
    :rtype: list

    >>> from pytodoist import todoist
    >>> todoist.get_timezones()
    [u'US/Hawaii', u'US/Alaska', u'US/Pacific', u'US/Arizona, ...]
    """
    response = API.get_timezones()
    _fail_if_contains_errors(response)
    timezones_as_json = response.json()
    return [timezone[0] for timezone in timezones_as_json]

class TodoistObject(object):
    # A helper class which 'converts' a JSON object
    # into a python object. It is designed to be inherited.

    def __init__(self, json):
        for attr in json:
            setattr(self, attr, json[attr])

    def __repr__(self):
        return str(self.__dict__)


class User(TodoistObject):
    """A Todoist User.

    :ivar full_name: The user's full name.
    """

    def __init__(self, json):
        self.token = None
        self.password = None
        super(User, self).__init__(json)

    def is_logged_in(self):
        """Return ``True`` if the user is logged in.

        A user is logged in if it's token is valid.

        :return: ``True`` if the user token is valid, ``False`` otherwise.
        :rtype: bool

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.is_logged_in()
        True
        >>> user.delete()
        >>> user.is_logged_in()
        False
        """
        if not self.token:
            return False
        response = API.ping(self.token)
        return not _contains_errors(response)

    def delete(self, reason=None):
        """Delete the user's account from Todoist.

        .. warning:: You cannot recover the user after deletion!

        :param reason: The reason for deletion.
        :type reason: string
        :raises AuthError: If ``user.password`` is wrong.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.delete()
        ... # The user token is now invalid and Todoist operations will fail.
        """
        if not hasattr(self, 'password'):
            raise TodoistError("Account is linked to Google.")
        response = API.delete_user(self.token, self.password,
                                   reason=reason, in_background=0)
        _fail_if_contains_errors(response)

    def update(self):
        """Update the user's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        :raises TodoistError: If the request to update is invalid.
        :raises BadValueError: If one of the new values is invalid e.g. the
            new email address is associated with an existing account.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.full_name = 'John Smith'
        ... # At this point Todoist still thinks the name is 'John Doe'.
        >>> user.update()
        ... # Now the name has been updated on Todoist.
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.full_name
        u'John Smith'
        """
        response = API.update_user(**self.__dict__)
        _fail_if_contains_errors(response)

    def change_avatar(self, image):
        """Change the user's avatar.

        :param image: The path to the image.
        :type image: string
        :raises BadValueError: If the image is an invalid format, too big or
            unable to be resized.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.change_avatar('~/pictures/avatar.png')
        """
        response = API.update_avatar(self.token, image=image)
        _fail_if_contains_errors(response)

    def use_default_avatar(self):
        """Change the user's avatar to the Todoist default avatar.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.use_default_avatar()
        """
        response = API.update_avatar(self.token, delete=1)
        _fail_if_contains_errors(response)

    def add_project(self, name, color=None, indent=None, order=None):
        """Add a project to the user's account.

        :param name: The project name.
        :type name: string
        :param color: The project color.
        :type color: int
        :param indent: The project indentation.
        :type indent: int
        :param order: The project ordering.
        :type order: int
        :return: The project that was added.
        :rtype: :mod:`pytodoist.todoist.Project`
        :raises BadValueError: If the project name is empty.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> project = user.add_project('Homework', color=1)
        >>> project.name
        u'Homework'
        """
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

    def get_project(self, project_name):
        for project in self.get_projects():
            if project.name == project_name:
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

    def get_uncompleted_tasks(self):
        tasks = (p.get_uncompleted_tasks() for p in self.get_projects())
        return list(itertools.chain.from_iterable(tasks))

    def get_completed_tasks(self):
        tasks = (p.get_completed_tasks() for p in self.get_projects())
        return list(itertools.chain.from_iterable(tasks))

    def search_completed_tasks(self, label=None, interval=None):
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

    def get_tasks(self):
        return self.get_uncompleted_tasks() + self.get_completed_tasks()

    def search_tasks(self, queries):
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

    def _get_notification_settings(self):
        response = API.get_notification_settings(self.token)
        _fail_if_contains_errors(response)
        return response.json()

    def _update_notification_settings(self, notification_type, service,
                                         should_notify):
        response = API.update_notification_settings(self.token,
                                                    notification_type,
                                                    service,
                                                    should_notify)
        _fail_if_contains_errors(response)

    def get_notification_types(self):
        return self._get_notification_settings().values()

    def is_receiving_email_notifications(self, notification_type):
        notification_settings = self._get_notification_settings()
        return notification_settings[notification_type]['notify_email']

    def is_receiving_push_notifications(self, notification_type):
        notification_settings = self._get_notification_settings()
        return notification_settings[notification_type]['notify_push']

    def enable_push_notifications(self, notification_type):
        self._update_notification_settings(notification_type, 'push', 0)

    def disable_push_notifications(self, notification_type):
        self._update_notification_settings(notification_type, 'push', 1)

    def enable_email_notifications(self, notification_type):
        self._update_notification_settings(notification_type, 'email', 0)

    def disable_email_notifications(self, notification_type):
        self._update_notification_settings(notification_type, 'email', 1)


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

    def collapse(self):
        response = api.update_project(self.owner.token, self.id, collapsed=1)
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

    def get_note_with_id(self, note_id):
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


class TodoistError(Exception):

    def __init__(self, response):
        self.response = response
        super(TodoistError, self).__init__(response.text)

class AuthError(TodoistError):

    def __init__(self, response):
        super(AuthError, self).__init__(response)

class RegistrationError(TodoistError):

    def __init__(self, response):
        super(RegistrationError, self).__init__(response)


class InternalError(TodoistError):

    def __init__(self, response):
        super(InternalError, self).__init__(response)


class BadValueError(TodoistError):

    def __init__(self, response):
        super(BadValueError, self).__init__(response)


class NotFoundError(TodoistError):

    def __init__(self, response):
        super(NotFoundError, self).__init__(response)


_ERROR_TEXT_EXCEPTION_MAPPING = {
    '"LOGIN_ERROR"':                       AuthError,
    '"EMAIL_MISMATCH"':                    AuthError,
    '"ACCOUNT_NOT_CONNECTED_WITH_GOOGLE"': AuthError,
    '"ALREADY_REGISTRED"':                 RegistrationError,
    '"INTERNAL_ERROR"':                    InternalError,
    '"UNKNOWN_ERROR"':                     InternalError,
    '"TOO_SHORT_PASSWORD"':                BadValueError,
    '"INVALID_EMAIL"':                     BadValueError,
    '"INVALID_TIMEZONE"':                  BadValueError,
    '"INVALID_FULL_NAME"':                 BadValueError,
    '"ERROR_PASSWORD_TOO_SHORT"':          BadValueError,
    '"ERROR_EMAIL_FOUND"':                 BadValueError,
    '"ERROR_NAME_IS_EMPTY"':               BadValueError,
    '"ERROR_WRONG_DATE_SYNTAX"':           BadValueError,
    '"UNKNOWN_IMAGE_FORMAT"':              BadValueError,
    '"UNABLE_TO_RESIZE_IMAGE"':            BadValueError,
    '"IMAGE_TOO_BIG"':                     BadValueError,
    '"ERROR_PROJECT_NOT_FOUND"':           NotFoundError,
    '"ERROR_ITEM_NOT_FOUND"':              NotFoundError
}

_ERROR_CODE_EXCEPTION_MAPPING = {
  '400': TodoistError,
  '403': AuthError,
}

_ERROR_TEXT_RESPONSES = _ERROR_TEXT_EXCEPTION_MAPPING.keys()

def _get_associated_exception(response):
    if response.text in _ERROR_TEXT_EXCEPTION_MAPPING:
      return _ERROR_TEXT_EXCEPTION_MAPPING[response.text]
    elif response.status_code in _ERROR_CODE_EXCEPTION_MAPPING:
      return _ERROR_CODE_EXCEPTION_MAPPING[response.status_code]
    return TodoistError(response)

def _fail_if_contains_errors(response):
    if _contains_errors(response):
        raise _get_associated_exception(response)

def _contains_errors(response):
    return response.status_code != 200 or response.text in _ERROR_TEXT_RESPONSES
