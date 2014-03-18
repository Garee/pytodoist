"""This module provides an abstract method for interacting with the Todoist API.

Classes:
    Todoist: A simple wrapper around the Todoist API using the requests module.
"""
import requests

class Todoist(object):
    """A wrapper around the Todoist web API: https://todoist.com/API

    Attributes:
      api_url (str): The URL of the Todoist API.
    """

    api_url = 'https://www.todoist.com/API/'

    def login(self, email, password):
        """Login to Todoist.

        Args:
            email (str): A Todoist user's email.
            password (str):  A Todoist user's password.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
              response.json(): The user's details.

            On failure:
              response.text: "LOGIN_ERROR".
        """
        params = {
            'email': email,
            'password': password
        }
        return self._get('login', params)

    def login_with_google(self, email, oauth2_token, **kwargs):
        """Login to Todoist using Google oauth2 authentication.

        Args:
            email (str): A Todoist user's Google email.

            oauth2_token (str):
                A valid oauth2_token for the user retrieved from Google's oauth2
                service.

            auto_signup (int):
                If 1 and a new user, automatically register an account.

            full_name (str):
                A full name to use if the user is registering. If no name is
                given, an email based nickname is used.

            timezone (str):
                A timezone to use if the user is registering. If not set, one is
                chosen based on the user's IP address.

        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json(): The user's details.

            On failure:
                response.text:
                    "LOGIN_ERROR": The oauth2_token is invalid or outdated.

                    "INTERNAL_ERROR":
                        The server is unable to check the token validity. It is
                        a signal to try again later.


                    "EMAIL_MISMATCH":
                        The token is valid but the email is not associated with
                        it.

                    "ACCOUNT_NOT_CONNECTED_WITH_GOOGLE":
                        The token and email are valid but the account is not
                        connected using Google.
        """
        params = {
            'email': email,
            'oauth2_token': oauth2_token
        }
        return self._get('loginWithGoogle', params, **kwargs)

    def ping(self, token):
        """Test a user's login token.

        Args:
            token (str): A Todoist user's login token.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.text: "ok"

            On failure:
                response.status_code: 401
        """
        params = {
            'token': token
        }
        return self._get('ping', params)

    def get_timezones(self):
        """Return the timezones that Todoist supports.

        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json(): The supported timezones.
        """
        return self._get('getTimezones')

    def register(self, email, full_name, password, **kwargs):
        """Register a new user on Todoist.

        Args:
            email (str): The user's email.
            full_name (str): The user's full name.
            password (str): The user's password. Must be > 4 chars.
            lang (str): The user's language.
            timezone (str): The user's timezone.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json(): The user's details.

            On failure:
                response.text:
                    "ALREADY_REGISTRED"
                    "TOO_SHORT_PASSWORD"
                    "INVALID_EMAIL"
                    "INVALID_TIMEZONE"
                    "INVALID_FULL_NAME"
                    "UNKNOWN_ERROR"
        """
        params = {
            'email': email,
            'full_name': full_name,
            'password': password
        }
        return self._get('register', params, **kwargs)

    def delete_user(self, token, password, **kwargs):
        """Delete a registered Todoist user's account.

        Args:
            token (str): The user's login token.
            password (str): The user's password.
            reason_for_delete (str): The reason for deletion.
            in_background (int, default=1):
                If set to 0 if the user should be deleted instantly.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.status_code: 200
                response.text: "ok"

            On failure:
                response.status_code: 403 (The password doesn't match.)
        """
        params = {
            'token': token,
            'current_password': password
        }
        return self._get('deleteUser', params, **kwargs)

    def update_user(self, token, **kwargs):
        """Update a registered Todoist user's account.

        Args:
            token (str): The user's login token.
            email (str): The updated email address.
            full_name (str): The updated full name.
            password (str): The updated password. Must be > 4 chars.
            timezone (str): The updated Todoist supported timezone.
            date_format (int): If 0: DD-MM-YYYY. If 1: MM-DD-YYYY.
            time_format (int): If 0: '13:00'. If 1: '1:00pm'.
            start_day (int): The first day of the week (1-7 - Mon-Sun).
            next_week (int): Which day to use when postponing (1-7 - Mon-Sun).

            start_page (str):
                "_blank": Show a blank page.
                "_info_page": Show the info page.
                "_project_$PROJECT_ID": Show a project page.
                "$ANY_QUERY": To show query results.

            default_reminder (str):
                "email": Reminders by email.
                "mobile" Reminders via sms.
                "push": Reminders to smart devices.
                "no_default": Turn off notifications.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json(): The updated user's details.

            On failure:
              response.status_code: 400 (Password is too short.)
              response.text: "ERROR_EMAIL_FOUND"
        """
        params = {
            'token': token
        }
        return self._get('updateUser', params, **kwargs)

    def update_avatar(self, token, **kwargs):
        """Update a registered Todoist user's avatar.

        Args:
            token (str): The user's login token.
            image (str):
                The avatar image. Must be encoded with multipart/form-data.
                Max size: 2mb.

            delete (bool):
                If true, delete current avatar and use a default.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json(): The updated user's details.

            On failure:
                response.text:
                    "UNKNOWN_IMAGE_FORMAT"
                    "UNABLE_TO_RESIZE_IMAGE"
                    "IMAGE_TOO_BIG"
        """
        params = {
            'token': token
        }
        return self._get('updateAvatar', params, **kwargs)

    def get_projects(self, token):
        """Return a list of all of a user's projects.

        Args:
            token (str): The user's login token.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
              response.json(): A list of projects.
        """
        params = {
            'token': token
        }
        return self._get('getProjects', params)

    def get_project(self, token, project_id):
        """Return a project's details.

        Args:
            token (str): The user's login token.
            project_id (str): The id of a project.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json(): Contains the project data.

            On failure:
                response.status_code: 400 (Invalid project ID).
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('getProject', params)

    def add_project(self, token, project_name, **kwargs):
        """Add a new project to a user's account.

        Args:
            token (str): The user's login token.
            name (str): The name of the new project.
            color (int): The color of the new project.
            indent (int): The indentation of the project: (1-4).
            order (int): The order of the project: (1+).
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json(): The project details.

            On failure:
                response.text: "ERROR_NAME_IS_EMPTY"
        """
        params = {
            'token': token,
            'name': project_name
        }
        return self._get('addProject', params, **kwargs)

    def update_project(self, token, project_id, **kwargs):
        """Update a user's project.

        Args:
            token (str): The user's login token.
            project_id (str): The id of the project to update.
            name (str): The name of the new project.
            color (int): The color of the new project.
            indent (int): The indent of the project: (1-4).
            order (int): The order of the project: (1+).
            collapsed (int): If set to 1 the project is collapsed.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json(): Contains the updated project data.

            On failure:
                response.status_code: 400 (Invalid project ID).
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('updateProject', params, **kwargs)

    def update_project_orders(self, token, ordered_project_ids):
        """Update a user's project orderings.

        Args:
            token (str): The user's login token.
            ordered_project_ids (list): An ordered list of project ids.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.text: "ok"

            On failure:
                response.text: "ERROR_PROJECT_NOT_FOUND"
        """
        params = {
            'token': token,
            'item_id_list': ordered_project_ids
        }
        return self._get('updateProjectOrders', params)

    def delete_project(self, token, project_id):
        """Delete a user's project.

        Args:
            token (str): The user's login token.
            project_id (str): The id of the project to delete.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.text: "ok"
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('deleteProject', params)

    def archive_project(self, token, project_id):
        """Archive a user's project.

        Note:
            Affects only Todoist premium users.
        Args:
            token (str): The user's login token.
            project_id (str): The id of the project to archive.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json():
                    A list of archived project_ids e.g. [1234,4324,3242].
                    [] if the user does not have Todoist premium.
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('archiveProject', params)

    def unarchive_project(self, token, project_id):
        """Unarchive a user's project.

        Note:
            Affects only Todoist premium users.
        Args:
            token (str): The user's login token.
            project_id (str): The id of the project to unarchive.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json():
                    A list of unarchived project_ids e.g. [1234,4324,3242].
                    [] if the user does not have Todoist premium.
        """
        params = {
            'token': token,
            'project_id': project_id
        }
        return self._get('unarchiveProject', params)

    def get_labels(self, token, **kwargs):
        """Return all of a user's labels.

        Args:
            token (str): The user's login token.
            as_list (int): If 1 return a list of names rather than objects.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json(): A list of labels.
        """
        params = {
          'token': token
        }
        return self._get('getLabels', params, **kwargs)

    def add_label(self, token, label_name, **kwargs):
        """Add a label or return an existing one.

        Args:
            token (str): The user's login token.
            label_name (str): The name of the label.
            color (int): The color of the label.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json(): The label details.
        """
        params = {
          'token': token,
          'name': label_name
        }
        return self._get('addLabel', params, **kwargs)

    def update_label_name(self, token, label_name, new_name):
        """Update the name of a user's label.

        Args:
            token (str): The user's login token.
            label_name (str): The name of the label.
            new_name (str): The name to change to.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json(): The updated label details.
        """
        params = {
          'token': token,
          'old_name': label_name,
          'new_name': new_name
        }
        return self._get('updateLabel', params)

    def update_label_color(self, token, label_name, color):
        """Update the color of a user's label.

        Args:
            token (str): The user's login token.
            label_name (str): The name of the label.
            color (int): The color to change to.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json(): The updated label details.
        """
        params = {
          'token': token,
          'name': label_name,
          'color': color
        }
        return self._get('updateLabelColor', params)

    def delete_label(self, token, label_name):
        """Delete a user's label.

          Args:
              token (str): The user's login token.
              label_name (str): The name of the label.
          Returns:
              response (requests.Response): The HTTP response to the request.

              On success:
                  response.text: "ok"
        """
        params = {
          'token': token,
          'name': label_name
        }
        return self._get('deleteLabel', params)

    def get_uncompleted_tasks(self, token, project_id, **kwargs):
         """Return a list of a project's uncompleted tasks.

         Args:
             token (str): The user's login token.
             project_id (str): The id of the project.
             js_date (int):
                 if 1: 'new Date("Sun Apr 29 2007 23:59:59")'
                 otherwise: 'Sun Apr 2007 23:59:59'
         Returns:
             response (requests.Response): The HTTP response to the request.

             On success:
                 response.json(): A list of uncompleted tasks.

             On failure:
                 response.status_code: 400 (Invalid project ID).
         """
         params = {
            'token': token,
            'project_id': project_id
         }
         return self._get('getUncompletedItems', params, **kwargs)

    def add_task(self, token, content, **kwargs):
      """Add a task to a project.

        Args:
            token (str): The user's login token.
            content (str): The task description.
            project_id (str, default=Inbox): The id of the project.
            date_string (str): The date of the task.
            priority (int): Natural -> Very Urgent (1 -> 4).
            indent (int): The task indentation (1-4).
            js_date (int):
                if 1: 'new Date("Sun Apr 29 2007 23:59:59")'
                otherwise: 'Sun Apr 2007 23:59:59'
            item_order (int): The task order.
            children (list): A list of child tasks IDs.
            labels (list): A list of label IDs.
            assigned_by_uid (str): The id of user who assigns current task.
                Accepts 0 or any user id from the list of project collaborators.
                If value is unset or invalid it will automatically be set up by
                your uid.
            responsible_uid (str): The id of user who is responsible for
                accomplishing the current task. Accepts 0 or any user id from
                the list of project collaborators. If the value is unset or
                invalid it will automatically be set to null.
            note (str): A task note.
        Returns:
            response (requests.Response): The HTTP response to the request.

            On success:
                response.json(): The task details.

            On failure:
                response.status_code: 400 (Invalid project ID).
                response.text:
                    "ERROR_WRONG_DATE_SYNTAX"
      """
      params = {
        'token': token,
        'content': content
      }
      return self._get('addItem', params, **kwargs)

    def _get(self, end_point, params=None, **kwargs):
        """Send a HTTP GET request to a Todoist API end-point.

        Args:
            end_point (str): The Todoist API end-point.
            params (dict): The required request parameters.
            kwargs (dict): Any additional parameters.
        Returns:
            response (requests.Response): The HTTP response to the request.
        """
        url = self.api_url + end_point
        if params and kwargs:
            params.update(kwargs)
        return requests.get(url, params=params)
