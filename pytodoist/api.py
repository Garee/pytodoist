"""This module abstracts underlying calls to the Todoist API so that they
may be performed in a simpler way. It is fundamentally a wrapper module that
neither adds nor takes away any functionality that is provided by Todoist.

If you do not need access to the raw HTTP response to the request, consider
using the higher level abstractions implemented in the :mod:`todoist` module.


*Example:*

>>> from pytodoist.api import TodoistAPI
>>> api = TodoistAPI()
>>> response = api.login('john.doe@gmail.com', 'passwd')
>>> user_info = response.json()
>>> user_info['email']
u'john.doe@gmail.com'
>>> user_info['full_name']
u'John Doe'
>>> user_token = user_info['token']
>>> response = api.ping(user_token)
>>> response.text
u'ok'
>>> response = api.get_projects(user_token)
>>> projects = response.json()
>>> len(projects)
2
"""
import requests

class TodoistAPI(object):
    """A wrapper around the Todoist web API: https://todoist.com/API.

    >>> from pytodoist.api import TodoistAPI
    >>> api = TodoistAPI()
    >>> api.URL
    'https://todoist.com/API/'
    """

    URL = 'https://todoist.com/API/'

    def login(self, email, password):
        """Login to Todoist.

        :param email: A Todoist user's email.
        :type email: string
        :param password: A Todoist user's password.
        :type password: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the user details.
        :on failure: ``response.text`` will contain ``"LOGIN_ERROR"``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_info['email']
        u'john.doe@gmail.com'
        """
        params = {
            'email': email,
            'password': password
        }
        return self._get('login', params)

    def login_with_google(self, email, oauth2_token, **kwargs):
        """Login to Todoist using Google's oauth2 authentication.

        :param email: A Todoist user's Google email.
        :type email: string
        :param oauth2_token:
            A valid oauth2_token for the user retrieved from Google's oauth2
            service.
        :type oauth2_token: string
        :param auto_signup:
            Register an account if this is ``1`` and no user is found.
        :type auto_signup: int
        :param full_name:
            A full name to use if the user is registering. If no name is
            given, an email based nickname is used.
        :type full_name: string
        :param timezone:
            A timezone to use if the user is registering. If not set, one is
            chosen based on the user's IP address.
        :type timezone: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the user details.
        :on failure: ``response.text`` will contain ``"LOGIN_ERROR"``,
            ``"INTERNAL_ERROR"``, ``"EMAIL_MISMATCH"`` or
            ``"ACCOUNT_NOT_CONNECTED_WITH_GOOGLE"``.

        >>> oauth2_token = get_token() # You must get the token somehow!
        >>> api = TodoistAPI()
        >>> response = api.login_with_google('john.doe@gmail.com', oauth2_token,
                                              auto_signup=1)
        >>> user_info = response.json()
        >>> user_info['email']
        u'john.doe@gmail.com'
        """
        params = {
            'email': email,
            'oauth2_token': oauth2_token
        }
        return self._get('loginWithGoogle', params, **kwargs)

    def ping(self, token):
        """Test a user's login token.

        A valid token is required to perform many of the API operations.

        :param token: A Todoist user's login token.
        :type token: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.
        :on failure: ``response.status_code`` will be ``401``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.ping(user_token)
        >>> response.text
        u"ok"
        """
        params = {
            'token': token
        }
        return self._get('ping', params)

    def get_timezones(self):
        """Return the timezones that Todoist supports.

        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the supported timezones.

        >>> api = TodoistAPI()
        >>> response = api.get_timezones()
        >>> response.json()
        [[u'US/Hawaii', u'(GMT-1000) Hawaii'], ...]
        """
        return self._get('getTimezones')

    def register(self, email, full_name, password, **kwargs):
        """Register a new user on Todoist.

        :param email: The user's email.
        :type email: string
        :param full_name: The user's full name.
        :type full_name: string
        :param password: The user's password. Must be 4 chars.
        :type password: string
        :param lang: The user's language.
        :type lang: string
        :param timezone: The user's timezone.
        :type timezone: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the user's details.
        :on failure: ``response.text`` will contain ``"ALREADY_REGISTRED"``,
            ``"TOO_SHORT_PASSWORD"``, ``"INVALID_EMAIL"``,
            ``"INVALID_TIMEZONE"``, ``"INVALID_FULL_NAME"`` or
            ``"UNKNOWN_ERROR"``.

        >>> api = TodoistAPI()]
        >>> response = api.register('john.doe@gmail.com', 'John Doe', 'passwd')
        >>> user_info = response.json()
        >>> user_info['email']
        u'john.doe@gmail.com'
        """
        params = {
            'email': email,
            'full_name': full_name,
            'password': password
        }
        return self._get('register', params, **kwargs)

    def delete_user(self, token, password, **kwargs):
        """Delete a registered Todoist user's account.

        :param token: A Todoist user's login token.
        :type token: string
        :param password: The user's password.
        :type password: string
        :param reason_for_delete: The reason for deletion.
        :type reason_for_delete: string
        :param in_background: If 0, delete the user instantly.
        :type in_background: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.
        :on failure: ``response.status_code`` will be ``403``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.delete_user(user_token, 'passwd')
        >>> response.text
        u'ok'
        """
        params = {
            'token': token,
            'current_password': password
        }
        return self._get('deleteUser', params, **kwargs)

    def update_user(self, token, **kwargs):
        """Update a registered Todoist user's account.

        :param token: The user's login token.
        :type token: string
        :param email: The new email address.
        :type email: string
        :param full_name: The new full name.
        :type full_name: string
        :param password: The new password.
        :type password: string
        :param timezone: The new timezone.
        :type timezone: string
        :param date_format: ``0``: ``DD-MM-YYYY``, ``1``: ``MM-DD-YYYY``.
        :type date_format: int
        :param time_format: ``0``: ``13:00``. ``1``: ``1:00pm``.
        :type time_format: int
        :param start_day: The new first day of the week ``(1-7, Mon-Sun)``.
        :type start_day: int
        :param next_week: The new day to use when postponing ``(1-7, Mon-Sun)``.
        :type next_week: int
        :param start_page: The new start page. ``_blank``: for a blank page,
            ``_info_page`` for the info page, ``_project_$PROJECT_ID`` for a
            project page or ``$ANY_QUERY`` to show query results.
        :type start_page: string
        :param default_reminder: ``email`` for email, ``mobile`` for SMS,
            ``push`` for smart device notifications or ``no_default`` to
            turn off notifications.
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the updated user details.
        :on failure: ``response.status_code`` will be ``400`` or
            ``response.text`` will contain ``"ERROR_EMAIL_FOUND"``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_info['full_name']
        u'John Doe'
        >>> user_token = user_info['token']
        >>> response = api.update_user(user_token, full_name='John Smith')
        >>> user_info = response.json()
        >>> user_info['full_name']
        u'John Smith'
        """
        params = {
            'token': token
        }
        return self._get('updateUser', params, **kwargs)

    def update_avatar(self, token, image=None, **kwargs):
        """Update a registered Todoist user's avatar.

        :param token: The user's login token.
        :type token: string
        :param image: The image. Must be encoded with multipart/form-data.
            The maximum size is 2mb.
        :type image: string
        :param delete: If ``1``, delete the current avatar and use the default.
        :type delete: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the updated user details.
        :on failure: ``response.text`` will contain ``"UNKNOWN_IMAGE_FORMAT"``,
            ``"UNABLE_TO_RESIZE_IMAGE"`` or ``"IMAGE_TOO_BIG"``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> api.update_avatar(user_token, delete=1) # Use default avatar.
        """
        params = {
            'token': token
        }
        files = {'image': image} if image else None
        return self._get('updateAvatar', params, files, **kwargs)

    def get_projects(self, token):
        """Return a list of all of a user's projects.

        :param token: The user's login token.
        :type token: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain a list of projects.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> for project in projects:
        ...     project['name']
        ...
        u'Inbox'
        """
        params = {
            'token': token
        }
        return self._get('getProjects', params)

    def get_project(self, token, project_id):
        """Return a project's details.

        :param token: The user's login token.
        :type token: string
        :param project_id: The ID of a project.
        :type project_id: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the project details.
        :on failure: ``response.status_code`` will be ``400``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_project(user_token, '4325')
        >>> project = response.json()
        >>> project['name']
        u'Inbox'
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('getProject', params)

    def add_project(self, token, project_name, **kwargs):
        """Add a new project to a user's account.

        :param token: The user's login token.
        :type token: string
        :param project_name: The name of the new project.
        :type project_id: string
        :param color: The color of the new project.
        :type color: int
        :param indent: The indentation of the new project ``(1-4)``.
        :type indent: int
        :param order: The order of the new project ``(1+)``.
        :type order: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the project details.
        :on failure: ``response.text`` will contain ``"ERROR_NAME_IS_EMPTY"``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_project(user_token, 'Work')
        >>> project = response.json()
        >>> project['name']
        u'Work'
        """
        params = {
            'token': token,
            'name': project_name
        }
        return self._get('addProject', params, **kwargs)

    def update_project(self, token, project_id, **kwargs):
        """Update a user's project.

        :param token: The user's login token.
        :type token: string
        :param project_id: The ID of a project.
        :type project_id: string
        :param name: The new name.
        :type name: string
        :param color: The new color.
        :type color: int
        :param indent: The new indentation ``(1-4)``.
        :type indent: int
        :param order: The new order ``(1+)``.
        :type order: int
        :param collapsed: If ``1``, collapse the project.
        :type collapsed: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the updated details.
        :on failure: ``response.status_code`` will be ``400``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_project(user_token, '5436')
        >>> project = response.json()
        >>> project['name']
        u'Work'
        >>> project_id = project['id']
        >>> response = api.update_project(user_token, project_id, name='Play')
        >>> project = response.json()
        >>> project['name']
        u'Play'
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('updateProject', params, **kwargs)

    def update_project_orders(self, token, ordered_project_ids):
        """Update a user's project orderings.

        :param token: The user's login token.
        :type token: string
        :param ordered_project_ids: An ordered list of project IDs.
        :type ordered_project_ids: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> reverse_order = [project['id'] for project in projects]
        >>> api.update_project_orders(user_token, str(reverse_order))
        """
        params = {
            'token': token,
            'item_id_list': ordered_project_ids
        }
        return self._get('updateProjectOrders', params)

    def delete_project(self, token, project_id):
        """Delete a user's project.

        :param token: The user's login token.
        :type token: string
        :param project_id: The ID of the project to delete.
        :type project_id: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_project(user_token, '5436')
        >>> project = response.json()
        >>> project['name']
        u'Work'
        >>> project_id = project['id']
        >>> api.delete_project(user_token, project_id)
        >>> response = api.get_project(user_token, project_id)
        >>> response.text
        u'"ERROR_PROJECT_NOT_FOUND"'
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('deleteProject', params)

    def archive_project(self, token, project_id):
        """Archive a user's project.

        .. warning:: Only works if the user has Todoist premium.

        :param token: The user's login token.
        :type token: string
        :param project_id: The ID of the project to archive.
        :type project_id: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain a list of archived
            project IDs. e.g. ``[1234, 3435, 5235]``. The list will be empty
            if the user does not have Todoist premium.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.archive_project(user_token, '4837')
        >>> archived_project_ids = response.json()
        >>> archived_project_ids
        [4837]
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('archiveProject', params)

    def unarchive_project(self, token, project_id):
        """Unarchive a user's project.

        .. warning:: Only works if the user has Todoist premium.

        :param token: The user's login token.
        :type token: string
        :param project_id: The ID of the project to unarchive.
        :type project_id: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain a list of unarchived
            project IDs. e.g. ``[1234, 3435, 5235]``. The list will be empty
            if the user does not have Todoist premium.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.unarchive_project(user_token, '4837')
        >>> unarchived_project_ids = response.json()
        >>> unarchived_project_ids
        [4837]
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('unarchiveProject', params)

    def get_labels(self, token, **kwargs):
        """Return all of a user's labels.

        :param token: The user's login token.
        :type token: string
        :param as_list: If ``1``, return a list of label names only.
        :type as_list: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain a map of
            label name -> label details.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> api.create_label(user_token, 'football')
        >>> response = api.get_labels(user_token)
        >>> labels = response.json()
        >>> for label in labels.values():
        ...     label['name']
        ...
        u'football'
        """
        params = {
          'token': token
        }
        return self._get('getLabels', params, **kwargs)

    def create_label(self, token, label_name, **kwargs):
        """Add a label.

        If a label with the name already exists it will be returned.

        :param token: The user's login token.
        :type token: string
        :param label_name: The name of the label.
        :type label_name: string
        :param color: The color of the label.
        :type color: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the label details.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.create_label(user_token, 'football')
        >>> label = response.json()
        >>> label['name']
        u'football'
        """
        params = {
          'token': token,
          'name': label_name
        }
        return self._get('addLabel', params, **kwargs)

    def update_label_name(self, token, label_name, new_name):
        """Update the name of a user's label.

        :param token: The user's login token.
        :type token: string
        :param label_name: The current name of the label.
        :type label_name: string
        :param new_name: The new name of the label.
        :type new_name: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the label details.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.create_label(user_token, 'football')
        >>> label = response.json()
        >>> label['name']
        u'football'
        >>> response = api.update_label_name(user_token, 'football', 'soccer')
        >>> label = response.json()
        >>> label['name']
        u'soccer'
        """
        params = {
          'token': token,
          'old_name': label_name,
          'new_name': new_name
        }
        return self._get('updateLabel', params)

    def update_label_color(self, token, label_name, color):
        """Update the color of a user's label.

        :param token: The user's login token.
        :type token: string
        :param label_name: The name of the label.
        :type label_name: string
        :param color: The new color of the label.
        :type color: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the label details.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.create_label(user_token, 'football', color=1)
        >>> label = response.json()
        >>> label['color']
        1
        >>> response = api.update_label_name(user_token, 'football', color=2)
        >>> label = response.json()
        >>> label['color']
        2
        """
        params = {
          'token': token,
          'name': label_name,
          'color': color
        }
        return self._get('updateLabelColor', params)

    def delete_label(self, token, label_name):
        """Delete a user's label.

        :param token: The user's login token.
        :type token: string
        :param label_name: The name of the label.
        :type label_name: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.delete_label(token, 'football')
        >>> response.text
        u'"ok"'
        """
        params = {
          'token': token,
          'name': label_name
        }
        return self._get('deleteLabel', params)

    def get_uncompleted_tasks(self, token, project_id, **kwargs):
        """Return a list of a project's uncompleted tasks.

        :param token: The user's login token.
        :type token: string
        :param project_id: The ID of the project to get tasks from.
        :type project_id: string
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain a list of tasks.
        :on failure: ``response.status_code`` will be ``400``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> project_id = projects[0]['id']
        >>> response = api.get_uncompleted_tasks(user_token, project_id)
        >>> uncompleted_tasks = response.json()
        >>> len(uncompleted_tasks)
        0
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('getUncompletedItems', params, **kwargs)

    def get_all_completed_tasks(self, token, **kwargs):
        """Return a list of a user's completed tasks.

        .. warning:: Only works if the user has Todoist premium.

        :param token: The user's login token.
        :type token: string
        :param project_id: Filter the tasks by project.
        :type project_id: string
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :param label: Filter the tasks by label.
        :type label: string
        :param interval: Filter the tasks by time range.
            Defaults to ``past 2 weeks``.
        :type interval: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain a list of tasks. The list
            will be empty is the user does not have Todoist premium.
        :on failure: ``response.status_code`` will be ``400``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_all_completed_tasks(user_token)
        >>> completed_tasks = response.json()
        >>> len(uncompleted_tasks)
        0
        """
        params = {
            'token': token
        }
        return self._get('getAllCompletedItems', params, **kwargs)

    def get_completed_tasks(self, token, project_id, **kwargs):
        """Return a list of a project's completed tasks.

        :param token: The user's login token.
        :type token: string
        :param project_id: The project to get tasks from.
        :type project_id: string
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain a list of tasks.
        :on failure: ``response.status_code`` will be ``400``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> project_id = projects[0]['id']
        >>> response = api.get_completed_tasks(user_token, project_id)
        >>> completed_tasks = response.json()
        >>> len(uncompleted_tasks)
        0
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('getCompletedItems', params, **kwargs)

    def get_tasks_by_id(self, token, task_ids, **kwargs):
        """Return a list of tasks with given IDs.

        :param token: The user's login token.
        :type token: string
        :param task_ids: A list of task IDs.
        :type task_ids: string
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain a list of tasks.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> task_ids = ['1324']
        >>> response = api.get_tasks_by_id(user_token, str(task_ids))
        >>> tasks = response.json()
        >>> len(tasks)
        1
        """
        params = {
            'token': token,
            'ids': task_ids
        }
        return self._get('getItemsById', params, **kwargs)

    def add_task(self, token, content, **kwargs):
        """Add a task to a project.

        :param token: The user's login token.
        :type token: string
        :param content: The task description.
        :type content: string
        :param project_id: The project to add the task to. Defaults to ``Inbox``
        :type project_id: string
        :param date_string: The deadline date for the task.
        :type date_string: string
        :param priority: The task priority ``(1-4)``.
        :type priority: int
        :param indent: The task indentation ``(1-4)``.
        :type indent: int
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :param item_order: The task order.
        :type item_order: int
        :param children: A list of child tasks IDs.
        :type children: string
        :param labels: A list of label IDs.
        :type labels: string
        :param assigned_by_uid: The ID of the user who assigns current task.
            Accepts 0 or any user id from the list of project collaborators.
            If value is unset or invalid it will automatically be set up by
            your uid.
        :type assigned_by_uid: string
        :param responsible_uid: The id of user who is responsible for
            accomplishing the current task. Accepts 0 or any user id from
            the list of project collaborators. If the value is unset or
            invalid it will automatically be set to null.
        :type responsible_uid: string
        :param note: Content of a note to add.
        :type note: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the task details.
        :on failure: ``response.status_code`` will be ``400`` or
            ``response.text`` will contain ``"ERROR_WRONG_DATE_SYNTAX"``

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Buy Milk')
        >>> task = response.json()
        >>> task['content']
        u'Buy Milk'
        """
        params = {
            'token': token,
            'content': content
        }
        return self._get('addItem', params, **kwargs)

    def update_task(self, token, task_id, **kwargs):
        """Update the details of a task.

        :param token: The user's login token.
        :type token: string
        :param task_id: The ID of the task to update.
        :type task_id: string
        :param content: The new task description.
        :type content: string
        :param project_id: The new project.
        :type project_id: string
        :param date_string: The new deadline date for the task.
        :type date_string: string
        :param priority: The newtask priority ``(1-4)``.
        :type priority: int
        :param indent: The new task indentation ``(1-4)``.
        :type indent: int
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :param item_order: The new task order.
        :type item_order: int
        :param children: The new list of child tasks IDs.
        :type children: string
        :param labels: The new list of label IDs.
        :type labels: string
        :param assigned_by_uid: The new ID of the user who assigns current task.
            Accepts 0 or any user id from the list of project collaborators.
            If value is unset or invalid it will automatically be set up by
            your uid.
        :type assigned_by_uid: string
        :param responsible_uid: The new id of user who is responsible for
            accomplishing the current task. Accepts 0 or any user id from
            the list of project collaborators. If the value is unset or
            invalid it will automatically be set to null.
        :type responsible_uid: string
        :param note: Content of a note to add.
        :type note: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the updated task details.
        :on failure: ``response.text`` will contain ``"ERROR_ITEM_NOT_FOUND"``

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Buy Milk')
        >>> task = response.json()
        >>> task['content']
        u'Buy Milk'
        >>> task_id = task['id']
        >>> response = api.update_task(user_token, task_id, content='Buy Bread')
        >>> task = response.json()
        >>> task['content']
        u'Buy Bread'
        """
        params = {
            'token': token,
            'id': task_id
        }
        return self._get('updateItem', params, **kwargs)

    def update_task_ordering(self, token, project_id, task_ids):
        """Update the order of a project's tasks.

        :param token: The user's login token.
        :type token: string
        :param project_id: The new project.
        :type project_id: string
        :param task_ids: An ordered list of task IDs.
        :type task_ids: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``
        :on failure: ``response.status_code`` will be ``400``

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        ... # Get Inbox project_id
        >>> response = api.get_uncompleted_tasks(user_token, project_id)
        >>> tasks = response.json()
        >>> task_ids = [task['id'] for task in tasks]
        >>> reverse_task_ids = str(task_ids[::-1])
        >>> response = api.update_task_ordering(user_token, reverse_task_ids)
        >>> response.text
        u'"ok"'
        """
        params = {
            'token': token,
            'project_id': project_id,
            'item_id_list': task_ids
        }
        return self._get('updateOrders', params)

    def move_tasks(self, token, task_locations, project_id):
        """Move tasks to another project.

        :param token: The user's login token.
        :type token: string
        :param task_locations: The current locations of the tasks to move. It is
            a map of ``project_id -> task_id`` e.g. ``{'1534': ['23453']}``.
        :type task_locations: string
        :param project_id: The project to move the tasks to.
        :type project_id: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the task counts of each
            project e.g. ``{"counts": {"1523": 0, "1245": 1}}``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        ... # Get the locations of the tasks to move.
        ... # and the project to move them to.
        >>> response = api.move_tasks(user_token, task_locations, project_id)
        >>> response.json()
        {"counts": {"1523": 0, "1245": 1}}
        """
        params = {
            'token': token,
            'project_items': task_locations,
            'to_project': project_id
        }
        return self._get('moveItems', params)

    def advance_recurring_dates(self, token, task_ids, **kwargs):
        """Update the recurring dates of a list of tasks. The date
        will be advanced to the next date with respect to their 'date_string'.

        :param token: The user's login token.
        :type token: string
        :param task_ids: The IDs of the tasks to update.
        :type task_ids: string
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the list of updated tasks.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> task_ids = ['2342', '4324']
        >>> response = api.advance_recurring_dates(user_token, str(task_ids))
        >>> tasks = response.json()
        >>> len(tasks)
        2
        """
        params = {
            'token': token,
            'ids': task_ids
        }
        return self._get('updateRecurringDate', params, **kwargs)

    def delete_tasks(self, token, task_ids):
        """Delete a given list of tasks.

        :param token: The user's login token.
        :type token: string
        :param task_ids: The IDs of the tasks to delete.
        :type task_ids: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Buy Milk')
        >>> task = response.json()
        >>> task_id = task['id']
        >>> task_ids = [task_id]
        >>> response = api.delete_tasks(user_token, str(task_ids))
        >>> response.text
        u'"ok"'
        """
        params = {
            'token': token,
            'ids': task_ids
        }
        return self._get('deleteItems', params)

    def complete_tasks(self, token, task_ids, **kwargs):
        """Complete a given list of tasks.

        :param token: The user's login token.
        :type token: string
        :param task_ids: The IDs of the tasks to complete.
        :type task_ids: string
        :param in_history: If ``0``, the tasks will not be moved to the history.
        :type in_history: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Buy Milk')
        >>> task = response.json()
        >>> task_id = task['id']
        >>> task_ids = [task_id]
        >>> response = api.complete_tasks(user_token, str(task_ids))
        >>> response.text
        u'"ok"'
        """
        params = {
            'token': token,
            'ids': task_ids
        }
        return self._get('completeItems', params, **kwargs)

    def uncomplete_tasks(self, token, task_ids):
        """Uncomplete a given list of tasks.

        :param token: The user's login token.
        :type token: string
        :param task_ids: The IDs of the tasks to complete.
        :type task_ids: string
        :param in_history: If ``0``, the tasks will not be moved to the history.
        :type in_history: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Buy Milk')
        >>> task = response.json()
        >>> task_id = task['id']
        >>> task_ids = [task_id]
        >>> api.complete_tasks(user_token, str(task_ids))
        >>> response = api.complete_tasks(user_token, str(task_ids))
        >>> response.text
        u'"ok"'
        """
        params = {
            'token': token,
            'ids': task_ids
        }
        return self._get('uncompleteItems', params)

    def add_note(self, token, task_id, note_content):
        """Add a note to a task.

        :param token: The user's login token.
        :type token: string
        :param task_id: The ID of the task to add the note to.
        :type task_id: string
        :param note_content: The note to add.
        :type note_content: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the note details.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        ... # Get a task_id
        >>> response = api.add_note(user_token, task_id, 'Call 0783766273')
        >>> note = response.json()
        >>> note['content']
        u'Call 0783766273'
        """
        params = {
            'token': token,
            'item_id': task_id,
            'content': note_content
        }
        return self._get('addNote', params)

    def update_note(self, token, note_id, new_content):
        """Update the content of a note.

        :param token: The user's login token.
        :type token: string
        :param note_id: The ID of the note to update.
        :type note_id: string
        :param note_content: The new note content.
        :type note_content: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        ... # Get a task_id
        >>> response = api.add_note(user_token, task_id, 'Call 0783766273')
        >>> note = response.json()
        >>> note['content']
        u'Call 0783766273'
        >>> note_id = note['id']
        >>> response = api.update_note(user_token, note_id, 'Don't Call!')
        >>> note = response.json()
        >>> note['content']
        u'Don't Call!'
        """
        params = {
            'token': token,
            'note_id': note_id,
            'content': new_content
        }
        return self._get('updateNote', params)

    def delete_note(self, token, task_id, note_id):
        """Delete a note from a task.

        :param token: The user's login token.
        :type token: string
        :param task_id: The ID of the task to delete the note from.
        :type task_id: string
        :param note_id: The ID of the note to delete.
        :type note_id: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        ... # Get a task_id and note_id.
        >>> response = api.delete_note(user_token, task_id, note_id)
        >>> response.text
        u'"ok"'
        """
        params = {
            'token': token,
            'item_id': task_id,
            'note_id': note_id
        }
        return self._get('deleteNote', params)

    def get_notes(self, token, task_id):
        """Return the list of notes for a task.

        :param token: The user's login token.
        :type token: string
        :param task_id: The ID of the task to get the notes from.
        :type task_id: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain a list of notes.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        ... # Get a task_id
        >>> response = api.get_notes(user_token, task_id)
        >>> notes = response.json()
        >>> len(notes)
        0
        """
        params = {
            'token': token,
            'item_id': task_id
        }
        return self._get('getNotes', params)

    def search_tasks(self, token, queries, **kwargs):
        """Return the list of tasks, each of which matches one of the
        provided queries.



        :param token: The user's login token.
        :type token: string
        :param queries: A list of queries.
        :type queries: string
        :param as_count: If ``1``, a count of the tasks will be returned.
        :type as_count: int
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain a list of queries and
            the tasks that matched them.

        .. note:: See https://todoist.com/Help/timeQuery for valid queries.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> queries = str(['tomorrow'])
        >>> response = api.search_tasks(user_token, queries, as_count=1)
        >>> counts = response.json()
        >>> counts
        '[{"count": 0, "query": "tomorrow", "type": "date"}]'
        """
        params = {
            'token': token,
            'queries': queries
        }
        return self._get('query', params, **kwargs)

    def get_notes_and_task(self, token, task_id):
        """Return the list of notes for a task and the task itself.

        :param token: The user's login token.
        :type token: string
        :param task_id: The ID of the task.
        :type task_id: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain the task and notes.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        ... # Get task_id
        >>> response = api.get_notes_and_task(user_token, task_id)
        >>> results = response.json()
        >>> notes = results['notes']
        >>> task = results['item']
        """
        params = {
            'token': token,
            'item_id': task_id
        }
        return self._get('getNotesData', params)

    def get_notification_settings(self, token):
        """Return a user's notification settings.

        :param token: The user's login token.
        :type token: string
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.json()`` will contain a list of settings.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_notification_settings(user_token)
        >>> response.json()
        {u'user_left_project':
            {u'notify_push': True, u'notify_email': False},
        ...}
        """
        params = {
            'token': token
        }
        return self._get('getNotificationSettings', params)

    def update_notification_settings(self, token, event,
                                     service, should_notify):
        """Update a user's notification settings.

        :param token: The user's login token.
        :type token: string
        :param event: Update the notification settings of this event.
        :type event: string
        :param service: ``email`` or ``push``
        :type service: string
        :param should_notify: If ``0`` notify, otherwise do not.
        :type should_notify: int
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'passwd')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.update_notification_settings(user_token,
        ...                                             'user_left_project',
        ...                                             'email', 0)
        >>> response.text
        u'"ok"'
        """
        params = {
            'token': token,
            'notification_type': event,
            'service': service,
            'dont_notify': should_notify
        }
        return self._get('updateNotificationSetting', params)

    def _getf(self, end_point, params=None, files=None):
        url = self.URL + end_point
        return requests.get(url, params=params, files=files)

    def _get(self, end_point, params=None, files=None, **kwargs):
        """Send a HTTP GET request to a Todoist API end-point.

        :param end_point: The Todoist API end-point.
        :type end_point: string
        :param params: The required request parameters.
        :type params: dict
        :param kwargs: Any optional parameters.
        :type kwargs: dict
        :return: The HTTP response to the request.
        :rtype: :mod:`requests.Response`
        """
        url = self.URL + end_point
        if params and kwargs:
            params.update(kwargs)
        return requests.get(url, params=params, files=files)