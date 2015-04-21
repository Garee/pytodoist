"""A module containing useful helper functions for unit tests."""

import string
import random
from pytodoist import todoist


def generate_id(size=10):
    """Return a random alphanumeric string."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


class TestUser(object):
    """A fake user to use in each unit test."""

    def __init__(self):
        self.full_name = "Test User"
        self.email = "pytodoist_" + generate_id() + "@gmail.com"
        self.password = "password"
        self.api_token = None
        self.api_seq_no = '0'


def create_user():
    """Return a newly registered logged in Todoist user."""
    user = TestUser()
    try:
        return todoist.register(user.full_name, user.email, user.password)
    except todoist.RequestError:
        existing_user = todoist.login(user.email, user.password)
        existing_user.delete()
        return todoist.register(user.full_name, user.email, user.password)
