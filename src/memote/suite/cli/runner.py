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

import logging
import os
import sys
import tempfile
from getpass import getpass
from gzip import GzipFile
from multiprocessing import Process
from os.path import isfile, join
from shutil import copy2, move
from tempfile import mkdtemp
from time import sleep

import click
import click_log
import git
import requests
import travis.encrypt as te
from cookiecutter.main import cookiecutter, get_user_config
from requests.exceptions import HTTPError
from sqlalchemy import create_engine
from sqlalchemy.exc import ArgumentError

import memote.suite.api as api
import memote.suite.cli.callbacks as callbacks
from memote import __version__
from memote.suite.cli import CONTEXT_SETTINGS
from memote.suite.cli.reports import report
from memote.suite.results import (
    HistoryManager,
    RepoResultManager,
    ResultManager,
    SQLResultManager,
)
from memote.utils import is_modified, stdout_notifications


try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus


LOGGER = logging.getLogger()
click_log.basic_config(LOGGER)


@click.group()
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-V")
@click_log.simple_verbosity_option(
    LOGGER,
    default="INFO",
    show_default=True,
    type=click.Choice(["CRITICAL", "ERROR", "WARN", "INFO", "DEBUG"]),
)
def cli():
    """
    Metabolic model testing command line tool.

    In its basic invocation memote runs a test suite on a metabolic model.
    Through various subcommands it can further generate three types of pretty
    HTML reports (snapshot, diff and history), generate a model repository
    structure for starting a new project, and recreate the test result history.

    """
    pass


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.option(
    "--collect/--no-collect",
    default=True,
    show_default=True,
    callback=callbacks.validate_collect,
    help="Whether or not to collect test data needed for " "generating a report.",
)
@click.option(
    "--filename",
    type=click.Path(exists=False, writable=True),
    default="result.json.gz",
    show_default=True,
    help="Path for the collected results as JSON. Ignored when "
    "working with a git repository.",
)
@click.option(
    "--location",
    envvar="MEMOTE_LOCATION",
    help="If invoked inside a git repository, try to interpret "
    "the string as an rfc1738 compatible database URL which will be "
    "used to store the test results. Otherwise write to this "
    "directory using the commit hash as the filename.",
)
@click.option(
    "--ignore-git", is_flag=True, help="Avoid checking the git repository status."
)
@click.option(
    "--pytest-args",
    "-a",
    callback=callbacks.validate_pytest_args,
    help="Any additional arguments you want to pass to pytest. "
    "Should be given as one continuous string in quotes.",
)
@click.option(
    "--exclusive",
    multiple=True,
    metavar="TEST",
    help="The name of a test or test module to be run exclusively. "
    "All other tests are skipped. This option can be used "
    "multiple times and takes precedence over '--skip'.",
)
@click.option(
    "--skip",
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
    "information on how to write custom tests "
    "(memote.readthedocs.io). This option can be specified "
    "multiple times.",
)
@click.option(
    "--deployment",
    default="gh-pages",
    show_default=True,
    help="Results will be read from and committed to the given " "branch.",
)
@click.option(
    "--skip-unchanged",
    is_flag=True,
    help="Skip memote run on commits where the model was not " "changed.",
)
@click.argument(
    "model", type=click.Path(exists=True, dir_okay=False), envvar="MEMOTE_MODEL"
)
def run(
    model,
    collect,
    filename,
    location,
    ignore_git,
    pytest_args,
    exclusive,
    skip,
    solver,
    solver_timeout,
    experimental,
    custom_tests,
    deployment,
    skip_unchanged,
):
    """
    Run the test suite on a single model and collect results.

    MODEL: Path to model file. Can also be supplied via the environment variable
    MEMOTE_MODEL or configured in 'setup.cfg' or 'memote.ini'.

    """

    def is_verbose(arg):
        return (
            arg.startswith("--verbosity")
            or arg.startswith("-v")
            or arg.startswith("--verbose")
            or arg.startswith("-q")
            or arg.startswith("--quiet")
        )

    if ignore_git:
        repo = None
    else:
        callbacks.git_installed()
        repo = callbacks.probe_git()
    if collect:
        if repo is not None:
            if location is None:
                LOGGER.critical(
                    "Working with a repository requires a storage location."
                )
                sys.exit(1)
    if not any(a.startswith("--tb") for a in pytest_args):
        pytest_args = ["--tb", "short"] + pytest_args
    if not any(is_verbose(a) for a in pytest_args):
        pytest_args.append("-vv")
    # Check if the model was changed in this commit. Exit `memote run` if this
    # was not the case.
    if skip_unchanged and repo is not None:
        commit = repo.head.commit
        if not is_modified(model, commit):
            LOGGER.info(
                "The model was not modified in commit '%s'. Skipping.", commit.hexsha
            )
            sys.exit(0)
    # Add further directories to search for tests.
    pytest_args.extend(custom_tests)
    # Check if the model can be loaded at all.
    model, sbml_ver, notifications = api.validate_model(model)
    if model is None:
        LOGGER.critical(
            "The model could not be loaded due to the following SBML errors."
        )
        stdout_notifications(notifications)
        sys.exit(1)
    model.solver = solver
    code, result = api.test_model(
        model=model,
        sbml_version=sbml_ver,
        results=True,
        pytest_args=pytest_args,
        skip=skip,
        exclusive=exclusive,
        experimental=experimental,
        solver_timeout=solver_timeout,
    )
    if collect:
        if repo is None:
            manager = ResultManager()
            manager.store(result, filename=filename)
        else:
            LOGGER.info("Checking out deployment branch.")
            # If the repo HEAD is pointing to the most recent branch then
            # GitPython's `repo.active_branch` works. Yet, if the repo is in
            # detached HEAD state, i.e., when a user has checked out a specific
            # commit as opposed to a branch, this won't work and throw a
            # `TypeError`, which we are circumventing below.
            try:
                previous = repo.active_branch
                previous_cmt = previous.commit
                is_branch = True
            except TypeError:
                previous_cmt = repo.head.commit
                is_branch = False
            repo.git.checkout(deployment)
            try:
                manager = SQLResultManager(repository=repo, location=location)
            except (AttributeError, ArgumentError):
                manager = RepoResultManager(repository=repo, location=location)
            LOGGER.info("Committing result and changing back to working branch.")
            manager.store(result, commit=previous_cmt.hexsha)
            repo.git.add(".")
            repo.git.commit(
                "--message", "chore: add result for {}".format(previous_cmt.hexsha)
            )
            if is_branch:
                previous.checkout()
            else:
                repo.commit(previous_cmt)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.option(
    "--replay",
    is_flag=True,
    help="Create a memote repository using the exact same answers "
    "as before. This will not overwrite existing directories. If "
    "you want to adjust the answers, edit the template "
    "'{}'.".format(join(get_user_config()["replay_dir"], "cookiecutter-memote.json")),
)
@click.option(
    "--directory",
    type=click.Path(exists=True, file_okay=False, writable=True),
    help="Create a new model repository in the given directory.",
)
def new(directory, replay):
    """
    Create a suitable model repository structure from a template.

    By using a cookiecutter template, memote will ask you a couple of questions
    and set up a new directory structure that will make your life easier. The
    new directory will be placed in the current directory or respect the given
    --directory option.

    """
    callbacks.git_installed()
    if directory is None:
        directory = os.getcwd()
    cookiecutter(
        "gh:opencobra/cookiecutter-memote", output_dir=directory, replay=replay
    )


