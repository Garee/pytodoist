"""This module introduces abstractions over Todoist entities such as Users,
Tasks and Projects. It's purpose is to hide the underlying API calls so that
you can interact with Todoist in a straightforward manner.

*Example:*

>>> from pytodoist import todoist
>>> user = todoist.register('John Doe', 'john.doe@gmail.com', 'password')
>>> inbox = user.get_project('Inbox')
>>> install_task = inbox.add_task('Install PyTodoist')
>>> uncompleted_tasks = user.get_uncompleted_tasks()
>>> for task in uncompleted_tasks:
...     print(task.content)
...
Install PyTodoist
>>> install_task.complete()
"""
import json
import uuid
import itertools
from pytodoist.api import TodoistAPI

# No magic numbers
_HTTP_OK = 200
_PAGE_LIMIT = 50

API = TodoistAPI()


def login(email, password):
    """Login to Todoist.

    :param email: A Todoist user's email address.
    :type email: str
    :param password: A Todoist user's password.
    :type password: str
    :return: The Todoist user.
    :rtype: :class:`pytodoist.todoist.User`

    >>> from pytodoist import todoist
    >>> user = todoist.login('john.doe@gmail.com', 'password')
    >>> print(user.full_name)
    John Doe
    """
    user = _login(API.login, email, password)
    user.password = password
    return user


def login_with_google(email, oauth2_token):
    """Login to Todoist using Google oauth2 authentication.

    :param email: A Todoist user's Google email address.
    :type email: str
    :param oauth2_token: The oauth2 token associated with the email.
    :type oauth2_token: str
    :return: The Todoist user.
    :rtype: :class:`pytodoist.todoist.User`

    .. note:: It is up to you to obtain the valid oauth2 token.

    >>> from pytodoist import todoist
    >>> oauth2_token = 'oauth2_token'
    >>> user = todoist.login_with_google('john.doe@gmail.com', oauth2_token)
    >>> print(user.full_name)
    John Doe
    """
    return _login(API.login_with_google, email, oauth2_token)


def login_with_api_token(api_token):
    """Login to Todoist using a user's api token.

    .. note:: It is up to you to obtain the api token.

    :param api_token: A Todoist user's api token.
    :type api_token: str
    :return: The Todoist user.
    :rtype: :class:`pytodoist.todoist.User`

    >>> from pytodoist import todoist
    >>> api_token = 'api_token'
    >>> user = todoist.login_with_api_token(api_token)
    >>> print(user.full_name)
    John Doe
    """
    response = API.sync(api_token, '*', '["user"]')
    _fail_if_contains_errors(response)
    user_json = response.json()['user']
    # Required as sync doesn't return the api_token.
    user_json['api_token'] = user_json['token']
    return User(user_json)


def _login(login_func, *args):
    """A helper function for logging in. It's purpose is to avoid duplicate
    code in the login functions.
    """
    response = login_func(*args)
    _fail_if_contains_errors(response)
    user_json = response.json()
    return User(user_json)


def register(full_name, email, password, lang=None, timezone=None):
    """Register a new Todoist account.

    :param full_name: The user's full name.
    :type full_name: str
    :param email: The user's email address.
    :type email: str
    :param password: The user's password.
    :type password: str
    :param lang: The user's language.
    :type lang: str
    :param timezone: The user's timezone.
    :type timezone: str
    :return: The Todoist user.
    :rtype: :class:`pytodoist.todoist.User`

    >>> from pytodoist import todoist
    >>> user = todoist.register('John Doe', 'john.doe@gmail.com', 'password')
    >>> print(user.full_name)
    John Doe
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
    :type full_name: str
    :param email: The user's email address.
    :type email: str
    :param oauth2_token: The oauth2 token associated with the email.
    :type oauth2_token: str
    :param lang: The user's language.
    :type lang: str
    :param timezone: The user's timezone.
    :type timezone: str
    :return: The Todoist user.
    :rtype: :class:`pytodoist.todoist.User`

    .. note:: It is up to you to obtain the valid oauth2 token.

    >>> from pytodoist import todoist
    >>> oauth2_token = 'oauth2_token'
    >>> user = todoist.register_with_google('John Doe', 'john.doe@gmail.com',
    ...                                      oauth2_token)
    >>> print(user.full_name)
    John Doe
    """
    response = API.login_with_google(email, oauth2_token, auto_signup=1,
                                     full_name=full_name, lang=lang,
                                     timezone=timezone)
    _fail_if_contains_errors(response)
    user_json = response.json()
    user = User(user_json)
    return user


def _fail_if_contains_errors(response, sync_uuid=None):
    """Raise a RequestError Exception if a given response
    does not denote a successful request.
    """
    if response.status_code != _HTTP_OK:
        raise RequestError(response)
    response_json = response.json()
    if sync_uuid and 'sync_status' in response_json:
        status = response_json['sync_status']
        if sync_uuid in status and 'error' in status[sync_uuid]:
            raise RequestError(response)


def _gen_uuid():
    """Return a randomly generated UUID string."""
    return str(uuid.uuid4())


def _perform_command(user, command_type, command_args):
    """Perform an operation on Todoist using the API sync end-point."""
    command_uuid = _gen_uuid()
    command = {
        'type': command_type,
        'args': command_args,
        'uuid': command_uuid,
        'temp_id': _gen_uuid()
    }
    commands = json.dumps([command])
    response = API.sync(user.api_token, user.sync_token, commands=commands)
    _fail_if_contains_errors(response, command_uuid)
    response_json = response.json()
    user.sync_token = response_json['sync_token']


