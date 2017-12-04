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

"""Ensure the expected functioning of ``memote.suite.api``."""

from __future__ import absolute_import

from os.path import exists
from builtins import str

import cobra
import pytest

import memote.suite.api as api
from memote.utils import register_with

MODEL_REGISTRY = dict()


@register_with(MODEL_REGISTRY)
def complete_failure(base):
    met_a = cobra.Metabolite("atp_c")
    met_b = cobra.Metabolite("A")
    met_c = cobra.Metabolite("B")
    rxn1 = cobra.Reaction("Gen")
    rxn1.add_metabolites({met_b: -1, met_a: 1, met_c: 1})
    rxn2 = cobra.Reaction("Recap", lower_bound=-1000, upper_bound=1000)
    rxn2.add_metabolites({met_c: -1, met_b: 1})
    rxn3 = cobra.Reaction("EX_atp_c", lower_bound=-1000, upper_bound=1000)
    rxn3.add_metabolites({met_a: -1})
    rxn4 = cobra.Reaction("EX_A_c", lower_bound=-1000, upper_bound=1000)
    rxn4.add_metabolites({met_b: -1})
    rxn5 = cobra.Reaction("EX_B_c", lower_bound=-1000, upper_bound=1000)
    rxn5.add_metabolites({met_c: -1})
    base.add_reactions([rxn1, rxn2, rxn3, rxn4, rxn5])
    return base


@pytest.mark.parametrize("model, code", [
    ("complete_failure", 1),
], indirect=["model"])
def test_test_model_code(model, code):
    assert api.test_model(model) == code


@pytest.mark.parametrize("model", [
    "complete_failure",
], indirect=["model"])
def test_test_model_result(model):
    _, result = api.test_model(model, results=True)
    # TODO: Once introduced perform schema checks here.
    assert len(result) > 0


@pytest.mark.parametrize("model", [
    "complete_failure",
], indirect=["model"])
def test_test_model_file(model, tmpdir):
    filename = str(tmpdir.join("result.json"))
    api.test_model(model, filename)
    assert exists(filename)


@pytest.mark.parametrize("model", [
    "complete_failure",
], indirect=["model"])
def test_basic_report_file(model, tmpdir):
    filename = str(tmpdir.join("index.html"))
    _, results = api.test_model(model, results=True)
    api.snapshot_report(results, filename)
    assert exists(filename)
    # TODO: Perform some content checks here.


@pytest.fixture(scope="module", params=["complete-failure"])
def history_directory(request, tmpdir_factory):
    model = model_builder(request.param)
    directory = tmpdir_factory.mkdir("Results")
    for i in range(3):
        filename = str(directory.join("{}.json".format(i)))
        api.test_model(model, filename)
    return str(directory)


@pytest.mark.xfail(reason="TODO: Need to mock a GitHub repo with history.")
def test_history_report_file(history_directory, tmpdir):
    filename = tmpdir.join("index.html")
    api.history_report(None, history_directory, filename)
    assert exists(filename)
    # TODO: Perform some content checks here.


@pytest.mark.xfail(reason="TODO: Function not implemented yet.")
def test_diff_report_file():
    api.diff_report()
