from __future__ import print_function

from setuptools import setup
import setuptools_scm

with open('importlib_metadata/version.txt', 'w') as f:
    print(setuptools_scm.get_version(), file=f)

setup()
