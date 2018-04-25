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

"""Provide commands for running the test suite on a metabolic model."""

from __future__ import absolute_import

import io
import os
import sys
import logging
from functools import partial
from os.path import join
from multiprocessing import Process
from getpass import getpass
from time import sleep

import click
import click_log
import git
import ruamel.yaml as yaml
from cookiecutter.main import cookiecutter, get_user_config
from github import (
    Github, BadCredentialsException, UnknownObjectException, GithubException)
from sqlalchemy.exc import ArgumentError
from travispy import TravisPy
from travispy.errors import TravisError
from travis.encrypt import encrypt_key, retrieve_public_key

import memote.suite.api as api
import memote.suite.cli.callbacks as callbacks
from memote import __version__
from memote.suite.cli import CONTEXT_SETTINGS
from memote.suite.cli.reports import report
from memote.suite.results import (
    ResultManager, RepoResultManager, SQLResultManager, HistoryManager)

LOGGER = logging.getLogger()
click_log.basic_config(LOGGER)


@click.group()
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-V")
@click_log.simple_verbosity_option(
    LOGGER, default="INFO", show_default=True,
    type=click.Choice(["CRITICAL", "ERROR", "WARN", "INFO", "DEBUG"]))
def cli():
    """
    Metabolic model testing command line tool.

    In its basic invocation memote runs a test suite on a metabolic model.
    Through various subcommands it can further generate a pretty HTML report,
    generate a model repository structure for starting a new project, and
    recreate the test result history.
    """
    pass


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.option("--collect/--no-collect", default=True, show_default=True,
              callback=callbacks.validate_collect,
              help="Whether or not to collect test data needed for "
                   "generating a report.")
@click.option("--filename", type=click.Path(exists=False, writable=True),
              default="result.json", show_default=True,
              help="Path for the collected results as JSON.")
@click.option("--location", type=str, envvar="MEMOTE_LOCATION",
              help="If invoked inside a git repository, try to interpret "
              "the string as an rfc1738 compatible database URL which will be "
              "used to store the test results. Otherwise write to this "
              "directory using the commit hash as the filename.")
@click.option("--ignore-git", is_flag=True, show_default=True,
              help="Avoid checking the git repository status.")
@click.option("--pytest-args", "-a", callback=callbacks.validate_pytest_args,
              help="Any additional arguments you want to pass to pytest. "
                   "Should be given as one continuous string in quotes.")
@click.option("--exclusive", type=str, multiple=True, metavar="TEST",
              help="The name of a test or test module to be run exclusively. "
                   "All other tests are skipped. This option can be used "
                   "multiple times and takes precedence over '--skip'.")
@click.option("--skip", type=str, multiple=True, metavar="TEST",
              help="The name of a test or test module to be skipped. This "
                   "option can be used multiple times.")
@click.option("--solver", type=click.Choice(["cplex", "glpk", "gurobi"]),
              default="glpk", show_default=True,
              help="Set the solver to be used.")
@click.option("--experimental", type=click.Path(exists=True, dir_okay=False),
              default=None, callback=callbacks.validate_experimental,
              help="Define additional tests using experimental data.")
@click.option("--custom-tests", type=click.Path(exists=True, file_okay=False),
              multiple=True,
              help="A path to a directory containing custom test "
                   "modules. Please refer to the documentation for more "
                   "information on how to write custom tests. May be "
                   "specified multiple times.")
@click.argument("model", type=click.Path(exists=True, dir_okay=False),
                envvar="MEMOTE_MODEL", callback=callbacks.validate_model)
