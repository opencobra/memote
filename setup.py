#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2017 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Install the metabolic model test suite."""

from __future__ import absolute_import

import sys

from setuptools import find_packages, setup

if sys.version_info[:2] == (3, 4):
    warn("Support for Python 3.4 was dropped by pandas. Since cobrapy is a "
         "pure Python package you can still install it but will have to "
         "carefully manage your own pandas and numpy versions. We no longer "
         "include it in our automatic testing.")

with open("README.rst") as readme_file:
    readme = readme_file.read()

setup_requirements = []
# prevent pytest-runner from being installed on every invocation
if set(['pytest', 'test', 'ptr']).intersection(sys.argv):
    setup_requirements.append("pytest-runner")

requirements = [
    "pip",
    "click",
    "click-configfile",
    "click-log",
    "six",
    "future",
    "pytest>=3.1",
    "gitpython",
    "pandas>=0.20.1",
    "dask>=0.14.3",
    "cloudpickle",
    "toolz",
    "Jinja2",
    "jinja2-ospath",
    "cookiecutter",
    "python-libsbml",
    "cobra>=0.9.1",
    "ruamel.yaml<0.15",
    "plotly",
    "travispy",
    "pygithub",
    "travis-encrypt",
    "sympy",
    "numpydoc"
]

test_requirements = [
    "pytest>=3.1"
    "pytest-raises"
]

setup(
    name="memote",
    version="0.5.1",
    description="the genome-scale metabolic model test suite",
    long_description=readme,
    author="Moritz E. Beber",
    author_email="morbeb@biosustain.dtu.dk",
    url="https://github.com/opencobra/memote",
    packages=find_packages(),
    include_package_data=True,
    setup_requires=setup_requirements,
    install_requires=requirements,
    tests_require=test_requirements,
    dependency_links=[],
    entry_points="""
        [console_scripts]
        memote=memote.suite.cli.runner:cli
    """,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="memote",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ]
)
