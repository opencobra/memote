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

import pytest
from jinja2 import Template

from memote.suite import TEST_DIRECTORY
from memote.suite.collect import ResultCollectionPlugin
from memote.suite.reporting import (
    SnapshotReport, DiffReport, HistoryReport, ReportConfiguration)
from memote.support import validation as val

__all__ = ("test_model", "snapshot_report", "diff_report", "history_report")

LOGGER = logging.getLogger(__name__)

def validate_model(path, results=False):
    """
    Validate a model structurally and optionally store results as JSON.

    Parameters
    ----------
    path :
        Path to model file.
    results : bool, optional
        Whether to return the results in addition to the return code.

    Returns
    -------
    model : cobra.Model
        The metabolic model under investigation.
    model_ver : tuple, optional
        A tuple reporting on the level, version, and FBC use of the SBML file.
    notifications: dict, optional
        A simple dictionary structure containing a list of errors and warnings.

    """
    notifications = {"warnings": [], "errors": []}
    model, model_ver = val.run_cobrapy_validation(path, notifications)

    if len(notifications["errors"]) > 1:
        val.run_libsbml_validation(notifications)

    if results:
        return model, model_ver, notifications
    else:
        return model


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


def snapshot_report(result, config=None, html=True):
    """
    Generate a snapshot report from a result set and configuration.

    Parameters
    ----------
    result : memote.MemoteResult
        Nested dictionary structure as returned from the test suite.
    config : dict, optional
        The final test report configuration (default None).
    html : bool, optional
        Whether to render the report as full HTML or JSON (default True).

    """
    if config is None:
        config = ReportConfiguration.load()
    report = SnapshotReport(result=result, configuration=config)
    if html:
        return report.render_html()
    else:
        return report.render_json()


def history_report(history, config=None, html=True):
    """
    Test a model and save a history report.

    Parameters
    ----------
    history : memote.HistoryManager
        The manager grants access to previous results.
    config : dict, optional
        The final test report configuration.
    html : bool, optional
        Whether to render the report as full HTML or JSON (default True).

    """
    if config is None:
        config = ReportConfiguration.load()
    report = HistoryReport(history=history, configuration=config)
    if html:
        return report.render_html()
    else:
        return report.render_json()


def diff_report(diff_results, config=None, html=True):
    """
    Generate a diff report from a result set and configuration.

    Parameters
    ----------
    result : memote.MemoteResult
        Nested dictionary structure as returned from the test suite.
    config : dict, optional
        The final test report configuration (default None).
    html : bool, optional
        Whether to render the report as full HTML or JSON (default True).

    """
    if config is None:
        config = ReportConfiguration.load()
    report = DiffReport(diff_results=diff_results, configuration=config)
    if html:
        return report.render_html()
    else:
        return report.render_json()


def validation_report(notifications):
    """
    Generate a validation report from a notification object.

    Parameters
    ----------
    notifications : dict
        A simple dictionary structure containing a list of errors and warnings.

    """
    template = Template(" ")
