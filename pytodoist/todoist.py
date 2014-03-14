"""A Python wrapper for the Todoist web API.

This module contains functionality for accessing the Todoist API using Python.
"""
import requests

class Todoist(object):
    """A wrapper around the Todoist web API: https://todoist.com/API

    Attributes:
      api_url (str): The URL of the Todoist API.
    """

    api_url = 'https://www.todoist.com/API/'

    def login(self, email, password):
        """Request to login to Todoist.

        Args:
          email (str): A Todoist user's email.
          password (str):  A Todoist user's password.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.json(): Contains the user details.

          On failure:
            response.text will contain "LOGIN_ERROR".
        """
        params = {'email': email, 'password': password}
        return self._get('login', params)

    def login_with_google(self, email, oauth2_token, **kwargs):
        """Request to login to Todoist using Google oauth2.

        See:
          https://developers.google.com/accounts/docs/OAuth2
        Args:
          email (str): A Todoist user's Google email.

          oauth2_token (str):  A valid oauth2_token for the user
                               retrevied from Google's oauth2 service.

          auto_signup (int, optional): If 1 and a new user, automatically
                                       register an account.

          full_name (str, optional): The user's full name if they are about
                                     to be registered. If not set, a nickname
                                     based on the email is used.

          timezone (str, optional): The user's timezone if they are about to
                                    be registered. If not set, a timezone based
                                    on the user's IP address is used.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.json(): Contains the user details.

          On failure:
           response.text:
             "LOGIN_ERROR": The oauth2_token is invalid or outdated.

             "INTERNAL_ERROR": The server is unable to check the token validity.
                               Try again later.

             "EMAIL_MISMATCH": The token is valid but the email doesn't
                               match it.

             "ACCOUNT_NOT_CONNECTED_WITH_GOOGLE": The token and email are valid,
                                                  but the Todoist account is not
                                                  connected with Google.
        """
        params = {'email': email, 'oauth2_token': oauth2_token}
        return self._get('loginWithGoogle', params, **kwargs)

    def ping(self, token):
        """Test a user's login token.

        Args:
          token (str): A Todoist user's login token.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.text: "ok"

          On failure:
            response.status_code: 401
            response.text: "Token not correct!"
        """
        params = {'token': token}
        return self._get('ping', params)

    def get_timezones(self):
        """Get the timezones that Todoist supports.

        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.json(): Contains a list of supported timezones.
        """
        return self._get('getTimezones')

    def register(self, email, full_name, password, **kwargs):
        """Register a new user on Todoist.

        Args:
          email (str): The user's email.
          full_name (str): The user's full name.
          password (str): The user's password (>= 5 chars).
          lang (str, optional): The user's language.
          timezone (str, optional): The user's timezone.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.json(): Contains the newly registered user details.

          On failure:
            response.text:
              "ALREADY_REGISTRED"
              "TOO_SHORT_PASSWORD"
              "INVALID_EMAIL"
              "INVALID_TIMEZONE"
              "INVALID_FULL_NAME"
              "UNKNOWN_ERROR"
        """
        params = {'email': email, 'full_name': full_name, 'password': password}
        return self._get('register', params, **kwargs)

    def delete_user(self, token, current_password, **kwargs):
        """Delete a registered Todoist user.

        Args:
          token (str): The user's login token.
          password (str): The user's current password.
          reason_for_delete (str, optional): The reason for deletion.
          in_background (int, optional): Default is 1, set to 0 if the user
                                         should be deleted instantly.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.text: "ok"

          On failure:
            response.status_code: 403
        """
        params = {'token': token, 'current_password': current_password}
        return self._get('deleteUser', params, **kwargs)

    def update_user(self, token, **kwargs):
        """Update a registered Todoist user.

        Args:
          token (str): The user's login token.
          email (str, optional): The updated email address.
          full_name (str, optional): The updated full name.
          password (str, optional): The updated password (>= 5 chars).
          timezone (str, optional): The updated Todoist supported timezone.
          date_format (int, optional): If 0: DD-MM-YYYY. If 1 MM-DD-YYYY.
          time_format (int, optional): If 0: '13:00'. If 1: '1:00pm'.
          start_day (int, optional): The first day of the week:
                                     (1-7 - Mon-Sun).
          next_week (int, optional): Which day to use when postponing:
                                     (1-7 - Mon-Sun).

          start_page (str, optional):
            "_blank" to show a blank page.
            "_info_page" to show the info page.
            "_project_$PROJECT_ID" to show a project page.
            "$ANY_QUERY" to query for anything.

          default_reminder (str, optional):
            "email" to send reminders by email.
            "mobile" to send reminders via sms.
            "push" to send reminders to smart devices.
            "no_default" to turn off notifications.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.json(): Contains the updated user data.

          On failure:
            response.text:
              "ERROR_PASSWORD_TOO_SHORT"
              "ERROR_EMAIL_FOUND"
        """
        params = {'token': token}
        return self._get('updateUser', params, **kwargs)

    def update_avatar(self, token, **kwargs):
        """Update a registered Todoist user's avatar.

        Args:
          token (str): The user's login token.
          image (str, optional): The avatar image. Must be encoded with
                                 multipart/form-data - Max size 2mb.
          delete (bool, optional): If true, delete current avatar
                                   and use default.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.json(): Contains the updated user data.

          On failure:
            response.text:
              "UNKNOWN_IMAGE_FORMAT"
              "UNABLE_TO_RESIZE_IMAGE"
              "IMAGE_TOO_BIG"
        """
        params = {'token': token}
        return self._get('updateAvatar', params, **kwargs)

    def get_projects(self, token):
        """Get a list of all of a user's projects.

        Args:
          token (str): The user's login token.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.json(): Contains a list of that user's projects.
        """
        params = {'token': token}
        return self._get('getProjects', params)

    def get_project(self, token, project_id):
        """Get details about a user's project.

        Args:
          token (str): The user's login token.
          project_id (str): The id of the project to fetch.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.json(): Contains the project data.

          On failure:
            response.text:
              "ERROR_PROJECT_NOT_FOUND"
        """
        params = {'token': token, 'project_id': project_id}
        return self._get('getProject', params)

    def add_project(self, token, name, **kwargs):
        """Add a new project.

        Args:
          token (str): The user's login token.
          name (str): The name of the new project.
          color (str, optional): The color of the new project.
          indent (int, optional): The indent of the project (1-4).
          order (int, optional): The order of the project (1+).
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.json(): Contains the new project data.

          On failure:
            response.text:
              "ERROR_NAME_IS_EMPTY"
        """
        params = {'token': token, 'name': name}
        return self._get('addProject', params, **kwargs)

    def update_project(self, token, project_id, **kwargs):
        """Update an existing project.

        Args:
          token (str): The user's login token.
          project_id (str): The ID of the project to update.
          name (str, optional): The name of the new project.
          color (str, optional): The color of the new project.
          indent (int, optional): The indent of the project (1-4).
          order (int, optional): The order of the project (1+).
          collapsed (int, optional): 1 - collapsed, otherwise 0.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.json(): Contains the updated project data.

          On failure:
            response.text:
              "ERROR_PROJECT_NOT_FOUND"
        """
        params = {'token': token, 'project_id': project_id}
        return self._get('updateProject', params, **kwargs)

    def update_project_orders(self, token, project_ids):
        """Update how the projects are ordered.

        Args:
          token (str): The user's login token.
          project_ids (list): An ordered list of project IDs.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.text: "ok"

          On failure:
            response.text:
              "ERROR_PROJECT_NOT_FOUND"
        """
        params = {'token': token, 'item_id_list': str(project_ids)}
        return self._get('updateProjectOrders', params)

    def delete_project(self, token, project_id):
        """Delete the project with 'project_id'.

        Args:
          token (str): The user's login token.
          project_id (str): The id of the project to delete.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.text: "ok"
        """
        params = {'token': token, 'project_id': project_id}
        return self._get('deleteProject', params)

    def archive_project(self, token, project_id):
        """Archive the project with 'project_id'.

        Args:
          token (str): The user's login token.
          project_id (str): The id of the project to archive.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.json(): A list of archived project_ids e.g.
                             [1234,4324,3242]. [] if the user does
                             not have Todoist premium
        Note:
          Only available for Todoist premium users.
        """
        params = {'token': token, 'project_id': project_id}
        return self._get('archiveProject', params)

    def unarchive_project(self, token, project_id):
        """Unarchive the project with 'project_id'.

        Args:
          token (str): The user's login token.
          project_id (str): The id of the project to unarchive.
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.json(): A list of unarchived project_ids e.g.
                             [1234,4324,3242]. [] if the user does
                             not have Todoist premium
        Note:
          Only available for Todoist premium users.
        """
        params = {'token': token, 'project_id': project_id}
        return self._get('unarchiveProject', params)

    def _get(self, end_point, params=None, **kwargs):
        """Send a HTTP GET request to a Todoist API end-point.

        Args:
          end_point (str): The Todoist API end-point e.g. 'login'.
          params (dict): The required HTTP GET request parameters.
          kwargs (dict): Contains any additional parameters.
        Returns:
          response (requests.Response): Contains the status of the request.
        """
        if params and kwargs:
            params.update(kwargs)
        return requests.get(self.api_url + end_point, params=params)
