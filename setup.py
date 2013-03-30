#!/usr/bin/env python
from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup (
    name = "tt - Time Tracker",
    version = "0.1",
    description="A simple command line utility to track the time you work on things.",
    author="Tammy D",
    author_email="tammyd@gmail.com",
    url="https://github.com/tammyd",
    package_data = {'': ['*.md']},
    packages = find_packages(exclude="test"),
    entry_points = {
        'console_scripts': ['tt=tt:main']
    },

    download_url = "https://github.com/tammyd/tt",
    zip_safe = True,
    install_requires=['prettytable>=0.7.1','parsedatetime>=1.1.2']
)