def _model_from_stream(stream, filename):
    fd, path = tempfile.mkstemp(suffix=".xml", text=True)
    LOGGER.debug("Creating temporary model file at {}.".format(path))
    if filename.endswith(".gz"):
        with GzipFile(fileobj=stream) as file_handle:
            os.write(fd, file_handle.read())
    else:
        os.write(fd, stream.read())
    os.close(fd)
    model, sbml_ver, notifications = api.validate_model(path)
    LOGGER.debug("Cleaning up temporary file.")
    os.remove(path)
    return model, sbml_ver, notifications


def _test_history(
    model,
    sbml_ver,
    solver,
    solver_timeout,
    manager,
    commit,
    pytest_args,
    skip,
    exclusive,
    experimental,
):
    model.solver = solver
    # Load the experimental configuration using model information.
    if experimental is not None:
        experimental.load(model)
    _, result = api.test_model(
        model,
        sbml_version=sbml_ver,
        results=True,
        pytest_args=pytest_args,
        skip=skip,
        exclusive=exclusive,
        experimental=experimental,
        solver_timeout=solver_timeout,
    )
    manager.store(result, commit=commit)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.option(
    "--rewrite/--no-rewrite",
    default=False,
    help="Whether to overwrite existing results.",
)
@click.option(
    "--location",
    envvar="MEMOTE_LOCATION",
    help="Location of test results. Can either by a directory or an "
    "rfc1738 compatible database URL.",
)
@click.option(
    "--pytest-args",
    "-a",
    callback=callbacks.validate_pytest_args,
    help="Any additional arguments you want to pass to pytest. "
    "Should be given as one continuous string.",
)
@click.option(
    "--deployment",
    default="gh-pages",
    show_default=True,
    help="Results will be read from and committed to the given " "branch.",
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
    default=None,
    help="Timeout in seconds to set on the mathematical " "optimization solver.",
)
@click.option(
    "--exclusive",
    multiple=True,
    metavar="TEST",
    help="The name of a test or test module to be run exclusively. "
    "All other tests are skipped. This option can be used "
    "multiple times and takes precedence over '--skip'.",
)
@click.option(
    "--skip",
    multiple=True,
    metavar="TEST",
    help="The name of a test or test module to be skipped. This "
    "option can be used multiple times.",
)
@click.argument(
    "model", type=click.Path(exists=False, dir_okay=False), envvar="MEMOTE_MODEL"
)
@click.argument("message")
@click.argument("commits", metavar="[COMMIT] ...", nargs=-1)
def history(
    model,
    message,
    rewrite,
    solver,
    solver_timeout,
    location,
    pytest_args,
    deployment,
    commits,
    skip,
    exclusive,
    experimental=None,
):
    """
    Re-compute test results for the git branch history.

    MODEL is the path to the model file.

    MESSAGE is a commit message in case results were modified or added.

    [COMMIT] ... It is possible to list out individual commits that should be
    re-computed or supply a range <oldest commit>..<newest commit>, for example,

        memote history model.xml "chore: re-compute history" 6b84d05..cd49c85

    There are two distinct modes:

    \b
    1. Completely re-compute test results for each commit in the git history.
       This should only be necessary when memote is first used with existing
       model repositories.
    2. By giving memote specific commit hashes, it will re-compute test results
       for those only. This can also be achieved by supplying a commit range.

    """  # noqa: D301
    # callbacks.validate_path(model)
    callbacks.git_installed()
    if location is None:
        raise click.BadParameter("No 'location' given or configured.")
    if "--tb" not in pytest_args:
        pytest_args = ["--tb", "no"] + pytest_args
    try:
        LOGGER.info("Identifying git repository!")
        repo = git.Repo()
    except git.InvalidGitRepositoryError:
        LOGGER.critical(
            "The history requires a git repository in order to follow "
            "the model's commit history."
        )
        sys.exit(1)
    else:
        LOGGER.info("Success!")
        previous = repo.active_branch
        LOGGER.info("Checking out deployment branch {}.".format(deployment))
        repo.git.checkout(deployment)
    # Temporarily move the results to a new location so that they are
    # available while checking out the various commits.
    engine = None
    tmp_location = mkdtemp()
    try:
        # Test if the location can be opened as a database.
        engine = create_engine(location)
        engine.dispose()
        new_location = location
        if location.startswith("sqlite"):
            # Copy the SQLite database to a temporary location. Other
            # databases are not file-based and thus git independent.
            url = location.split("/", maxsplit=3)
            if isfile(url[3]):
                copy2(url[3], tmp_location)
            new_location = "{}/{}".format("/".join(url[:3] + [tmp_location]), url[3])
            LOGGER.info(
                "Temporarily moving database from '%s' to '%s'.",
                url[3],
                join(tmp_location, url[3]),
            )
        manager = SQLResultManager(repository=repo, location=new_location)
    except (AttributeError, ArgumentError):
        LOGGER.info(
            "Temporarily moving results from '%s' to '%s'.", location, tmp_location
        )
        move(location, tmp_location)
        new_location = join(tmp_location, location)
        manager = RepoResultManager(repository=repo, location=new_location)
    LOGGER.info("Recomputing result history!")
    history = HistoryManager(repository=repo, manager=manager)
    history.load_history(model, skip={deployment})
    if len(commits) == 0:
        commits = list(history.iter_commits())
    elif len(commits) == 1 and ".." in commits[0]:
        commits = repo.git.rev_list(commits[0]).split(os.linesep)
    for commit in commits:
        cmt = repo.commit(commit)
        # Rewrite to full length hexsha.
        commit = cmt.hexsha
        if not is_modified(model, cmt):
            LOGGER.info(
                "The model was not modified in commit '{}'. " "Skipping.".format(commit)
            )
            continue
        # Should we overwrite an existing result?
        if commit in history and not rewrite:
            LOGGER.info("Result for commit '{}' exists. Skipping.".format(commit))
            continue
        LOGGER.info("Running the test suite for commit '{}'.".format(commit))
        blob = cmt.tree[model]
        model_obj, sbml_ver, notifications = _model_from_stream(
            blob.data_stream, blob.name
        )
        if model_obj is None:
            LOGGER.critical(
                "The model could not be loaded due to the " "following SBML errors."
            )
            stdout_notifications(notifications)
            continue
        proc = Process(
            target=_test_history,
            args=(
                model_obj,
                sbml_ver,
                solver,
                solver_timeout,
                manager,
                commit,
                pytest_args,
                skip,
                exclusive,
                experimental,
            ),
        )
        proc.start()
        proc.join()
    LOGGER.info("Finished recomputing!")
    # Copy back all new and modified files and add them to the index.
    LOGGER.info("Committing recomputed results!")
    repo.git.checkout(deployment)
    if engine is not None:
        manager.session.close()
        if location.startswith("sqlite"):
            copy2(join(tmp_location, url[3]), url[3])
    else:
        move(new_location, os.getcwd())
    repo.git.add(".")
    repo.git.commit("--message", message)
    LOGGER.info("Success!")
    # Checkout the original branch.
    previous.checkout()
    LOGGER.info("Done.")