class TodoistObject(object):
    """A helper class which 'converts' a JSON object into a python object."""

    _CUSTOM_ATTRS = [
        'to_update',  # Keeps track of the attributes which have changed.
    ]

    def __init__(self, object_json):
        for attr in object_json:
            setattr(self, attr, object_json[attr])

    def __setattr__(self, key, value):
        if hasattr(self, 'to_update') and key not in self._CUSTOM_ATTRS:
            self.to_update.add(key)  # Don't update on __init__.
        super(TodoistObject, self).__setattr__(key, value)


class User(TodoistObject):
    """A Todoist User that has the following attributes:

    :ivar id: The ID of the user.
    :ivar email: The user's email address.
    :ivar password: The user's password.
    :ivar full_name: The user's full name.
    :ivar join_date: The date the user joined Todoist.
    :ivar is_premium: Does the user have Todoist premium?
    :ivar premium_until: The date on which the premium status is revoked.
    :ivar tz_info: The user's timezone information.
    :ivar time_format: The user's selected time_format. If ``0`` then show
        time as ``13:00`` otherwise ``1pm``.
    :ivar date_format: The user's selected date format. If ``0`` show
        dates as ``DD-MM-YYY`` otherwise ``MM-DD-YYYY``.
    :ivar start_page: The new start page. ``_blank``: for a blank page,
        ``_info_page`` for the info page, ``_project_$PROJECT_ID`` for a
        project page or ``$ANY_QUERY`` to show query results.
    :ivar start_day: The new first day of the week ``(1-7, Mon-Sun)``.
    :ivar next_week: The day to use when postponing ``(1-7, Mon-Sun)``.
    :ivar sort_order: The user's sort order. If it's ``0`` then show the
        oldest dates first when viewing projects, otherwise oldest dates last.
    :ivar mobile_number: The user's mobile number.
    :ivar mobile_host: The host of the user's mobile.
    :ivar business_account_id: The ID of the user's business account.
    :ivar karma: The user's karma.
    :ivar karma_trend: The user's karma trend.
    :ivar default_reminder: ``email`` for email, ``mobile`` for SMS,
        ``push`` for smart device notifications or ``no_default`` to
        turn off notifications. Only for premium users.
    :ivar inbox_project: The ID of the user's Inbox project.
    :ivar team_inbox: The ID of the user's team Inbox project.
    :ivar api_token: The user's API token.
    :ivar shard_id: The user's shard ID.
    :ivar image_id: The ID of the user's avatar.
    :ivar is_biz_admin: Is the user a business administrator?
    :ivar last_used_ip: The IP address of the computer last used to login.
    :ivar auto_reminder: The auto reminder of the user.
    """

    # Don't try to update these attributes on Todoist.
    _CUSTOM_ATTRS = [
        'projects',
        'tasks',
        'notes',
        'labels',
        'filters',
        'reminders',
        'password',
        'sync_token',
    ] + TodoistObject._CUSTOM_ATTRS

    def __init__(self, user_json):
        self.id = ''
        self.email = ''
        self.full_name = ''
        self.join_date = ''
        self.is_premium = ''
        self.premium_until = ''
        self.tz_info = ''
        self.time_format = ''
        self.date_format = ''
        self.start_page = ''
        self.start_day = ''
        self.next_week = ''
        self.sort_order = ''
        self.mobile_number = ''
        self.mobile_host = ''
        self.business_account_id = ''
        self.karma = ''
        self.karma_trend = ''
        self.default_reminder = ''
        self.inbox_project = ''
        self.team_inbox = ''
        self.api_token = ''
        self.shard_id = ''
        self.image_id = ''
        self.is_biz_admin = ''
        self.last_used_ip = ''
        self.auto_reminder = ''
        super(User, self).__init__(user_json)
        self.password = ''
        self.projects = {}
        self.tasks = {}
        self.notes = {}
        self.labels = {}
        self.filters = {}
        self.reminders = {}
        self.sync_token = '*'
        self.sync()
        self.to_update = set()

    def update(self):
        """Update the user's details on Todoist.

        This method must be called to register any local attribute changes
        with Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.full_name = 'John Smith'
        >>> # At this point Todoist still thinks the name is 'John Doe'.
        >>> user.update()
        >>> # Now the name has been updated on Todoist.
        """
        args = {attr: getattr(self, attr) for attr in self.to_update}
        _perform_command(self, 'user_update', args)

    def sync(self, resource_types='["all"]'):
        """Synchronize the user's data with the Todoist server.

        This function will pull data from the Todoist server and update the
        state of the user object such that they match. It does not *push* data
        to Todoist. If you want to do that use
        :func:`pytodoist.todoist.User.update`.

        :param resource_types: A JSON-encoded list of Todoist resources which
            should be synced. By default this is everything, but you can
            choose to sync only selected resources. See
            `here <https://developer.todoist.com/#retrieve-data>`_ for a list
            of resources.
        """
        response = API.sync(self.api_token, '*', resource_types)
        _fail_if_contains_errors(response)
        response_json = response.json()
        self.sync_token = response_json['sync_token']
        if 'projects' in response_json:
            self._sync_projects(response_json['projects'])
        if 'items' in response_json:
            self._sync_tasks(response_json['items'])
        if 'notes' in response_json:
            self._sync_notes(response_json['notes'])
        if 'labels' in response_json:
            self._sync_labels(response_json['labels'])
        if 'filters' in response_json:
            self._sync_filters(response_json['filters'])
        if 'reminders' in response_json:
            self._sync_filters(response_json['reminders'])

    def _sync_projects(self, projects_json):
        """"Populate the user's projects from a JSON encoded list."""
        for project_json in projects_json:
            project_id = project_json['id']
            self.projects[project_id] = Project(project_json, self)

    def _sync_tasks(self, tasks_json):
        """"Populate the user's tasks from a JSON encoded list."""
        for task_json in tasks_json:
            task_id = task_json['id']
            project_id = task_json['project_id']
            project = self.projects[project_id]
            self.tasks[task_id] = Task(task_json, project)

    def _sync_notes(self, notes_json):
        """"Populate the user's notes from a JSON encoded list."""
        for note_json in notes_json:
            note_id = note_json['id']
            task_id = note_json['item_id']
            task = self.tasks[task_id]
            self.notes[note_id] = Note(note_json, task)

    def _sync_labels(self, labels_json):
        """"Populate the user's labels from a JSON encoded list."""
        for label_json in labels_json:
            label_id = label_json['id']
            self.labels[label_id] = Label(label_json, self)

    def _sync_filters(self, filters_json):
        """"Populate the user's filters from a JSON encoded list."""
        for filter_json in filters_json:
            filter_id = filter_json['id']
            self.filters[filter_id] = Filter(filter_json, self)

    def _sync_reminders(self, reminders_json):
        """"Populate the user's reminders from a JSON encoded list."""
        for reminder_json in reminders_json:
            reminder_id = reminder_json['id']
            task_id = reminder_json['item_id']
            task = self.tasks[task_id]
            self.reminders[reminder_id] = Reminder(reminder_json, task)

    def add_project(self, name, color=None, indent=None, order=None):
        """Add a project to the user's account.

        :param name: The project name.
        :type name: str
        :return: The project that was added.
        :rtype: :class:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.add_project('PyTodoist')
        >>> print(project.name)
        PyTodoist
        """
        args = {
            'name': name,
            'color': color,
            'indent': indent,
            'order': order
        }
        args = {k: args[k] for k in args if args[k] is not None}
        _perform_command(self, 'project_add', args)
        return self.get_project(name)

    def get_project(self, project_name):
        """Return the project with a given name.

        :param project_name: The name to search for.
        :type project_name: str
        :return: The project that has the name ``project_name`` or ``None``
            if no project is found.
        :rtype: :class:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Inbox')
        >>> print(project.name)
        Inbox
        """
        for project in self.get_projects():
            if project.name == project_name:
                return project

    def get_projects(self):
        """Return a list of a user's projects.

        :return: The user's projects.
        :rtype: list of :class:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.add_project('PyTodoist')
        >>> projects = user.get_projects()
        >>> for project in projects:
        ...    print(project.name)
        Inbox
        PyTodoist
        """
        self.sync()
        return list(self.projects.values())

    def get_archived_projects(self):
        """Return a list of a user's archived projects.

        :return: The user's archived projects.
        :rtype: list of :class:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.archive()
        >>> projects = user.get_archived_projects()
        >>> for project in projects:
        ...    print(project.name)
        PyTodoist
        """
        return [p for p in self.get_projects() if p.is_archived]

    def get_uncompleted_tasks(self):
        """Return all of a user's uncompleted tasks.

        .. warning:: Requires Todoist premium.

        :return: A list of uncompleted tasks.
        :rtype: list of :class:`pytodoist.todoist.Task`

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

        .. warning:: Requires Todoist premium.

        :return: A list of completed tasks.
        :rtype: list of :class:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> completed_tasks = user.get_completed_tasks()
        >>> for task in completed_tasks:
        ...     task.uncomplete()
        """
        tasks = (p.get_completed_tasks() for p in self.get_projects())
        return list(itertools.chain.from_iterable(tasks))

    def get_tasks(self):
        """Return all of a user's tasks, regardless of completion state.

        :return: A list of all of a user's tasks.
        :rtype: list of :class:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> tasks = user.get_tasks()
        """
        self.sync()
        return list(self.tasks.values())

    def search_tasks(self, *queries):
        """Return a list of tasks that match some search criteria.

        .. note:: Example queries can be found
            `here <https://todoist.com/Help/timeQuery>`_.

        .. note:: A standard set of queries are available
            in the :class:`pytodoist.todoist.Query` class.

        :param queries: Return tasks that match at least one of these queries.
        :type queries: list str
        :return: A list tasks that match at least one query.
        :rtype: list of :class:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> tasks = user.search_tasks(todoist.Query.TOMORROW, '18 Sep')
        """
        queries = json.dumps(queries)
        response = API.query(self.api_token, queries)
        _fail_if_contains_errors(response)
        query_results = response.json()
        tasks = []
        for result in query_results:
            if 'data' not in result:
                continue
            all_tasks = result['data']
            if result['type'] == Query.ALL:
                all_projects = all_tasks
                for project_json in all_projects:
                    uncompleted_tasks = project_json.get('uncompleted', [])
                    completed_tasks = project_json.get('completed', [])
                    all_tasks = uncompleted_tasks + completed_tasks
            for task_json in all_tasks:
                project_id = task_json['project_id']
                project = self.projects[project_id]
                task = Task(task_json, project)
                tasks.append(task)
        return tasks

    def add_label(self, name, color=None):
        """Create a new label.

        .. warning:: Requires Todoist premium.

        :param name: The name of the label.
        :type name: str
        :param color: The color of the label.
        :type color: str
        :return: The newly created label.
        :rtype: :class:`pytodoist.todoist.Label`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> label = user.add_label('family')
        """
        args = {
            'name': name,
            'color': color
        }
        _perform_command(self, 'label_register', args)
        return self.get_label(name)

    def get_label(self, label_name):
        """Return the user's label that has a given name.

        :param label_name: The name to search for.
        :type label_name: str
        :return: A label that has a matching name or ``None`` if not found.
        :rtype: :class:`pytodoist.todoist.Label`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> label = user.get_label('family')
        """
        for label in self.get_labels():
            if label.name == label_name:
                return label

    def get_labels(self):
        """Return a list of all of a user's labels.

        :return: A list of labels.
        :rtype: list of :class:`pytodoist.todoist.Label`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> labels = user.get_labels()
        """
        self.sync()
        return list(self.labels.values())

    def get_notes(self):
        """Return a list of all of a user's notes.

        :return: A list of notes.
        :rtype: list of :class:`pytodoist.todoist.Note`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> notes = user.get_notes()
        """
        self.sync()
        return list(self.notes.values())

    def add_filter(self, name, query, color=None, item_order=None):
        """Create a new filter.

        .. warning:: Requires Todoist premium.

        :param name: The name of the filter.
        :param query: The query to search for.
        :param color: The color of the filter.
        :param item_order: The filter's order in the filter list.
        :return: The newly created filter.
        :rtype: :class:`pytodoist.todoist.Filter`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> overdue_filter = user.add_filter('Overdue', todoist.Query.OVERDUE)
        """
        args = {
            'name': name,
            'query': query,
            'color': color,
            'item_order': item_order
        }
        _perform_command(self, 'filter_add', args)
        return self.get_filter(name)

    def get_filter(self, name):
        """Return the filter that has the given filter name.

        :param name: The name to search for.
        :return: The filter with the given name.
        :rtype: :class:`pytodoist.todoist.Filter`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.add_filter('Overdue', todoist.Query.OVERDUE)
        >>> overdue_filter = user.get_filter('Overdue')
        """
        for flter in self.get_filters():
            if flter.name == name:
                return flter

    def get_filters(self):
        """Return a list of all a user's filters.

        :return: A list of filters.
        :rtype: list of :class:`pytodoist.todoist.Filter`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> filters = user.get_filters()
        """
        self.sync()
        return list(self.filters.values())

    def clear_reminder_locations(self):
        """Clear all reminder locations set for the user.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.clear_reminder_locations()
        """
        _perform_command(self, 'clear_locations', {})

    def get_reminders(self):
        """Return a list of the user's reminders.

        :return: A list of reminders.
        :rtype: list of :class:`pytodoist.todoist.Reminder`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> reminders = user.get_reminders()
        """
        self.sync()
        return list(self.reminders.values())

    def _update_notification_settings(self, event, service,
                                      should_notify):
        """Update the settings of a an events notifications.

        :param event: Update the notification settings of this event.
        :type event: str
        :param service: The notification service to update.
        :type service: str
        :param should_notify: Notify if this is ``1``.
        :type should_notify: int
        """
        response = API.update_notification_settings(self.api_token, event,
                                                    service, should_notify)
        _fail_if_contains_errors(response)

    def enable_push_notifications(self, event):
        """Enable push notifications for a given event.

        :param event: The event to enable push notifications for.
        :type event: str

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.enable_push_notifications(todoist.Event.NOTE_ADDED)
        """
        self._update_notification_settings(event, 'push', 0)

    def disable_push_notifications(self, event):
        """Disable push notifications for a given event.

        :param event: The event to disable push notifications for.
        :type event: str

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.disable_push_notifications(todoist.Event.NOTE_ADDED)
        """
        self._update_notification_settings(event, 'push', 1)

    def enable_email_notifications(self, event):
        """Enable email notifications for a given event.

        :param event: The event to enable email notifications for.
        :type event: str

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.enable_email_notifications(todoist.Event.NOTE_ADDED)
        """
        self._update_notification_settings(event, 'email', 0)

    def disable_email_notifications(self, event):
        """Disable email notifications for a given event.

        :param event: The event to disable email notifications for.
        :type event: str

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.disable_email_notifications(todoist.Event.NOTE_ADDED)
        """
        self._update_notification_settings(event, 'email', 1)

    def get_productivity_stats(self):
        """Return the user's productivity stats.

        :return: A JSON-encoded representation of the user's productivity
            stats.
        :rtype: A JSON-encoded object.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> stats = user.get_productivity_stats()
        >>> print(stats)
        {"karma_last_update": 50.0, "karma_trend": "up", ... }
        """
        response = API.get_productivity_stats(self.api_token)
        _fail_if_contains_errors(response)
        return response.json()

    def enable_karma(self):
        """Enable karma for the user.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.enable_karma()
        """
        args = {'karma_disabled': 0}
        _perform_command(self, 'update_goals', args)

    def disable_karma(self):
        """Disable karma for the user.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.disable_karma()
        """
        args = {'karma_disabled': 1}
        _perform_command(self, 'update_goals', args)

    def enable_vacation(self):
        """Enable vacation for the user.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.enable_vacation()
        """
        args = {'vacation_mode': 1}
        _perform_command(self, 'update_goals', args)

    def disable_vacation(self):
        """Disable vacation for the user.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.disable_vacation()
        """
        args = {'vacation_mode': 0}
        _perform_command(self, 'update_goals', args)

    def update_daily_karma_goal(self, goal):
        """Update the user's daily karma goal.

        :param goal: The daily karma goal.
        :type goal: int

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.update_daily_karma_goal(100)
        """
        args = {'daily_goal': goal}
        _perform_command(self, 'update_goals', args)

    def update_weekly_karma_goal(self, goal):
        """Set the user's weekly karma goal.

        :param goal: The weekly karma goal.
        :type goal: int

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.update_weekly_karma_goal(700)
        """
        args = {'weekly_goal': goal}
        _perform_command(self, 'update_goals', args)

    def get_redirect_link(self):
        """Return the absolute URL to redirect or to open in
        a browser. The first time the link is used it logs in the user
        automatically and performs a redirect to a given page. Once used,
        the link keeps working as a plain redirect.

        :return: The user's redirect link.
        :rtype: str

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> print(user.get_redirect_link())
        https://todoist.com/secureRedirect?path=%2Fapp&token ...
        """
        response = API.get_redirect_link(self.api_token)
        _fail_if_contains_errors(response)
        link_json = response.json()
        return link_json['link']

    def delete(self, reason=None):
        """Delete the user's account from Todoist.

        .. warning:: You cannot recover the user after deletion!

        :param reason: The reason for deletion.
        :type reason: str

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.delete()
        ... # The user token is now invalid and Todoist operations will fail.
        """
        response = API.delete_user(self.api_token, self.password,
                                   reason=reason, in_background=0)
        _fail_if_contains_errors(response)


