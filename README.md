pytodoist
---------

PyTodoist is a Python package that provides simple methods for interacting with Todoist. It hides the underlying web API calls with higher-level abstractions that make it easy to use Todoist with Python.

Documentation
-------------

Comprehensive online documentation can be found at http://pytodoist.readthedocs.org

Install
-------

Install the latest version:

    $ pip install pytodoist

Install from source:

    $ git clone git://github.com/Garee/PyTodoist.git
    $ cd PyTodoist
    $ python setup.py install

Example
-------

```python
>>> from pytodoist import todoist
>>> user = todoist.login('gary@garyblackwood.co.uk', 'mysecretpassword')
>>> user.is_logged_in()
True
>>> print user.full_name
Gary Blackwood
>>> projects = user.get_projects()
>>> for project in projects:
...     print project.name
...
Inbox
PyTodoist
>>> inbox = user.get_project('Inbox')
>>> task = inbox.add_task('Install PyTodoist',
...                        priority=todoist.Priority.VERY_HIGH)
>>> task.complete()
```
