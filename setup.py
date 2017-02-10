#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Install the metabolic model checks provided by memote."""

from __future__ import absolute_import

import sys

from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

setup_requirements = []
# prevent pytest-runner from being installed on every invocation
if {'pytest', 'test', 'ptr'}.intersection(sys.argv):
    setup_requirements.append("pytest-runner")

requirements = [
    "python-libsbml",
    "swiglpk",
    "cobra",
    "click",
    "click-configfile"
]

test_requirements = [
    "pytest"
]

setup(
    name="memote",
    version="0.2.1",
    description="Genome-scale metabolic model test suite.",
    long_description=readme + "\n\n" + history,
    author="Moritz E. Beber",
    author_email="morbeb@biosustain.dtu.dk",
    url="https://github.com/biosustain/memote",
    packages=[
        "memote",
    ],
    package_dir={"memote":
                 "memote"},
    include_package_data=True,
    setup_requires=setup_requirements,
    install_requires=requirements,
    tests_require=test_requirements,
    # this is currently not working, setup ignores the link
    # could subprocess the pip install or for now:
    # pip install -r requirements.in
    #   "https://github.com/opencobra/cobrapy.git@devel-2#egg=cobra"
    dependency_links=[],
    entry_points="""
        [console_scripts]
        memote=memote.suite.runner:cli
    """,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="memote",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
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
