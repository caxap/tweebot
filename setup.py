#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(name="tweebot",
      version="1.0",
      description="Python library to build twitter bots",
      license="MIT License",
      author="Maxim Kamenkov",
      author_email="mkamenkov@gmail.com",
      url="http://github.com/caxap/tweebot",
      packages = find_packages(),
      keywords= ["twitter", "bot", "library"],
      zip_safe = True)