class Project(TodoistObject):
    """A Todoist Project with the following attributes:

    :ivar id: The ID of the project.
    :ivar name: The name of the project.
    :ivar color: The color of the project.
    :ivar collapsed: Is this project collapsed?
    :ivar owner: The owner of the project.
    :ivar last_updated: When the project was last updated.
    :ivar cache_count: The cache count of the project.
    :ivar item_order: The task ordering.
    :ivar indent: The indentation level of the project.
    :ivar is_deleted: Has this project been deleted?
    :ivar is_archived: Is this project archived?
    :ivar inbox_project: Is this project the Inbox?
    """

    _CUSTOM_ATTRS = [
        'owner',
    ] + TodoistObject._CUSTOM_ATTRS

    def __init__(self, project_json, owner):
        self.id = ''
        self.name = ''
        self.color = ''
        self.collapsed = ''
        self.user_id = ''
        self.shared = ''
        self.item_order = ''
        self.indent = ''
        self.is_deleted = ''
        self.is_archived = ''
        self.archived_date = ''
        self.archived_timestamp = ''
        super(Project, self).__init__(project_json)
        self.owner = owner
        self.to_update = set()

    def update(self):
        """Update the project's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.name = 'Homework'
        ... # At this point Todoist still thinks the name is 'PyTodoist'.
        >>> project.update()
        ... # Now the name has been updated on Todoist.
        """
        args = {attr: getattr(self, attr) for attr in self.to_update}
        args['id'] = self.id
        _perform_command(self.owner, 'project_update', args)

    def archive(self):
        """Archive the project.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.archive()
        """
        args = {'id': self.id}
        _perform_command(self.owner, 'project_archive', args)
        self.is_archived = '1'

    def unarchive(self):
        """Unarchive the project.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.unarchive()
        """
        args = {'id': self.id}
        _perform_command(self.owner, 'project_unarchive', args)

    def collapse(self):
        """Collapse the project on Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.collapse()
        """
        self.collapsed = True
        self.update()

    def add_task(self, content, date=None, priority=None):
        """Add a task to the project

        :param content: The task description.
        :type content: str
        :param date: The task deadline.
        :type date: str
        :param priority: The priority of the task.
        :type priority: int
        :return: The added task.
        :rtype: :class:`pytodoist.todoist.Task`

        .. note:: See `here <https://todoist.com/Help/timeInsert>`_
            for possible date strings.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist')
        >>> print(task.content)
        Install PyTodoist
        """
        response = API.add_item(self.owner.token, content, project_id=self.id,
                                date_string=date, priority=priority)
        _fail_if_contains_errors(response)
        task_json = response.json()
        return Task(task_json, self)

    def get_uncompleted_tasks(self):
        """Return a list of all uncompleted tasks in this project.

        .. warning:: Requires Todoist premium.

        :return: A list of all uncompleted tasks in this project.
        :rtype: list of :class:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.add_task('Install PyTodoist')
        >>> uncompleted_tasks = project.get_uncompleted_tasks()
        >>> for task in uncompleted_tasks:
        ...    task.complete()
        """
        all_tasks = self.get_tasks()
        completed_tasks = self.get_completed_tasks()
        return [t for t in all_tasks if t not in completed_tasks]

    def get_completed_tasks(self):
        """Return a list of all completed tasks in this project.

        :return: A list of all completed tasks in this project.
        :rtype: list of :class:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist')
        >>> task.complete()
        >>> completed_tasks = project.get_completed_tasks()
        >>> for task in completed_tasks:
        ...    task.uncomplete()
        """
        self.owner.sync()
        tasks = []
        offset = 0
        while True:
            response = API.get_all_completed_tasks(self.owner.api_token,
                                                   limit=_PAGE_LIMIT,
                                                   offset=offset,
                                                   project_id=self.id)
            _fail_if_contains_errors(response)
            response_json = response.json()
            tasks_json = response_json['items']
            if len(tasks_json) == 0:
                break  # There are no more completed tasks to retreive.
            for task_json in tasks_json:
                project = self.owner.projects[task_json['project_id']]
                tasks.append(Task(task_json, project))
            offset += _PAGE_LIMIT
        return tasks

    def get_tasks(self):
        """Return all tasks in this project.

        :return: A list of all tasks in this project.class
        :rtype: list of :class:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.add_task('Install PyTodoist')
        >>> project.add_task('Have fun!')
        >>> tasks = project.get_tasks()
        >>> for task in tasks:
        ...    print(task.content)
        Install PyTodoist
        Have fun!
        """
        self.owner.sync()
        return [t for t in self.owner.tasks.values()
                if t.project_id == self.id]

    def add_note(self, content):
        """Add a note to the project.

        .. warning:: Requires Todoist premium.

        :param content: The note content.
        :type content: str

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.add_note('Remember to update to the latest version.')
        """
        args = {
            'project_id': self.id,
            'content': content
        }
        _perform_command(self.owner, 'note_add', args)

    def get_notes(self):
        """Return a list of all of the project's notes.

        :return: A list of notes.
        :rtype: list of :class:`pytodoist.todoist.Note`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> notes = project.get_notes()
        """
        self.owner.sync()
        notes = self.owner.notes.values()
        return [n for n in notes if n.project_id == self.id]

    def share(self, email, message=None):
        """Share the project with another Todoist user.

        :param email: The other user's email address.
        :type email: str
        :param message: Optional message to send with the invitation.
        :type message: str

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.share('jane.doe@gmail.com')
        """
        args = {
            'project_id': self.id,
            'email': email,
            'message': message
        }
        _perform_command(self.owner, 'share_project', args)

    def delete_collaborator(self, email):
        """Remove a collaborating user from the shared project.

        :param email: The collaborator's email address.
        :type email: str

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.delete_collaborator('jane.doe@gmail.com')
        """
        args = {
            'project_id': self.id,
            'email': email,
        }
        _perform_command(self.owner, 'delete_collaborator', args)

    def take_ownership(self):
        """Take ownership of the shared project.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.take_ownership()
        """
        args = {
            'project_id': self.id,
        }
        _perform_command(self.owner, 'take_ownership', args)

    def delete(self):
        """Delete the project.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.delete()
        """
        args = {'ids': [self.id]}
        _perform_command(self.owner, 'project_delete', args)
        del self.owner.projects[self.id]


