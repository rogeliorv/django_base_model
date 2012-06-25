#!/usr/bin/env python
'''
Created on Jun 15, 2012

@author: rogelio
'''

from setuptools import setup, find_packages

setup(name="django_base_model",
      version="0.2.1",
      description="A model from which all django models can extend. Gives some additional utility functions",
      license="MIT",
      author="@rogeliorv",
      author_email="rogelio@rogeliorv.com",
      url="http://github.com/rogeliorv/django_base_model",
      packages = find_packages(),
      keywords= "django model",
      install_requires= ['django'],
      zip_safe = True)
