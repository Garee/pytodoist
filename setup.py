#!/usr/bin/env python

"""Setup script for the pytodoist package."""
import pytodoist
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='pytodoist',
      version=pytodoist.__version__,
      license='MIT',
      description='A python wrapper for the Todoist API.',
      long_description=open('README.rst').read(),
      author='Gary Blackwood',
      author_email='gary@garyblackwood.co.uk',
      url='http://www.github.com/Garee/pytodoist',
      packages=['pytodoist'],
      install_requires=['requests'],
      classifiers=(
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.0',
          'Programming Language :: Python :: 3.1',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6'
      ),)