class Task(TodoistObject):
    """A Todoist Task with the following attributes:

    :ivar id: The task ID.
    :ivar content: The task content.
    :ivar due_date_utc: When is the task due (in UTC).
    :ivar date_string: How did the user enter the task? Could be every day
        or every day @ 10. The time should be shown when formating the date if
        @ OR at is found anywhere in the string.
    :ivar project: The parent project.
    :ivar project_id: The ID of the parent project.
    :ivar checked: Is the task checked?
    :ivar priority: The task priority.
    :ivar is_archived: Is the task archived?
    :ivar indent: The task indentation level.
    :ivar labels: A list of attached label names.
    :ivar sync_id: The task sync ID.
    :ivar in_history: Is the task in the task history?
    :ivar user_id: The ID of the user who owns the task.
    :ivar date_added: The date the task was added.
    :ivar children: A list of child tasks.
    :ivar item_order: The task order.
    :ivar collapsed: Is the task collapsed?
    :ivar has_notifications: Does the task have notifications?
    :ivar is_deleted: Has the task been deleted?
    :ivar assigned_by_uid: ID of the user who assigned the task.
    :ivar responsible_uid: ID of the user who responsible for the task.
    """

    _CUSTOM_ATTRS = [
        'project'
    ] + TodoistObject._CUSTOM_ATTRS

    def __init__(self, task_json, project):
        self.id = ''
        self.content = ''
        self.due_date = ''
        self.due_date_utc = ''
        self.date_string = ''
        self.project_id = ''
        self.checked = ''
        self.priority = ''
        self.is_archived = ''
        self.indent = ''
        self.labels = ''
        self.sync_id = ''
        self.in_history = ''
        self.user_id = ''
        self.date_added = ''
        self.children = ''
        self.item_order = ''
        self.collapsed = ''
        self.has_notifications = ''
        self.is_deleted = ''
        self.assigned_by_uid = ''
        self.responsible_uid = ''
        super(Task, self).__init__(task_json)
        self.project = project
        self.to_update = set()

    def update(self):
        """Update the task's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist')
        >>> task.content = 'Install the latest version of PyTodoist'
        ... # At this point Todoist still thinks the content is
        ... # 'Install PyTodoist'
        >>> task.update()
        ... # Now the content has been updated on Todoist.
        """
        args = {attr: getattr(self, attr) for attr in self.to_update}
        args['id'] = self.id
        _perform_command(self.project.owner, 'item_update', args)

    def complete(self):
        """Mark the task complete.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist')
        >>> task.complete()
        """
        args = {
            'id': self.id
        }
        _perform_command(self.project.owner, 'item_close', args)

    def uncomplete(self):
        """Mark the task uncomplete.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist')
        >>> task.uncomplete()
        """
        args = {
            'project_id': self.project.id,
            'ids': [self.id]
        }
        owner = self.project.owner
        _perform_command(owner, 'item_uncomplete', args)

    def add_note(self, content):
        """Add a note to the Task.

        .. warning:: Requires Todoist premium.

        :param content: The content of the note.
        :type content: str
        :return: The added note.
        :rtype: :class:`pytodoist.todoist.Note`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install Todoist.')
        >>> note = task.add_note('https://pypi.python.org/pypi')
        >>> print(note.content)
        https://pypi.python.org/pypi
        """
        args = {
            'item_id': self.id,
            'content': content
        }
        _perform_command(self.project.owner, 'note_add', args)

    def get_notes(self):
        """Return all notes attached to this Task.

        :return: A list of all notes attached to this Task.
        :rtype: list of :class:`pytodoist.todoist.Note`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist.')
        >>> task.add_note('https://pypi.python.org/pypi')
        >>> notes = task.get_notes()
        >>> print(len(notes))
        1
        """
        owner = self.project.owner
        owner.sync()
        return [n for n in owner.notes.values() if n.item_id == self.id]

    def move(self, project):
        """Move this task to another project.

        :param project: The project to move the task to.
        :type project: :class:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist')
        >>> print(task.project.name)
        PyTodoist
        >>> inbox = user.get_project('Inbox')
        >>> task.move(inbox)
        >>> print(task.project.name)
        Inbox
        """
        args = {
            'project_items': {self.project.id: [self.id]},
            'to_project': project.id
        }
        _perform_command(self.project.owner, 'item_move', args)
        self.project = project

    def add_date_reminder(self, service, due_date):
        """Add a reminder to the task which activates on a given date.

        .. warning:: Requires Todoist premium.

        :param service: ```email```, ```sms``` or ```push``` for mobile.
        :type service: str
        :param due_date: The due date in UTC, formatted as
            ```YYYY-MM-DDTHH:MM```
        :type due_date: str

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist')
        >>> task.add_date_reminder('email', '2015-12-01T09:00')
        """
        args = {
            'item_id': self.id,
            'service': service,
            'type': 'absolute',
            'due_date_utc': due_date
        }
        _perform_command(self.project.owner, 'reminder_add', args)

    def add_location_reminder(self, service, name, lat, long, trigger, radius):
        """Add a reminder to the task which activates on at a given location.

        .. warning:: Requires Todoist premium.

        :param service: ```email```, ```sms``` or ```push``` for mobile.
        :type service: str
        :param name: An alias for the location.
        :type name: str
        :param lat: The location latitude.
        :type lat: float
        :param long: The location longitude.
        :type long: float
        :param trigger: ```on_enter``` or ```on_leave```.
        :type trigger: str
        :param radius: The radius around the location that is still considered
            the location.
        :type radius: float

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist')
        >>> task.add_location_reminder('email', 'Leave Glasgow',
        ...                            55.8580, 4.2590, 'on_leave', 100)
        """
        args = {
            'item_id': self.id,
            'service': service,
            'type': 'location',
            'name': name,
            'loc_lat': lat,
            'loc_long': long,
            'loc_trigger': trigger,
            'radius': radius
        }
        _perform_command(self.project.owner, 'reminder_add', args)

    def get_reminders(self):
        """Return a list of the task's reminders.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist')
        >>> task.add_date_reminder('email', '2015-12-01T09:00')
        >>> reminders = task.get_reminders()
        """
        owner = self.project.owner
        return [r for r in owner.get_reminders() if r.id == self.id]

    def delete(self):
        """Delete the task.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = project.add_task('Read Chapter 4')
        >>> task.delete()
        """
        args = {'ids': [self.id]}
        _perform_command(self.project.owner, 'item_delete', args)
        del self.project.owner.tasks[self.id]


