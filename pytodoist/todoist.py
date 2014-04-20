"""This module introduces abstractions over Todoist entities such as Users,
Tasks and Projects. It's purpose is to hide the underlying API calls so that
you can interact with Todoist in a straightforward manner.

*Example:*

>>> from pytodoist import todoist
>>> user = todoist.register('John Doe', 'john.doe@gmail.com', 'password')
>>> user.is_logged_in()
True
>>> install_task = user.add_task('Install PyTodoist.')
>>> uncompleted_tasks = user.get_uncompleted_tasks()
>>> for task in uncompleted_tasks:
...     print task.content
...
Install PyTodoist
>>> install_task.complete()
"""
import json
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

    >>> from pytodoist import todoist
    >>> user = todoist.login('john.doe@gmail.com', 'password')
    >>> print user.join_date
    Sun 09 Mar 2014 19:54:01 +0000
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

    .. note:: It is up to you to obtain the valid oauth2 token.

    >>> from pytodoist import todoist
    ... # Get the oauth2 token.
    >>> user = todoist.login_with_google('john.doe@gmail.com', oauth2_token)
    >>> print user.join_date
    Sun 09 Mar 2014 19:54:01 +0000
    """
    return _login(API.login_with_google, email, oauth2_token)

def _login(login_func, *args):
    """A helper function for logging in.

    It's purpose is to avoid duplicate code in login and login_with_google.
    """
    response = login_func(*args)
    _fail_if_contains_errors(response)
    user_json = response.json()
    return User(user_json)

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

    >>> from pytodoist import todoist
    >>> user = todoist.register('John Doe', 'john.doe@gmail.com', 'password')
    >>> user.is_logged_in()
    True
    """
    response = API.register(email, full_name, password,
                            lang=lang, timezone=timezone)
    _fail_if_contains_errors(response)
    user_json = response.json()
    user = User(user_json)
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

    .. note:: It is up to you to obtain the valid oauth2 token.

    >>> from pytodoist import todoist
    ... # Get the oauth2 token.
    >>> user = todoist.register_with_google('John Doe', 'john.doe@gmail.com',
    ...                                      oauth2_token)
    >>> user.is_logged_in()
    True
    """
    response = API.login_with_google(email, oauth2_token, auto_signup=1,
                                     full_name=full_name, lang=lang,
                                     timezone=timezone)
    _fail_if_contains_errors(response)
    user_json = response.json()
    user = User(user_json)
    return user

def get_timezones():
    """Return a list of Todoist supported timezones.

    :return: A list of timezones
    :rtype: list string

    >>> from pytodoist import todoist
    >>> todoist.get_timezones()
    [u'US/Hawaii', u'US/Alaska', u'US/Pacific', u'US/Arizona, ...]
    """
    response = API.get_timezones()
    _fail_if_contains_errors(response)
    timezones_json = response.json()
    return [timezone_json[0] for timezone_json in timezones_json]

class TodoistObject(object):
    # A helper class which 'converts' a JSON object into a python object.

    def __init__(self, object_json):
        for attr in object_json:
            setattr(self, attr, object_json[attr])


class User(TodoistObject):
    """A Todoist User that has the following attributes:

    :ivar full_name: The user's full name.
    :ivar start_page: The new start page. ``_blank``: for a blank page,
        ``_info_page`` for the info page, ``_project_$PROJECT_ID`` for a
        project page or ``$ANY_QUERY`` to show query results.
    :ivar join_date: The date the user joined Todoist.
    :ivar last_used_ip: The IP address of the computer last used to login.
    :ivar is_premium: Does the user have Todoist premium?
    :ivar sort_order: The user's sort order. If it's ``0`` then show the oldest
        dates first when viewing projects, otherwise oldest dates last.
    :ivar api_token: The user's API token.
    :ivar shard_id: The user's shard ID.
    :ivar timezone: The user's chosen timezone.
    :ivar id: The ID of the user.
    :ivar next_week: The new day to use when postponing ``(1-7, Mon-Sun)``.
    :ivar tz_offset: The user's timezone offset.
    :ivar email: The user's email address.
    :ivar start_day: The new first day of the week ``(1-7, Mon-Sun)``.
    :ivar is_dummy: Is this a real or a dummy user?
    :ivar inbox_project: The ID of the user's Inbox project.
    :ivar time_format: The user's selected time_format. If ``0`` then show time
        as ``13:00`` otherwise ``1pm``.
    :ivar image_id: The ID of the user's avatar.
    :ivar beta: The user's beta status.
    :ivar premium_until: The date on which the user's premium status is revoked.
    :ivar mobile_number: The user's mobile number.
    :ivar mobile_host: The host of the user's mobile.
    :ivar password: The user's password.
    :ivar has_push_reminders: Does this user have push reminders?
    :ivar date_format: The user's selected date format. If ``0`` show
        dates as ``DD-MM-YYY`` otherwise ``MM-DD-YYYY``.
    :ivar karma: The user's karma.
    :ivar karma_trend: The user's karma trend.
    :ivar token: The user's secret token.
    :ivar seq_no: The user's sequence number.
    :ivar default_reminder: ``email`` for email, ``mobile`` for SMS,
        ``push`` for smart device notifications or ``no_default`` to
        turn off notifications. Only for premium users.
    """

    def __init__(self, user_json):
        self.token = None
        self.password = None
        super(User, self).__init__(user_json)

    def is_logged_in(self):
        """Return ``True`` if the user is logged in.

        A user is logged in if it's token is valid.

        :return: ``True`` if the user token is valid, ``False`` otherwise.
        :rtype: bool

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
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

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.delete()
        ... # The user token is now invalid and Todoist operations will fail.
        """
        response = API.delete_user(self.token, self.password,
                                   reason=reason, in_background=0)
        _fail_if_contains_errors(response)

    def update(self):
        """Update the user's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.full_name = 'John Smith'
        ... # At this point Todoist still thinks the name is 'John Doe'.
        >>> user.update()
        ... # Now the name has been updated on Todoist.
        """
        response = API.update_user(**self.__dict__)
        _fail_if_contains_errors(response)

    def change_avatar(self, image_file):
        """Change the user's avatar.

        :param image: The path to the image.
        :type image: string

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.change_avatar('/home/john/pictures/avatar.png')
        """
        with open(image_file, 'r') as image:
            response = API.update_avatar(self.token, image)
            _fail_if_contains_errors(response)

    def use_default_avatar(self):
        """Change the user's avatar to the Todoist default avatar.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
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

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.add_project('Homework')
        >>> print project.name
        Homework
        """
        response = API.add_project(self.token, name,
                                   color=color, indent=indent, order=order)
        _fail_if_contains_errors(response)
        project_json = response.json()
        return Project(project_json, self)

    def get_projects(self):
        """Return a list of a user's projects.

        :return: The user's projects.
        :rtype: list :mod:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.add_project('Homework')
        >>> projects = user.get_projects()
        >>> for project in projects:
        ...    print project.name
        Inbox
        Homework
        """
        response = API.get_projects(self.token)
        _fail_if_contains_errors(response)
        projects_json = response.json()
        return [Project(project_json, self) for project_json in projects_json]

    def get_project(self, project_name):
        """Return the project with a given name.

        :param project_name: The name to search for.
        :type project_name: string
        :return: The project that has the name ``project_name`` or ``None``
            if no project is found.
        :rtype: :mod:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> inbox = user.get_project('Inbox')
        >>> print inbox.name
        Inbox
        """
        for project in self.get_projects():
            if project.name == project_name:
                return project

    def get_project_with_id(self, project_id):
        """Return the project with a given ID.

        :param project_id: The ID to search for.
        :type project_id: string
        :return: The project that has the ID ``project_id``.
        :rtype: :mod:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> inbox = user.get_project('Inbox')
        >>> projct = user.get_project_with_id(inbox.id)
        >>> print project.name
        Inbox
        """
        response = API.get_project(self.token, project_id)
        _fail_if_contains_errors(response)
        project_json = response.json()
        return Project(project_json, self)

    def update_project_orders(self, projects):
        """Update the order in which projects are displayed on Todoist.

        :param projects: A list of projects in the order to be displayed.
        :type projects: list :mod:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> projects = user.get_projects()
        >>> for project in projects:
        ...    print project.name
        Homework
        Shopping
        >>> rev_projects = projects[::-1]
        >>> user.update_project_orders(rev_projects)
        >>> projects = user.get_projects()
        >>> for project in projects:
        ...    print project.name
        Shopping
        Homework
        """
        project_ids = str([project.id for project in projects])
        response = API.update_project_orders(self.token, project_ids)
        _fail_if_contains_errors(response)

    def get_uncompleted_tasks(self):
        """Return all of a user's uncompleted tasks.

        :return: A list of uncompleted tasks.
        :rtype: list :mod:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> uncompleted_tasks = user.get_uncompleted_tasks()
        >>> for task in uncompleted_tasks:
        ...    task.complete()
        """
        tasks = (p.get_uncompleted_tasks() for p in self.get_projects())
        return list(itertools.chain.from_iterable(tasks))

    def get_completed_tasks(self):
        """Return all of a user's completed tasks.

        :return: A list of completed tasks.
        :rtype: list :mod:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> completed_tasks = user.get_completed_tasks()
        >>> for task in completed_tasks:
        ...     task.uncomplete()
        """
        tasks = (p.get_completed_tasks() for p in self.get_projects())
        return list(itertools.chain.from_iterable(tasks))

    def search_completed_tasks(self, label_name=None, interval=None):
        """Return a filtered list of a user's completed tasks.

        .. warning:: Requires the user to have Todoist premium.

        :param label_name: Only return tasks with this label.
        :type label_name: string
        :param interval: Only return tasks completed this time period.
        :type interval: string
        :return: A list of tasks that meet the search criteria. If the user
            does not have Todoist premium an empty list is returned.
        :rtype: list :mod:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> completed_tasks = user.search_completed_tasks(label_name='School')
        >>> for task in completed_tasks:
        ...     task.uncomplete()
        """
        response = API.get_all_completed_tasks(self.token, label=label_name,
                                               interval=interval)
        _fail_if_contains_errors(response)
        tasks_json = response.json()['items']
        tasks = []
        for task_json in tasks_json:
            project_id = json['project_id']
            project = self.get_project_with_id(project_id)
            tasks.append(Task(task_json, project))
        return tasks

    def get_tasks(self):
        """Return all of a user's tasks, regardless of completion state.

        :return: A list of all of a user's tasks.
        :rtype: list :mod:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> tasks = user.get_tasks()
        """
        return self.get_uncompleted_tasks() + self.get_completed_tasks()

    def search_tasks(self, queries):
        """Return a list of tasks that match some search criteria.

        :param queries: Return tasks that match at least one of these queries.
        :type queries: list string
        :return: A list tasks that match at least one query.
        :rtype: list :mod:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> queries = ['today', 'tomorrow']
        >>> tasks = user.search_tasks(queries)
        """
        queries = json.dumps(queries)
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
                for task_json in found_tasks:
                    project_id = task_json['project_id']
                    project = self.get_project_with_id(project_id)
                    task = Task(task_json, project)
                    tasks.append(task)
        return tasks

    def get_label(self, label_name):
        """Return the user's label that has a given name.

        :param label_name: The name to search for.
        :type label_name: string
        :return: A label that has a matching name or ``None`` if not found.
        :rtype: :mod:`pytodoist.todoist.Label`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> label = user.get_label('School')
        """
        for label in self.get_labels():
            if label.name == label_name:
                return label

    def get_labels(self):
        """Return a list of all of a user's labels.

        :return: A list of labels.
        :rtype: list :mod:`pytodoist.todoist.Label`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> labels = user.get_labels()
        """
        response = API.get_labels(self.token)
        _fail_if_contains_errors(response)
        labels_json = response.json().values()
        return [Label(label_json, self) for label_json in labels_json]

    def create_label(self, name, color=None):
        """Create a new label.

        :param name: The name of the label.
        :type name: string
        :rtype: :mod:`pytodoist.todoist.Label`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> label = user.create_label('School')
        """
        response = API.create_label(self.token, name, color=color)
        _fail_if_contains_errors(response)
        label_json = response.json()
        return Label(label_json, self)

    def _get_notification_settings(self):
        """Return a list of all notification settings.

        :return: A JSON representation of the settings.
        :rtype: string
        """
        response = API.get_notification_settings(self.token)
        _fail_if_contains_errors(response)
        return response.json()

    def _update_notification_settings(self, event, service,
                                      should_notify):
        """Update the settings of a an events notifications.

        :param event: Update the notification settings of this event.
        :type event: string
        :param service: The notification service to update.
        :type service: string
        :param should_notify: Notify if this is ``1``.
        :type should_notify: int
        """
        response = API.update_notification_settings(self.token, event,
                                                    service, should_notify)
        _fail_if_contains_errors(response)

    def is_email_notified_when(self, event):
        """Find out if a user is receiving emails for a given
        event.

        :param event: The type of the notification.
        :type event: string
        :return: ``True`` if the user's settings allow for emails,
            ``False`` otherwise.
        :rtype: bool

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.is_email_notified_when(todoist.Event.NOTE_ADDED)
        True
        """
        notification_settings = self._get_notification_settings()
        return notification_settings[event]['notify_email']

    def is_push_notified_when(self, event):
        """Find out if a user is receiving push notifications for
        a given event.

        :param event: The type of the notification.
        :type event: string
        :return: ``True`` if the user's settings allow for push
            notifications, ``False`` otherwise.
        :rtype: bool

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.is_push_notified_when(todoist.Event.NOTE_ADDED)
        True
        """
        notification_settings = self._get_notification_settings()
        return notification_settings[event]['notify_push']

    def enable_push_notifications(self, event):
        """Enable push notifications for a given event.

        :param event: The event to enable push notifications for.
        :type event: string

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.enable_push_notifications(todoist.Event.NOTE_ADDED)
        """
        self._update_notification_settings(event, 'push', 0)

    def disable_push_notifications(self, event):
        """Disable push notifications for a given event.

        :param event: The event to disable push notifications for.
        :type event: string

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.disable_push_notifications(todoist.Event.NOTE_ADDED)
        """
        self._update_notification_settings(event, 'push', 1)

    def enable_email_notifications(self, event):
        """Enable email notifications for a given event.

        :param event: The event to enable email notifications for.
        :type event: string

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.enable_email_notifications(todoist.Event.NOTE_ADDED)
        """
        self._update_notification_settings(event, 'email', 0)

    def disable_email_notifications(self, event):
        """Disable email notifications for a given event.

        :param event: The event to disable email notifications for.
        :type event: string

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.disable_email_notifications(todoist.Event.NOTE_ADDED)
        """
        self._update_notification_settings(event, 'email', 1)


class Project(TodoistObject):
    """A Todoist Project with the following attributes:

    :ivar user_id: The user ID of the owner.
    :ivar name: The name of the project.
    :ivar color: The color of the project.
    :ivar is_deleted: Has this project been deleted?
    :ivar collapsed: Is this project collapsed?
    :ivar cache_count: The cache count of the project.
    :ivar inbox_project: Is this project the Inbox?
    :ivar archived_date: The date on which the project was archived.
    :ivar item_order: The task ordering.
    :ivar indent: The indentation level of the project.
    :ivar is_archived: Is this project archived?
    :ivar archived_timestamp: The timestamp of the project archiving.
    :ivar owner: The owner of the project.
    :ivar last_updated: When the project was last updated.
    :ivar id: The ID of the project.
    """

    def __init__(self, project_json, owner):
        self.id = None
        self.owner = owner
        super(Project, self).__init__(project_json)

    def delete(self):
        """Delete the project.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> project.delete()
        """
        response = API.delete_project(self.owner.token, self.id)
        _fail_if_contains_errors(response)

    def update(self):
        """Update the project's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> project.name = 'Find Employment'
        ... # At this point Todoist still thinks the name is 'Homework'
        >>> project.update()
        ... # Now the name has been updated on Todoist.
        """
        response = API.update_project(self.owner.token, self.id,
                                      **self.__dict__)
        _fail_if_contains_errors(response)

    def archive(self):
        """Archive the project.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> project.archive()
        """
        response = API.archive_project(self.owner.token, self.id)
        _fail_if_contains_errors(response)

    def unarchive(self):
        """Unarchive the project.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> project.unarchive()
        """
        response = API.unarchive_project(self.owner.token, self.id)
        _fail_if_contains_errors(response)

    def collapse(self):
        """Collapse the project on Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> project.collapse()
        """
        response = API.update_project(self.owner.token, self.id, collapsed=1)
        _fail_if_contains_errors(response)

    def add_task(self, content, date=None, priority=None):
        """Add a task to the project

        :param content: The task description.
        :type content: string
        :param date: The task deadline.
        :type date: string
        :param priority: The priority of the task.
        :type priority: int
        :return: The added task.
        :rtype: :mod:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = project.add_task('Read chapter 4.')
        >>> print task.content
        Read Chapter 4
        """
        response = API.add_task(self.owner.token, content, project_id=self.id,
                                date_string=date, priority=priority)
        _fail_if_contains_errors(response)
        task_json = response.json()
        return Task(task_json, self)

    def get_tasks(self):
        """Return all tasks in this project.

        :return: A list of all tasks in this project.
        :rtype: list :mod:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> project.add_task('Read chapter 4.')
        >>> tasks = project.get_tasks()
        >>> for task in tasks:
        ...    print task.content
        Read Chapter 4.
        """
        return self.get_uncompleted_tasks() + self.get_completed_tasks()

    def get_uncompleted_tasks(self):
        """Return a list of all uncompleted tasks in this project.

        :return: A list of all uncompleted tasks in this project.
        :rtype: list :mod:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> project.add_task('Read chapter 4.')
        >>> uncompleted_tasks = project.get_uncompleted_tasks()
        >>> for task in uncompleted_tasks:
        ...    print task.complete()
        """
        response = API.get_uncompleted_tasks(self.owner.token, self.id)
        _fail_if_contains_errors(response)
        tasks_json = response.json()
        return [Task(task_json, self) for task_json in tasks_json]

    def get_completed_tasks(self):
        """Return a list of all completed tasks in this project.

        :return: A list of all completed tasks in this project.
        :rtype: list :mod:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = project.add_task('Read chapter 4.')
        >>> task.complete()
        >>> completed_tasks = project.get_completed_tasks()
        >>> for task in completed_tasks:
        ...    print task.uncomplete()
        """
        response = API.get_completed_tasks(self.owner.token, self.id)
        _fail_if_contains_errors(response)
        tasks_json = response.json()
        return [Task(task_json, self) for task_json in tasks_json]

    def update_task_orders(self, tasks):
        """Update the order in which tasks are displayed on Todoist.

        :param tasks: A list of tasks in the order to be displayed.
        :type tasks: list :mod:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> tasks = project.get_tasks()
        >>> rev_tasks = tasks[::-1]
        >>> project.update_task_orders(rev_tasks)
        """
        task_ids = str([task.id for task in tasks])
        response = API.update_task_ordering(self.owner.token, self.id, task_ids)
        _fail_if_contains_errors(response)


class Task(TodoistObject):
    """A Todoist Task with the following attributes:

    :ivar is_archived: Is the task archived?
    :ivar labels: A list of attached label names.
    :ivar sync_id: The task sync ID.
    :ivar in_history: Is the task in the task history?
    :ivar date_added: The date the task was added.
    :ivar children: A list of child tasks.
    :ivar content: The task content.
    :ivar checked: Is the task checked?
    :ivar id: The task ID.
    :ivar priority: The task priority.
    :ivar item_order: The task order.
    :ivar project_id: The ID of the parent project.
    :ivar date_string: How did the user enter the task? Could be every day or
        every day @ 10. The time should be shown when formating the date if @ OR
        at is found anywhere in the string.
    :ivar due_date: When is the task due?
    :ivar due_date_utc: When is the task due (in UTC).
    :ivar assigned_by_uid: ID of the user who assigned the task.
    :ivar responsible_uid: ID of the user who responsible for the task.
    :ivar collapsed: Is the task collapsed?
    :ivar has_notifications: Does the task have notifications?
    :ivar indent: The task indentation level.
    :ivar is_deleted: Has the task been deleted?
    :ivar user_id: The ID of the user who owns the task.
    :ivar project: The parent project.
    """

    def __init__(self, task_json, project):
        self.id = None
        self.project = project
        super(Task, self).__init__(task_json)

    def update(self):
        """Update the task's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = user.add_task('Read Chapter 4.')
        >>> task.content = 'Read Chapter 5'
        ... # At this point Todoist still thinks the content is 'Read Chapter 4'
        >>> task.update()
        ... # Now the content has been updated on Todoist.
        """
        response = API.update_task(self.project.owner.token, self.id,
                                   **self.__dict__)
        _fail_if_contains_errors(response)

    def delete(self):
        """Delete the task.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = user.add_task('Read Chapter 4.')
        >>> task.delete()
        """
        task_ids = '[{id}]'.format(id=self.id)
        response = API.delete_tasks(self.project.owner.token, task_ids)
        _fail_if_contains_errors(response)

    def complete(self):
        """Mark the task complete.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = user.add_task('Read Chapter 4.')
        >>> task.complete()
        """
        task_ids = '[{id}]'.format(id=self.id)
        response = API.complete_tasks(self.project.owner.token, task_ids)
        _fail_if_contains_errors(response)

    def uncomplete(self):
        """Mark the task uncomplete.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = user.add_task('Read Chapter 4.')
        >>> task.uncomplete()
        """
        task_ids = '[{id}]'.format(id=self.id)
        response = API.uncomplete_tasks(self.project.owner.token, task_ids)
        _fail_if_contains_errors(response)

    def add_note(self, content):
        """Add a note to the Task.

        :param content: The content of the note.
        :type content: string
        :return: The added note.
        :rtype: :mod:`pytodoist.todoist.Note`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = user.add_task('Read Chapter 4.')
        >>> note = task.add_note('Page 56')
        >>> print note.content
        Page 56
        """
        response = API.add_note(self.project.owner.token, self.id, content)
        _fail_if_contains_errors(response)
        note_json = response.json()
        return Note(note_json, self)

    def get_notes(self):
        """Return all notes attached to this Task.

        :return: A list of all notes attached to this Task.
        :rtype: list :mod:`pytodoist.todoist.Note`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = user.add_task('Read Chapter 4.')
        >>> task.add_note('Page 56')
        >>> notes = task.get_notes()
        >>> len(notes)
        1
        """
        response = API.get_notes(self.project.owner.token, self.id)
        _fail_if_contains_errors(response)
        notes_json = response.json()
        return [Note(note_json, self) for note_json in notes_json]

    def advance_recurring_date(self):
        """Advance the recurring date of this task.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = user.add_task('Read Chapter 4.')
        >>> task.due_date
        Sun 09 Mar 2014 19:54:01 +0000
        >>> task.advance_recurring_date()
        >>> task.due_date
        Sun 10 Mar 2014 19:54:01 +0000
        """
        task_ids = '[{id}]'.format(id=self.id)
        response = API.advance_recurring_dates(self.project.owner.token,
                                               task_ids)
        _fail_if_contains_errors(response)
        task_json = response.json()[0]
        self.__init__(task_json, self.project)

    def move(self, project):
        """Move this task to another project.

        :param project: The project to move the task to.
        :type project: :mod:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = user.add_task('Read Chapter 4.')
        >>> print task.project.name
        Homework
        >>> inbox = user.get_project('Inbox')
        >>> task.move(inbox)
        >>> print task.project.name
        Inbox
        """
        current_pos = '{{"{p_id}":["{t_id}"]}}'.format(p_id=self.project.id,
                                                       t_id=self.id)
        response = API.move_tasks(self.project.owner.token, current_pos,
                                  project.id)
        _fail_if_contains_errors(response)
        self.project = project


class Note(TodoistObject):
    """A Todoist note with the following attributes:

    :ivar task: The task it is attached to.
    :ivar is_deleted: Has the note been deleted?
    :ivar is_archived: Has the note been archived?
    :ivar content: The note content.
    :ivar posted_uid: The ID of the user who attached the note.
    :ivar item_id: The ID of the task it is attached to.
    :ivar uids_to_notify: List of user IDs to notify.
    :ivar id: The note ID.
    :ivar posted: The date/time the note was posted.
    """

    def __init__(self, note_json, task):
        self.id = None
        self.content = None
        self.task = task
        super(Note, self).__init__(note_json)

    def update(self):
        """Update the note's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = user.add_task('Read Chapter 4.')
        >>> note = task.add_note('Page 56')
        >>> note.content = 'Page 65'
        ... # At this point Todoist still thinks the content is 'Page 56'
        >>> note.update()
        ... # Now the content has been updated on Todoist.
        """
        response = API.update_note(self.task.project.owner.token, self.id,
                                   self.content)
        _fail_if_contains_errors(response)

    def delete(self):
        """Delete the note, removing it from it's task.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = user.add_task('Read Chapter 4.')
        >>> note = task.add_note('Page 56')
        >>> note.delete()
        >>> notes = task.get_notes()
        >>> len(notes)
        0
        """
        response = API.delete_note(self.task.project.owner.token,
                                   self.task.id, self.id)
        _fail_if_contains_errors(response)


class Label(TodoistObject):
    """A Todoist label with the following attributes:

    :ivar is_deleted: Has the label been deleted?
    :ivar name: The label name.
    :ivar color: The color of the label.
    :ivar owner: The user who owns the label.
    :ivar id: The ID of the label.
    :ivar uid: The ID of user who owns the label.
    """

    def __init__(self, label_json, owner):
        self.name = None
        self.color = None
        self.owner = owner
        super(Label, self).__init__(label_json)
        self.id = self.name

    def update(self):
        """Update the label's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> label = user.create_label('work')
        >>> label.name = 'football'
        ... # At this point Todoist still thinks the name is 'work'
        >>> label.update()
        ... # Now the name has been updated on Todoist.
        """
        response = API.update_label_name(self.owner.token, self.id, self.name)
        _fail_if_contains_errors(response)
        self.id = self.name
        response = API.update_label_color(self.owner.token, self.id, self.color)
        _fail_if_contains_errors(response)

    def delete(self):
        """Delete the label.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> label = user.create_label('work')
        >>> label.delete()
        """
        response = API.delete_label(self.owner.token, self.id)
        _fail_if_contains_errors(response)


class Color(object):
    """This class acts as an easy way to specify Todoist project
    colors.

    >>> from pytodoist import todoist
    >>> user = todoist.login('john.doe@gmail.com', 'password')
    >>> user.add_project('Homework', color=todoist.Color.RED)

    The supported colors:
        * GREEN
        * PINK
        * LIGHT_ORANGE
        * YELLOW
        * DARK_BLUE
        * BROWN
        * PURPLE
        * GRAY
        * RED
        * DARK_ORANGE
        * CYAN
        * LIGHT_BLUE
    """
    GREEN = 0
    PINK = 1
    LIGHT_ORANGE = 2
    YELLOW = 3
    DARK_BLUE = 4
    BROWN = 5
    PURPLE = 6
    GRAY = 7
    RED = 8
    DARK_ORANGE = 9
    CYAN = 10
    LIGHT_BLUE = 11


class Priority(object):
    """This class acts as an easy way to specify Todoist task
    priority.

    >>> from pytodoist import todoist
    >>> user = todoist.login('john.doe@gmail.com', 'password')
    >>> inbox = user.get_project('Inbox')
    >>> inbox.add_task('Read Chapter 4', priority=todoist.Priority.LOW)

    The supported priorities:
        * NO
        * LOW
        * NORMAL
        * HIGH
        * VERY_HIGH
    """
    NO = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    VERY_HIGH = 4

class Event(object):
    """This class acts as an easy way to specify Todoist event
    types.

    >>> from pytodoist import todoist
    >>> user = todoist.login('john.doe@gmail.com', 'password')
    >>> user.enable_email_notifications(todoist.Event.NOTE_ADDED)

    The supported events:
        * USER_LEFT_PROJECT
        * USER_REMOVED_FROM_PROJECT
        * ITEM_COMPLETED
        * ITEM_UNCOMPLETED
        * ITEM_ASSIGNED
        * SHARE_INVITATION_REJECTED
        * SHARE NOTIFICATION_ACCEPTED
        * NOTE_ADDED
    """
    USER_LEFT_PROJECT = 'user_left_project'
    USER_REMOVED_FROM_PROJECT = 'user_removed_from_project'
    ITEM_COMPLETED = 'item_completed'
    ITEM_UNCOMPLETED = 'item_uncompleted'
    ITEM_ASSIGNED = 'item_assigned'
    SHARE_INVITATION_REJECTED = 'share_invitation_rejected'
    SHARE_NOTIFICATION_ACCEPTED = 'share_notification_accepted'
    NOTE_ADDED = 'note_added'


class RequestError(Exception):
    """Will be raised whenever a Todoist API call fails."""

    def __init__(self, response):
        self.response = response
        super(RequestError, self).__init__(response.text)

# Avoid magic numbers.
HTTP_OK = 200

_ERROR_TEXT_RESPONSES = [
    '"LOGIN_ERROR"',
    '"INTERNAL_ERROR"',
    '"EMAIL_MISMATCH"',
    '"ACCOUNT_NOT_CONNECTED_WITH_GOOGLE"',
    '"ALREADY_REGISTRED"',
    '"TOO_SHORT_PASSWORD"',
    '"INVALID_EMAIL"',
    '"INVALID_TIMEZONE"',
    '"INVALID_FULL_NAME"',
    '"UNKNOWN_ERROR"',
    '"ERROR_PASSWORD_TOO_SHORT"',
    '"ERROR_EMAIL_FOUND"',
    '"UNKNOWN_IMAGE_FORMAT"',
    '"AVATAR_NOT_FOUND"',
    '"UNABLE_TO_RESIZE_IMAGE"',
    '"IMAGE_TOO_BIG"',
    '"UNABLE_TO_RESIZE_IMAGE"',
    '"ERROR_PROJECT_NOT_FOUND"',
    '"ERROR_NAME_IS_EMPTY"',
    '"ERROR_WRONG_DATE_SYNTAX"',
    '"ERROR_ITEM_NOT_FOUND"',
]

def _fail_if_contains_errors(response):
    """Raise a RequestError Exception if a given response
    does not denote a successful request.
    """
    if _contains_errors(response):
        raise RequestError(response)

def _contains_errors(response):
    """Return True if a given response contains errors."""
    return (response.status_code != HTTP_OK
            or response.text in _ERROR_TEXT_RESPONSES)
