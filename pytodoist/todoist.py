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

        See:
          https://todoist.com/API/#users
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
          https://todoist.com/API/#users
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
        if kwargs:
            params.update(kwargs)
        return self._get('loginWithGoogle', params)

    def ping(self, token):
        """Test a user's login token.

        See:
          https://todoist.com/API/#users
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

        See:
          https://todoist.com/API/#users
        Returns:
          response (requests.Response): Contains the status of the request.

          On success:
            response.status_code: 200
            response.json(): Contains a list of supported timezones.
        """
        return self._get('getTimezones')

    def register(self, email, full_name, password, **kwargs):
        """Register a new user on Todoist.

        See:
          https://todoist.com/API/#users
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
        if kwargs:
            params.update(kwargs)
        return self._get('register', params)

    def delete_user(self, token, current_password, **kwargs):
        """Delete a registered Todoist user.

        See:
          https://todoist.com/API/#users
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
        if kwargs:
            params.update(kwargs)
        return self._get('deleteUser', params)

    def _get(self, end_point, params=None):
        """Send a HTTP GET request to a Todoist API end-point.

        Args:
          end_point (str): The Todoist API end-point e.g. 'login'.
          params (dict): The HTTP GET request parameters.
        Returns:
          response (requests.Response): Contains the status of the request.
        """
        return requests.get(self.api_url + end_point, params=params)
