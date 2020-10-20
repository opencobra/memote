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

"""Provide commands for generating report files."""

from __future__ import absolute_import

import logging
import os
import sys
from builtins import open
from functools import partial
from multiprocessing import Pool, cpu_count

import click
import git
from libsbml import SBMLError
from sqlalchemy.exc import ArgumentError

import memote.suite.api as api
import memote.suite.cli.callbacks as callbacks
import memote.suite.results as managers
import memote.utils as utils
from memote.suite.cli import CONTEXT_SETTINGS
from memote.suite.reporting import ReportConfiguration


LOGGER = logging.getLogger(__name__)


@click.group()
@click.help_option("--help", "-h")
def report():
    """Generate one of three different types of reports."""
    pass


@report.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.argument(
    "model", type=click.Path(exists=True, dir_okay=False), envvar="MEMOTE_MODEL"
)
@click.option(
    "--filename",
    type=click.Path(exists=False, writable=True),
    default="index.html",
    show_default=True,
    help="Path for the HTML report output.",
)
@click.option(
    "--pytest-args",
    "-a",
    callback=callbacks.validate_pytest_args,
    help="Any additional arguments you want to pass to pytest. "
    "Should be given as one continuous string.",
)
@click.option(
    "--exclusive",
    type=str,
    multiple=True,
    metavar="TEST",
    help="The name of a test or test module to be run exclusively. "
    "All other tests are skipped. This option can be used "
    "multiple times and takes precedence over '--skip'.",
)
@click.option(
    "--skip",
    type=str,
    multiple=True,
    metavar="TEST",
    help="The name of a test or test module to be skipped. This "
    "option can be used multiple times.",
)
@click.option(
    "--solver",
    type=click.Choice(["cplex", "glpk", "gurobi", "glpk_exact"]),
    default="glpk",
    show_default=True,
    help="Set the solver to be used.",
)
@click.option(
    "--solver-timeout",
    type=int,
    default=10,
    help="Timeout in seconds to set on the mathematical optimization solver.",
)
@click.option(
    "--experimental",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    callback=callbacks.validate_experimental,
    help="Define additional tests using experimental data.",
)
@click.option(
    "--custom-tests",
    type=click.Path(exists=True, file_okay=False),
    multiple=True,
    help="A path to a directory containing custom test "
    "modules. Please refer to the documentation for more "
    "information on how to write custom tests. May be "
    "specified multiple times.",
)
@click.option(
    "--custom-config",
    type=click.Path(exists=True, dir_okay=False),
    multiple=True,
    help="A path to a report configuration file that will be merged "
    "into the default configuration. It's primary use is to "
    "configure the placement and scoring of custom tests but "
    "it can also alter the default behavior. Please refer to "
    "the documentation for the expected YAML format used. This "
    "option can be specified multiple times.",
)
def snapshot(
    model,
    filename,
    pytest_args,
    exclusive,
    skip,
    solver,
    solver_timeout,
    experimental,
    custom_tests,
    custom_config,
):
    """
    Take a snapshot of a model's state and generate a report.

    MODEL: Path to model file. Can also be supplied via the environment variable
    MEMOTE_MODEL or configured in 'setup.cfg' or 'memote.ini'.
    """
    model_obj, sbml_ver, notifications = api.validate_model(model)
    if model_obj is None:
        LOGGER.critical(
            "The model could not be loaded due to the following SBML errors."
        )
        utils.stdout_notifications(notifications)
        api.validation_report(model, notifications, filename)
        sys.exit(1)
    if not any(a.startswith("--tb") for a in pytest_args):
        pytest_args = ["--tb", "no"] + pytest_args
    # Add further directories to search for tests.
    pytest_args.extend(custom_tests)
    config = ReportConfiguration.load()
    # Update the default test configuration with custom ones (if any).
    for custom in custom_config:
        config.merge(ReportConfiguration.load(custom))
    model_obj.solver = solver
    _, results = api.test_model(
        model_obj,
        sbml_version=sbml_ver,
        results=True,
        pytest_args=pytest_args,
        skip=skip,
        exclusive=exclusive,
        experimental=experimental,
        solver_timeout=solver_timeout,
    )
    with open(filename, "w", encoding="utf-8") as file_handle:
        LOGGER.info("Writing snapshot report to '%s'.", filename)
        file_handle.write(api.snapshot_report(results, config))


