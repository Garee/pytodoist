#!/usr/bin/env python

"""Setup script for the pytodoist package."""
import pytodoist
from distutils.core import setup

setup(name='pytodoist',
      version=pytodoist.__version__,
      license='MIT',
      description='A python wrapper for the Todoist API.',
      long_description=open('README').read(),
      author='Gary Blackwood',
      author_email='gary@garyblackwood.co.uk',
      url='http://www.github.com/Garee/pytodoist',
      packages=['pytodoist'],
      install_requires=['requests'],
      include_package_data=True,
      classifiers=(
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: MIT Software License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
      ))
