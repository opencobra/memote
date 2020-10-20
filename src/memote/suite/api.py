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
import os
from io import open

import pytest
from jinja2 import Environment, PackageLoader, select_autoescape

from memote.suite import TEST_DIRECTORY
from memote.suite.collect import ResultCollectionPlugin
from memote.suite.reporting import (
    DiffReport,
    HistoryReport,
    ReportConfiguration,
    SnapshotReport,
)
from memote.support import validation as val


__all__ = (
    "validate_model",
    "test_model",
    "snapshot_report",
    "diff_report",
    "history_report",
)

LOGGER = logging.getLogger(__name__)


def validate_model(path):
    """
    Validate a model structurally and optionally store results as JSON.

    Parameters
    ----------
    path :
        Path to model file.

    Returns
    -------
    tuple
        cobra.Model
            The metabolic model under investigation.
        tuple
            A tuple reporting on the SBML level, version, and FBC package
            version used (if any) in the SBML document.
        dict
            A simple dictionary containing a list of errors and warnings.

    """
    notifications = {"warnings": [], "errors": []}
    model, sbml_ver = val.load_cobra_model(path, notifications)
    return model, sbml_ver, notifications


def test_model(
    model,
    sbml_version=None,
    results=False,
    pytest_args=None,
    exclusive=None,
    skip=None,
    experimental=None,
    solver_timeout=10,
):
    """
    Test a model and optionally store results as JSON.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    sbml_version: tuple, optional
        A tuple reporting on the level, version, and FBC use of the SBML file.
    results : bool, optional
        Whether to return the results in addition to the return code.
    pytest_args : list, optional
        Additional arguments for the pytest suite.
    exclusive : iterable, optional
        Names of test cases or modules to run and exclude all others. Takes
        precedence over ``skip``.
    skip : iterable, optional
        Names of test cases or modules to skip.
    solver_timeout: int, optional
        Timeout in seconds to set on the mathematical optimization solver (default 10).

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
    if "-s" not in pytest_args and LOGGER.getEffectiveLevel() <= logging.DEBUG:
        # Disable pytest capturing so that the solver log output can be seen
        # immediately.
        pytest_args.insert(0, "-s")
    model.solver.configuration.timeout = solver_timeout
    # Load the experimental configuration using model information.
    if experimental is not None:
        experimental.load(model)
    plugin = ResultCollectionPlugin(
        model,
        sbml_version=sbml_version,
        exclusive=exclusive,
        skip=skip,
        experimental_config=experimental,
    )
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
    diff_results : iterable of memote.MemoteResult
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


def validation_report(path, notifications, filename):
    """
    Generate a validation report from a notification object.

    Parameters
    ----------
    path : string
        Path to model file.
    notifications : dict
        A simple dictionary structure containing a list of errors and warnings.

    """
    env = Environment(
        loader=PackageLoader("memote.suite", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("validation_template.html")
    model = os.path.basename(path)
    with open(filename, "w") as file_h:
        file_h.write(template.render(model=model, notifications=notifications))
