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


@pytest.mark.parametrize("func, func_name", [
    (one, "one"),
    (two, "two"),
    (three, "three"),
    (four, "four")
])
def test_register_with(func, func_name):
    registry = dict()
    utils.register_with(registry)(func)
    assert func_name in registry
    assert registry[func_name] is func


@pytest.mark.parametrize("notes, func, summary", [
    (dict(title="One", data=4, format_type="raw"), one,
     """One line."""),
    (dict(title="Two", data="some text", format_type="raw"), two,
     """Two lines.
    Why?
    """),
    (dict(title="Three", data=[2, 4, 51, 63], format_type="count"), three,
     """
    Three lines.
    Why?
    """),
    (dict(title="Four", data=None, format_type="raw"), four,
     """
    Fourth summary.

    A proper description.

    Returns
    -------
    None

    """),
    pytest.param(dict(title="Some Title",format_type="wrong_type"), one, "",
                 marks=pytest.mark.raises(exception=ValueError))
])
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
    assert lines[1].startswith("System Information")
    assert lines[2].startswith("==================")
    assert lines[3].startswith("OS")
    assert lines[4].startswith("OS-release")
    assert lines[5].startswith("Python")

    assert lines[7].startswith("Package Versions")
    assert lines[8].startswith("================")
    assert any(l.startswith("memote") for l in lines[9:])
