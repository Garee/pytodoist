from api import TodoistAPI

api = TodoistAPI()

def _fail_if_contains_errors(response):
    if _contains_errors(response):
        raise TodoistException(response)

def _contains_errors(response):
    return response.text in api.ERRORS or response.status_code != 200

class TodoistException(Exception):
    def __init__(self, response):
        self.response = response
        Exception.__init__(self, response.text)

class User(object):

    def __init__(self, email, full_name, password=None, oauth2_token=None):
        self.email = email
        self.full_name = full_name
        self.password = password
        self.oauth2_token = oauth2_token
        self.lang = None
        self.timezone = None

    def register(self):
        response = api.register(self.email,
                                self.full_name,
                                self.password,
                                lang=self.lang,
                                timezone=self.timezone)
        _fail_if_contains_errors(response)

    def is_registered(self):
        try:
            self._fetch_user_info()
        except TodoistException:
            return False
        return True

    def login(self):
        user_info = self._fetch_user_info()
        for info in user_info:
            setattr(self, info, user_info[info])

    def is_logged_in(self):
        if not hasattr(self, 'token'):
            return False
        response = api.ping(self.token)
        return not _contains_errors(response)

    def delete(self):
        response = api.delete_user(self.token, self.password)
        _fail_if_contains_errors(response)

    def add_project(self, project):
        response = api.add_project(self.token,
                                   project.name,
                                   color=project.color,
                                   indent=project.indent,
                                   order=project.item_order)
        _fail_if_contains_errors(response)
        project_details = response.json()
        project.update(project_details)

    def get_projects(self):
        response = api.get_projects(self.token)
        _fail_if_contains_errors(response)
        projects_as_json = response.json()
        return [Project.init_with_json(p) for p in projects_as_json]

    def get_project(self, project_id):
        response = api.get_projects(self.token, project_id)
        _fail_if_contains_errors(response)
        project_as_json = response.json()
        return Project.init_with_json(project_as_json)

    def _fetch_user_info(self):
        if self.oauth2_token:
            return self._login(api.login_with_google,
                               self.oauth2_token,
                               self.password)
        return self._login(api.login, self.email, self.password)

    def _login(self, login_func, *args):
        response = login_func(*args)
        _fail_if_contains_errors(response)
        return response.json()


class Project(object):

    def __init__(self, name, color=None, indent=None, order=None):
        self.name = name
        self.color = color
        self.indent = indent
        self.item_order = order

    @classmethod
    def init_with_json(cls, json):
        name = json['name']
        return cls(name).update(json)

    def update(self, json):
        for attr in json:
            setattr(self, attr, json[attr])