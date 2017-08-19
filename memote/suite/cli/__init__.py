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

"""memote command line interface."""

from __future__ import absolute_import

import locale
from builtins import dict

import click
from colorama import init, Fore

from memote.suite.cli.config import ConfigFileProcessor

locale.setlocale(locale.LC_ALL, "")  # set to system default
init()

try:
    CONTEXT_SETTINGS = dict(
        default_map=ConfigFileProcessor.read_config()
    )
except click.BadParameter as err:
    click.echo(
        Fore.RED +
        "Error in configuration file: {}\nAll configured values will "
        "be ignored!".format(str(err))
        + Fore.RESET, err=True)  # noqa: W503
    CONTEXT_SETTINGS = dict()


