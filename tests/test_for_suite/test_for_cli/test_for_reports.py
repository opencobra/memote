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

"""Test the memote report command line interface."""

from __future__ import absolute_import

from builtins import str
from os.path import exists

import pytest

from memote.suite.cli.reports import report


def test_report(runner):
    """Expect a simple memote report invocation to be successful."""
    result = runner.invoke(report)
    assert result.exit_code == 0
    assert result.output.startswith(
        "Usage: report [OPTIONS] COMMAND [ARGS]...")


def test_snapshot(runner, model_file):
    """Expect the snapshot report to function."""
    output = model_file.split(".", 1)[0] + ".html"
    result = runner.invoke(report, [
        "snapshot", "--filename", output, model_file])
    assert result.exit_code == 0
    assert exists(output)
