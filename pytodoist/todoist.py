"""This module introduces abstractions over Todoist entities such as Users,
Tasks and Projects. It's purpose is to hide the underlying API calls so that
you can interact with Todoist in a straightforward manner.

*Example:*

>>> from pytodoist import todoist
>>> user = todoist.register('John Doe', 'john.doe@gmail.com', 'password')
>>> user.is_logged_in()
True
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
import itertools
from pytodoist.api import TodoistAPI

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
    >>> print(user.is_logged_in())
    True
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
    >>> print(user.is_logged_in())
    True
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
    >>> print(user.is_logged_in())
    True
    """
    return _login(API.update_user, api_token)


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
    >>> print(user.is_logged_in())
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
    >>> print(user.is_logged_in())
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
    :rtype: list of str

    >>> from pytodoist import todoist
    >>> print(todoist.get_timezones())
    [u'US/Hawaii', u'US/Alaska', u'US/Pacific', u'US/Arizona, ...]
    """
    response = API.get_timezones()
    _fail_if_contains_errors(response)
    timezones_json = response.json()
    return [timezone_json[0] for timezone_json in timezones_json]


def _fail_if_contains_errors(response):
    """Raise a RequestError Exception if a given response
    does not denote a successful request.
    """
    if not API.is_response_success(response):
        raise RequestError(response)


class TodoistObject(object):
    """A helper class which 'converts' a JSON object into a python object."""

    def __init__(self, object_json):
        for attr in object_json:
            setattr(self, attr, object_json[attr])


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
    :ivar token: The user's secret token.
    :ivar api_token: The user's API token.
    :ivar shard_id: The user's shard ID.
    :ivar seq_no: The user's sequence number.
    :ivar beta: The user's beta status.
    :ivar image_id: The ID of the user's avatar.
    :ivar is_biz_admin: Is the user a business administrator?
    :ivar last_used_ip: The IP address of the computer last used to login.
    :ivar is_dummy: Is this a real or a dummy user?
    """

    def __init__(self, user_json):
        self.id = None
        self.email = None
        self.password = None
        self.full_name = None
        self.join_date = None
        self.is_premium = None
        self.premium_until = None
        self.timezone = None
        self.tz_offset = None
        self.time_format = None
        self.date_format = None
        self.start_page = None
        self.start_day = None
        self.next_week = None
        self.sort_order = None
        self.mobile_number = None
        self.mobile_host = None
        self.business_account_id = None
        self.karma = None
        self.karma_trend = None
        self.has_push_reminders = None
        self.default_reminder = None
        self.inbox_project = None
        self.team_inbox = None
        self.token = None
        self.api_token = None
        self.shard_id = None
        self.seq_no = None
        self.beta = None
        self.image_id = None
        self.is_biz_admin = None
        self.last_used_ip = None
        self.is_dummy = None
        super(User, self).__init__(user_json)

    def is_logged_in(self):
        """Return ``True`` if the user is logged in.

        A user is logged in if it's token is valid.

        :return: ``True`` if the user token is valid, ``False`` otherwise.
        :rtype: bool

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> print(user.is_logged_in())
        True
        >>> user.delete()
        >>> print(user.is_logged_in())
        False
        """
        if not self.token:
            return False
        response = API.ping(self.token)
        return API.is_response_success(response)

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

        :param image_file: The path to the image.
        :type image_file: str

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> user.change_avatar('/home/john/pictures/avatar.png')
        """
        with open(image_file) as image:
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
        response = API.get_redirect_link(self.token)
        _fail_if_contains_errors(response)
        link_json = response.json()
        return link_json['link']

    def add_project(self, name, color=None, indent=None, order=None):
        """Add a project to the user's account.

        :param name: The project name.
        :type name: str
        :param color: The project color.
        :type color: int
        :param indent: The project indentation.
        :type indent: int
        :param order: The project ordering.
        :type order: int
        :return: The project that was added.
        :rtype: :class:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.add_project('PyTodoist')
        >>> print(project.name)
        PyTodoist
        """
        response = API.add_project(self.token, name,
                                   color=color, indent=indent, order=order)
        _fail_if_contains_errors(response)
        project_json = response.json()
        return Project(project_json, self)

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
        response = API.get_projects(self.token)
        _fail_if_contains_errors(response)
        projects_json = response.json()
        return [Project(project_json, self) for project_json in projects_json]

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
        response = API.get_archived_projects(self.token)
        archived_project_info = response.json()
        archived_project_ids = (info['id'] for info in archived_project_info)
        archived_projects = []
        for project_id in archived_project_ids:
            project = self.get_project_with_id(project_id)
            archived_projects.append(project)
        return archived_projects

    def get_project_with_id(self, project_id):
        """Return the project with a given ID.

        :param project_id: The ID to search for.
        :type project_id: str
        :return: The project that has the ID ``project_id``.
        :rtype: :class:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> inbox = user.get_project('Inbox')
        >>> project = user.get_project_with_id(inbox.id)
        >>> print(project.name)
        Inbox
        """
        response = API.get_project(self.token, project_id)
        _fail_if_contains_errors(response)
        project_json = response.json()
        return Project(project_json, self)

    def update_project_orders(self, projects):
        """Update the order in which projects are displayed on Todoist.

        :param projects: A list of projects in the order to be displayed.
        :type projects: list :class:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> projects = user.get_projects()
        >>> for project in projects:
        ...    print(project.name)
        PyTodoist
        Homework
        >>> rev_projects = projects[::-1]
        >>> user.update_project_orders(rev_projects)
        >>> projects = user.get_projects()
        >>> for project in projects:
        ...    print(project.name)
        Homework
        PyTodoist
        """
        project_ids = str([project.id for project in projects])
        response = API.update_project_orders(self.token, project_ids)
        _fail_if_contains_errors(response)

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

    def search_completed_tasks(self, limit=None, from_date=None):
        """Return a filtered list of a user's completed tasks.

        .. warning:: Requires the user to have Todoist premium.

        :param limit: The maximum number of tasks to return (default ``30``).
        :type limit: int
        :param from_date: Return tasks with a completion date on or older than
            from_date. Formatted as ``2007-4-29T10:13``.
        :type from_date: str
        :return: A list of tasks that meet the search criteria. If the user
            does not have Todoist premium an empty list is returned.
        :rtype: list of :class:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> completed_tasks = user.search_completed_tasks(limit=5)
        >>> for task in completed_tasks:
        ...     task.uncomplete()
        """
        response = API.get_all_completed_tasks(self.token, limit=limit,
                                               from_date=from_date)
        _fail_if_contains_errors(response)
        tasks_json = response.json()['items']
        tasks = []
        for task_json in tasks_json:
            project_id = task_json['project_id']
            project = self.get_project_with_id(project_id)
            tasks.append(Task(task_json, project))
        return tasks

    def get_tasks(self):
        """Return all of a user's tasks, regardless of completion state.

        :return: A list of all of a user's tasks.
        :rtype: list of :class:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> tasks = user.get_tasks()
        """
        return self.get_uncompleted_tasks() + self.get_completed_tasks()

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
        response = API.search_tasks(self.token, queries)
        _fail_if_contains_errors(response)
        query_results = response.json()
        tasks = []
        for result in query_results:
            if not 'data' in result:
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
                project = self.get_project_with_id(project_id)
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
        response = API.get_labels(self.token)
        _fail_if_contains_errors(response)
        labels_json = list(response.json().values())
        return [Label(label_json, self) for label_json in labels_json]

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
        response = API.add_label(self.token, name, color=color)
        _fail_if_contains_errors(response)
        label_json = response.json()
        return Label(label_json, self)

    def _get_notification_settings(self):
        """Return a list of all notification settings.

        :return: A JSON representation of the settings.
        :rtype: dict
        """
        response = API.get_notification_settings(self.token)
        _fail_if_contains_errors(response)
        return response.json()

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
        response = API.update_notification_settings(self.token, event,
                                                    service, should_notify)
        _fail_if_contains_errors(response)

    def is_email_notified_when(self, event):
        """Find out if a user is receiving emails for a given
        event.

        :param event: The type of the notification.
        :type event: str
        :return: ``True`` if the user's settings allow for emails,
            ``False`` otherwise.
        :rtype: bool

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> print(user.is_email_notified_when(todoist.Event.NOTE_ADDED))
        True
        """
        notification_settings = self._get_notification_settings()
        return notification_settings[event]['notify_email']

    def is_push_notified_when(self, event):
        """Find out if a user is receiving push notifications for
        a given event.

        :param event: The type of the notification.
        :type event: str
        :return: ``True`` if the user's settings allow for push
            notifications, ``False`` otherwise.
        :rtype: bool

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> print(user.is_push_notified_when(todoist.Event.NOTE_ADDED))
        True
        """
        notification_settings = self._get_notification_settings()
        return notification_settings[event]['notify_push']

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

    def __init__(self, project_json, owner):
        self.id = None
        self.name = None
        self.color = None
        self.collapsed = None
        self.owner = owner
        self.last_updated = None
        self.user_id = None
        self.cache_count = None
        self.item_order = None
        self.indent = None
        self.is_deleted = None
        self.is_archived = None
        self.archived_date = None
        self.archived_timestamp = None
        self.inbox_project = None
        super(Project, self).__init__(project_json)

    def delete(self):
        """Delete the project.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
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
        >>> project = user.get_project('PyTodoist')
        >>> project.name = 'Homework'
        ... # At this point Todoist still thinks the name is 'PyTodoist'.
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
        >>> project = user.get_project('PyTodoist')
        >>> project.archive()
        """
        response = API.archive_project(self.owner.token, self.id)
        _fail_if_contains_errors(response)

    def unarchive(self):
        """Unarchive the project.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.unarchive()
        """
        response = API.unarchive_project(self.owner.token, self.id)
        _fail_if_contains_errors(response)

    def collapse(self):
        """Collapse the project on Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> project.collapse()
        """
        response = API.update_project(self.owner.token, self.id, collapsed=1)
        _fail_if_contains_errors(response)

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
        response = API.add_task(self.owner.token, content, project_id=self.id,
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
        return self.get_uncompleted_tasks() + self.get_completed_tasks()

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
        response = API.get_uncompleted_tasks(self.owner.token, self.id)
        _fail_if_contains_errors(response)
        tasks_json = response.json()
        return [Task(task_json, self) for task_json in tasks_json]

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
        response = API.get_completed_tasks(self.owner.token, self.id)
        _fail_if_contains_errors(response)
        tasks_json = response.json()
        return [Task(task_json, self) for task_json in tasks_json]

    def update_task_orders(self, tasks):
        """Update the order in which tasks are displayed on Todoist.

        :param tasks: A list of tasks in the order to be displayed.
        :type tasks: list :class:`pytodoist.todoist.Task`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> tasks = project.get_tasks()
        >>> rev_tasks = tasks[::-1]
        >>> project.update_task_orders(rev_tasks)
        """
        task_ids = str([task.id for task in tasks])
        response = API.update_task_ordering(self.owner.token,
                                            self.id, task_ids)
        _fail_if_contains_errors(response)


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

    def __init__(self, task_json, project):
        self.id = None
        self.content = None
        self.due_date = None
        self.due_date_utc = None
        self.date_string = None
        self.project = project
        self.project_id = None
        self.checked = None
        self.priority = None
        self.is_archived = None
        self.indent = None
        self.labels = None
        self.sync_id = None
        self.in_history = None
        self.user_id = None
        self.date_added = None
        self.children = None
        self.item_order = None
        self.collapsed = None
        self.has_notifications = None
        self.is_deleted = None
        self.assigned_by_uid = None
        self.responsible_uid = None
        super(Task, self).__init__(task_json)

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
        response = API.update_task(self.project.owner.token, self.id,
                                   **self.__dict__)
        _fail_if_contains_errors(response)

    def delete(self):
        """Delete the task.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('Homework')
        >>> task = project.add_task('Read Chapter 4')
        >>> task.delete()
        """
        task_ids = '[{id}]'.format(id=self.id)
        response = API.delete_tasks(self.project.owner.token, task_ids)
        _fail_if_contains_errors(response)

    def complete(self):
        """Mark the task complete.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist')
        >>> task.complete()
        """
        task_ids = '[{id}]'.format(id=self.id)
        response = API.complete_tasks(self.project.owner.token, task_ids)
        _fail_if_contains_errors(response)

    def uncomplete(self):
        """Mark the task uncomplete.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist')
        >>> task.uncomplete()
        """
        task_ids = '[{id}]'.format(id=self.id)
        response = API.uncomplete_tasks(self.project.owner.token, task_ids)
        _fail_if_contains_errors(response)

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
        response = API.add_note(self.project.owner.token, self.id, content)
        _fail_if_contains_errors(response)
        note_json = response.json()
        return Note(note_json, self)

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
        response = API.get_notes(self.project.owner.token, self.id)
        _fail_if_contains_errors(response)
        notes_json = response.json()
        return [Note(note_json, self) for note_json in notes_json]

    def advance_recurring_date(self):
        """Advance the recurring date of this task.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> project = user.get_project('PyTodoist')
        >>> task = project.add_task('Install PyTodoist', date='today')
        >>> print(task.due_date)
        Sun 09 Mar 2014 19:54:01 +0000
        >>> task.advance_recurring_date()
        >>> print(task.due_date)
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
        current_pos = '{{"{p_id}":["{t_id}"]}}'.format(p_id=self.project.id,
                                                       t_id=self.id)
        response = API.move_tasks(self.project.owner.token, current_pos,
                                  project.id)
        _fail_if_contains_errors(response)
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

    def __init__(self, note_json, task):
        self.id = None
        self.content = None
        self.item_id = None
        self.task = task
        self.posted = None
        self.is_deleted = None
        self.is_archived = None
        self.posted_uid = None
        self.uids_to_notify = None
        super(Note, self).__init__(note_json)

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
        response = API.update_note(self.task.project.owner.token, self.id,
                                   self.content)
        _fail_if_contains_errors(response)

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
        response = API.delete_note(self.task.project.owner.token,
                                   self.task.id, self.id)
        _fail_if_contains_errors(response)


class Label(TodoistObject):
    """A Todoist label with the following attributes:

    :ivar id: The ID of the label.
    :ivar uid: The UID of the label.
    :ivar name: The label name.
    :ivar color: The color of the label.
    :ivar owner: The user who owns the label.
    :ivar is_deleted: Has the label been deleted?
    """

    def __init__(self, label_json, owner):
        self.id = None
        self.uid = None
        self.name = None
        self.color = None
        self.owner = owner
        self.is_deleted = None
        super(Label, self).__init__(label_json)
        self.name_id = self.name

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
        response = API.update_label_name(self.owner.token, self.name_id,
                                         self.name)
        _fail_if_contains_errors(response)
        self.name_id = self.name
        response = API.update_label_color(self.owner.token,
                                          self.name_id, self.color)
        _fail_if_contains_errors(response)

    def delete(self):
        """Delete the label.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'password')
        >>> label = user.add_label('family')
        >>> label.delete()
        """
        response = API.delete_label(self.owner.token, self.name_id)
        _fail_if_contains_errors(response)


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
