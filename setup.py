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

import io
import sys
from warnings import warn

from setuptools import setup


if sys.version_info[:2] == (3, 4):
    warn("Support for Python 3.4 was dropped by pandas. Since memote is a "
         "pure Python package you can still install it but will have to "
         "carefully manage your own pandas and numpy versions. We no longer "
         "include it in our automatic testing.")


with io.open('requirements.txt') as file_handle:
    requirements = file_handle.readlines()

with io.open('test_requirements.txt') as file_handle:
    test_requirements = file_handle.readlines()


# All other keys are defined in setup.cfg under [metadata] and [options].
setup(
    version="0.6.0",
    install_requires=requirements,
    tests_require=test_requirements,
    entry_points="""
        [console_scripts]
        memote=memote.suite.cli.runner:cli
    """
)