def _setup_gh_repo(github_repository, github_username, note):
    password = getpass("GitHub Password: ")

    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Memote Query"}
    credentials = (github_username, password)

    # Authenticate user on GitHub
    try:
        LOGGER.info("Using your credentials to authenticate you on GitHub.")
        response = requests.get(
            "https://api.github.com/user", auth=credentials, headers=headers
        )
        response.raise_for_status()
    except HTTPError as error:
        if error.response.status_code == 401:
            LOGGER.critical("Authentication failed! " "Incorrect username or password?")
            sys.exit(1)
        else:
            LOGGER.critical(
                "Your account could not be authenticated. " "{}".format(str(error))
            )
            sys.exit(1)
    else:
        user = response.json()
        when = user[u"created_at"]
        LOGGER.info(
            "Logged in to user '{}' created on '{}'.".format(user[u"login"], when)
        )

    # Get a user's repository or create the repository if it doesn't exist on
    # GitHub.
    try:
        LOGGER.info("Retrieving repository {}".format(github_repository))
        endpoint = "https://api.github.com/repos/{}/{}".format(
            user["login"], github_repository
        )
        response = requests.get(endpoint, auth=credentials, headers=headers)
        response.raise_for_status()
        LOGGER.warning(
            "Using existing repository '{}'. This may override previous "
            "settings.".format(github_repository)
        )
        gh_repo = response.json()
    except HTTPError as error:
        if error.response.status_code == 404:
            try:
                LOGGER.info(
                    "'{}' did not exist on GitHub yet."
                    " Creating it for you now!".format(github_repository)
                )
                response = requests.post(
                    "https://api.github.com/user/repos",
                    auth=credentials,
                    headers=headers,
                    json={"name": github_repository},
                )
                response.raise_for_status()
            except HTTPError as error:
                LOGGER.critical(
                    "The repository cannot be created on GitHub. "
                    "{}".format(str(error))
                )
                sys.exit(1)
            else:
                gh_repo = response.json()
        else:
            LOGGER.critical(
                "The repository cannot be found on GitHub. " "{}".format(str(error))
            )
            sys.exit(1)

    # Create a personal access token on GitHub which is only used to generate
    # the Travis APIv3 access token.
    auth_note = "Travis APIv3 Auth for {}".format(github_repository)
    payload = {
        "scopes": [
            "read:org",
            "user:email",
            "repo_deployment",
            "repo:status",
            "write:repo_hook",
        ],
        "note": auth_note,
    }
    try:
        LOGGER.info("Creating Travis APIv3 authentication token for you now!")
        response = requests.post(
            "https://api.github.com/authorizations",
            auth=credentials,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
    except HTTPError as error:
        LOGGER.info(
            "An error occurred. Most likely an authentication token with the "
            "note '{}' already exists. If so, please delete it and try again."
            "If not, please refer to the following error code for "
            "further information: {}".format(auth_note, str(error))
        )
        sys.exit(1)
    else:
        auth_response = response.json()
        LOGGER.info("Success!")

    # Create a personal access token that allows Travis to push to a repo.
    payload = {"scopes": ["repo"], "note": note}
    try:
        LOGGER.info("Creating repo access token.")
        response = requests.post(
            "https://api.github.com/authorizations",
            auth=credentials,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
    except HTTPError as error:
        LOGGER.critical(
            "An error occurred. Most likely a repo access token with the "
            "note '{}' already exists. "
            "Either delete it or choose another note using the option "
            "'--note'. If not, please refer to the following error code for "
            "further information: {}".format(note, str(error))
        )
        sys.exit(1)
    else:
        repo_access_response = response.json()
        LOGGER.info("Success!")
    return gh_repo["full_name"], auth_response["token"], repo_access_response["token"]


def _setup_travis_ci(gh_repo_name, auth_token, repo_access_token):
    # travis-ci.org is the open source endpoint only! We will need to hit
    # travis-ci.com for private projects!

    # Headers for API v2. This is only necessary because generating a Travis
    # API token from a GitHub Token isn't possible in the API v3 yet. This way
    # is recommended as per:
    # https://github.com/travis-ci/travis-ci/issues/9273
    headers_v2_only = {
        "User-Agent": "Memote",
        "Accept": "application/vnd.travis-ci.2+json",
    }

    # Generate Travis API token:
    try:
        LOGGER.info("Generating Travis API token.")
        response = requests.post(
            "https://api.travis-ci.org/auth/github",
            headers=headers_v2_only,
            data={"github_token": auth_token},
        )
        response.raise_for_status()
    except HTTPError as error:
        LOGGER.critical(
            "Something is wrong with the generated APIv3 authentication token "
            "or you did not link your GitHub account on "
            "'https://travis-ci.org/'? Please refer to the following error "
            "message for further information: {}".format(str(error))
        )
        sys.exit(1)
    else:
        LOGGER.info("Success!")
        travis_api_token = response.json()["access_token"]

    # Headers for API v3!
    headers = {
        "Travis-API-Version": "3",
        "Authorization": "token {}".format(travis_api_token),
        "User-Agent": "Memote Query",
    }

    # Authenticate the User on Travis
    try:
        LOGGER.info("Authorizing with TravisCI.")
        response = requests.get("https://api.travis-ci.org/user", headers=headers)
        response.raise_for_status()
    except HTTPError as error:
        LOGGER.critical(
            "Something is wrong with the generated token or you did not "
            "link your GitHub account on 'https://travis-ci.org/'? Please "
            "refer to the following error code for "
            "further information: {}".format(str(error))
        )
        sys.exit(1)
    else:
        LOGGER.info("Success!")
        t_user = response.json()

    # Synchronize a User's projects between GitHub and Travis
    LOGGER.info("Synchronizing user projects between GitHub and Travis.")
    synced = False
    for _ in range(60):
        response = requests.post(
            "https://api.travis-ci.org/user/{}/sync".format(t_user["id"]),
            headers=headers,
        )
        if response.status_code == 200:
            synced = True
            LOGGER.info("Success!")
            break
        else:
            LOGGER.info("Still synchronizing...")
            sleep(0.5)
    if not synced:
        LOGGER.critical(
            "Could not synchronize your projects between GitHub and Travis!"
            "The latest response code is {}".format(response.status_code)
        )
        sys.exit(1)

    # Make sure GitHub repo can be found on Travis CI.#
    url_safe_repo_name = quote_plus(gh_repo_name)
    try:
        LOGGER.info("Find repository {} on Travis CI".format(gh_repo_name))
        response = requests.get(
            "https://api.travis-ci.org/repo/{}".format(url_safe_repo_name),
            headers=headers,
        )
        response.raise_for_status()
    except HTTPError as error:
        if error.response.status_code == 404:
            LOGGER.critical(
                "Repository could not be found. Is it on GitHub already and "
                "spelled correctly?"
            )
            sys.exit(1)
        else:
            LOGGER.critical(
                "An error occurred. Please refer to the following error "
                "message for further information: {}".format(str(error))
            )
            sys.exit(1)
    else:
        LOGGER.info("Success!")
        t_repo = response.json()

    # Use repo ID to activate Travis CI for this repo
    try:
        LOGGER.info("Activating automatic testing for you " "on Travis CI.")
        endpoint = "https://api.travis-ci.org/repo/{}/activate".format(
            url_safe_repo_name
        )
        response = requests.post(endpoint, headers=headers)
        response.raise_for_status()
    except HTTPError as error:
        LOGGER.critical(
            "Unable to enable automatic testing on Travis CI! "
            "Please refer to the following error message for "
            "further information: {}".format(str(error))
        )
        sys.exit(1)

    # Check if activation was successful
    activated = False
    for _ in range(60):
        try:
            LOGGER.info(
                "Check if activation {} on Travis CI "
                "was successful".format(gh_repo_name)
            )
            response = requests.get(
                "https://api.travis-ci.org/repo/{}".format(url_safe_repo_name),
                headers=headers,
            )
        except HTTPError as error:
            LOGGER.critical(
                "An error occurred. Please refer to the following error "
                "message for further information: {}".format(str(error))
            )
            sys.exit(1)
        else:
            t_repo = response.json()
        if t_repo["active"]:
            activated = True
            LOGGER.info(
                "Your repository is now on GitHub and automatic testing has "
                "been enabled on Travis CI. Congrats!"
            )
            break
        else:
            LOGGER.info("Still activating...")
            sleep(0.5)
    if not activated:
        LOGGER.critical(
            "Unable to enable automatic testing on Travis CI! "
            "Delete all tokens belonging to this repo at "
            "https://github.com/settings/tokens then try running "
            "`memote online` again. If this fails yet again, "
            "please open an issue at "
            "https://github.com/opencobra/memote/issues."
        )
        sys.exit(1)
    LOGGER.info("Encrypting GitHub token for repo '{}'.".format(gh_repo_name))
    key = te.retrieve_public_key(gh_repo_name)
    secret = te.encrypt_key(key, "GITHUB_TOKEN={}".format(repo_access_token).encode())
    return secret


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.help_option("--help", "-h")
@click.option(
    "--note",
    default="memote-ci access",
    show_default=True,
    help="A note describing a personal access token on GitHub. " "Must be unique!",
)
@click.option(
    "--github_repository",
    callback=callbacks.validate_repository,
    help="The repository name on GitHub. Usually this is configured " "for you.",
)
@click.option(
    "--github_username",
    callback=callbacks.validate_username,
    help="The GitHub username. Usually this is configured for you.",
)
def online(note, github_repository, github_username):
    """Upload the repository to GitHub and enable testing on Travis CI."""
    callbacks.git_installed()
    try:
        repo = git.Repo()
    except git.InvalidGitRepositoryError:
        LOGGER.critical(
            "'memote online' requires a git repository in order to follow "
            "the current branch's commit history."
        )
        sys.exit(1)
    if note == "memote-ci access":
        note = "{} to {}".format(note, github_repository)

    # Github API calls
    # Set up the git repository on GitHub via API v3.
    gh_repo_name, auth_token, repo_access_token = _setup_gh_repo(
        github_repository, github_username, note
    )

    # Travis API calls
    # Configure Travis CI to use Github auth token then return encrypted token.
    secret = _setup_travis_ci(gh_repo_name, auth_token, repo_access_token)

    # Save the encrypted token in the travis config then commit and push
    LOGGER.info("Storing GitHub token in '.travis.yml'.")
    config = te.load_travis_configuration(".travis.yml")
    global_env = config.setdefault("env", {}).get("global")
    if global_env is None:
        config["env"]["global"] = global_env = {}
    try:
        global_env["secure"] = secret
    except TypeError:
        global_env.append({"secure": secret})
    te.dump_travis_configuration(config, ".travis.yml")
    LOGGER.info("Add, commit and push changes to '.travis.yml' to GitHub.")
    repo.index.add([".travis.yml"])
    repo.git.commit("--message", "chore: add encrypted GitHub access token")
    repo.git.push("--set-upstream", "origin", repo.active_branch.name)


cli.add_command(report)
