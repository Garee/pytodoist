<p align="center">
<img src="https://imgur.com/WAXg5z7.png" title="PyTodoist" />
</p>

<p align="center">
<a href="https://pypi.python.org/pypi/pytodoist"><img src="https://img.shields.io/pypi/v/pytodoist.svg?maxAge=600" alt="PyPI" /></a>
<a href="https://pypi.python.org/pypi/pytodoist"><img src="https://img.shields.io/pypi/pyversions/pytodoist.svg" alt="Python versions"></a>
<a href="https://github.com/garee/pytodoist/blob/master/LICENSE"><img src="https://img.shields.io/github/license/garee/pytodoist.svg" alt="License" /></a> <a href="https://travis-ci.com/Garee/pytodoist"><img src="https://travis-ci.com/Garee/pytodoist.svg?branch=master" alt="Build status"></a>
</p>

**PyTodoist** is a Python package for interacting with [Todoist](http://www.todoist.com). It hides the underlying API calls with higher-level abstractions that make it easy to use Todoist with Python.

## Quick Start

Install the latest version:

```sh
$ pip install pytodoist
```

Have fun:

```python
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
```

## Documentation

Comprehensive online documentation can be found at https://pytodoist.readthedocs.org
