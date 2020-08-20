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

import logging
import shlex
import sys
from subprocess import CalledProcessError, check_output

import click
import git

from memote.experimental import ExperimentConfiguration


LOGGER = logging.getLogger(__name__)


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
        raise click.BadParameter("No GitHub repository slug provided or configured.")


def validate_username(context, param, value):
    """Load username from different locations."""
    if value is not None:
        return value
    else:
        raise click.BadParameter("No GitHub username provided or configured.")


def probe_git():
    """Return a git repository instance if it exists."""
    try:
        repo = git.Repo()
    except git.InvalidGitRepositoryError:
        LOGGER.warning(
            "We highly recommend keeping your model in a git repository."
            " It allows you to track changes and to easily collaborate with"
            " others via online platforms such as https://github.com.\n"
        )
        return
    if repo.is_dirty():
        LOGGER.critical(
            "Please git commit or git stash all changes before running"
            " the memote suite."
        )
        sys.exit(1)
    return repo


def abort_if_false(ctx, param, value):
    """Require confirmation."""
    if not value:
        ctx.abort()


def git_installed():
    """Interrupt execution of memote if `git` has not been installed."""
    LOGGER.info("Checking `git` installation.")
    try:
        check_output(["git", "--version"])
    except CalledProcessError as e:
        LOGGER.critical(
            "The execution of memote was interrupted since no installation of "
            "`git` could be detected. Please install git to use "
            "this functionality: "
            "https://git-scm.com/book/en/v2/Getting-Started-Installing-Git"
        )
        LOGGER.debug("Underlying error:", exc_info=e)
        sys.exit(1)
