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

import os
import shlex
import sys
import logging
import warnings
from os.path import isfile, isdir, exists

import click
import git
from colorama import Fore
from cobra.io import read_sbml_model

LOGGER = logging.getLogger(__name__)


def _load_model(filename):
    """Load the model defined in SBML."""
    # TODO: Record the SBML warnings and add them to the report.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        return read_sbml_model(filename)


def validate_model(context, param, value):
    """Load model path from different locations."""
    if value is not None:
        return _load_model(value)
    elif "MEMOTE_MODEL" in os.environ:
        value = os.environ["MEMOTE_MODEL"]
        if not exists(value):
            raise click.BadParameter(
                "The given path of MEMOTE_MODEL '{}' does not exist."
                "".format(value))
        if not isfile(value):
            raise click.BadParameter(
                "The given path of MEMOTE_MODEL '{}' is not a valid file."
                "".format(value))
        return _load_model(value)
    elif "model" in context.default_map:
        value = context.default_map["model"]
        if not exists(value):
            raise click.BadParameter(
                "The path configured for 'model' ({}) does not exist."
                "".format(value))
        if not isfile(value):
            raise click.BadParameter(
                "The path configured for 'model' ({}) is not a valid file."
                "".format(value))
        return _load_model(value)
    else:
        raise click.BadParameter("No 'model' path given or configured.")


def validate_directory(context, param, value):
    """Load directory from different locations."""
    if value is not None:
        return value
    elif "MEMOTE_DIRECTORY" in os.environ:
        value = os.environ["MEMOTE_DIRECTORY"]
        if not exists(value):
            raise click.BadParameter(
                "The given path of MEMOTE_DIRECTORY '{}' does not exist."
                "".format(value))
        if not isdir(value):
            raise click.BadParameter(
                "The given path of MEMOTE_DIRECTORY '{}' is not a valid "
                "directory.".format(value))
        return value
    elif "directory" in context.default_map:
        value = context.default_map["directory"]
        if not exists(value):
            raise click.BadParameter(
                "The path configured for 'directory' ({}) does not exist."
                "".format(value))
        if not isdir(value):
            raise click.BadParameter(
                "The path configured for 'directory' ({}) is not a valid "
                "directory.".format(value))
        return value


def validate_collect(context, param, value):
    """Handle the report collection flag."""
    if value is not None:
        return value
    elif "collect" in context.default_map:
        return context.default_map["collect"]
    else:
        return True


def validate_pytest_args(context, param, value):
    """Handle additional arguments to pytest."""
    if value is not None:
        return shlex.split(value)
    elif "addargs" in context.default_map:
        return shlex.split(context.default_map["addargs"])
    else:
        return list()


def validate_repository(context, param, value):
    """Load repository slug from different locations."""
    if value is not None:
        return value
    elif "github_repository" in context.default_map:
        return context.default_map["github_repository"]
    else:
        raise click.BadParameter(
            "No GitHub repository slug provided or configured.")


def validate_username(context, param, value):
    """Load username from different locations."""
    if value is not None:
        return value
    elif "github_username" in context.default_map:
        return context.default_map["github_username"]
    else:
        raise click.BadParameter(
            "No GitHub username provided or configured.")


def probe_git():
    """Return a git repository instance if it exists."""
    try:
        repo = git.Repo()
    except git.InvalidGitRepositoryError:
        click.echo(
            Fore.YELLOW +
            "We highly recommend keeping your model in a git repository."
            " It allows you to track changes and to easily collaborate with"
            " others via online platforms such as https://github.com.\n"
            + Fore.RESET)  # noqa: W503
        return
    if repo.is_dirty():
        click.echo(
            Fore.RED +
            "Please git commit or git stash all changes before running"
            " the memote suite." + Fore.RESET, err=True)
        sys.exit(1)
    return repo


def abort_if_false(ctx, param, value):
    """Require confirmation."""
    if not value:
        ctx.abort()
