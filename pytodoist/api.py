"""This module is a pure wrapper around version 6 of the Todoist API.

If you do not need access to the raw HTTP response to the request, consider
using the higher level abstractions implemented in the :mod:`pytodoist.todoist`
module.

*Example:*

>>> from pytodoist.api import TodoistAPI
>>> api = TodoistAPI()
>>> response = api.login('john.doe@gmail.com', 'password')
>>> user_info = response.json()
>>> full_name = user_info['full_name']
>>> print(full_name)
John Doe
"""
import os
import requests

# No magic numbers
_HTTP_OK = 200


class TodoistAPI(object):
    """A wrapper around version 7 of the Todoist API.

    >>> from pytodoist.api import TodoistAPI
    >>> api = TodoistAPI()
    >>> print(api.URL)
    https://api.todoist.com/API/v7/
    """

    VERSION = '7'
    URL = 'https://api.todoist.com/API/v{0}/'.format(VERSION)

    def login(self, email, password):
        """Login to Todoist.

        :param email: The user's email address.
        :type email: str
        :param password: The user's password.
        :type password: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> full_name = user_info['full_name']
        >>> print(full_name)
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
        :param lang: The user's language.
        :type lang: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> oauth2_token = 'oauth2_token'  # Get this from Google.
        >>> response = api.login_with_google('john.doe@gmail.com',
        ...                                  oauth2_token)
        >>> user_info = response.json()
        >>> full_name = user_info['full_name']
        >>> print(full_name)
        John Doe
        """
        params = {
            'email': email,
            'oauth2_token': oauth2_token
        }
        req_func = self._get
        if kwargs.get('auto_signup', 0) == 1:  # POST if we're creating a user.
            req_func = self._post
        return req_func('login_with_google', params, **kwargs)

    def register(self, email, full_name, password, **kwargs):
        """Register a new Todoist user.

        :param email: The user's email.
        :type email: str
        :param full_name: The user's full name.
        :type full_name: str
        :param password: The user's password.
        :type password: str
        :param lang: The user's language.
        :type lang: str
        :param timezone: The user's timezone.
        :type timezone: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.register('john.doe@gmail.com', 'John Doe',
        ...                         'password')
        >>> user_info = response.json()
        >>> full_name = user_info['full_name']
        >>> print(full_name)
        John Doe
        """
        params = {
            'email': email,
            'full_name': full_name,
            'password': password
        }
        return self._post('register', params, **kwargs)

    def delete_user(self, api_token, password, **kwargs):
        """Delete a registered Todoist user's account.

        :param api_token: The user's login api_token.
        :type api_token: str
        :param password: The user's password.
        :type password: str
        :param reason_for_delete: The reason for deletion.
        :type reason_for_delete: str
        :param in_background: If ``0``, delete the user instantly.
        :type in_background: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        """
        params = {
            'token': api_token,
            'current_password': password
        }
        return self._post('delete_user', params, **kwargs)

    def sync(self, api_token, sync_token, resource_types='["all"]', **kwargs):
        """Update and retrieve Todoist data.

        :param api_token: The user's login api_token.
        :type api_token: str
        :param seq_no: The request sequence number. On initial request pass
            ``0``. On all others pass the last seq_no you received.
        :type seq_no: int
        :param seq_no_global: The request sequence number. On initial request
            pass ``0``. On all others pass the last seq_no you received.
        :type seq_no_global: int
        :param resource_types: Specifies which subset of data you want to
           receive e.g. only projects. Defaults to all data.
        :type resources_types: str
        :param commands: A list of JSON commands to perform.
        :type commands: list (str)
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.register('john.doe@gmail.com', 'John Doe',
        ...                         'password')
        >>> user_info = response.json()
        >>> api_token = user_info['api_token']
        >>> response = api.sync(api_token, 0, 0, '["projects"]')
        >>> print(response.json())
        {'seq_no_global': 3848029654, 'seq_no': 3848029654, 'Projects': ...}
        """
        params = {
            'token': api_token,
            'sync_token': sync_token,
        }
        req_func = self._post
        if 'commands' not in kwargs:  # GET if we're not changing data.
            req_func = self._get
            params['resource_types'] = resource_types
        return req_func('sync', params, **kwargs)

    def query(self, api_token, queries, **kwargs):
        """Search all of a user's tasks using date, priority and label queries.

        :param api_token: The user's login api_token.
        :type api_token: str
        :param queries: A JSON list of queries to search. See examples
            `here <https://todoist.com/Help/timeQuery>`_.
        :type queries: list (str)
        :param as_count: If ``1`` then return the count of matching tasks.
        :type as_count: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        """
        params = {
            'token': api_token,
            'queries': queries
        }
        return self._get('query', params, **kwargs)

    def add_item(self, api_token, content, **kwargs):
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

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_api_token = user_info['token']
        >>> response = api.add_item(user_api_token, 'Install PyTodoist')
        >>> task = response.json()
        >>> print(task['content'])
        Install PyTodoist
        """
        params = {
            'token': api_token,
            'content': content
        }
        return self._post('add_item', params, **kwargs)

    def get_all_completed_tasks(self, api_token, **kwargs):
        """Return a list of a user's completed tasks.

        .. warning:: Requires Todoist premium.

        :param api_token: The user's login api_token.
        :type api_token: str
        :param project_id: Filter the tasks by project.
        :type project_id: str
        :param limit: The maximum number of tasks to return
            (default ``30``, max ``50``).
        :type limit: int
        :param offset: Used for pagination if there are more tasks than limit.
        :type offset: int
        :param from_date: Return tasks with a completion date on or older than
            from_date. Formatted as ``2007-4-29T10:13``.
        :type from_date: str
        :param to: Return tasks with a completion date on or less than
            to_date. Formatted as ``2007-4-29T10:13``.
        :type from_date: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_api_token = user_info['api_token']
        >>> response = api.get_all_completed_tasks(user_api_token)
        >>> completed_tasks = response.json()
        """
        params = {
            'token': api_token
        }
        return self._get('get_all_completed_items', params, **kwargs)

    def upload_file(self, api_token, file_path, **kwargs):
        """Upload a file suitable to be passed as a file_attachment.

        :param api_token: The user's login api_token.
        :type api_token: str
        :param file_path: The path of the file to be uploaded.
        :type file_path: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        """
        params = {
            'token': api_token,
            'file_name': os.path.basename(file_path)
        }
        with open(file_path, 'rb') as f:
            files = {'file': f}
            return self._post('upload_file', params, files, **kwargs)

    def get_productivity_stats(self, api_token, **kwargs):
        """Return a user's productivity stats.

        :param api_token: The user's login api_token.
        :type api_token: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`
        """
        params = {
            'token': api_token
        }
        return self._get('get_productivity_stats', params, **kwargs)

    def update_notification_settings(self, api_token, event,
                                     service, should_notify):
        """Update a user's notification settings.

        :param api_token: The user's login api_token.
        :type api_token: str
        :param event: Update the notification settings of this event.
        :type event: str
        :param service: ``email`` or ``push``
        :type service: str
        :param should_notify: If ``0`` notify, otherwise do not.
        :type should_notify: int
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_api_token = user_info['api_token']
        >>> response = api.update_notification_settings(user_api_token,
        ...                                             'user_left_project',
        ...                                             'email', 0)
        ...
        """
        params = {
            'token': api_token,
            'notification_type': event,
            'service': service,
            'dont_notify': should_notify
        }
        return self._post('update_notification_setting', params)

    def get_redirect_link(self, api_token, **kwargs):
        """Return the absolute URL to redirect or to open in
        a browser. The first time the link is used it logs in the user
        automatically and performs a redirect to a given page. Once used,
        the link keeps working as a plain redirect.

        :param api_token: The user's login api_token.
        :type api_token: str
        :param path: The path to redirect the user's browser. Default ``/app``.
        :type path: str
        :param hash: The has part of the path to redirect the user's browser.
        :type hash: str
        :return: The HTTP response to the request.
        :rtype: :class:`requests.Response`

        >>> from pytodoist.api import TodoistAPI
        >>> api = TodoistAPI()
        >>> response = api.login('john.doe@gmail.com', 'password')
        >>> user_info = response.json()
        >>> user_api_token = user_info['api_token']
        >>> response = api.get_redirect_link(user_api_token)
        >>> link_info = response.json()
        >>> redirect_link = link_info['link']
        >>> print(redirect_link)
        https://todoist.com/secureRedirect?path=adflk...
        """
        params = {
            'token': api_token
        }
        return self._get('get_redirect_link', params, **kwargs)

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
