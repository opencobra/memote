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
from os.path import join
from multiprocessing import Process
from getpass import getpass
from time import sleep

import click
import git
import ruamel.yaml as yaml
from colorama import Fore
from cookiecutter.main import cookiecutter, get_user_config
from github import (
    Github, BadCredentialsException, UnknownObjectException, GithubException)
from travispy import TravisPy
from travispy.errors import TravisError
from travis.encrypt import encrypt_key, retrieve_public_key

import memote.suite.api as api
import memote.suite.cli.callbacks as callbacks
from memote import __version__
from memote.suite.cli import CONTEXT_SETTINGS
from memote.suite.cli.reports import report

LOGGER = logging.getLogger()


@click.group()
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-V")
@click.option("--level", "-l", default="INFO",
              type=click.Choice(["CRITICAL", "ERROR", "WARN", "INFO", "DEBUG"]),
              help="Set the log level.", show_default=True)
def cli(level):
    """
    Metabolic model testing command line tool.

    In its basic invocation memote runs a test suite on a metabolic model.
    Through various subcommands it can further generate a pretty HTML report,
    generate a model repository structure for starting a new project, and
    recreate the test result history.
    """
    logging.basicConfig(level=level, format="%(levelname)s - %(message)s")


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.argument("model", type=click.Path(exists=True, dir_okay=False),
                required=False, callback=callbacks.validate_model)
@click.option("--collect/--no-collect", default=True, show_default=True,
              callback=callbacks.validate_collect,
              help="Whether or not to collect test data needed for "
                   "generating a report.")
@click.option("--filename", type=click.Path(exists=False, writable=True),
              default="result.json", show_default=True,
              help="Path for the collected results as JSON.")
@click.option("--directory", type=click.Path(exists=True, file_okay=False,
                                             writable=True),
              callback=callbacks.validate_directory,
              help="If invoked inside a git repository, write the test results "
              "to this directory using the commit hash as the filename.")
@click.option("--ignore-git", is_flag=True,
              help="Avoid checking the git repository status.")
@click.option("--pytest-args", "-a", callback=callbacks.validate_pytest_args,
              help="Any additional arguments you want to pass to pytest. "
                   "Should be given as one continuous string.")
def run(model, collect, filename, directory, ignore_git, pytest_args):
    """
    Run the test suite and collect results.

    MODEL: Path to model file. Can also be supplied via the environment variable
    MEMOTE_MODEL or configured in 'setup.cfg' or 'memote.ini'.
    """
    if ignore_git:
        repo = None
    else:
        repo = callbacks.probe_git()
    if "--tb" not in pytest_args:
        pytest_args = ["--tb", "line"] + pytest_args
    if collect:
        if repo is not None and directory is not None:
            filename = join(directory,
                            "{}.json".format(repo.active_branch.commit.hexsha))
        code = api.test_model(model, filename, pytest_args=pytest_args)
    else:
        code = api.test_model(model, pytest_args=pytest_args)
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


def _test_history(context, filename, pytest_args):
    model = callbacks.validate_model(context, "model", None)
    api.test_model(model, filename, pytest_args=pytest_args)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@click.help_option("--help", "-h")
@click.option("--yes", "-y", is_flag=True, callback=callbacks.abort_if_false,
              expose_value=False, help="Confirm overwriting previous results.",
              prompt="Are you sure that you want to change history?")
@click.option("--directory", type=click.Path(exists=True, file_okay=False,
                                             writable=True),
              callback=callbacks.validate_directory,
              help="Generated JSON files from the commit history will be "
                   "written to this directory.")
@click.option("--pytest-args", "-a", callback=callbacks.validate_pytest_args,
              help="Any additional arguments you want to pass to pytest. "
                   "Should be given as one continuous string.")
