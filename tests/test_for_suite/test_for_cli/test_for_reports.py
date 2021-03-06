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

"""Ensure the expected functioning of ``memote.suite.cli.reports``."""

from __future__ import absolute_import

import os
from os.path import basename

from memote.suite.cli.config import ConfigFileProcessor
from memote.suite.cli.reports import report


def test_report(runner):
    """Expect a simple memote report invocation to be successful."""
    result = runner.invoke(report)
    assert result.exit_code == 0
    assert result.output.startswith("Usage: report [OPTIONS] COMMAND [ARGS]...")


def test_snapshot(tmp_path, runner, model_file):
    """Expect the snapshot report to function."""
    output = tmp_path / (basename(model_file).split(".", 1)[0] + ".html")
    result = runner.invoke(report, ["snapshot", "--filename", str(output), model_file])
    assert result.exit_code == 0
    assert output.exists()


def test_diff(tmp_path, runner, model_file):
    """Expect the diff report to function."""
    output = tmp_path / "diff.html"
    result = runner.invoke(
        report, ["diff", "--filename", str(output), model_file, model_file]
    )
    assert result.exit_code == 0
    assert output.exists()


def test_history(runner, mock_repo):
    """Expect the history report to function."""
    # Initialize mock repo
    previous_wd = os.getcwd()
    os.chdir(mock_repo[0])

    # Build context_settings
    context_settings = ConfigFileProcessor.read_config()
    model = context_settings["model"]
    location = context_settings["location"]
    result = runner.invoke(
        report, ["history", "--model", model, "--location", location]
    )
    # Teardown
    os.chdir(previous_wd)
    assert result.exit_code == 0
