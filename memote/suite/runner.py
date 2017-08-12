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
import io
import shlex
import sys
import logging
from os.path import join, dirname
from multiprocessing import Process

import click
import pytest
import git
from click_configfile import (
    ConfigFileReader, Param, SectionSchema, matches_section)
from colorama import init, Fore
from cookiecutter.main import cookiecutter

from memote import __version__
from memote.suite.collect import ResultCollectionPlugin
from memote.suite.reporting.reports import HistoryReport

locale.setlocale(locale.LC_ALL, "")  # set to system default
init()
LOGGER = logging.getLogger()


class ConfigSectionSchema(object):
    """Describes all sections of the memote configuration file."""

    @matches_section("memote")
    class Memote(SectionSchema):
        """Describes the memote configuration keys and values."""

        collect = Param(type=bool, default=True)
        addargs = Param(type=str, default="")
        model = Param(type=click.Path(exists=True, dir_okay=False))
        directory = Param(type=click.Path(exists=True, file_okay=False,
                                          writable=True))


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
    tests_dir = join(dirname(__file__), "tests")
    if args is not None:
        return shlex.split(args) + [tests_dir]
    elif "addargs" in context.default_map:
        return shlex.split(context.default_map["addargs"]) +\
            [tests_dir]
    else:
        return [tests_dir]


def process_model(model, context):
    """Load model path from different locations."""
    if model is not None:
        return model
    elif "MEMOTE_MODEL" in os.environ:
        assert os.path.isfile(os.environ["MEMOTE_MODEL"])
        return os.environ["MEMOTE_MODEL"]
    elif "model" in context.default_map:
        return context.default_map["model"]


def process_directory(directory, context):
    """Load directory from different locations."""
    if directory is not None:
        return directory
    elif "MEMOTE_DIRECTORY" in os.environ:
        assert os.path.isdir(os.environ["MEMOTE_DIRECTORY"])
        return os.environ["MEMOTE_DIRECTORY"]
    elif "directory" in context.default_map:
        return context.default_map["directory"]


def probe_git():
    """Return meta data if in git repository."""
    try:
        repo = git.Repo()
    except git.InvalidGitRepositoryError:
        click.echo(
            Fore.YELLOW +
            "We highly recommend keeping your model in a git repository."
            " It allows you to track changes and easily collaborate with"
            " others via online platforms such as https://github.com.\n"
            + Fore.RESET)  # noqa: W503
        return
    if repo.is_dirty():
        click.echo(
            Fore.RED +
            "Please git commit or git stash all changes before running"
            " the memote suite.", err=True)
        sys.exit(1)
    return repo


def check_model(ctx):
    """Ensure that the model option is defined."""
    if ctx.obj["model"] is None:
        click.echo(
            Fore.RED +
            "No metabolic model found. Specify one using the --model"
            " option, using the environment variable MEMOTE_MODEL, or in"
            " either the 'memote.ini' or 'setup.cfg' configuration file.",
            err=True
        )
        sys.exit(2)


def check_directory(ctx):
    """Ensure that the directory option is defined."""
    if ctx.obj["directory"] is None:
        click.echo(
            Fore.RED +
            "No suitable directory found. Specify one using the --directory"
            " option, using the environment variable MEMOTE_DIRECTORY, or"
            " in either the 'memote.ini' or 'setup.cfg' configuration file.",
            err=True
        )
        sys.exit(2)


def check_repo(ctx):
    """Ensure that the repository option is defined."""
    if ctx.obj["repo"] is None:
        click.echo(
            Fore.RED +
            "The feature rich report only works in a git repository."
            " Please use the --one-time option instead or setup a repository.",
            err=True
        )
        sys.exit(2)


def abort_if_false(ctx, param, value):
    """Require confirmation."""
    if not value:
        ctx.abort()


def collect(ctx):
    """Act like a collect subcommand."""
    check_model(ctx)
    if ctx.obj["collect"]:
        mode = "collect"
        if "--tb" not in ctx.obj["pytest_args"]:
            ctx.obj["pytest_args"].extend(["--tb", "no"])
    else:
        mode = "basic"
    if ctx.obj["repo"] is not None and ctx.obj["collect"]:
        mode = "git-{}".format(mode)
    if mode == "collect" and ctx.obj["filename"] is None:
        ctx.obj["filename"] = "result.json"
    elif mode == "git-collect" and ctx.obj["filename"] is None:
        check_directory(ctx)
        if "commit" in ctx.obj:
            sha = ctx.obj["commit"].hexsha
        elif "branch" in ctx.obj:
            sha = ctx.obj["branch"].commit.hexsha
        else:
            sha = ctx.obj["repo"].active_branch.commit.hexsha
        ctx.obj["filename"] = join(ctx.obj["directory"], "{}.json".format(sha))
    plugin = ResultCollectionPlugin(
        ctx.obj["model"], mode=mode, filename=ctx.obj["filename"],
        directory=ctx.obj["directory"], repo=ctx.obj["repo"],
        branch=ctx.obj.get("branch"), commit=ctx.obj.get("commit"))
    errno = pytest.main(ctx.obj["pytest_args"], plugins=[plugin])
    return errno


@click.group(invoke_without_command=True,
             context_settings=dict(
                 default_map=ConfigFileProcessor.read_config()
             ))
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-V")
@click.option("--level", "-l", default="WARN",
              type=click.Choice(["ERROR", "WARN", "INFO", "DEBUG"]),
              help="Set the log level (default WARN).")
