"""This module is a pure wrapper around the Todoist API that neither adds or
takes away any functionality that is provided by Todoist. It uses the
popular requests package to provide a simple way in which to use the API in
Python.

For :class:`requests.Response` documentation see here:

    http://docs.python-requests.org/en/latest/api/#requests.Response

If you do not need access to the raw HTTP response to the request, consider
using the higher level abstractions implemented in the :mod:`pytodoist.todoist`
module.

*Example:*

>>> from pytodoist.api import TodoistAPI
>>> api = TodoistAPI()
>>> response = api.login('john.doe@gmail.com', 'password')
>>> user_info = response.json()
>>> print user_info['full_name']
John Doe
>>> user_token = user_info['token']
>>> response = api.ping(user_token)
>>> print response.status_code
200
>>> response = api.add_task(user_token, 'Install PyTodoist')
>>> install_task = response.json()
>>> response = api.get_projects(user_token)
>>> projects = response.json()
>>> for project in projects:
...     response = api.get_uncompleted_tasks(user_token, project['id'])
...     uncompleted_tasks = response.json()
...     for task in uncompleted_tasks:
...         print task['content']
...
Install PyTodoist
"""
import requests

# No magic numbers
_HTTP_OK = 200


# noinspection PyDocstring
class TodoistAPI(object):
    """A wrapper around the Todoist API.

    >>> from pytodoist.api import TodoistAPI
    >>> api = TodoistAPI()
    >>> api.URL
    'https://todoist.com/API/'
    """

    URL = 'https://todoist.com/API/'

    ERROR_TEXT_RESPONSES = [
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
        '"ERROR_ITEM_NOT_FOUND"'
    ]

    def login(self, email, password):
        """Login to Todoist.

        :param email: The user's email address.
        :type email: str
        :param password: The user's password.
        :type password: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the user details.
        :on failure: ``response.text`` will contain ``"LOGIN_ERROR"``.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> print user_info['full_name']
        John Doe
        """
        params = {
            'email': email,
            'password': password
        }
        return self._get('login', params)

    def login_with_google(self, email, oauth2_token, **kwargs):
        """Login to Todoist using Google's oauth2 authentication.

        :param email: The user's Google email address.
        :type email: str
        :param oauth2_token: The user's Google oauth2 token.
        :type oauth2_token: str
        :param auto_signup: If ``1`` register an account automatically.
        :type auto_signup: int
        :param full_name: The full name to use if the account is registered
            automatically. If no name is given an email based nickname is used.
        :type full_name: str
        :param timezone: The timezone to use if the account is registered
            automatically. If no timezone is given one is chosen based on the
            user's IP address.
        :type timezone: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the user details.
        :on failure: ``response.text`` will contain ``"LOGIN_ERROR"``,
            ``"INTERNAL_ERROR"``, ``"EMAIL_MISMATCH"`` or
            ``"ACCOUNT_NOT_CONNECTED_WITH_GOOGLE"``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        ... # Get the oauth2_token from Google.
        >>> response = api.login_with_google('john.doe@gmail.com',
                                              oauth2_token)
        >>> user_info = response.json()
        >>> print user_info['full_name']
        John Doe
        """
        params = {
            'email': email,
            'oauth2_token': oauth2_token
        }
        return self._get('loginWithGoogle', params, **kwargs)

    def ping(self, token):
        """Test a user's login token.

        :param token: The user's login token.
        :type token: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.text`` will contain ``ok``.
        :on failure: ``response.status_code`` will be ``401``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.ping(user_token)
        >>> print response.text
        ok
        """
        params = {
            'token': token
        }
        return self._get('ping', params)

    def get_timezones(self):
        """Return the timezones that Todoist supports.

        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the supported timezones.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.get_timezones()
        >>> print response.json()
        [[u'US/Hawaii', u'(GMT-1000) Hawaii'], ...]
        """
        return self._get('getTimezones')

    def register(self, email, full_name, password, **kwargs):
        """Register a new user on Todoist.

        :param email: The user's email.
        :type email: str
        :param full_name: The user's full name.
        :type full_name: str
        :param password: The user's password. Must be at least 4 characters.
        :type password: str
        :param lang: The user's language.
        :type lang: str
        :param timezone: The user's timezone.
        :type timezone: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the user's details.
        :on failure: ``response.text`` will contain ``"ALREADY_REGISTRED"``,
            ``"TOO_SHORT_PASSWORD"``, ``"INVALID_EMAIL"``,
            ``"INVALID_TIMEZONE"``, ``"INVALID_FULL_NAME"`` or
            ``"UNKNOWN_ERROR"``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.register('john.doe@gmail.com', 'John Doe',
        ...                         'password')
        >>> user_info = response.json()
        >>> print user_info['full_name']
        John Doe
        """
        params = {
            'email': email,
            'full_name': full_name,
            'password': password
        }
        return self._post('register', params, **kwargs)

    def delete_user(self, token, password, **kwargs):
        """Delete a registered Todoist user's account.

        :param token: The user's login token.
        :type token: str
        :param password: The user's password.
        :type password: str
        :param reason_for_delete: The reason for deletion.
        :type reason_for_delete: str
        :param in_background: If ``0``, delete the user instantly.
        :type in_background: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.
        :on failure: ``response.status_code`` will be ``403``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.delete_user(user_token, 'password')
        >>> print response.text
        ok
        """
        params = {
            'token': token,
            'current_password': password
        }
        return self._post('deleteUser', params, **kwargs)

    def update_user(self, token, **kwargs):
        """Update a registered Todoist user's account.

        :param token: The user's login token.
        :type token: str
        :param email: The new email address.
        :type email: str
        :param full_name: The new full name.
        :type full_name: str
        :param password: The new password.
        :type password: str
        :param timezone: The new timezone.
        :type timezone: str
        :param date_format: ``0``: ``DD-MM-YYYY``, ``1``: ``MM-DD-YYYY``.
        :type date_format: int
        :param time_format: ``0``: ``13:00``. ``1``: ``1:00pm``.
        :type time_format: int
        :param start_day: New first day of the week ``(1-7, Mon-Sun)``.
        :type start_day: int
        :param next_week: New day to use when postponing ``(1-7, Mon-Sun)``.
        :type next_week: int
        :param start_page: The new start page. ``_blank``: for a blank page,
            ``_info_page`` for the info page, ``_project_$PROJECT_ID`` for a
            project page or ``$ANY_QUERY`` to show query results.
        :type start_page: str
        :param default_reminder: ``email`` for email, ``mobile`` for SMS,
            ``push`` for smart device notifications or ``no_default`` to
            turn off notifications.
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the updated user details.
        :on failure: ``response.status_code`` will be ``400`` or
            ``response.text`` will contain ``"ERROR_EMAIL_FOUND"``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> print user_info['full_name']
        John Doe
        >>> user_token = user_info['token']
        >>> response = api.update_user(user_token, full_name='John Smith')
        >>> user_info = response.json()
        >>> user_info['full_name']
        John Smith
        """
        params = {
            'token': token
        }
        return self._post('updateUser', params, **kwargs)

    def update_avatar(self, token, image=None, **kwargs):
        """Update a registered Todoist user's avatar.

        :param token: The user's login token.
        :type token: str
        :param image: The image file. The maximum size is 2mb.
        :type image: fileIO[str]
        :param delete: If ``1``, delete the current avatar and use the default.
        :type delete: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the updated user details.
        :on failure: ``response.text`` will contain ``"UNKNOWN_IMAGE_FORMAT"``,
            ``"UNABLE_TO_RESIZE_IMAGE"`` or ``"IMAGE_TOO_BIG"``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> with open('/path/to/avatar.png') as image:
        ...    api.update_avatar(user_token, image)
        """
        params = {
            'token': token
        }
        files = {'image': image} if image else None
        return self._post('updateAvatar', params, files, **kwargs)

    def get_redirect_link(self, token, **kwargs):
        """Return the absolute URL to redirect or to open in
        a browser. The first time the link is used it logs in the user
        automatically and performs a redirect to a given page. Once used,
        the link keeps working as a plain redirect.

        :param token: The user's login token.
        :type token: str
        :param path: The path to redirect the user's browser. Default ``/app``.
        :type path: str
        :param hash: The has part of the path to redirect the user's browser.
        :type hash: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the redirect link.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_redirect_link(user_token)
        >>> print response.json()['link']
        https://todoist.com/secureRedirect?path=adflk...
        """
        params = {
            'token': token
        }
        return self._get('getRedirectLink', params, **kwargs)

    def get_projects(self, token):
        """Return a list of all of a user's projects.

        :param token: The user's login token.
        :type token: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain a list of projects.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> for project in projects:
        ...     print project['name']
        ...
        Inbox
        """
        params = {
            'token': token
        }
        return self._get('getProjects', params)

    def get_project(self, token, project_id):
        """Return a project's details.

        :param token: The user's login token.
        :type token: str
        :param project_id: The ID of a project.
        :type project_id: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the project details.
        :on failure: ``response.status_code`` will be ``400``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> for project in projects:
        ...     if project['name'] == 'Inbox':
        ...         project_id = project['id']
        ...
        >>> response = api.get_project(user_token, project_id)
        >>> project = response.json()
        >>> print project['name']
        Inbox
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('getProject', params)

    def add_project(self, token, project_name, **kwargs):
        """Add a new project to a user's account.

        :param token: The user's login token.
        :type token: str
        :param project_name: The name of the new project.
        :type project_name: str
        :param color: The color of the new project.
        :type color: int
        :param indent: The indentation of the new project ``(1-4)``.
        :type indent: int
        :param order: The order of the new project ``(1+)``.
        :type order: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the project details.
        :on failure: ``response.text`` will contain ``"ERROR_NAME_IS_EMPTY"``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_project(user_token, 'PyTodoist')
        >>> project = response.json()
        >>> print project['name']
        PyTodoist
        """
        params = {
            'token': token,
            'name': project_name
        }
        return self._post('addProject', params, **kwargs)

    def update_project(self, token, project_id, **kwargs):
        """Update a user's project.

        :param token: The user's login token.
        :type token: str
        :param project_id: The ID of a project.
        :type project_id: str
        :param name: The new name.
        :type name: str
        :param color: The new color.
        :type color: int
        :param indent: The new indentation ``(1-4)``.
        :type indent: int
        :param order: The new order ``(1+)``.
        :type order: int
        :param collapsed: If ``1``, collapse the project.
        :type collapsed: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the updated details.
        :on failure: ``response.status_code`` will be ``400``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> for project in projects:
        ...     if project['name'] == 'PyTodoist':
        ...         project_id = project['id']
        ...
        >>> response = api.get_project(user_token, project_id)
        >>> project = response.json()
        >>> print project['name']
        PyTodoist
        >>> project_id = project['id']
        >>> response = api.update_project(user_token, project_id, name='Work')
        >>> project = response.json()
        >>> print project['name']
        Work
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._post('updateProject', params, **kwargs)

    def update_project_orders(self, token, ordered_project_ids):
        """Update a user's project orderings.

        :param token: The user's login token.
        :type token: str
        :param ordered_project_ids: An ordered list of project IDs.
        :type ordered_project_ids: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> current_order = [project['id'] for project in projects]
        >>> reverse_order = str(current_order[::-1])
        >>> api.update_project_orders(user_token, reverse_order)
        """
        params = {
            'token': token,
            'item_id_list': ordered_project_ids
        }
        return self._post('updateProjectOrders', params)

    def delete_project(self, token, project_id):
        """Delete a user's project.

        :param token: The user's login token.
        :type token: str
        :param project_id: The ID of the project to delete.
        :type project_id: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> for project in projects:
        ...     if project['name'] == 'PyTodoist':
        ...         project_id = project['id']
        ...
        >>> response = api.get_project(user_token, project_id)
        >>> project = response.json()
        >>> print project['name']
        PyTodoist
        >>> project_id = project['id']
        >>> api.delete_project(user_token, project_id)
        >>> response = api.get_project(user_token, project_id)
        >>> print response.text
        "ERROR_PROJECT_NOT_FOUND"
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._post('deleteProject', params)

    def archive_project(self, token, project_id):
        """Archive a user's project.

        .. warning:: Only works if the user has Todoist premium.

        :param token: The user's login token.
        :type token: str
        :param project_id: The ID of the project to archive.
        :type project_id: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain a list of archived
            project IDs. e.g. ``[1234, 3435, 5235]``. The list will be empty
            if the user does not have Todoist premium.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> for project in projects:
        ...     if project['name'] == 'PyTodoist':
        ...         project_id = project['id']
        ...
        >>> response = api.archive_project(user_token, project_id)
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._post('archiveProject', params)

    def get_archived_projects(self, token):
        """Returns a user's archived projects.

        :param token: The user's login token.
        :type token: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain a list of archived
            project IDs. e.g. ``[1234, 3435, 5235]``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_archived_projects(user_token)
        >>> archived_project_ids = response.json()
        """
        params = {
            'token': token
        }
        return self._get('getArchived', params)

    def unarchive_project(self, token, project_id):
        """Unarchive a user's project.

        .. warning:: Only works if the user has Todoist premium.

        :param token: The user's login token.
        :type token: str
        :param project_id: The ID of the project to unarchive.
        :type project_id: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain a list of unarchived
            project IDs. e.g. ``[1234, 3435, 5235]``. The list will be empty
            if the user does not have Todoist premium.

        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> for project in projects:
        ...     if project['name'] == 'PyTodoist':
        ...         project_id = project['id']
        ...
        >>> response = api.unarchive_project(user_token, project_id)
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._post('unarchiveProject', params)

    def get_labels(self, token, **kwargs):
        """Return all of a user's labels.

        :param token: The user's login token.
        :type token: str
        :param as_list: If ``1``, return a list of label names only.
        :type as_list: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain a map of
            label name -> label details.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> api.add_label(user_token, 'Python')
        >>> response = api.get_labels(user_token)
        >>> labels = response.json().values()
        >>> for label in labels:
        ...     print label['name']
        ...
        Python
        """
        params = {
            'token': token
        }
        return self._get('getLabels', params, **kwargs)

    def add_label(self, token, label_name, **kwargs):
        """Add a label.

        If a label with the given name already exists it will be returned.

        :param token: The user's login token.
        :type token: str
        :param label_name: The name of the label.
        :type label_name: str
        :param color: The color of the label.
        :type color: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the label details.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_label(user_token, 'Python')
        >>> label = response.json()
        >>> print label['name']
        Python
        """
        params = {
            'token': token,
            'name': label_name
        }
        return self._post('addLabel', params, **kwargs)

    def update_label_name(self, token, label_name, new_name):
        """Update the name of a user's label.

        :param token: The user's login token.
        :type token: str
        :param label_name: The current name of the label.
        :type label_name: str
        :param new_name: The new name of the label.
        :type new_name: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the label details.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_label(user_token, 'Python')
        >>> label = response.json()
        >>> print label['name']
        Python
        >>> response = api.update_label_name(user_token, 'Python', 'Cobra')
        >>> label = response.json()
        >>> print label['name']
        Cobra
        """
        params = {
            'token': token,
            'old_name': label_name,
            'new_name': new_name
        }
        return self._post('updateLabel', params)

    def update_label_color(self, token, label_name, color):
        """Update the color of a user's label.

        :param token: The user's login token.
        :type token: str
        :param label_name: The name of the label.
        :type label_name: str
        :param color: The new color of the label.
        :type color: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the label details.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_label(user_token, 'Python')
        >>> label = response.json()
        >>> print label['color']
        0
        >>> response = api.update_label_name(user_token, 'football', color=1)
        >>> label = response.json()
        >>> print label['color']
        1
        """
        params = {
            'token': token,
            'name': label_name,
            'color': color
        }
        return self._post('updateLabelColor', params)

    def delete_label(self, token, label_name):
        """Delete a user's label.

        :param token: The user's login token.
        :type token: str
        :param label_name: The name of the label.
        :type label_name: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.delete_label(user_token, 'Python')
        >>> print response.text
        "ok"
        """
        params = {
            'token': token,
            'name': label_name
        }
        return self._post('deleteLabel', params)

    def get_uncompleted_tasks(self, token, project_id, **kwargs):
        """Return a list of a project's uncompleted tasks.

        :param token: The user's login token.
        :type token: str
        :param project_id: The ID of the project to get tasks from.
        :type project_id: str
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain a list of tasks.
        :on failure: ``response.status_code`` will be ``400``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> uncompleted_tasks = []
        >>> for project in projects:
        ...     response = api.get_uncompleted_tasks(user_token, project['id'])
        ...     uncompleted_tasks.append(response.json())
        ...
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
        :type token: str
        :param project_id: Filter the tasks by project.
        :type project_id: str
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :param label: Filter the tasks by label.
        :type label: str
        :param interval: Filter the tasks by time range.
            Defaults to ``past 2 weeks``.
        :type interval: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain a list of tasks. The list
            will be empty is the user does not have Todoist premium.
        :on failure: ``response.status_code`` will be ``400``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_all_completed_tasks(user_token)
        >>> completed_tasks = response.json()
        """
        params = {
            'token': token
        }
        return self._get('getAllCompletedItems', params, **kwargs)

    def get_completed_tasks(self, token, project_id, **kwargs):
        """Return a list of a project's completed tasks.

        :param token: The user's login token.
        :type token: str
        :param project_id: The project to get tasks from.
        :type project_id: str
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain a list of tasks.
        :on failure: ``response.status_code`` will be ``400``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> completed_tasks = []
        >>> for project in projects:
        ...     response = api.get_completed_tasks(user_token, project['id'])
        ...     completed_tasks.append(response.json())
        ...
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('getCompletedItems', params, **kwargs)

    def get_tasks_by_id(self, token, task_ids, **kwargs):
        """Return a list of tasks with given IDs.

        :param token: The user's login token.
        :type token: str
        :param task_ids: A list of task IDs.
        :type task_ids: str
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain a list of tasks.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> for project in projects:
        ...     if project['name'] == 'PyTodoist':
        ...         project_id = project['id']
        ...
        >>> task_ids = str([project_id])
        >>> response = api.get_tasks_by_id(user_token, task_ids)
        >>> tasks = response.json()
        >>> len(tasks)
        1
        >>> pytodoist_task = tasks[0]
        >>> print pytodoist_task['name']
        PyTodoist
        """
        params = {
            'token': token,
            'ids': task_ids
        }
        return self._get('getItemsById', params, **kwargs)

    def add_task(self, token, content, **kwargs):
        """Add a task to a project.

        :param token: The user's login token.
        :type token: str
        :param content: The task description.
        :type content: str
        :param project_id: The project to add the task to. Default is ``Inbox``
        :type project_id: str
        :param date_string: The deadline date for the task.
        :type date_string: str
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
        :type children: str
        :param labels: A list of label IDs.
        :type labels: str
        :param assigned_by_uid: The ID of the user who assigns current task.
            Accepts 0 or any user id from the list of project collaborators.
            If value is unset or invalid it will automatically be set up by
            your uid.
        :type assigned_by_uid: str
        :param responsible_uid: The id of user who is responsible for
            accomplishing the current task. Accepts 0 or any user id from
            the list of project collaborators. If the value is unset or
            invalid it will automatically be set to null.
        :type responsible_uid: str
        :param note: Content of a note to add.
        :type note: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the task details.
        :on failure: ``response.status_code`` will be ``400`` or
            ``response.text`` will contain ``"ERROR_WRONG_DATE_SYNTAX"``

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Install PyTodoist')
        >>> task = response.json()
        >>> print task['content']
        Install PyTodoist
        """
        params = {
            'token': token,
            'content': content
        }
        return self._post('addItem', params, **kwargs)

    def update_task(self, token, task_id, **kwargs):
        """Update the details of a task.

        :param token: The user's login token.
        :type token: str
        :param task_id: The ID of the task to update.
        :type task_id: str
        :param content: The new task description.
        :type content: str
        :param project_id: The new project.
        :type project_id: str
        :param date_string: The new deadline date for the task.
        :type date_string: str
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
        :type children: str
        :param labels: The new list of label IDs.
        :type labels: str
        :param assigned_by_uid: New ID of the user who assigns current task.
            Accepts 0 or any user id from the list of project collaborators.
            If value is unset or invalid it will automatically be set up by
            your uid.
        :type assigned_by_uid: str
        :param responsible_uid: The new id of user who is responsible for
            accomplishing the current task. Accepts 0 or any user id from
            the list of project collaborators. If the value is unset or
            invalid it will automatically be set to null.
        :type responsible_uid: str
        :param note: Content of a note to add.
        :type note: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the updated task details.
        :on failure: ``response.text`` will contain ``"ERROR_ITEM_NOT_FOUND"``

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Install PyTodoist')
        >>> task = response.json()
        >>> print task['content']
        Install PyTodoist
        >>> task_id = task['id']
        >>> response = api.update_task(user_token, task_id,
                                       content='Read Docs')
        >>> task = response.json()
        >>> print task['content']
        Read Docs
        """
        params = {
            'token': token,
            'id': task_id
        }
        return self._post('updateItem', params, **kwargs)

    def update_task_ordering(self, token, project_id, task_ids):
        """Update the order of a project's tasks.

        :param token: The user's login token.
        :type token: str
        :param project_id: The new project.
        :type project_id: str
        :param task_ids: An ordered list of task IDs.
        :type task_ids: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``
        :on failure: ``response.status_code`` will be ``400``

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_projects(user_token)
        >>> projects = response.json()
        >>> for project in projects:
        ...     if project['name'] == 'Inbox':
        ...         project_id = project['id']
        ...
        >>> response = api.get_uncompleted_tasks(user_token, project_id)
        >>> tasks = response.json()
        >>> task_ids = [task['id'] for task in tasks]
        >>> reverse_task_ids = str(task_ids[::-1])
        >>> api.update_task_ordering(user_token, reverse_task_ids)
        """
        params = {
            'token': token,
            'project_id': project_id,
            'item_id_list': task_ids
        }
        return self._post('updateOrders', params)

    def move_tasks(self, token, task_locations, project_id):
        """Move tasks to another project.

        :param token: The user's login token.
        :type token: str
        :param task_locations: The current locations of the tasks to move. It
            is a map of ``project_id -> task_id`` e.g. ``{'1534': ['23453']}``.
        :type task_locations: str
        :param project_id: The project to move the tasks to.
        :type project_id: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the task counts of each
            project e.g. ``{"counts": {"1523": 0, "1245": 1}}``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> task_locations = '{'1534': ['23453']}'
        >>> project_id = '1234'
        >>> response = api.move_tasks(user_token, task_locations, project_id)
        >>> print response.json()
        {"counts": {"1534": 0, "1245": 1}}
        """
        params = {
            'token': token,
            'project_items': task_locations,
            'to_project': project_id
        }
        return self._post('moveItems', params)

    def advance_recurring_dates(self, token, task_ids, **kwargs):
        """Update the recurring dates of a list of tasks. The date
        will be advanced to the next date with respect to their 'date_str'.

        :param token: The user's login token.
        :type token: str
        :param task_ids: The IDs of the tasks to update.
        :type task_ids: str
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the list of updated
            tasks.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        ... # Get the ID(s) of the task(s) you want to update.
        >>> task_ids = '[1234, 5678]'
        >>> response = api.advance_recurring_dates(user_token, task_ids)
        >>> tasks = response.json()
        >>> len(tasks)
        1
        """
        params = {
            'token': token,
            'ids': task_ids
        }
        return self._post('updateRecurringDate', params, **kwargs)

    def delete_tasks(self, token, task_ids):
        """Delete a given list of tasks.

        :param token: The user's login token.
        :type token: str
        :param task_ids: The IDs of the tasks to delete.
        :type task_ids: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Install PyTodoist')
        >>> task = response.json()
        >>> task_id = task['id']
        >>> task_ids = str([task_id])
        >>> response = api.delete_tasks(user_token, task_ids)
        >>> print response.text
        "ok"
        """
        params = {
            'token': token,
            'ids': task_ids
        }
        return self._post('deleteItems', params)

    def complete_tasks(self, token, task_ids, **kwargs):
        """Complete a given list of tasks.

        :param token: The user's login token.
        :type token: str
        :param task_ids: The IDs of the tasks to complete.
        :type task_ids: str
        :param in_history: If ``0``, tasks will not be moved to the history.
        :type in_history: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Install PyTodoist')
        >>> task = response.json()
        >>> task_id = task['id']
        >>> task_ids = str([task_id])
        >>> response = api.complete_tasks(user_token, task_ids)
        >>> print response.text
        "ok"
        """
        params = {
            'token': token,
            'ids': task_ids
        }
        return self._post('completeItems', params, **kwargs)

    def uncomplete_tasks(self, token, task_ids, **kwargs):
        """Uncomplete a given list of tasks.

        :param token: The user's login token.
        :type token: str
        :param task_ids: The IDs of the tasks to complete.
        :type task_ids: str
        :param in_history: If ``0``, tasks will not be moved to the history.
        :type in_history: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Install PyTodoist')
        >>> task = response.json()
        >>> task_id = task['id']
        >>> task_ids = str([task_id])
        >>> response = api.complete_tasks(user_token, task_ids)
        >>> print response.text
        "ok"
        """
        params = {
            'token': token,
            'ids': task_ids
        }
        return self._post('uncompleteItems', params, **kwargs)

    def add_note(self, token, task_id, note_content):
        """Add a note to a task.

        :param token: The user's login token.
        :type token: str
        :param task_id: The ID of the task to add the note to.
        :type task_id: str
        :param note_content: The note to add.
        :type note_content: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the note details.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Install PyTodoist')
        >>> task = response.json()
        >>> response = api.add_note(user_token, task['id'], 'Do it now!')
        >>> note = response.json()
        >>> print note['content']
        Do it now!
        """
        params = {
            'token': token,
            'item_id': task_id,
            'content': note_content
        }
        return self._post('addNote', params)

    def update_note(self, token, note_id, new_content):
        """Update the content of a note.

        :param token: The user's login token.
        :type token: str
        :param note_id: The ID of the note to update.
        :type note_id: str
        :param new_content: The new note content.
        :type new_content: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Install PyTodoist')
        >>> task = response.json()
        >>> response = api.add_note(user_token, task['id'], 'Do it now!')
        >>> note = response.json()
        >>> print note['content']
        Do it now!
        >>> note_id = note['id']
        >>> response = api.update_note(user_token, note_id, 'Hurry up!')
        >>> note = response.json()
        >>> print note['content']
        Hurry up!
        """
        params = {
            'token': token,
            'note_id': note_id,
            'content': new_content
        }
        return self._post('updateNote', params)

    def delete_note(self, token, task_id, note_id):
        """Delete a note from a task.

        :param token: The user's login token.
        :type token: str
        :param task_id: The ID of the task to delete the note from.
        :type task_id: str
        :param note_id: The ID of the note to delete.
        :type note_id: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Install PyTodoist')
        >>> task = response.json()
        >>> response = api.add_note(user_token, task['id'], 'Do it now!')
        >>> note = response.json()
        >>> response = api.delete_note(user_token, task['id'], note['id'])
        >>> print response.text
        "ok"
        """
        params = {
            'token': token,
            'item_id': task_id,
            'note_id': note_id
        }
        return self._post('deleteNote', params)

    def get_notes(self, token, task_id):
        """Return the list of notes for a task.

        :param token: The user's login token.
        :type token: str
        :param task_id: The ID of the task to get the notes from.
        :type task_id: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain a list of notes.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Install PyTodoist')
        >>> task = response.json()
        >>> api.add_note(user_token, task['id'], 'Do it now!')
        >>> response = api.get_notes(user_token, task['id'])
        >>> notes = response.json()
        >>> len(notes)
        1
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
        :type token: str
        :param queries: A list of queries.
        :type queries: str
        :param as_count: If ``1``, a count of the tasks will be returned.
        :type as_count: int
        :param js_date: If ``1``: ``new Date("Sun Apr 29 2007 23:59:59")``,
            otherwise ``Sun Apr 2007 23:59:59``.
        :type js_date: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain a list of queries and
            the tasks that matched them.

        .. note:: See https://todoist.com/Help/timeQuery for valid queries.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> queries = str(['tomorrow'])
        >>> response = api.search_tasks(user_token, queries, as_count=1)
        >>> counts = response.json()
        >>> print counts
        [{"count": 0, "query": "tomorrow", "type": "date"}]
        """
        params = {
            'token': token,
            'queries': queries
        }
        return self._get('query', params, **kwargs)

    def get_notes_and_task(self, token, task_id):
        """Return the list of notes for a task and the task itself.

        :param token: The user's login token.
        :type token: str
        :param task_id: The ID of the task.
        :type task_id: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain the task and notes.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.add_task(user_token, 'Install PyTodoist')
        >>> task = response.json()
        >>> api.add_note(user_token, task['id'], 'Do it now!')
        >>> response = api.get_notes_and_task(user_token, task['id'])
        >>> results = response.json()
        >>> task = results['item']
        >>> notes = results['notes']
        >>> print len(notes)
        1
        """
        params = {
            'token': token,
            'item_id': task_id
        }
        return self._get('getNotesData', params)

    def get_notification_settings(self, token):
        """Return a user's notification settings.

        :param token: The user's login token.
        :type token: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.json()`` will contain a list of settings.

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.get_notification_settings(user_token)
        >>> print response.json()
        {u'user_left_project':
            {u'notify_push': True, u'notify_email': False},
            ...
        }
        """
        params = {
            'token': token
        }
        return self._get('getNotificationSettings', params)

    def update_notification_settings(self, token, event,
                                     service, should_notify):
        """Update a user's notification settings.

        :param token: The user's login token.
        :type token: str
        :param event: Update the notification settings of this event.
        :type event: str
        :param service: ``email`` or ``push``
        :type service: str
        :param should_notify: If ``0`` notify, otherwise do not.
        :type should_notify: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        :on success: ``response.text`` will contain ``"ok"``

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_token = user_info['token']
        >>> response = api.update_notification_settings(user_token,
        ...                                             'user_left_project',
        ...                                             'email', 0)
        ...
        """
        params = {
            'token': token,
            'notification_type': event,
            'service': service,
            'dont_notify': should_notify
        }
        return self._post('updateNotificationSetting', params)

    def is_response_success(self, response):
        """Return True if the given response contains no todoist API errors
        and indicates a successful request.

        :param response: The response to check.
        :type response: :class:`requests.Response`
        :return: True if the request was successful, false otherwise.
        :rtype: bool

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> is_successful_request = api.is_response_success(response)
        >>> print is_successful_request
        True
        """
        return (response.status_code == _HTTP_OK and
                response.text not in self.ERROR_TEXT_RESPONSES)

    def _get(self, end_point, params=None, **kwargs):
        """Send a HTTP GET request to a Todoist API end-point.

        :param end_point: The Todoist API end-point.
        :type end_point: str
        :param params: The required request parameters.
        :type params: dict
        :param kwargs: Any optional parameters.
        :type kwargs: dict
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        """
        return self._request(requests.get, end_point, params, **kwargs)

    def _post(self, end_point, params=None, files=None, **kwargs):
        """Send a HTTP POST request to a Todoist API end-point.

        :param end_point: The Todoist API end-point.
        :type end_point: str
        :param params: The required request parameters.
        :type params: dict
        :param files: Any files that are being sent as multipart/form-data.
        :type files: dict
        :param kwargs: Any optional parameters.
        :type kwargs: dict
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        """
        return self._request(requests.post, end_point, params, files, **kwargs)

    def _request(self, req_func, end_point, params=None, files=None, **kwargs):
        """Send a HTTP request to a Todoist API end-point.

        :param req_func: The request function to use e.g. get or post.
        :type req_func: A request function from the :class:`requests` module.
        :param end_point: The Todoist API end-point.
        :type end_point: str
        :param params: The required request parameters.
        :type params: dict
        :param files: Any files that are being sent as multipart/form-data.
        :type files: dict
        :param kwargs: Any optional parameters.
        :type kwargs: dict
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        """
        url = self.URL + end_point
        if params and kwargs:
            params.update(kwargs)
        return req_func(url, params=params, files=files)
