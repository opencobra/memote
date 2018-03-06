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
from builtins import open

import pytest

from memote.suite import TEST_DIRECTORY
from memote.suite.collect import ResultCollectionPlugin
from memote.suite.results import HistoryManager
from memote.suite.reporting import (
    SnapshotReport, HistoryReport, ReportConfiguration)

__all__ = ("test_model", "snapshot_report", "diff_report", "history_report")

LOGGER = logging.getLogger(__name__)


def test_model(model, results=False, pytest_args=None,
               exclusive=None, skip=None, experimental=None):
    """
    Test a model and optionally store results as JSON.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    results : bool, optional
        Whether to return the results in addition to the return code.
    pytest_args : list, optional
        Additional arguments for the pytest suite.
    exclusive : iterable, optional
        Names of test cases or modules to run and exclude all others. Takes
        precedence over ``skip``.
    skip : iterable, optional
        Names of test cases or modules to skip.

    Returns
    -------
    int
        The return code of the pytest suite.
    memote.Result, optional
        A nested dictionary structure that contains the complete test results.

    """
    if pytest_args is None:
        pytest_args = ["--tb", "short", TEST_DIRECTORY]
    elif not any(a.startswith("--tb") for a in pytest_args):
        pytest_args.extend(["--tb", "short"])
    if TEST_DIRECTORY not in pytest_args:
        pytest_args.append(TEST_DIRECTORY)
    plugin = ResultCollectionPlugin(model, exclusive=exclusive, skip=skip,
                                    experimental_config=experimental)
    code = pytest.main(pytest_args, plugins=[plugin])
    if results:
        return code, plugin.results
    else:
        return code


def snapshot_report(result, config=None, filename=None):
    """
    Test a model and save a basic report.

    Parameters
    ----------
    result : memote.MemoteResult
        Nested dictionary structure as returned from the test suite.
    config : dict, optional
        The final test report configuration.
    filename : str or pathlib.Path
        A filename for the HTML report.

    """
    if config is None:
        config = ReportConfiguration.load()
    report = SnapshotReport(result=result, configuration=config)
    LOGGER.info("Writing snapshot report to '%s'.", filename)
    with open(filename, "w", encoding="utf-8") as file_h:
        file_h.write(report.render_html())


def history_report(repository, manager, filename, index="hash", config=None):
    """
    Test a model and save a history report.

    Parameters
    ----------
    repository : git.Repo, optional
        An instance of the working directory git repository.
    manager : memote.RepoResultManager
        The manager grants access to previous results.
    filename : str or pathlib.Path
        A filename for the HTML report.
    index : {"hash", "time"}, optional
        The default horizontal axis type for all plots.
    config : dict, optional
        The final test report configuration.

    """
    if config is None:
        config = ReportConfiguration.load()
    report = HistoryReport(
        history=HistoryManager(repository=repository, manager=manager),
        configuration=config, index=index)
    LOGGER.info("Writing history report '%s'.", filename)
    with open(filename, "w", encoding="utf-8") as file_h:
        file_h.write(report.render_html())


def diff_report():
    u"""Coming soon™."""
    raise NotImplementedError(u"Coming soon™.")