@report.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.option(
    "--location",
    envvar="MEMOTE_LOCATION",
    help="Location of test results. Can either by a directory or an "
    "rfc1738 compatible database URL.",
)
@click.option(
    "--model",
    envvar="MEMOTE_MODEL",
    help="The path of the model file. Used to check if it was " "modified.",
)
@click.option(
    "--filename",
    type=click.Path(exists=False, writable=True),
    default="index.html",
    show_default=True,
    help="Path for the HTML report output.",
)
@click.option(
    "--deployment",
    default="gh-pages",
    show_default=True,
    help="Results will be read from and committed to the given " "branch.",
)
@click.option(
    "--custom-config",
    type=click.Path(exists=True, dir_okay=False),
    multiple=True,
    help="A path to a report configuration file that will be merged "
    "into the default configuration. It's primary use is to "
    "configure the placement and scoring of custom tests but "
    "it can also alter the default behavior. Please refer to "
    "the documentation for the expected YAML format used. This "
    "option can be specified multiple times.",
)
def history(location, model, filename, deployment, custom_config):
    """Generate a report over a model's git commit history."""
    callbacks.git_installed()
    LOGGER.info("Initialising history report generation.")
    if location is None:
        raise click.BadParameter("No 'location' given or configured.")
    try:
        repo = git.Repo()
    except git.InvalidGitRepositoryError:
        LOGGER.critical(
            "The history report requires a git repository in order to check "
            "the model's commit history."
        )
        sys.exit(1)
    LOGGER.info(
        "Obtaining history of results from "
        "the deployment branch {}.".format(deployment)
    )
    repo.git.checkout(deployment)
    try:
        manager = managers.SQLResultManager(repository=repo, location=location)
    except (AttributeError, ArgumentError):
        manager = managers.RepoResultManager(repository=repo, location=location)
    config = ReportConfiguration.load()
    # Update the default test configuration with custom ones (if any).
    for custom in custom_config:
        config.merge(ReportConfiguration.load(custom))
    LOGGER.info("Tracing the commit history.")
    history = managers.HistoryManager(repository=repo, manager=manager)
    history.load_history(model, skip={deployment})
    LOGGER.info("Composing the history report.")
    report = api.history_report(history, config=config)
    with open(filename, "w", encoding="utf-8") as file_handle:
        file_handle.write(report)


def _test_diff(
    model_and_model_ver_tuple,
    pytest_args,
    skip,
    exclusive,
    experimental,
    solver_timeout,
):
    model, sbml_ver = model_and_model_ver_tuple
    _, diff_results = api.test_model(
        model,
        sbml_version=sbml_ver,
        results=True,
        pytest_args=pytest_args,
        skip=skip,
        exclusive=exclusive,
        experimental=experimental,
        solver_timeout=solver_timeout,
    )
    return diff_results