@click.argument("commits", metavar="[COMMIT] ...", nargs=-1)
def history(context, directory, pytest_args, commits):
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
        branch = repo.active_branch
    except git.InvalidGitRepositoryError:
        click.echo(
            Fore.RED +
            "The history requires a git repository in order to follow "
            "the current branch's commit history."
            + Fore.RESET, err=True)  # noqa: W503
        sys.exit(1)
    if len(commits) > 0:
        # TODO: Convert hashes to git.Commit instances.
        raise NotImplementedError(u"Coming soon™.")
    else:
        commits = list(branch.commit.iter_parents())
        commits.insert(0, branch.commit)
    for commit in commits:
        repo.git.checkout(commit)
        click.echo(
            Fore.GREEN +
            "Running the test suite for commit '{}'.".format(
                branch.commit.hexsha)
            + Fore.RESET)  # noqa: W503
        filename = join(directory, "{}.json".format(commit.hexsha))
        proc = Process(target=_test_history,
                       args=(context, filename, pytest_args))
        proc.start()
        proc.join()
    repo.git.checkout(branch)
    # repo.head.reset(index=True, working_tree=True)  # superfluous?


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.option("--note", default="memote-ci access", show_default=True,
              help="A note describing a personal access token on GitHub. "
                   "Must be unique!")
@click.option("--repository", callback=callbacks.validate_repository,
              help="The repository name on GitHub. Usually this is configured "
                   "for you.")
@click.option("--username", callback=callbacks.validate_username,
              help="The GitHub username. Usually this is configured for you.")
@click.pass_context
def online(context, note, repository, username):
    """Upload the repository to GitHub and enable testing on Travis CI."""
    try:
        repo = git.Repo()
    except git.InvalidGitRepositoryError:
        click.echo(
            Fore.RED +
            "The history requires a git repository in order to follow "
            "the current branch's commit history."
            + Fore.RESET, err=True)  # noqa: W503
        sys.exit(1)
    password = getpass("GitHub Password: ")
    gh = Github(username, password)
    user = gh.get_user()
    try:
        when = user.created_at.isoformat(sep=" ")
        click.echo(
            "Logged in to user '{}' created on '{}'.".format(user.login, when))
    except BadCredentialsException:
        click.echo(
            Fore.RED +
            "Incorrect username or password!"
            + Fore.RESET, err=True)  # noqa: W503
        sys.exit(1)
    try:
        gh_repo = user.get_repo(repository)
        click.echo(
            Fore.YELLOW +
            "Using existing repository '{}'. This may override previous "
            "settings.".format(repository)
            + Fore.RESET)  # noqa: W503
    except UnknownObjectException:
        gh_repo = user.create_repo(repository)
    try:
        click.echo("Creating token.")
        auth = user.create_authorization(scopes=["repo"], note=note)
    except GithubException:
        click.echo(
            Fore.RED +
            "A personal access token with the note '{}' already exists. "
            "Either delete it or choose another note.".format(note)
            + Fore.RESET, err=True)  # noqa: W503
        sys.exit(1)
    try:
        click.echo("Authorizing with TravisCI.")
        travis = TravisPy.github_auth(auth.token)
        t_user = travis.user()
    except TravisError:
        click.echo(
            Fore.RED +
            "Something is wrong with the generated token or you did not "
            "link your GitHub account on 'https://travis-ci.org/'!"
            + Fore.RESET, err=True)  # noqa: W503
        sys.exit(1)
    click.echo("Synchronizing repositories.")
    while not t_user.sync():
        sleep(0.1)
    try:
        t_repo = travis.repo(gh_repo.full_name)
    except TravisError:
        click.echo(
            Fore.RED +
            "Repository could not be found. Is it on GitHub already and "
            "spelled correctly?"
            + Fore.RESET, err=True)  # noqa: W503
        sys.exit(1)
    if t_repo.enable():
        click.echo(
            Fore.GREEN +
            "Your repository is now on GitHub and automatic testing has "
            "been enabled on Travis CI. Congrats!" + Fore.RESET)  # noqa: W503
    else:
        click.echo(
            Fore.RED +
            "Unable to enable automatic testing on Travis CI!",
            + Fore.RESET, err=True)  # noqa: W503
        sys.exit(1)
    click.echo(
        "Encrypting GitHub token for repo '{}'.".format(gh_repo.full_name))
    key = retrieve_public_key(gh_repo.full_name)
    secret = encrypt_key(key, "GITHUB_TOKEN={}".format(auth.token).encode())
    click.echo("Storing GitHub token in '.travis.yml'.")
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
