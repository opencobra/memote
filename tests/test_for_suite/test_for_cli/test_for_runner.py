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

"""Ensure the expected functioning of ``memote.suite.cli.runner``."""

from __future__ import absolute_import

import os
from builtins import str
from os.path import exists, join, dirname, pardir
from subprocess import check_output

import pytest


from memote.suite.cli.runner import cli
import memote.suite.cli.runner
from memote.suite.cli.config import ConfigFileProcessor


def test_cli(runner):
    """Expect a simple memote invocation to be successful."""
    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert result.output.startswith(
        "Usage: cli [OPTIONS] COMMAND [ARGS]...")


def test_run_simple(runner, model_file):
    """Expect a simple run to function."""
    result = runner.invoke(cli, [
        "run", "--no-collect", "--ignore-git", model_file])
    assert result.exit_code == 0


def test_run_with_experimental_data(runner, model_file):
    """Expect a simple run to function."""
    result = runner.invoke(cli, [
        "run", "--no-collect", "--ignore-git", "--experimental",
        join(dirname(__file__), "data", "valid.yml"), model_file
    ])
    assert result.exit_code == 0


def test_run_output(runner, model_file):
    """Expect a memote run to collect the results as json."""
    output = model_file.split(".", 1)[0] + ".json"
    result = runner.invoke(cli, [
        "run", "--filename", output, "--ignore-git", model_file])
    assert result.exit_code == 0
    assert exists(output)


def test_run_no_location(runner, mock_repo):
    """
    Expect memote run to error when in repo but without specified location.

    """
    previous_wd = os.getcwd()
    os.chdir(mock_repo[0])
    repo = mock_repo[1]
    repo.git.checkout('eb959dd016aaa71fcef96f00b94ce045d6af8f4c')
    result = runner.invoke(cli, ["run", "--location", None, "test.xml"])
    os.chdir(previous_wd)
    assert result.exit_code == 1


def test_run_no_repo_ignore_git_false(runner, model_file, tmpdir):
    """
    Expect memote run to warn user if it was not invoked inside a git repo.

    """
    previous_wd = tmpdir.chdir()
    result = runner.invoke(cli, ["-v", "WARN", "run", model_file])
    previous_wd.chdir()
    assert "warning: We highly recommend" in result.output


def test_run_dirty_repo_ignore_git_false(runner, mock_repo):
    """
    Expect memote run to error if it was invoked inside a dirty git repo.

    """
    previous_wd = os.getcwd()
    os.chdir(mock_repo[0])
    repo = mock_repo[1]
    repo.git.checkout('eb959dd016aaa71fcef96f00b94ce045d6af8f4c')
    new_file = join(mock_repo[0], 'new_file.txt')
    open(new_file, 'a').close()
    repo.git.add(new_file)
    result = runner.invoke(cli, ["run", "test.xml"])
    os.chdir(previous_wd)
    assert result.exit_code == 1
    assert "Please git commit or git stash all changes" in result.output


def test_run_error_when_invalid(runner, invalid_file):
    """
    Expect memote run to error when a provided model fails SBML validation.

    """
    result = runner.invoke(cli, ["run", invalid_file])
    assert result.exit_code == 1


def test_run_skip_unchanged_false(runner, mock_repo):
    """Expect `memote run` to run when invoked on a commit with no changes."""
    previous_wd = os.getcwd()
    os.chdir(mock_repo[0])
    repo = mock_repo[1]
    repo.git.checkout('eb959dd016aaa71fcef96f00b94ce045d6af8f4c')
    result = runner.invoke(cli, ["run", "--location", "results", "test.xml"])
    assert result.exit_code == 0
    repo.git.checkout('gh-pages')
    number_of_result_files = len(os.listdir(join(mock_repo[0], 'results')))
    # Clean up the one commit made to the gh-pages branch.
    repo.git.reset("HEAD~", hard=True)
    os.chdir(previous_wd)
    assert number_of_result_files == 4


def test_run_skip_unchanged_true(runner, mock_repo):
    """Expect `memote run` to skip when invoked on a commit with no changes."""
    previous_wd = os.getcwd()
    os.chdir(mock_repo[0])
    repo = mock_repo[1]
    repo.git.checkout('eb959dd016aaa71fcef96f00b94ce045d6af8f4c')
    result = runner.invoke(cli, ["run", "--location",
                                 "results", "--skip-unchanged",
                                 "test.xml"])
    assert result.exit_code == 0
    repo.git.checkout('gh-pages')
    number_of_result_files = len(os.listdir(join(mock_repo[0], 'results')))
    os.chdir(previous_wd)
    assert number_of_result_files == 3


def test_new(runner, tmpdir):
    """Expect memote new to create a cookiecutter repo."""
    target_dir = str(tmpdir)
    user_responses = "John\nj@d.com\nJD\nmock-repo\nmock-repo\n" \
                     "description\n2019-02-07\n2019\n0.1.0\n" \
                     "default\ndefault\ngh-pages"
    result = runner.invoke(cli, [
        "new", "--directory", target_dir], input=user_responses)
    assert result.exit_code == 0


def test_online(runner, mock_repo, monkeypatch):
    # Build-up
    def mock_setup_gh_repo(*args, **kwargs):
        return "mock_repo_name", "mock_auth_token", "mock_repo_access_token"

    def mock_setup_travis_ci(*args, **kwargs):
        return "mock_secret"

    monkeypatch.setattr(
        memote.suite.cli.runner, "_setup_gh_repo", mock_setup_gh_repo)
    monkeypatch.setattr(
        memote.suite.cli.runner, "_setup_travis_ci", mock_setup_travis_ci)
    previous_wd = os.getcwd()

    # Use the Repository from the mock_repo fixture as the origin to clone from
    path2origin = mock_repo[0]
    originrepo = mock_repo[1]

    # We have to set the local repo to allow pushing into it.
    os.chdir(path2origin)
    check_output(['git', 'config', 'receive.denyCurrentBranch', 'ignore'])

    # Create a directory at a temporary path to clone the mock_repo into.
    # Cloning configures the mock_repo as the origin of the "local" repo which
    # allows us to push from one local directory to another.
    path2local = join(path2origin, pardir, 'cloned_repo')
    os.mkdir(path2local)
    localrepo = originrepo.clone(path2local)
    os.chdir(path2local)

    # Build context_settings
    context_settings = ConfigFileProcessor.read_config()
    github_repository = context_settings["github_repository"]
    github_username = context_settings["github_username"]

    result = runner.invoke(
        cli,
        ["online", "--github_repository", github_repository,
         "--github_username", github_username])
    assert result.exit_code == 0

    # Teardown
    localrepo.git.reset("--hard", 'HEAD~')
    localrepo.git.push('--force', 'origin', 'master')
    os.chdir(previous_wd)


def test_history(runner, mock_repo):
    # Initialize mock repo
    previous_wd = os.getcwd()
    os.chdir(mock_repo[0])

    # Build context_settings
    context_settings = ConfigFileProcessor.read_config()
    model = context_settings["model"]
    location = context_settings["location"]

    result = runner.invoke(cli, ["history", model, "Mock Commit Message",
                                 "--location", location])
    # Teardown
    os.chdir(previous_wd)
    assert result.exit_code == 0