class Note(TodoistObject):
    """A Todoist note with the following attributes:

    :ivar id: The note ID.
    :ivar content: The note content.
    :ivar item_id: The ID of the task it is attached to.
    :ivar task: The task it is attached to.
    :ivar posted: The date/time the note was posted.
    :ivar is_deleted: Has the note been deleted?
    :ivar is_archived: Has the note been archived?
    :ivar posted_uid: The ID of the user who attached the note.
    :ivar uids_to_notify: List of user IDs to notify.
    """

    _CUSTOM_ATTRS = [
        'task'
    ] + TodoistObject._CUSTOM_ATTRS

    def __init__(self, note_json, task):
        self.id = ''
        self.content = ''
        self.item_id = ''
        self.posted = ''
        self.is_deleted = ''
        self.is_archived = ''
        self.posted_uid = ''
        self.uids_to_notify = ''
        super(Note, self).__init__(note_json)
        self.task = task
        self.to_update = set()

    def update(self):
        """Update the note's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = project.add_task('Install PyTodoist.')
        >>> note = task.add_note('https://pypi.python.org/pypi')
        >>> note.content = 'https://pypi.python.org/pypi/pytodoist'
        ... # At this point Todoist still thinks the content is the old URL.
        >>> note.update()
        ... # Now the content has been updated on Todoist.
        """
        args = {attr: getattr(self, attr) for attr in self.to_update}
        args['id'] = self.id
        owner = self.task.project.owner
        _perform_command(owner, 'note_update', args)

    def delete(self):
        """Delete the note, removing it from it's task.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist.')
        >>> note = task.add_note('https://pypi.python.org/pypi')
        >>> note.delete()
        >>> notes = task.get_notes()
        >>> print(len(notes))
        0
        """
        args = {'id': self.id}
        owner = self.task.project.owner
        _perform_command(owner, 'note_delete', args)


