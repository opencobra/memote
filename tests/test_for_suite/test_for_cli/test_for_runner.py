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
from os.path import exists, join

import pytest

from memote.suite.cli.runner import cli


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


def test_run_output(runner, model_file):
    """Expect a simple run to function."""
    output = model_file.split(".", 1)[0] + ".json"
    result = runner.invoke(cli, [
        "run", "--filename", output, "--ignore-git", model_file])
    assert result.exit_code == 0
    assert exists(output)


@pytest.mark.skip(reason="TODO: Need to provide input somehow.")
def test_run_output_TODO(runner, tmpdir):
    """Expect a simple run to function."""
    output = str(tmpdir)
    result = runner.invoke(cli, [
        "new", "--directory", output])
    assert result.exit_code == 0
    assert exists(output)
    # TODO: Check complete template structure.


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
