# -*- coding: utf-8 -*-

# Copyright 2018 Novo Nordisk Foundation Center for Biosustainability,
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

"""Ensure the expected functioning of ``memote.experimental.medium``."""

from __future__ import absolute_import

import pytest
from numpy import isclose
from numpy.random import random_sample
from pandas import DataFrame

from memote.experimental.tabular import read_tabular


@pytest.fixture(scope="module", params=["empty", "half"])
def table(request):
    if request.param == "empty":
        return DataFrame({
            "numeric": random_sample(10),
            "integer": range(10),
            "comments": None
        })
    elif request.param == "half":
        df = DataFrame({
            "numeric": random_sample(10),
            "integer": range(10),
            "comments": None
        })
        df.loc[range(0, 10, 2), "comments"] = "Wise comment."
        return df


def test_read_csv(table, tmpdir):
    filename = str(tmpdir.mkdir("data").join("table.csv"))
    table.to_csv(filename, index=False, encoding="utf-8")
    df = read_tabular(filename)
    assert (df["integer"] == table["integer"]).all()
    assert isclose(df["numeric"], table["numeric"]).all()
    assert (df["comments"].isnull() == table["comments"].isnull()).all()
    assert (df.loc[df["comments"].notnull(), "comments"] ==
            table.loc[table["comments"].notnull(), "comments"]).all()


def test_read_tsv(table, tmpdir):
    filename = str(tmpdir.mkdir("data").join("table.tsv"))
    table.to_csv(filename, sep="\t", index=False, encoding="utf-8")
    df = read_tabular(filename)
    assert (df["integer"] == table["integer"]).all()
    assert isclose(df["numeric"], table["numeric"]).all()
    assert (df["comments"].isnull() == table["comments"].isnull()).all()
    assert (df.loc[df["comments"].notnull(), "comments"] ==
            table.loc[table["comments"].notnull(), "comments"]).all()


def test_read_xls(table, tmpdir):
    filename = str(tmpdir.mkdir("data").join("table.xls"))
    table.to_excel(filename, index=False)
    df = read_tabular(filename)
    assert (df["integer"] == table["integer"]).all()
    assert isclose(df["numeric"], table["numeric"]).all()
    assert (df["comments"].isnull() == table["comments"].isnull()).all()
    assert (df.loc[df["comments"].notnull(), "comments"] ==
            table.loc[table["comments"].notnull(), "comments"]).all()


def test_read_xlsx(table, tmpdir):
    filename = str(tmpdir.mkdir("data").join("table.xlsx"))
    table.to_excel(filename, index=False)
    df = read_tabular(filename)
    assert (df["integer"] == table["integer"]).all()
    assert isclose(df["numeric"], table["numeric"]).all()
    assert (df["comments"].isnull() == table["comments"].isnull()).all()
    assert (df.loc[df["comments"].notnull(), "comments"] ==
            table.loc[table["comments"].notnull(), "comments"]).all()
