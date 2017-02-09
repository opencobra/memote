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

"""
Run the test suite on an instance of `cobra.Model`.
"""

from __future__ import absolute_import

import sys
import shlex
from os.path import dirname

import click
import pytest

from .. import __version__


class MyPlugin:
    def pytest_sessionfinish(self):
        print("*** test run reporting finishing")


@click.command()
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-v")
@click.option("--pytest-args", "-a", default="")
def cli(pytest_args):
    args = shlex.split(pytest_args) + [dirname(__file__)]
    errno = pytest.main(args)
#    errno = pytest.main(shlex.split(pytest_args), plugins=[MyPlugin()])
    sys.exit(errno)
