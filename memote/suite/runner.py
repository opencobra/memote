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

"""Run the test suite on an instance of `cobra.Model`."""

from __future__ import absolute_import
from builtins import dict

import locale
import os
import shlex
import sys
from os.path import dirname

import click
import pytest
from click_configfile import (
    ConfigFileReader, Param, SectionSchema, matches_section)

from memote import __version__
from memote.suite.collect import ResultCollectionPlugin

locale.setlocale(locale.LC_ALL, "")  # set to system default


class ConfigSectionSchema(object):
    """Describes all sections of the memote configuration file."""

    @matches_section("memote")
    class Memote(SectionSchema):
        """Describes the memote configuration keys and values."""

        collect = Param(type=bool, default=True)
        addargs = Param(type=str, default="")
        model = Param(type=click.Path(exists=True, dir_okay=False))


class ConfigFileProcessor(ConfigFileReader):
    """Determine which files to look for and what sections."""

    config_files = ["memote.ini", "setup.cfg"]
    config_section_schemas = [ConfigSectionSchema.Memote]


def process_collect_flag(no_flag, context):
    """Handle the report collection flag."""
    if no_flag is not None:
        return not no_flag
    elif "collect" in context.default_map:
        return context.default_map["collect"]
    else:
        return True


def process_addargs(args, context):
    """Handle additional args to pytest."""
    if args is not None:
        return shlex.split(args) + [dirname(__file__)]
    elif "addargs" in context.default_map:
        return shlex.split(context.default_map["addargs"]) +\
            [dirname(__file__)]
    else:
        return [dirname(__file__)]


def process_model(model, context):
    """Load model path from different locations."""
    if model is not None:
        os.environ["MEMOTE_MODEL"] = model
    elif "MEMOTE_MODEL" in os.environ:
        assert os.path.isfile(os.environ["MEMOTE_MODEL"])
    elif "model" in context.default_map:
        os.environ["MEMOTE_MODEL"] = context.default_map["model"]
    else:
        raise ValueError(
            "No metabolic model found. Specify one as an option, in the"
            " environment variable MEMOTE_MODEL, or in a configuration file."
        )


@click.group(invoke_without_command=True,
             context_settings=dict(
                default_map=ConfigFileProcessor.read_config()
            ))
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-V")
@click.option("--no-collect", type=bool, is_flag=True,
              help="Do *not* collect test data needed for generating a report.")
@click.option("--pytest-args", "-a",
              help="Any additional arguments you want to pass to pytest as a"
                   " string.")
@click.option("--model", type=click.Path(exists=True, dir_okay=False),
              help="Path to model file. Can also be given via the environment"
              " variable MEMOTE_MODEL or configured in 'setup.cfg' or"
              " 'memote.ini'.")
@click.option("--filename", type=click.Path(exists=False, writable=True),
              help="Path for either the collected results as JSON or the"
              " HTML report. In the former case the default is either"
              " 'out.json'. In the latter case the default is 'out.html'.")
@click.pass_context
def cli(ctx, model, pytest_args, no_collect, filename):
    """
    Memote command line tool.

    Run `memote -h` for a better explanation.
    """
    collect = process_collect_flag(no_collect, ctx)
    args = process_addargs(pytest_args, ctx)
    if collect and ("--tb" not in args):
        args.extend(["--tb", "no"])
    if ctx.invoked_subcommand is None:
        try:
            process_model(model, ctx)
        except ValueError as err:
            click.echo(str(err))
            sys.exit(2)
        if collect:
            collect = "collect"
        else:
            collect = "basic"
        if filename is None:
            filename = "out.json"
        errno = pytest.main(args, plugins=[ResultCollectionPlugin(
            collect, filename)])
        sys.exit(errno)
    else:
        if "--tb" not in args:
            args.extend(["--tb", "no"])
        ctx.obj = dict()
        ctx.obj["pytest_args"] = args
        ctx.obj["model"] = model
        ctx.obj["filename"] = filename


@cli.command()
@click.help_option("--help", "-h")
@click.option("--directory", type=click.Path(exists=True, file_okay=False,
                                             writable=True),
              help="Create report from JSON files in the given directory.")
@click.pass_context
def report(ctx, directory):
    try:
        process_model(ctx.obj["model"], ctx)
    except ValueError as err:
        click.echo(str(err))
        sys.exit(2)
    if ctx.obj["filename"] is None:
        ctx.obj["filename"] = "out.html"
    errno = pytest.main(ctx.obj["pytest_args"], plugins=[ResultCollectionPlugin(
        "html", ctx.obj["filename"])])
    sys.exit(errno)