def run(model, collect, filename, location, ignore_git, pytest_args, exclusive,
        skip, solver, experimental, custom_tests):
    """
    Run the test suite and collect results.

    MODEL: Path to model file. Can also be supplied via the environment variable
    MEMOTE_MODEL or configured in 'setup.cfg' or 'memote.ini'.
    """
    if ignore_git:
        repo = None
    else:
        repo = callbacks.probe_git()
    if not any(a.startswith("--tb") for a in pytest_args):
        pytest_args = ["--tb", "short"] + pytest_args
    if not any(a.startswith("-v") for a in pytest_args):
        pytest_args.append("-vv")
    # Add further directories to search for tests.
    pytest_args.extend(custom_tests)
    model.solver = solver
    if collect:
        if repo is None:
            manager = ResultManager()
            store = partial(manager.store, filename=filename)
        else:
            if location is None:
                LOGGER.critical(
                    "Working with a repository requires a storage location.")
                sys.exit(1)
            try:
                manager = SQLResultManager(repository=repo, location=location)
            except (AttributeError, ArgumentError):
                manager = RepoResultManager(repository=repo, location=location)
            store = manager.store
    code, result = api.test_model(
        model=model, results=True, pytest_args=pytest_args, skip=skip,
        exclusive=exclusive, experimental=experimental)
    if collect:
        store(result=result)
    sys.exit(code)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.option("--replay", is_flag=True,
              help="Create a memote repository using the exact same answers "
              "as before. This will not overwrite existing directories. If "
              "you want to adjust the answers, edit the template "
              "'{}'.".format(join(get_user_config()["replay_dir"],
                                  "cookiecutter-memote.json")))
@click.option("--directory", type=click.Path(exists=True, file_okay=False,
                                             writable=True),
              envvar="MEMOTE_DIRECTORY",
              help="Create a new model repository in the given directory.")
def new(directory, replay):
    """
    Create a suitable model repository structure from a template.

    By using a cookiecutter template, memote will ask you a couple of questions
    and set up a new directory structure that will make your life easier. The
    new directory will be placed in the current directory or respect the given
    --directory option.
    """
    if directory is None:
        directory = os.getcwd()
    cookiecutter("gh:opencobra/cookiecutter-memote", output_dir=directory,
                 replay=replay)


def _test_history(model, solver, manager, commit, pytest_args, skip,
                  exclusive, experimental):
    model = callbacks.validate_model(None, "model", model)
    model.solver = solver
    _, result = api.test_model(
        model, results=True, pytest_args=pytest_args, skip=skip,
        exclusive=exclusive, experimental=experimental)
    manager.store(result, commit=commit)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.option("--yes", "-y", is_flag=True, callback=callbacks.abort_if_false,
              expose_value=False, help="Confirm overwriting previous results.",
              prompt="Are you sure that you want to change history?")
@click.option("--location", type=str, envvar="MEMOTE_LOCATION",
              help="Generated JSON files from the commit history will be "
                   "written to this directory.")
@click.option("--pytest-args", "-a", callback=callbacks.validate_pytest_args,
              help="Any additional arguments you want to pass to pytest. "
                   "Should be given as one continuous string.")
@click.option("--solver", type=click.Choice(["cplex", "glpk", "gurobi"]),
              default="glpk", show_default=True,
              help="Set the solver to be used.")
@click.option("--experimental", type=click.Path(exists=True, dir_okay=False),
              default=None, callback=callbacks.validate_experimental,
              help="Define additional tests using experimental data.")
@click.option("--exclusive", type=str, multiple=True, metavar="TEST",
              help="The name of a test or test module to be run exclusively. "
                   "All other tests are skipped. This option can be used "
                   "multiple times and takes precedence over '--skip'.")
@click.option("--skip", type=str, multiple=True, metavar="TEST",
              help="The name of a test or test module to be skipped. This "
                   "option can be used multiple times.")
@click.argument("model", type=click.Path(exists=True, dir_okay=False),
                envvar="MEMOTE_MODEL")
@click.argument("commits", metavar="[COMMIT] ...", nargs=-1)
def history(model, solver, location, pytest_args, commits, skip,
            exclusive, experimental):  # noqa: D301
    """
    Re-compute test results for the git branch history.

    This command requires the model file to be supplied either by the
    environment variable MEMOTE_MODEL or configured in a 'setup.cfg' or
    'memote.ini' file.

    There are two distinct modes:

    \b
    1. Completely re-compute test results for each commit in the git history.
       This should only be necessary when memote is first used with existing
       model repositories.
    2. By giving memote specific commit hashes, it will re-compute test results
       for those only.
    """
    if "--tb" not in pytest_args:
        pytest_args = ["--tb", "no"] + pytest_args
    try:
        repo = git.Repo()
    # TODO: If no directory was given use system tempdir and create report in
    #  gh-pages.
    except git.InvalidGitRepositoryError:
        LOGGER.critical(
            "The history requires a git repository in order to follow "
            "the current branch's commit history.")
        sys.exit(1)
    try:
        manager = SQLResultManager(repository=repo, location=location)
    except (AttributeError, ArgumentError):
        manager = RepoResultManager(repository=repo, location=location)
    if len(commits) > 0:
        # TODO: Convert hashes to `git.Commit` instances.
        raise NotImplementedError(u"Coming soon™.")
    else:
        history = HistoryManager(repository=repo, manager=manager)
        history.build_branch_structure()
    for commit in history.iter_commits():
        repo.git.checkout(commit)
        # TODO: Skip this commit if model was not touched.
        LOGGER.info(
            "Running the test suite for commit '{}'.".format(commit))
        proc = Process(
            target=_test_history,
            args=(model, solver, manager, commit, pytest_args, skip,
                  exclusive, experimental))
        proc.start()
        proc.join()
    history.reset()


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.option("--note", default="memote-ci access", show_default=True,
              help="A note describing a personal access token on GitHub. "
                   "Must be unique!")
