# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
import os
import re
import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 5, 0):
    raise RuntimeError("iss-positioner requires Python 3.5.0+")

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
VERSION_REGEXP = re.compile(r"^__version__ = [\'\"](.+?)[\'\"]$", re.MULTILINE)


def read(fn):
    with codecs.open(os.path.join(PROJECT_DIR, fn), encoding='utf-8') as f:
        return f.read().strip()


def version():
    try:
        return VERSION_REGEXP.findall(read(os.path.join('iss_positioner', '__init__.py')))[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


vn = version()
url = 'https://github.com/nkoshell/iss-positioner'

setup(
    name='iss-positioner',
    description='ISS position computing service',
    long_description=read('README.rst'),
    version=vn,
    packages=find_packages(),
    include_package_data=True,
    url=url,
    download_url='{url}/archive/{version}.tar.gz'.format(url=url, version=vn),
    license='MIT',
    author='nkoshell',
    author_email='nikita.koshelev@gmail.com',
    install_requires=read('requirements.in').splitlines(),
)
