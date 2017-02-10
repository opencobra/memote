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
import os
from os.path import dirname

import click
import pytest
from click_configfile import (ConfigFileReader, Param, SectionSchema,
                              matches_section)

from .. import __version__


class ConfigSectionSchema(object):
    """Describes all sections of the memote configuration file."""

    @matches_section("memote")
    class Memote(SectionSchema):
        """Describes the memote configuration keys and values."""
        collect = Param(type=bool, default=True)
        addargs = Param(type=str, default="")
        model = Param(type=click.Path(exists=True, dir_okay=False),
                      multiple=True)


class ConfigFileProcessor(ConfigFileReader):
    config_files = ["memote.ini", "setup.cfg"]
    config_section_schemas = [ConfigSectionSchema.Memote]


class MyPlugin:
    def pytest_sessionfinish(self):
        click.echo("Storing report data.")


def process_collect_flag(no_flag, context):
    if no_flag is not None:
        return not no_flag
    elif "collect" in context.default_map:
        return context.default_map["collect"]
    else:
        return True


def process_addargs(args, context):
    if args is not None:
        return shlex.split(args) + [dirname(__file__)]
    elif "addargs" in context.default_map:
        return shlex.split(context.default_map["addargs"]) +\
            [dirname(__file__)]
    else:
        return [dirname(__file__)]


def process_model(model, context):
    if len(model) > 0:
        os.environ["MEMOTE_MODEL"] = os.pathsep.join(model)
    elif "MEMOTE_MODEL" in os.environ:
        return
    elif "model" in context.default_map:
        os.environ["MEMOTE_MODEL"] = os.pathsep.join(
            context.default_map["model"]
        )
    else:
        raise ValueError(
            "No metabolic model found. Specify one as an argument, as an"
            " environment variable MEMOTE_MODEL, or in a configuration file."
        )


@click.command(context_settings={"default_map": ConfigFileProcessor.read_config()})
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-V")
@click.option("--no-collect", type=bool, is_flag=True,
              help="Do *not* collect test data needed for generating a report.")
@click.option("--pytest-args", "-a",
              help="Any additional arguments you want to pass to pytest as a"
                   " string.")
@click.argument("model", type=click.Path(exists=True, dir_okay=False), nargs=-1)
@click.pass_context
def cli(ctx, model, pytest_args, no_collect):
    collect = process_collect_flag(no_collect, ctx)
    args = process_addargs(pytest_args, ctx)
    try:
        process_model(model, ctx)
    except ValueError as err:
        click.echo(str(err))
        sys.exit(1)
    click.echo(os.environ["MEMOTE_MODEL"])
    if collect:
        errno = pytest.main(args, plugins=[MyPlugin()])
    else:
        errno = pytest.main(args)
    sys.exit(errno)