@click.option("--no-collect", type=bool, is_flag=True,
              help="Do *not* collect test data needed for generating a report.")
@click.option("--model", type=click.Path(exists=True, dir_okay=False),
              help="Path to model file. Can also be given via the environment"
              " variable MEMOTE_MODEL or configured in 'setup.cfg' or"
              " 'memote.ini'.")
@click.option("--filename", type=click.Path(exists=False, writable=True),
              help="Path for either the collected results as JSON or the"
              " HTML report. In the former case the default is 'result.json'."
              " In the latter case the default is 'index.html'.")
@click.option("--directory", type=click.Path(exists=True, file_okay=False,
                                             writable=True),
              help="Depending on the invoked subcommand:"
              " Either create a report from JSON files in the given"
              " directory, write test results to the directory using the"
              " git commit hash, or create a new model repository inside it.")
@click.option("--pytest-args", "-a",
              help="Any additional arguments you want to pass to pytest."
              "Should be given as one continuous string.")
@click.pass_context
def cli(ctx, level, no_collect, model, filename, directory, pytest_args):
    """
    Metabolic model testing command line tool.

    In its basic invocation memote performs a test suite on a metabolic model.
    Through various subcommands it can further generate a pretty HTML report,
    generate a model repository structure for starting a new project, and
    recreate the test result history.
    """
    logging.basicConfig(level=level, format="%(levelname)s - %(message)s")
    ctx.obj = dict()
    ctx.obj["collect"] = process_collect_flag(no_collect, ctx)
    ctx.obj["model"] = process_model(model, ctx)
    ctx.obj["filename"] = filename
    ctx.obj["directory"] = process_model(directory, ctx)
    ctx.obj["pytest_args"] = process_addargs(pytest_args, ctx)
    ctx.obj["repo"] = probe_git()
    if ctx.invoked_subcommand is None:
        sys.exit(collect(ctx))


@cli.command()
@click.help_option("--help", "-h")
@click.option("--one-time", is_flag=True,
              help="Generate a one-time report.")
@click.option("--index", type=click.Choice(["time", "hash"]), default="time",
              help="Use either time (default) or commit hashes as the index.")
@click.pass_context
def report(ctx, one_time, index):
    """
    Generate a one-time or feature rich report.

    The one-time report generates a quick overview of the current model state.
    If the model lives in a git repository and there is a history of test
    results, memote can generate a more rich report.
    """
    check_model(ctx)
    if ctx.obj["filename"] is None:
        ctx.obj["filename"] = "index.html"
    if one_time:
        if "--tb" not in ctx.obj["pytest_args"]:
            ctx.obj["pytest_args"].extend(["--tb", "no"])
        errno = pytest.main(
            ctx.obj["pytest_args"],
            plugins=[ResultCollectionPlugin(
                ctx.obj["model"], mode="html", filename=ctx.obj["filename"])
            ]
        )
        sys.exit(errno)
    check_directory(ctx)
    check_repo(ctx)
    report = HistoryReport(ctx.obj["repo"], ctx.obj["directory"],
                           index=index)
    click.echo(u"Writing report '{}'".format(ctx.obj["filename"]))
    with io.open(ctx.obj["filename"], "w") as file_h:
        file_h.write(report.render_html())


@cli.command()
@click.help_option("--help", "-h")
@click.pass_context
def new(ctx):
    """
    Create a suitable model repository structure from a template.

    By using a cookiecutter template, memote will ask you a couple of questions
    and set up a new directory structure that will make your life easier. The
    new directory will be placed in the current directory or respect the given
    --directory option.
    """
    directory = ctx.obj["directory"]
    if directory is None:
        directory = os.getcwd()
    cookiecutter("gh:opencobra/cookiecutter-memote", output_dir=directory)


@cli.command()
@click.help_option("--help", "-h")
@click.option("--yes", "-y", is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt="Are you sure that you want to change history?")
@click.argument("commits", metavar="[COMMIT] ...", nargs=-1)
@click.pass_context
def history(ctx, commits):
    """
    Re-compute test results for the complete git branch history.

    There are three distinct modes:

    \b
    1. Completely re-compute test results for each commit in the git history.
       This should only be necessary when memote is first used with existing
       model repositories.
    2. Update mode complements existing test results with metrics that were
       newly introduced and not available before. It also fills gaps in the
       history.
    3. By giving memote specific commit hashes, it will re-compute test results
       for those only.
    """
    if len(commits) > 0:
        raise NotImplementedError(u"Coming soon™.")
    repo = ctx.obj["repo"]
    branch = repo.active_branch
    ctx.obj["branch"] = branch
    ctx.obj["commit"] = branch.commit
    LOGGER.info(
        "%sRunning the test suite for commit '%s'.%s",
        Fore.GREEN, branch.commit.hexsha, Fore.RESET)
    # Need to use a subprocess here such that the pytest plugin can be
    # successfully initialized with new arguments each time. Otherwise the
    # plugin remains immutable.
    proc = Process(target=collect, args=(ctx,))
    proc.start()
    proc.join()
    for commit in branch.commit.iter_parents():
        repo.git.checkout(commit)
        ctx.obj["commit"] = commit
        LOGGER.info(
            "%sRunning the test suite for commit '%s'.%s",
            Fore.GREEN, commit.hexsha, Fore.RESET)
        proc = Process(target=collect, args=(ctx,))
        proc.start()
        proc.join()
    repo.git.checkout(branch)
    # repo.head.reset(index=True, working_tree=True)  # superfluous?
