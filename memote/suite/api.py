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

import io
import logging
try:
    import simplejson as json
except ImportError:
    import json

import pytest
from os.path import join, dirname

from memote.suite.collect import ResultCollectionPlugin
from memote.suite.reporting.reports import BasicReport, HistoryReport

__all__ = ("test_model", "basic_report", "diff_report", "history_report")

LOGGER = logging.getLogger(__name__)


def test_model(model, filename=None, results=False, pytest_args=None):
    """
    Test a model and optionally store results as JSON.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    filename : str or pathlib.Path, optional
        A filename if JSON output of the results is desired.
    results : bool, optional
        Whether to return the results in addition to the return code.
    pytest_args : list, optional
        Additional arguments for the pytest suite.

    Returns
    -------
    int
        The return code of the pytest suite.
    dict, optional
        A nested dictionary structure that contains the complete test results.

    """
    tests_dir = join(dirname(__file__), "tests")
    if pytest_args is None:
        pytest_args = ["--tb", "line", tests_dir]
    elif "--tb" not in pytest_args:
        pytest_args.extend(["--tb", "line"])
    elif tests_dir not in pytest_args:
        pytest_args.append(tests_dir)
    plugin = ResultCollectionPlugin(model)
    code = pytest.main(pytest_args, plugins=[plugin])
    if filename is not None:
        with open(filename, "w") as file_h:
            LOGGER.info("Writing JSON output '%s'.", filename)
            json.dump(plugin.results, file_h, sort_keys=True, indent=4,
                      separators=(",", ": "))
    if results:
        return code, plugin.results
    else:
        return code


def basic_report(model, filename, result_file=None, pytest_args=None):
    """
    Test a model and save a basic report.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    filename : str or pathlib.Path
        A filename for the HTML report.
    result_file : str or pathlib.Path, optional
        If you want to save the test results as JSON in addition to the report.
    pytest_args : list, optional
        Additional arguments for the pytest suite.

    Returns
    -------
    int
        The return code of the pytest suite.

    """
    if pytest_args is None:
        pytest_args = ["--tb", "no"]
    elif "--tb" not in pytest_args:
        pytest_args.extend(["--tb", "no"])
    code, results = test_model(model, filename=result_file, results=True,
                               pytest_args=pytest_args)
    report = BasicReport(results)
    LOGGER.info("Writing basic report '%s'.", filename)
    with io.open(filename, "w") as file_h:
        file_h.write(report.render_html())
    return code


def history_report(repository, directory, filename, index="hash"):
    """
    Test a model and save a history report.

    Parameters
    ----------
    repository : git.Repo, optional
        An instance of the working directory git repository.
    directory : str or pathlib.Path
        Use the JSON files in the directory that correspond to this git branch's
        commit history to generate the report.
    filename : str or pathlib.Path
        A filename for the HTML report.
    index : {"hash", "time"}, optional
        The default horizontal axis type for all plots.

    """
    report = HistoryReport(repository, directory, index=index)
    LOGGER.info("Writing history report '%s'.", filename)
    with io.open(filename, "w") as file_h:
        file_h.write(report.render_html())


def diff_report():
    raise NotImplementedError
