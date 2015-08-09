PyTodoist
=========

**PyTodoist** is a Python package for interacting with `Todoist <http://www.todoist.com>`_. It hides the underlying API calls with higher-level abstractions that make it easy to use Todoist with Python.

Quick Start
-----------

Install the latest version:

.. code-block:: bash

    $ pip install pytodoist

Have fun:

.. code-block:: python

    >>> from pytodoist import todoist
    >>> user = todoist.login('gary@garyblackwood.co.uk', 'pa$$w0rd')
    >>> projects = user.get_projects()
    >>> for project in projects:
    ...     print(project.name)
    ...
    Inbox
    Books to read
    Movies to watch
    Shopping
    Work
    Personal
    Health
    >>> inbox = user.get_project('Inbox')
    >>> task = inbox.add_task('Install PyTodoist',
    ...                        priority=todoist.Priority.VERY_HIGH)
    >>> task.complete()

Documentation
-------------

Comprehensive online documentation can be found at http://pytodoist.readthedocs.org
