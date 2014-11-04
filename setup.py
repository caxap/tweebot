#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="tweebot",
    version="1.0",
    description="Python library to build twitter bots",
    license="MIT",
    author="Maxim Kamenkov",
    author_email="mkamenkov@gmail.com",
    url="http://github.com/caxap/tweebot",
    packages=find_packages(),
    install_requires=[
        'tweepy'
    ],
    keywords=["twitter", "bot", "library", "api"],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ]
)
