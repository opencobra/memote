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

"""Programmatically interact with the memote test suite."""

from __future__ import absolute_import

import logging
import shlex

import pytest
from os.path import join, dirname

from memote.suite.collect import ResultCollectionPlugin

__all__ = ("test_model",)

LOGGER = logging.getLogger(__name__)


def test_model(model, result_file=None, report_file=None, results=False,
               pytest_args="--tb no"):
    """
    Test a model and optionally create output.

    Parameters
    ----------
    model
    result_file
    report_file
    results
    pytest_args

    Returns
    -------

    """
    tests_dir = join(dirname(__file__), "tests")
    pytest_args = shlex.split(pytest_args) + [tests_dir]
    mode = "basic"
    filename = None
    if result_file is not None:
        mode = "collect"
        filename = result_file
    if report_file is not None:
        mode = "html"
        filename = report_file
    plugin = ResultCollectionPlugin(
        model, mode=mode, filename=filename)
    errno = pytest.main(pytest_args, plugins=[plugin])
    if results:
        return errno, plugin.results
    else:
        return errno