@report.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.argument("models", type=click.Path(exists=True, dir_okay=False), nargs=-1)
@click.option(
    "--filename",
    type=click.Path(exists=False, writable=True),
    default="index.html",
    show_default=True,
    help="Path for the HTML report output.",
)
@click.option(
    "--pytest-args",
    "-a",
    callback=callbacks.validate_pytest_args,
    help="Any additional arguments you want to pass to pytest. "
    "Should be given as one continuous string.",
)
@click.option(
    "--exclusive",
    type=str,
    multiple=True,
    metavar="TEST",
    help="The name of a test or test module to be run exclusively. "
    "All other tests are skipped. This option can be used "
    "multiple times and takes precedence over '--skip'.",
)
@click.option(
    "--skip",
    type=str,
    multiple=True,
    metavar="TEST",
    help="The name of a test or test module to be skipped. This "
    "option can be used multiple times.",
)
@click.option(
    "--solver",
    type=click.Choice(["cplex", "glpk", "gurobi"]),
    default="glpk",
    show_default=True,
    help="Set the solver to be used.",
)
@click.option(
    "--solver-timeout",
    type=int,
    default=10,
    help="Timeout in seconds to set on the mathematical optimization solver.",
)
@click.option(
    "--experimental",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    callback=callbacks.validate_experimental,
    help="Define additional tests using experimental data.",
)
@click.option(
    "--custom-tests",
    type=click.Path(exists=True, file_okay=False),
    multiple=True,
    help="A path to a directory containing custom test "
    "modules. Please refer to the documentation for more "
    "information on how to write custom tests "
    "(memote.readthedocs.io). This option can be specified "
    "multiple times.",
)
@click.option(
    "--custom-config",
    type=click.Path(exists=True, dir_okay=False),
    multiple=True,
    help="A path to a report configuration file that will be merged "
    "into the default configuration. It's primary use is to "
    "configure the placement and scoring of custom tests but "
    "it can also alter the default behavior. Please refer to "
    "the documentation for the expected YAML format used "
    "(memote.readthedocs.io). This option can be specified "
    "multiple times.",
)
def diff(
    models,
    filename,
    pytest_args,
    exclusive,
    skip,
    solver,
    solver_timeout,
    experimental,
    custom_tests,
    custom_config,
):
    """
    Take a snapshot of all the supplied models and generate a diff report.

    MODELS: List of paths to two or more model files.
    """
    if not any(a.startswith("--tb") for a in pytest_args):
        pytest_args = ["--tb", "no"] + pytest_args
    # Add further directories to search for tests.
    pytest_args.extend(custom_tests)
    config = ReportConfiguration.load()
    # Update the default test configuration with custom ones (if any).
    for custom in custom_config:
        config.merge(ReportConfiguration.load(custom))
    # Build the diff report specific data structure
    diff_results = dict()
    model_and_model_ver_tuple = list()
    for model_path in models:
        try:
            model_filename = os.path.basename(model_path)
            diff_results.setdefault(model_filename, dict())
            model, model_ver, notifications = api.validate_model(model_path)
            if model is None:
                head, tail = os.path.split(filename)
                report_path = os.path.join(
                    head, "{}_structural_report.html".format(model_filename)
                )
                api.validation_report(model_path, notifications, report_path)
                LOGGER.critical(
                    "The model {} could not be loaded due to SBML errors "
                    "reported in {}.".format(model_filename, report_path)
                )
                continue
            model.solver = solver
            model_and_model_ver_tuple.append((model, model_ver))
        except (IOError, SBMLError):
            LOGGER.debug(exc_info=True)
            LOGGER.warning(
                "An error occurred while loading the model '%s'. " "Skipping.",
                model_filename,
            )
    # Abort the diff report unless at least two models can be loaded
    # successfully.
    if len(model_and_model_ver_tuple) < 2:
        LOGGER.critical(
            "Out of the %d provided models only %d could be loaded. Please, "
            "check if the models that could not be loaded are valid SBML. "
            "Aborting.",
            len(models),
            len(model_and_model_ver_tuple),
        )
        sys.exit(1)
    # Running pytest in individual processes to avoid interference
    partial_test_diff = partial(
        _test_diff,
        pytest_args=pytest_args,
        skip=skip,
        exclusive=exclusive,
        experimental=experimental,
        solver_timeout=solver_timeout,
    )
    pool = Pool(min(len(models), cpu_count()))
    results = pool.map(partial_test_diff, model_and_model_ver_tuple)

    for model_path, result in zip(models, results):
        model_filename = os.path.basename(model_path)
        diff_results[model_filename] = result

    with open(filename, "w", encoding="utf-8") as file_handle:
        LOGGER.info("Writing diff report to '%s'.", filename)
        file_handle.write(api.diff_report(diff_results, config))
