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
    return _login(API.login, email, password)


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
    response = API.sync(api_token, 0, '["user"]')
    _fail_if_contains_errors(response)
    user_json = response.json()['User']
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
    if sync_uuid and 'SyncStatus' in response_json:
        status = response_json['SyncStatus']
        if sync_uuid in status and 'error' in status[sync_uuid]:
            raise RequestError(response)


def _gen_uuid():
    """Return a randomly generated UUID string."""
    return str(uuid.uuid4())


def _perform_command(user, command_type, command_args):
    command_uuid = _gen_uuid()
    command = {
        'type': command_type,
        'args': command_args,
        'uuid': command_uuid,
        'temp_id': _gen_uuid()
    }
    commands = json.dumps([command])
    response = API.sync(user.api_token, user.api_seq_no, commands=commands)
    _fail_if_contains_errors(response, command_uuid)
    return response.json()['seq_no']


class TodoistObject(object):
    """A helper class which 'converts' a JSON object into a python object."""

    _CUSTOM_ATTRS = [
        'to_update',
    ]

    def __init__(self, object_json):
        for attr in object_json:
            setattr(self, attr, object_json[attr])

    def __setattr__(self, key, value):
        if hasattr(self, 'to_update') and key not in self._CUSTOM_ATTRS:
            self.to_update.add(key)
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
    :ivar timezone: The user's chosen timezone.
    :ivar tz_offset: The user's timezone offset.
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
    :ivar has_push_reminders: Does the user have a push reminder enabled?
    :ivar default_reminder: ``email`` for email, ``mobile`` for SMS,
        ``push`` for smart device notifications or ``no_default`` to
        turn off notifications. Only for premium users.
    :ivar inbox_project: The ID of the user's Inbox project.
    :ivar team_inbox: The ID of the user's team Inbox project.
    :ivar api_token: The user's API token.
    :ivar shard_id: The user's shard ID.
    :ivar seq_no: The user's sequence number.
    :ivar beta: The user's beta status.
    :ivar image_id: The ID of the user's avatar.
    :ivar is_biz_admin: Is the user a business administrator?
    :ivar last_used_ip: The IP address of the computer last used to login.
    :ivar is_dummy: Is this a real or a dummy user?
    :ivar auto_reminder: The auto reminder of the user.
    :ivar guide_mode: The guide mode of the user.
    """

    _CUSTOM_ATTRS = [
        'projects',
        'tasks',
        'notes',
        'labels',
        'password',
        'api_seq_no',
    ] + TodoistObject._CUSTOM_ATTRS

    def __init__(self, user_json):
        self.id = ''
        self.email = ''
        self.full_name = ''
        self.join_date = ''
        self.is_premium = False
        self.premium_until = ''
        self.timezone = ''
        self.tz_offset = ''
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
        self.has_push_reminders = False
        self.default_reminder = ''
        self.inbox_project = ''
        self.team_inbox = ''
        self.api_token = ''
        self.shard_id = ''
        self.seq_no = ''
        self.beta = ''
        self.image_id = ''
        self.is_biz_admin = False
        self.last_used_ip = ''
        self.is_dummy = False
        self.auto_reminder = ''
        self.guide_mode = ''
        super(User, self).__init__(user_json)
        self.password = ''
        self.projects = {}
        self.tasks = {}
        self.notes = {}
        self.labels = {}
        self.filters = {}
        self.api_seq_no = 0
        self.sync()
        self.to_update = set()

    def sync(self, resource_types='["all"]'):
        response = API.sync(self.api_token, self.api_seq_no, resource_types)
        _fail_if_contains_errors(response)
        response_json = response.json()
        self.api_seq_no = response_json['seq_no']
        projects_json = response_json.get('Projects', [])
        for project_json in projects_json:
            project_id = project_json['id']
            self.projects[project_id] = Project(project_json, self)
        items_json = response_json.get('Items', [])
        for task_json in items_json:
            task_id = task_json['id']
            project_id = task_json['project_id']
            project = self.projects[project_id]
            self.tasks[task_id] = Task(task_json, project)
        notes_json = response_json.get('Notes', [])
        for note_json in notes_json:
            note_id = note_json['id']
            task_id = note_json['item_id']
            task = self.tasks[task_id]
            self.notes[note_id] = Note(note_json, task)
        labels_json = response_json.get('Labels', [])
        for label_json in labels_json:
            label_id = label_json['id']
            self.labels[label_id] = Label(label_json, self)
        filters_json = response_json.get('Filters', [])
        for filter_json in filters_json:
            filter_id = filter_json['id']
            self.filters[filter_id] = Filter(filter_json, self)

    def update(self):
        args = {attr: getattr(self, attr) for attr in self.to_update}
        self.api_seq_no = _perform_command(self, 'user_update', args)

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
        # Possible bug in Todoist API returns a status code of 400 even
        # if the user is deleted.
        if response.status_code != 400:
            _fail_if_contains_errors(response)

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

    def add_project(self, name):
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
            'name': name
        }
        self.api_seq_no = _perform_command(self, 'project_add', args)
        return self.get_project(name)

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

    def add_label(self, name, color=None):
        """Create a new label.

        :param name: The name of the label.
        :type name: str
        :param color: The color of the label.
        :type color: str
        :rtype: :class:`pytodoist.todoist.Label`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> label = user.add_label('family')
        """
        args = {
            'name': name,
            'color': color
        }
        self.api_seq_no = _perform_command(self, 'label_register', args)
        return self.get_label(name)

    def get_notes(self):
        self.sync()
        return list(self.notes.values())

    def add_filter(self, name, query, color=None, item_order=None):
        args = {
            'name': name,
            'query': query,
            'color': color,
            'item_order': item_order
        }
        self.api_seq_no = _perform_command(self, 'filter_add', args)
        return self.get_filter(name)

    def get_filter(self, name):
        for flter in self.get_filters():
            if flter.name == name:
                return flter

    def get_filters(self):
        self.sync()
        return list(self.filters.values())

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
        response = API.get_productivity_stats(self.api_token)
        _fail_if_contains_errors(response)
        return response.json()


class Project(TodoistObject):
    """A Todoist Project with the following attributes:

    :ivar id: The ID of the project.
    :ivar name: The name of the project.
    :ivar color: The color of the project.
    :ivar collapsed: Is this project collapsed?
    :ivar owner: The owner of the project.
    :ivar last_updated: When the project was last updated.
    :ivar user_id: The user ID of the owner.
    :ivar cache_count: The cache count of the project.
    :ivar item_order: The task ordering.
    :ivar indent: The indentation level of the project.
    :ivar is_deleted: Has this project been deleted?
    :ivar is_archived: Is this project archived?
    :ivar archived_date: The date on which the project was archived.
    :ivar archived_timestamp: The timestamp of the project archiving.
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
        self.owner.api_seq_no = _perform_command(self.owner,
                                                 'project_update', args)

    def archive(self):
        args = {'id': self.id}
        self.owner.api_seq_no = _perform_command(self.owner,
                                                 'project_archive', args)

    def unarchive(self):
        args = {'id': self.id}

        self.owner.api_seq_no = _perform_command(self.owner,
                                                 'project_unarchive', args)

    def delete(self):
        """Delete the project.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.delete()
        """
        args = {'ids': [self.id]}
        self.owner.api_seq_no = _perform_command(self.owner,
                                                 'project_delete', args)

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
        return list(self.owner.tasks.values())

    def get_uncompleted_tasks(self):
        """Return a list of all uncompleted tasks in this project.

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
        response = API.get_all_completed_tasks(self.owner.api_token,
                                               project_id=self.id)
        _fail_if_contains_errors(response)
        tasks_json = response.json()['Items']
        return [self.owner.tasks[task['id']] for task in tasks_json]

    def add_note(self, content):
        args = {
            'project_id': self.id,
            'content': content
        }
        self.owner.api_seq_no = _perform_command(self.owner, 'note_add', args)

    def get_notes(self):
        self.owner.sync()
        notes = self.owner.notes.values()
        return [n for n in notes if n.project_id == self.id]

    def share(self, email, message=None):
        args = {
            'project_id': self.id,
            'email': email,
            'message': message
        }
        self.owner.api_seq_no = _perform_command(self.owner,
                                                 'share_project', args)

    def delete_collaborator(self, email):
        args = {
            'project_id': self.id,
            'email': email,
        }
        self.owner.api_seq_no = _perform_command(self.owner,
                                                 'delete_collaborator', args)

    def take_ownership(self):
        args = {
            'project_id': self.id,
        }
        self.owner.api_seq_no = _perform_command(self.owner,
                                                 'take_ownership', args)


class Task(TodoistObject):
    """A Todoist Task with the following attributes:

    :ivar id: The task ID.
    :ivar content: The task content.
    :ivar due_date: When is the task due?
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
        self.checked = False
        self.priority = ''
        self.is_archived = False
        self.indent = ''
        self.labels = ''
        self.sync_id = ''
        self.in_history = False
        self.user_id = ''
        self.date_added = ''
        self.children = ''
        self.item_order = ''
        self.collapsed = False
        self.has_notifications = False
        self.is_deleted = False
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
        self.project.owner.api_seq_no = _perform_command(self.project.owner,
                                                         'item_update', args)

    def delete(self):
        """Delete the task.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = project.add_task('Read Chapter 4')
        >>> task.delete()
        """
        args = {'ids': [self.id]}
        self.project.owner.api_seq_no = _perform_command(self.project.owner,
                                                         'item_delete', args)

    def complete(self):
        """Mark the task complete.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist')
        >>> task.complete()
        """
        args = {
            'project_id': self.project.id,
            'ids': [self.id]
        }
        self.project.owner.api_seq_no = _perform_command(self.project.owner,
                                                         'item_complete', args)

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
        owner.api_seq_no = _perform_command(owner, 'item_uncomplete', args)

    def add_note(self, content):
        """Add a note to the Task.

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
        self.project.owner.api_seq_no = _perform_command(self.project.owner,
                                                         'note_add', args)

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
        self.project.owner.api_seq_no = _perform_command(self.project.owner,
                                                         'item_move', args)
        self.project = project


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
        self.is_deleted = False
        self.is_archived = False
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
        owner.api_seq_no = _perform_command(owner, 'note_update', args)

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
        owner.api_seq_no = _perform_command(owner, 'note_delete', args)


class Label(TodoistObject):
    """A Todoist label with the following attributes:

    :ivar id: The ID of the label.
    :ivar uid: The UID of the label.
    :ivar name: The label name.
    :ivar color: The color of the label.
    :ivar owner: The user who owns the label.
    :ivar is_deleted: Has the label been deleted?
    """

    _CUSTOM_ATTRS = [
        'owner'
    ] + TodoistObject._CUSTOM_ATTRS

    def __init__(self, label_json, owner):
        self.id = ''
        self.uid = ''
        self.name = ''
        self.color = ''
        self.is_deleted = True
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
        self.owner.api_seq_no = _perform_command(self.owner,
                                                 'label_update', args)

    def delete(self):
        """Delete the label.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> label = user.add_label('family')
        >>> label.delete()
        """
        args = {'id': self.id}
        self.owner.api_seq_no = _perform_command(self.owner,
                                                 'label_update', args)


class Filter(TodoistObject):

    _CUSTOM_ATTRS = [
        'owner'
    ] + TodoistObject._CUSTOM_ATTRS

    def __init__(self, filter_json, owner):
        self.id = ''
        self.name = ''
        self.item_order = ''
        self.color = ''
        self.query = ''
        super(Filter, self).__init__(filter_json)
        self.owner = owner
        self.to_update = set()

    def update(self):
        args = {attr: getattr(self, attr) for attr in self.to_update}
        args['id'] = self.id
        self.owner.api_seq_no = _perform_command(self.owner,
                                                 'filter_update', args)

    def delete(self):
        args = {'id': self.id}
        self.owner.api_seq_no = _perform_command(self.owner,
                                                 'filter_delete', args)


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
    OVERDUE = 'over due'
    PRIORITY_1 = 'p1'
    PRIORITY_2 = 'p2'
    PRIORITY_3 = 'p3'


class RequestError(Exception):
    """Will be raised whenever a Todoist API call fails."""

    def __init__(self, response):
        self.response = response
        super(RequestError, self).__init__(response.text)
