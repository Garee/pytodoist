import itertools
from json import dumps
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
                                     full_name=full_name, lang=lang,
                                     timezone=timezone)
    _fail_if_contains_errors(response)
    user_as_json = response.json()
    user = User(user_as_json)
    return user

def get_timezones():
    """Return a list of Todoist supported timezones.

    :return: A list of timezones
    :rtype: list (string)

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
    """A Todoist User that has the following attributes:

    :ivar full_name: The user's full name.
    :ivar start_page: The first page the user will see on Todoist.
    :ivar join_date: The date the user joined Todoist.
    :ivar last_used_ip: The IP address of the computer last used to login.
    :ivar is_premium: Does the user have Todoist premium?
    :ivar sort_order: The user's sort order.
    :ivar api_token: The user's API token.
    :ivar shard_id: The user's shard ID.
    :ivar timezone: The user's chosen timezone.
    :ivar id: The ID of the user.
    :ivar next_week: The day on which a task is delayed until.
    :ivar tz_offset: The user's timezone offset.
    :ivar email: The user's email address.
    :ivar start_day: The first day of the week.
    :ivar is_dummy: Is this a real or a dummy user?
    :ivar inbox_project: The ID of the user's Inbox project.
    :ivar time_format: The user's selected time_format.
    :ivar image_id: The ID of the user's avatar.
    :ivar beta: The user's beta status.
    :ivar premium_until: The date on which the user's premium status is revoked.
    :ivar mobile_number: The user's mobile number.
    :ivar mobile_host: The host of the user's mobile.
    :ivar password: The user's password.
    :ivar has_push_reminders: Does this user have push reminders?
    :ivar date_format: The user's selected date format.
    :ivar karma: The user's karma.
    :ivar karma_trend: The user's karma trend.
    :ivar token: The user's secret token.
    :ivar seq_no: The user's sequence number.
    :ivar default_reminder: The user's default reminder.
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

    def change_avatar(self, image_file):
        """Change the user's avatar.

        :param image: The path to the image.
        :type image: string
        :raises BadValueError: If the image is an invalid format, too big or
            unable to be resized.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.change_avatar('~/pictures/avatar.png')
        """
        with open(image_file) as image:
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
        """Return a list of a user's projects.

        :return: The user's projects.
        :rtype: list (:mod:`pytodoist.todoist.Project`)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.add_project('Homework', color=1)
        >>> projects = user.get_projects()
        >>> for project in projects:
        ...    print project.name
        u'Inbox'
        u'Homework'
        """
        response = API.get_projects(self.token)
        _fail_if_contains_errors(response)
        projects_as_json = response.json()
        return [Project(json, self) for json in projects_as_json]

    def get_project(self, project_name):
        """Return the project with a given name.

        :param project_name: The name to search for.
        :type project_name: string
        :return: The project that has the name ``project_name`` or ``None``
            if no project is found.
        :rtype: :mod:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> inbox = user.get_project('Inbox')
        >>> inbox.name
        u'Inbox'
        """
        for project in self.get_projects():
            if project.name == project_name:
                return project

    def get_project_with_id(self, project_id):
        """Return the project with a given ID.

        :param project_id: The ID to search for.
        :type project_id: string
        :return: The project that has the ID ``project_id`` or ``None``
            if no project is found.
        :rtype: :mod:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> inbox = user.get_project('Inbox')
        >>> project_id = inbox.id
        >>> inbox = user.get_project_with_id(project_id)
        >>> inbox.name
        u'Inbox'
        """
        response = API.get_project(self.token, project_id)
        _fail_if_contains_errors(response)
        project_as_json = response.json()
        return Project(project_as_json, self)

    def update_project_orders(self, projects):
        """Update the order in which projects are displayed on Todoist.

        :param projects: A list of projects in the order to be displayed.
        :type projects: list (:mod:`pytodoist.todoist.Project`)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> projects = user.get_projects()
        >>> for project in projects:
        ...    print project.name
        u'Homework'
        u'Shopping'
        >>> rev_projects = projects[::-1]
        >>> user.update_project_orders(rev_projects)
        >>> projects = user.get_projects()
        >>> for project in projects:
        ...    print project.name
        u'Shopping'
        u'Homework'
        """
        project_ids = str([project.id for project in projects])
        response = API.update_project_orders(self.token, project_ids)
        _fail_if_contains_errors(response)

    def get_uncompleted_tasks(self):
        """Return all of a user's uncompleted tasks.

        :return: A list of uncompleted tasks.
        :rtype: list (:mod:`pytodoist.todoist.Task`)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> tasks = user.get_uncompleted_tasks()
        """
        tasks = (p.get_uncompleted_tasks() for p in self.get_projects())
        return list(itertools.chain.from_iterable(tasks))

    def get_completed_tasks(self):
        """Return all of a user's completed tasks.

        :return: A list of completed tasks.
        :rtype: list (:mod:`pytodoist.todoist.Task`)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> tasks = user.get_completed_tasks()
        """
        tasks = (p.get_completed_tasks() for p in self.get_projects())
        return list(itertools.chain.from_iterable(tasks))

    def search_completed_tasks(self, label=None, interval=None):
        """Return a filtered list of a user's completed tasks.

        .. warning:: Requires the user to have Todoist premium.

        :param label: Only return tasks with this label.
        :type label: :mod:`pytodoist.todoist.Label`
        :param interval: Only return tasks completed this time period.
        :type interval: string
        :return: A list of tasks that meet the search criteria. If the user
            does not have Todoist premium an empty list is returned.
        :rtype: list (:mod:`pytodoist.todoist.Task`)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> tasks = user.search_completed_tasks(label='School')
        """
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
        """Return all of a user's tasks, regardless of completion state.

        :return: A list of all of a user's tasks.
        :rtype: list (:mod:`pytodoist.todoist.Task`)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> tasks = user.get_tasks()
        """
        return self.get_uncompleted_tasks() + self.get_completed_tasks()

    def search_tasks(self, queries):
        """Return a list of tasks that match some search criteria.

        :param queries: Return tasks that match at least one of these queries.
        :type queries: list (string)
        :return: A list tasks that match at least one query.
        :rtype: list (:mod:`pytodoist.todoist.Task`)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> queries = ['today', 'tomorrow']
        >>> tasks = user.search_tasks(queries)
        """
        queries = dumps(queries)
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
        """Return the user's label that has a given name.

        :param label_name: The name to search for.
        :type label_name: string
        :return: A label that has a matching name or ``None`` if not found.
        :rtype: :mod:`pytodoist.todoist.Label`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> label = user.get_label('School')
        """
        for label in self.get_labels():
            if label.name == label_name:
                return label

    def get_labels(self):
        """Return a list of all of a user's labels.

        :return: A list of labels.
        :rtype: list (:mod:`pytodoist.todoist.Label`)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> labels = user.get_labels()
        """
        response = API.get_labels(self.token)
        _fail_if_contains_errors(response)
        labels_as_json = response.json().values()
        return [Label(json, self) for json in labels_as_json]

    def create_label(self, name, color=None):
        """Create a new label.

        :param name: The name of the label.
        :type name: string
        :rtype: :mod:`pytodoist.todoist.Label`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> label = user.create_label('School')
        """
        response = API.create_label(self.token, name, color=color)
        _fail_if_contains_errors(response)
        label_as_json = response.json()
        return Label(label_as_json, self)

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

    def get_notifiable_events(self):
        """Return a list of notifiable events.

        :return: A list of notifiable events.
        :rtype: list (string)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.get_notifiable_events()
        [u'user_left_project', u'item_completed', ...]
        """
        return self._get_notification_settings().keys()

    def is_email_notified_when(self, event):
        """Find out if a user is receiving emails for a given
        event.

        :param event: The type of the notification.
        :type event: string
        :return: ``True`` if the user's settings allow for emails,
            ``False`` otherwise.
        :rtype: bool

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.is_email_notified_when('note_added')
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
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.is_push_notified_when('note_added')
        True
        """
        notification_settings = self._get_notification_settings()
        return notification_settings[event]['notify_push']

    def enable_push_notifications(self, event):
        """Enable push notifications for a given event.

        :param event: The event to enable push notifications for.
        :type event: string

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.enable_push_notifications('note_added')
        """
        self._update_notification_settings(event, 'push', 0)

    def disable_push_notifications(self, event):
        """Disable push notifications for a given event.

        :param event: The event to disable push notifications for.
        :type event: string

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.disable_push_notifications('note_added')
        """
        self._update_notification_settings(event, 'push', 1)

    def enable_email_notifications(self, event):
        """Enable email notifications for a given event.

        :param event: The event to enable email notifications for.
        :type event: string

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.enable_email_notifications('note_added')
        """
        self._update_notification_settings(event, 'email', 0)

    def disable_email_notifications(self, event):
        """Disable email notifications for a given event.

        :param event: The event to disable email notifications for.
        :type event: string

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> user.disable_email_notifications('note_added')
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

    def __init__(self, json, owner):
        self.id = None
        self.owner = owner
        super(Project, self).__init__(json)

    def delete(self):
        """Delete the project.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> project = user.get_project('Homework')
        >>> project.delete()
        """
        response = API.delete_project(self.owner.token, self.id)
        _fail_if_contains_errors(response)

    def update(self):
        """Update the project's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        :raises TodoistError: If the request to update is invalid.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> project = user.get_project('Homework')
        >>> project.name = 'Find Employment'
        ... # At this point Todoist still thinks the name is 'Homework'
        >>> project.update()
        ... # Now the name has been updated on Todoist.
        >>> project = user.get_project('Homework')
        >>> project == None
        True
        """
        response = API.update_project(self.owner.token, self.id,
                                      **self.__dict__)
        _fail_if_contains_errors(response)

    def archive(self):
        """Archive the project.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> project = user.get_project('Homework')
        >>> project.archive()
        """
        response = API.archive_project(self.owner.token, self.id)
        _fail_if_contains_errors(response)

    def unarchive(self):
        """Unarchive the project.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> project = user.get_project('Homework')
        >>> project.unarchive()
        """
        response = API.unarchive_project(self.owner.token, self.id)
        _fail_if_contains_errors(response)

    def collapse(self):
        """Collapse the project on Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> project = user.get_project('Homework')
        >>> project.collapse()
        """
        response = api.update_project(self.owner.token, self.id, collapsed=1)
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
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> project = user.get_project('Homework')
        >>> task = project.add_task('Read chapter 4.')
        >>> task.content
        u'Read Chapter 4'
        """
        response = API.add_task(self.owner.token, content, project_id=self.id,
                                date_string=date, priority=priority)
        _fail_if_contains_errors(response)
        task_as_json = response.json()
        return Task(task_as_json, self)

    def get_tasks(self):
        """Return all tasks in this project.

        :return: A list of all tasks in this project.
        :rtype: list (:mod:`pytodoist.todoist.Task`)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> project = user.get_project('Homework')
        >>> project.add_task('Read chapter 4.')
        >>> tasks = project.get_tasks()
        >>> for task in tasks:
        ...    print task.content
        u'Read Chapter 4.'
        """
        return self.get_uncompleted_tasks() + self.get_completed_tasks()

    def get_uncompleted_tasks(self):
        """Return a list of all uncompleted tasks in this project.

        :return: A list of all uncompleted tasks in this project.
        :rtype: list (:mod:`pytodoist.todoist.Task`)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> project = user.get_project('Homework')
        >>> project.add_task('Read chapter 4.')
        >>> uncompleted_tasks = project.get_uncompleted_tasks()
        >>> for task in uncompleted_tasks:
        ...    print task.content
        u'Read Chapter 4.'
        """
        response = API.get_uncompleted_tasks(self.owner.token, self.id)
        _fail_if_contains_errors(response)
        tasks_as_json = response.json()
        return [Task(json, self) for json in tasks_as_json]

    def get_completed_tasks(self):
        """Return a list of all completed tasks in this project.

        :return: A list of all completed tasks in this project.
        :rtype: list (:mod:`pytodoist.todoist.Task`)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> project = user.get_project('Homework')
        >>> task = project.add_task('Read chapter 4.')
        >>> task.complete()
        >>> completed_tasks = project.get_completed_tasks()
        >>> for task in completed_tasks:
        ...    print task.content
        u'Read Chapter 4.'
        """
        response = API.get_completed_tasks(self.owner.token, self.id)
        _fail_if_contains_errors(response)
        tasks_as_json = response.json()
        return [Task(json, self) for json in tasks_as_json]

    def update_task_orders(self, tasks):
        """Update the order in which tasks are displayed on Todoist.

        :param tasks: A list of tasks in the order to be displayed.
        :type tasks: list (:mod:`pytodoist.todoist.Task`)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
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

    """

    def __init__(self, json, project):
        self.id = None
        self.project = project
        super(Task, self).__init__(json)

    def update(self):
        """Update the task's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        :raises TodoistError: If the request to update is invalid.
        :raises NotFoundError: If the task cannot be found on Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
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
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
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
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
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
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
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
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> project = user.get_project('Homework')
        >>> task = user.add_task('Read Chapter 4.')
        >>> note = task.add_note('Page 56')
        >>> note.content
        u'Page 56'
        """
        response = API.add_note(self.project.owner.token, self.id, content)
        _fail_if_contains_errors(response)
        note_as_json = response.json()
        return Note(note_as_json, self)

    def get_notes(self):
        """Return all notes attached to this Task.

        :return: A list of all notes attached to this Task.
        :rtype: list (:mod:`pytodoist.todoist.Note`)

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> project = user.get_project('Homework')
        >>> task = user.add_task('Read Chapter 4.')
        >>> task.add_note('Page 56')
        >>> notes = task.get_notes()
        >>> len(notes)
        1
        """
        response = API.get_notes(self.project.owner.token, self.id)
        _fail_if_contains_errors(response)
        notes_as_json = response.json()
        return [Note(json, self) for json in notes_as_json]

    def advance_recurring_date(self):
        """Advance the recurring date of this task.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
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
        task_as_json = response.json()[0]
        self.__init__(task_as_json, self.project)

    def move(self, project):
        """Move this task to another project.

        :param project: The project to move the task to.
        :type project: :mod:`pytodoist.todoist.Project`

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> project = user.get_project('Homework')
        >>> task = user.add_task('Read Chapter 4.')
        >>> task.project.name
        u'Homework'
        >>> inbox = user.get_project('Inbox')
        >>> task.move(inbox)
        >>> task.project.name
        u'Inbox'
        """
        current_pos = '{{"{p_id}":["{t_id}"]}}'.format(p_id=self.project.id,
                                                       t_id=self.id)
        response = API.move_tasks(self.project.owner.token, current_pos,
                                  project.id)
        _fail_if_contains_errors(response)
        self.project = project


class Note(TodoistObject):
    """A Todoist note with the following attributes:

    """

    def __init__(self, json, task):
        self.id = None
        self.content = None
        self.task = task
        super(Note, self).__init__(json)

    def update(self):
        """Update the note's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
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
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
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

    """

    def __init__(self, json, owner):
        self.name = None
        self.color = None
        self.owner = owner
        super(Label, self).__init__(json)
        self.id = self.name

    def update(self):
        """Update the label's details on Todoist.

        You must call this method to register any local attribute changes with
        Todoist.

        >>> from pytodoist import todoist
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
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
        >>> user = todoist.login('john.doe@gmail.com', 'passwd')
        >>> label = user.create_label('work')
        >>> label.delete()
        """
        response = API.delete_label(self.owner.token, self.id)
        _fail_if_contains_errors(response)


class TodoistError(Exception):
    """Will be raised whenever a Todoist API call fails.

    This is the generic TodoistError that will be raised when there
    are no others suitable.
    """

    def __init__(self, response):
        self.response = response
        super(TodoistError, self).__init__(response.text)

class AuthError(TodoistError):
    """Raised when Todoist authentication fails."""

    def __init__(self, response):
        super(AuthError, self).__init__(response)

class RegistrationError(TodoistError):
    """Raised when Todoist registration fails."""

    def __init__(self, response):
        super(RegistrationError, self).__init__(response)


class InternalError(TodoistError):
    """Raised when an error occurs due to Todoist server problems."""

    def __init__(self, response):
        super(InternalError, self).__init__(response)


class BadValueError(TodoistError):
    """Raised when an invalid parameter is passed in an API call."""

    def __init__(self, response):
        super(BadValueError, self).__init__(response)


class NotFoundError(TodoistError):
    """Raised when a Todoist object cannot be found."""

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
    return TodoistError

def _fail_if_contains_errors(response):
    if _contains_errors(response):
        exception = _get_associated_exception(response)
        raise exception(response)

def _contains_errors(response):
    return response.status_code != 200 or response.text in _ERROR_TEXT_RESPONSES