class Label(TodoistObject):
    """A Todoist label with the following attributes:

    :ivar id: The ID of the label.
    :ivar name: The label name.
    :ivar color: The color of the label.
    :ivar owner: The user who owns the label.
    :ivar is_deleted: Has the label been deleted?

    .. warning:: Requires Todoist premium.
    """

    _CUSTOM_ATTRS = [
        'owner'
    ] + TodoistObject._CUSTOM_ATTRS

    def __init__(self, label_json, owner):
        self.id = ''
        self.uid = ''
        self.name = ''
        self.color = ''
        self.is_deleted = ''
        super(Label, self).__init__(label_json)
        self.owner = owner
        self.to_update = set()

    def update(self):
        """Update the label's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> label = user.add_label('family')
        >>> label.name = 'friends'
        ... # At this point Todoist still thinks the name is 'family'.
        >>> label.update()
        ... # Now the name has been updated on Todoist.
        """
        args = {attr: getattr(self, attr) for attr in self.to_update}
        args['id'] = self.id
        _perform_command(self.owner, 'label_update', args)

    def delete(self):
        """Delete the label.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> label = user.add_label('family')
        >>> label.delete()
        """
        args = {'id': self.id}
        _perform_command(self.owner, 'label_update', args)


class Filter(TodoistObject):
    """A Todoist filter with the following attributes:

    :ivar id: The ID of the filter.
    :ivar name: The filter name.
    :ivar query: The filter query.
    :ivar color: The color of the filter.
    :ivar item_order: The order of the filter in the filters list.
    :ivar owner: The user who owns the label.
    """

    _CUSTOM_ATTRS = [
        'owner'
    ] + TodoistObject._CUSTOM_ATTRS

    def __init__(self, filter_json, owner):
        self.id = ''
        self.name = ''
        self.query = ''
        self.color = ''
        self.item_order = ''
        super(Filter, self).__init__(filter_json)
        self.owner = owner
        self.to_update = set()

    def update(self):
        """Update the filter's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> overdue_filter = user.add_filter('Overdue', todoist.Query.OVERDUE)
        >>> overdue_filter.name = 'OVERDUE!'
        ... # At this point Todoist still thinks the name is 'Overdue'.
        >>> overdue_filter.update()
        ... # Now the name has been updated on Todoist.
        """
        args = {attr: getattr(self, attr) for attr in self.to_update}
        args['id'] = self.id
        _perform_command(self.owner, 'filter_update', args)

    def delete(self):
        """Delete the filter.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> overdue_filter = user.add_filter('Overdue', todoist.Query.OVERDUE)
        >>> overdue_filter.delete()
        """
        args = {'id': self.id}
        _perform_command(self.owner, 'filter_delete', args)


