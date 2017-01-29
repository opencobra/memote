#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

setup_requirements = [
    "pytest-runner"
]

requirements = [
    "python-libsbml",
    "swiglpk",
    "cameo"
]

test_requirements = [
    "pytest"
]

setup(
    name="memote",
    version="0.1.0",
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
