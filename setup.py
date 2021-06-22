#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals

from setuptools import setup


setup(
    name='django3-robokassa',
    version='1.0',
    author='Kzilot',
    author_email='fadeev2012fadeev@gmail.com',

    packages=['robokassa', 'robokassa.migrations'],

    url='https://github.com/EugeneFadeev/django3-robokassa',
    license='MIT License',
    description='Приложение для интеграции платежной системы ROBOKASSA в проекты на Django 3.0.',
    long_description=open('README.rst').read() + "\n\n" + open('CHANGES.rst').read(),

    install_requires=[
        'Django>=2'
    ],

    classifiers=(
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Russian',
    ),
)
