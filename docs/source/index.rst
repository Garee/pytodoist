PyTodoist |release| Documentation
=================================

Overview
--------
**PyTodoist** is a Python package for interacting with the `Todoist <http://www.todoist.com>`_ web application. It hides the underlying API calls with higher-level abstractions that make it easy to use Todoist with Python.

Examples
--------

>>> from pytodoist import todoist
>>> user = todoist.register('John Doe', 'john.doe@gmail.com', 'passwd')
>>> user.is_logged_in()
True
>>> print user.full_name
John Doe
>>> install_task = user.add_task('Install PyTodoist.')
>>> uncompleted_tasks = user.get_uncompleted_tasks()
>>> for task in uncompleted_tasks:
...     print task.content
...
Install PyTodoist
>>> install_task.complete()

Install
-------

The package is hosted on `The Python Package Index <https://pypi.python.org/pypi>`_ and can be installed using `pip <https://pypi.python.org/pypi/pip>`_:

.. code-block:: bash

   $ pip install pytodoist

To install a specific version:

.. code-block:: bash

   $ pip install pytodoist==0.5

To install from source:

.. code-block:: bash

   $ git clone git://github.com/Garee/PyTodoist.git
   $ cd PyTodoist
   $ python setup.py install

Modules
-------
:doc:`todoist`
    Abstracts the underlying API and provides an easy way to interact with Todoist.

:doc:`api`
    A direct wrapper over the Todoist API.

Issues
------
Please report all issues using the github `issue tracker <https://github.com/Garee/PyTodoist/issues>`_. If you would like to ask a question, feel free to send me an `email <mailto:gary@garyblackwood.co.uk>`_.

Contributing
------------

All contributions are welcome. To contribute, please fork the project on `github <https://github.com/Garee/PyTodoist>`_ and submit a pull request.

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
