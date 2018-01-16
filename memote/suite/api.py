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
from six import iteritems

from memote.suite import TEST_DIRECTORY
from memote.suite.collect import ResultCollectionPlugin
from memote.suite.reporting.reports import SnapshotReport, HistoryReport

__all__ = ("test_model", "snapshot_report", "diff_report", "history_report")

LOGGER = logging.getLogger(__name__)


def test_model(model, filename=None, results=False, pytest_args=None,
               exclusive=None, skip=None, solver=None, custom=(None, None)):
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
    exclusive : iterable, optional
        Names of test cases or modules to run and exclude all others. Takes
        precedence over ``skip``.
    skip : iterable, optional
        Names of test cases or modules to skip.
    custom : tuple, optional
        A tuple with the absolute path to a directory that contains custom test
        modules at index 0 and the absolute path to the corresponding config
        file at index 1.

    Returns
    -------
    int
        The return code of the pytest suite.
    dict, optional
        A nested dictionary structure that contains the complete test results.

    """
    if pytest_args is None:
        pytest_args = ["--tb", "short", TEST_DIRECTORY]
    elif not any(a.startswith("--tb") for a in pytest_args):
        pytest_args.extend(["--tb", "short"])
    if TEST_DIRECTORY not in pytest_args:
        pytest_args.append(TEST_DIRECTORY)
    LOGGER.debug("%s", str(custom))
    if custom != (None, None):
        custom_test_path, custom_config = custom
        pytest_args.append(custom_test_path)
        plugin = ResultCollectionPlugin(model, exclusive=exclusive, skip=skip,
                                        custom_config=custom_config)
        LOGGER.info("#" * 50)
        LOGGER.info("%s", plugin.custom_config)
        LOGGER.info("#" * 50)
    else:
        plugin = ResultCollectionPlugin(model, exclusive=exclusive, skip=skip)
    code = pytest.main(pytest_args, plugins=[plugin])
    if filename is not None:
        with open(filename, "w") as file_h:
            LOGGER.info("Writing JSON output '%s'.", filename)
            try:
                json.dump(plugin.results, file_h, sort_keys=True, indent=4,
                          separators=(",", ": "))
            except TypeError:
                # Log information to easily find the culprit.
                json_types = (type(None), int, float, str, list, dict)
                for name, annotation in iteritems(plugin.results["tests"]):
                    data = annotation.get("data")
                    try:
                        for key, value in iteritems(data):
                            if not isinstance(value, json_types):
                                LOGGER.debug(
                                    "  %s - %s: %s", name, key, type(
                                        value)
                                )
                    except AttributeError:
                        if not isinstance(data, json_types):
                            LOGGER.debug("  %s: %s", name, type(data))

    if results:
        return code, plugin.results
    else:
        return code


def snapshot_report(results, filename):
    """
    Test a model and save a basic report.

    Parameters
    ----------
    results : dict
        Nested dictionary structure as returned from the test suite.
    filename : str or pathlib.Path
        A filename for the HTML report.

    """
    report = SnapshotReport(results)
    LOGGER.info("Writing basic report '%s'.", filename)
    with io.open(filename, "w") as file_h:
        file_h.write(report.render_html())


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
    u"""Coming soon™."""
    raise NotImplementedError(u"Coming soon™.")