@click.option("--github_repository", callback=callbacks.validate_repository,
              help="The repository name on GitHub. Usually this is configured "
                   "for you.")
@click.option("--github_username", callback=callbacks.validate_username,
              help="The GitHub username. Usually this is configured for you.")
def online(note, github_repository, github_username):
    """Upload the repository to GitHub and enable testing on Travis CI."""
    try:
        repo = git.Repo()
    except git.InvalidGitRepositoryError:
        LOGGER.critical(
            "The history requires a git repository in order to follow "
            "the current branch's commit history.")
        sys.exit(1)
    password = getpass("GitHub Password: ")
    gh = Github(github_username, password)
    user = gh.get_user()
    try:
        when = user.created_at.isoformat(sep=" ")
        LOGGER.info(
            "Logged in to user '{}' created on '{}'.".format(user.login, when))
    except BadCredentialsException:
        LOGGER.critical("Incorrect username or password!")
        sys.exit(1)
    try:
        gh_repo = user.get_repo(github_repository)
        LOGGER.warning(
            "Using existing repository '{}'. This may override previous "
            "settings.".format(github_repository))
    except UnknownObjectException:
        gh_repo = user.create_repo(github_repository)
    try:
        LOGGER.info("Creating token.")
        auth = user.create_authorization(scopes=["repo"], note=note)
    except GithubException:
        LOGGER.critical(
            "A personal access token with the note '{}' already exists. "
            "Either delete it or choose another note.".format(note))
        sys.exit(1)
    try:
        LOGGER.info("Authorizing with TravisCI.")
        travis = TravisPy.github_auth(auth.token)
        t_user = travis.user()
    except TravisError:
        LOGGER.critical(
            "Something is wrong with the generated token or you did not "
            "link your GitHub account on 'https://travis-ci.org/'!")
        sys.exit(1)
    LOGGER.info("Synchronizing repositories.")
    while not t_user.sync():
        sleep(0.1)
    try:
        t_repo = travis.repo(gh_repo.full_name)
    except TravisError:
        LOGGER.critical(
            "Repository could not be found. Is it on GitHub already and "
            "spelled correctly?")
        sys.exit(1)
    if t_repo.enable():
        LOGGER.info(
            "Your repository is now on GitHub and automatic testing has "
            "been enabled on Travis CI. Congrats!")
    else:
        LOGGER.critical("Unable to enable automatic testing on Travis CI!")
        sys.exit(1)
    LOGGER.info(
        "Encrypting GitHub token for repo '{}'.".format(gh_repo.full_name))
    key = retrieve_public_key(gh_repo.full_name)
    secret = encrypt_key(key, "GITHUB_TOKEN={}".format(auth.token).encode())
    LOGGER.info("Storing GitHub token in '.travis.yml'.")
    with io.open(".travis.yml", "r") as file_h:
        config = yaml.load(file_h, yaml.RoundTripLoader)
    config["env"]["global"].append({"secure": secret})
    with io.open(".travis.yml", "w") as file_h:
        yaml.dump(config, file_h, Dumper=yaml.RoundTripDumper)
    repo.index.add([".travis.yml"])
    repo.index.commit("chore: add encrypted GitHub access token")
    repo.remotes.origin.push(all=True)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.argument("message")
def save(message):
    """
    Save current model changes with the given message.

    If a remote repository 'origin' exists the changes will also be uploaded.
    """
    raise NotImplementedError(u"Coming soon™.")


cli.add_command(report)
