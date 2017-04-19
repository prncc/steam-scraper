#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'steam-scraper',
    version = '0.9.2',
    packages = find_packages(),
    entry_points =  {'scrapy': ['settings = steam.settings']},
    install_requires=[
        'scrapy',
        'smart_getenv',
        'botocore'
    ]
)