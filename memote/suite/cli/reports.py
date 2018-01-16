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
import sys

import click
import git

import memote.suite.api as api
from memote.suite.cli import CONTEXT_SETTINGS
import memote.suite.cli.callbacks as callbacks

LOGGER = logging.getLogger(__name__)


@click.group()
@click.help_option("--help", "-h")
def report():
    """Generate one of three different types of reports."""
    pass


@report.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.argument("model", type=click.Path(exists=True, dir_okay=False),
                envvar="MEMOTE_MODEL",
                callback=callbacks.validate_model)
@click.option("--filename", type=click.Path(exists=False, writable=True),
              default="index.html", show_default=True,
              help="Path for the HTML report output.")
@click.option("--pytest-args", "-a", callback=callbacks.validate_pytest_args,
              help="Any additional arguments you want to pass to pytest. "
                   "Should be given as one continuous string.")
@click.option("--solver", type=click.Choice(["cplex", "glpk", "gurobi"]),
              default="glpk", show_default=True,
              help="Set the solver to be used.")
@click.option("--custom", type=(click.Path(exists=True, file_okay=False),
                                click.Path(exists=True, dir_okay=False)),
              default=(None, None), show_default=True,
              help="The absolute path to a directory containing custom test "
                   "modules followed by the absolute path to a config file "
                   "corresponding to the custom test modules. Please refer to "
                   "the documentation for more information on the required "
                   "file formats.")
def snapshot(model, filename, pytest_args, solver, custom):
    """
    Take a snapshot of a model's state and generate a report.

    MODEL: Path to model file. Can also be supplied via the environment variable
    MEMOTE_MODEL or configured in 'setup.cfg' or 'memote.ini'.
    """
    if not any(a.startswith("--tb") for a in pytest_args):
        pytest_args = ["--tb", "short"] + pytest_args
    if not any(a.startswith("-v") for a in pytest_args):
        pytest_args.append("-vv")
    model.solver = solver
    _, results = api.test_model(model, results=True, pytest_args=pytest_args,
                                custom=custom)
    api.snapshot_report(results, filename)


@report.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.argument("directory", type=click.Path(exists=True, file_okay=False),
                envvar="MEMOTE_DIRECTORY")
@click.option("--filename", type=click.Path(exists=False, writable=True),
              default="index.html", show_default=True,
              help="Path for the HTML report output.")
@click.option("--index", type=click.Choice(["hash", "time"]), default="hash",
              show_default=True,
              help="Use either commit hashes or time as the independent "
                   "variable for plots.")
def history(directory, filename, index):
    """
    Generate a report over a model's git commit history.

    DIRECTORY: Expect JSON files corresponding to the branch's commit history
    to be found here. Can also be supplied via the environment variable
    MEMOTE_DIRECTORY or configured in 'setup.cfg' or 'memote.ini'.
    """
    try:
        repo = git.Repo()
    except git.InvalidGitRepositoryError:
        LOGGER.critical(
            "The history report requires a git repository in order to check "
            "the current branch's commit history.")
        sys.exit(1)
    api.history_report(repo, directory, filename, index)


@report.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.argument("model1", type=click.Path(exists=True, dir_okay=False))
@click.argument("model2", type=click.Path(exists=True, dir_okay=False))
@click.option("--filename", type=click.Path(exists=False, writable=True),
              default="index.html", show_default=True,
              help="Path for the HTML report output.")
def diff(model1, model2, filename):
    """Compare two metabolic models against each other."""
    raise NotImplementedError(u"Coming soon™.")