class Reminder(TodoistObject):
    """A Todoist reminder with the following attributes:

    :ivar id: The ID of the filter.
    :ivar item_id: The ID of the associated task.
    :ivar service: ```email```, ```sms``` or ```push``` for mobile.
    :ivar due_date_utc: The due date in UTC.
    :ivar date_string: The due date in free form text e.g. ```every day @ 10```
    :ivar date_lang: The language of the date_string.
    :ivar notify_uid: The ID of the user who should be notified.
    :ivar task: The task associated with the reminder.
    """

    _CUSTOM_ATTRS = [
        'task'
    ] + TodoistObject._CUSTOM_ATTRS

    def __init__(self, reminder_json, task):
        self.id = ''
        self.item_id = ''
        self.service = ''
        self.type = ''
        self.due_date_utc = ''
        self.date_string = ''
        self.date_lang = ''
        self.notify_uid = ''
        super(Reminder, self).__init__(reminder_json)
        self.task = task
        self.to_update = set()

    def delete(self):
        """Delete the reminder.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist')
        >>> task.add_date_reminder('email', '2015-12-01T09:00')
        >>> for reminder in task.get_reminders():
        ...     reminder.delete()
        """
        args = {'id': self.id}
        owner = self.task.project.owner
        _perform_command(owner, 'reminder_delete', args)


