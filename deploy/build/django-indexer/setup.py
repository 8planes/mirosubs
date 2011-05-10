#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-indexer',
    version=".".join(map(str, __import__('indexer').__version__)),
    author='David Cramer',
    author_email='dcramer@gmail.com',
    description='Key/Value Indexer',
    url='http://github.com/dcramer/django-indexer',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)