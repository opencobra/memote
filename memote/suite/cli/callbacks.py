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

"""Callbacks for command line parameters."""

from __future__ import absolute_import

import shlex
import sys
import logging
import warnings

import click
import git
from cobra.io import read_sbml_model

from memote.experimental import ExperimentConfiguration

LOGGER = logging.getLogger(__name__)


def _load_model(filename):
    """Load the model defined in SBML."""
    # TODO: Record the SBML warnings and add them to the report.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        return read_sbml_model(filename)


def validate_model(context, param, value):
    """Load model from path if it exists."""
    if value is not None:
        return _load_model(value)
    else:
        raise click.BadParameter("No 'model' path given or configured.")


def validate_collect(context, param, value):
    """Handle the report collection flag."""
    if value is not None:
        return value
    else:
        return True


def validate_experimental(context, param, value):
    """Load and validate an experimental data configuration."""
    if value is None:
        return
    config = ExperimentConfiguration(value)
    config.validate()
    return config


def validate_pytest_args(context, param, value):
    """Handle additional arguments to pytest."""
    if value is not None:
        return shlex.split(value)
    else:
        return list()


def validate_repository(context, param, value):
    """Load repository slug from different locations."""
    if value is not None:
        return value
    else:
        raise click.BadParameter(
            "No GitHub repository slug provided or configured.")


def validate_username(context, param, value):
    """Load username from different locations."""
    if value is not None:
        return value
    else:
        raise click.BadParameter(
            "No GitHub username provided or configured.")


def probe_git():
    """Return a git repository instance if it exists."""
    try:
        repo = git.Repo()
    except git.InvalidGitRepositoryError:
        LOGGER.warning(
            "We highly recommend keeping your model in a git repository."
            " It allows you to track changes and to easily collaborate with"
            " others via online platforms such as https://github.com.\n")
        return
    if repo.is_dirty():
        LOGGER.critical(
            "Please git commit or git stash all changes before running"
            " the memote suite.")
        sys.exit(1)
    return repo


def abort_if_false(ctx, param, value):
    """Require confirmation."""
    if not value:
        ctx.abort()
