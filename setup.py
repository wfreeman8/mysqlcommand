#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['mysql-connector-python']
setup(
    author="Worth Freeman",
    author_email="wfreeman8@users.noreply.github.com",
    description="Mysql query builder",
    install_requires=requirements,
    license="MIT",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords='mysqlcommand',
    name='mysqlcommand',
    packages=find_packages(include=['mysqlcommand']),
    url='https://github.com/wfreeman8/mysqlcommand',
    version='0.1.1',
    zip_safe=True,
    python_requires='>=3.6',
)