class Color(object):
    """This class acts as an easy way to specify Todoist project
    colors.

    >>> from pytodoist import todoist
    >>> user = todoist.login('john.doe@gmail.com', 'password')
    >>> user.add_project('PyTodoist', color=todoist.Color.RED)

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
    >>> inbox.add_task('Install PyTodoist', priority=todoist.Priority.HIGH)

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
        * BIZ_TRIAL_WILL_END
        * BIZ_TRIAL_ENTER_CC
        * BIZ_ACCOUNT_DISABLED
        * BIZ_INVITATION_REJECTED
        * BIZ_INVITATION_ACCEPTED
        * BIZ_PAYMENT_FAILED
    """
    USER_LEFT_PROJECT = 'user_left_project'
    USER_REMOVED_FROM_PROJECT = 'user_removed_from_project'
    ITEM_COMPLETED = 'item_completed'
    ITEM_UNCOMPLETED = 'item_uncompleted'
    ITEM_ASSIGNED = 'item_assigned'
    SHARE_INVITATION_REJECTED = 'share_invitation_rejected'
    SHARE_NOTIFICATION_ACCEPTED = 'share_notification_accepted'
    NOTE_ADDED = 'note_added'
    BIZ_TRIAL_WILL_END = 'biz_trial_will_end'
    BIZ_TRIAL_ENTER_CC = 'biz_trial_enter_cc'
    BIZ_ACCOUNT_DISABLED = 'biz_account_disabled'
    BIZ_INVITATION_REJECTED = 'biz_invitation_rejected'
    BIZ_INVITATION_ACCEPTED = 'biz_invitation_accepted'
    BIZ_PAYMENT_FAILED = 'biz_payment_failed'


class Query(object):
    """This class acts as an easy way to specify search queries.

    >>> from pytodoist import todoist
    >>> user = todoist.login('john.doe@gmail.com', 'password')
    >>> tasks = user.search_tasks(todoist.Query.TOMORROW,
    ...                           todoist.Query.SUNDAY)

    The supported queries:
        * ALL
        * TODAY
        * TOMORROW
        * MONDAY
        * TUESDAY
        * WEDNESDAY
        * THURSDAY
        * FRIDAY
        * SATURDAY
        * SUNDAY
        * NO_DUE_DATE
        * OVERDUE
        * PRIORITY_1
        * PRIORITY_2
        * PRIORITY_3
    """
    ALL = 'viewall'
    TODAY = 'today'
    TOMORROW = 'tomorrow'
    MONDAY = 'mon'
    TUESDAY = 'tue'
    WEDNESDAY = 'wed'
    THURSDAY = 'thu'
    FRIDAY = 'fri'
    SATURDAY = 'sat'
    SUNDAY = 'sun'
    NO_DUE_DATE = 'no due date'
    OVERDUE = 'overdue'
    PRIORITY_1 = 'p1'
    PRIORITY_2 = 'p2'
    PRIORITY_3 = 'p3'


class RequestError(Exception):
    """Will be raised whenever a Todoist API call fails."""

    def __init__(self, response):
        self.response = response
        super(RequestError, self).__init__(response.text)
