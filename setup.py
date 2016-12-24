#!/usr/bin/env python

from distutils.core import setup

setup(name='gofetch',
    packages=['gofetch', 'sqlite'],
    version='0.1',
    description='A lightweight database layer for Python',
    author='Pierce Freeman',
    author_email='pierce@piercefreeman.net',
    url='https://github.com/piercefreeman/GoFetch',
    download_url = 'https://github.com/piercefreeman/GoFetch/tarball/0.1',
    keywords = ['database'],
    install_requires=[
          'sqlite3',
    ],
 )
