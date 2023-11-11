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

import os

import git
import pytest

import memote.utils as utils


def one():
    """One line."""
    pass


def two():
    """Two lines.
    Why?
    """
    pass


def three():
    """
    Three lines.
    Why?
    """
    pass


def four():
    """
    Fourth summary.

    A proper description.

    Returns
    -------
    None

    """
    pass


@pytest.mark.parametrize(
    "func, func_name", [(one, "one"), (two, "two"), (three, "three"), (four, "four")]
)
def test_register_with(func, func_name):
    registry = dict()
    utils.register_with(registry)(func)
    assert func_name in registry
    assert registry[func_name] is func


@pytest.mark.parametrize(
    "notes, func, summary",
    [
        (dict(title="One", data=4, format_type="raw"), one, """One line."""),
        (
            dict(title="Two", data="some text", format_type="raw"),
            two,
            """Two lines.
    Why?
    """,
        ),
        (
            dict(title="Three", data=[2, 4, 51, 63], format_type="count"),
            three,
            """
    Three lines.
    Why?
    """,
        ),
        (
            dict(title="Four", data=None, format_type="raw"),
            four,
            """
    Fourth summary.

    A proper description.

    Returns
    -------
    None

    """,
        ),
        pytest.param(
            dict(title="Some Title", format_type="wrong_type"),
            one,
            "",
            marks=pytest.mark.raises(exception=ValueError),
        ),
    ],
)
def test_annotate(notes, func, summary):
    res = utils.annotate(**notes)(func)
    assert res.annotation["title"] == notes["title"]
    assert res.annotation["summary"] == utils.extended_summary(func)
    assert res.annotation["data"] is notes["data"]
    assert res.annotation["message"] is None
    assert res.annotation["format_type"] == notes["format_type"]
    assert res.annotation["metric"] == 1.0


def test_show_versions(capsys):
    utils.show_versions()
    captured = capsys.readouterr()
    lines = captured.out.split("\n")
    assert lines[1].startswith("Package Information")
    assert lines[2].startswith("------------------")
    assert lines[3].startswith("memote")

    assert lines[5].startswith("Dependency Information")
    assert lines[6].startswith("------------------")


@pytest.fixture(scope="function")
def mock_repo(tmpdir_factory):
    """Mock repo with history: add, modify, do nothing, delete file."""
    path = str(tmpdir_factory.mktemp("memote-mock-repo"))
    repo = git.Repo.init(path)
    with repo.config_writer() as writer:
        writer.set_value("user", "name", "memote-bot").release()
        writer.set_value("user", "email", "bot@memote.io").release()
    relname = "test_file.txt"
    absname = os.path.join(path, relname)

    for message in "Add file.", "Modify file.":
        with open(absname, "w") as f:
            f.write(message)
        repo.index.add([relname])
        repo.git.commit("--message", message)

    with open(os.path.join(path, "unrelated_file.txt"), "w") as f:
        f.write("Unrelated file.")
    repo.index.add(["unrelated_file.txt"])
    repo.git.commit("--message", "A commit that does not touch {}".format(relname))

    repo.index.remove([relname], working_tree=True)
    repo.git.commit("--message", "Delete file.")

    return relname, repo


def test_is_modified_deleted(mock_repo):
    """Don't report file deletion as modification."""
    relname, repo = mock_repo
    # File history (newest first): deleted, unchanged, modified, created
    # Don't report file deletion as "modification"
    # for purposes of running memote tests on the file.
    want = False, False, True, True
    # Convert to tuple so we can compare want == got,
    # which pytest will introspect helpfully if the assertion fails.
    got = tuple(utils.is_modified(relname, commit) for commit in repo.iter_commits())
    assert want == got
