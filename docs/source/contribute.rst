Contributing
============

Reporting Issues
----------------

Please report all issues using the github `issue tracker <https://github.com/Garee/PyTodoist/issues>`_. If you would like to ask a question, feel free to send me an `email <mailto:gary@garyblackwood.co.uk>`_.

Pull Requests
-------------

Please fork the project on `github <https://github.com/Garee/PyTodoist>`_ and submit a pull request.

1. Write tests for any new code.
2. Ensure that your code meets the PEP8 standards.
3. Update the documentation.
4. Add yourself to credits.rst

Setup for Development
----------------------------

First you need to install the needed packages:

.. code-block:: bash
    sudo pip install flake8
    sudo pip install -Ur requirements.txt

You can run the tests with:

.. code-block:: bash
    make test

** With virtualenv **

.. code-block:: bash
    sudo pip install virtualenv
    make bootstrap

Now you can start the virtual environment with:

.. code-block:: bash
    . .venv/bin/activate

And you can deactivate it with:

.. code-block:: bash
    deactivate

You can also run the tests in the virtual environment with:

.. code-block:: bash
    make env-test
