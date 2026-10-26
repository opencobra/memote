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

from builtins import str
from os.path import exists

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


@pytest.mark.parametrize(
    "model, code",
    [
        ("complete_failure", 1),
    ],
    indirect=["model"],
)
def test_test_model_code(model, code):
    assert api.test_model(model) == code


@pytest.mark.parametrize(
    "model",
    [
        "complete_failure",
    ],
    indirect=["model"],
)
def test_test_model_result(model):
    _, result = api.test_model(model, results=True)
    # TODO: Once introduced perform schema checks here.
    assert len(result) > 0


@pytest.mark.parametrize("model", ["textbook"], indirect=["model"])
def test_test_model_timeout(model):
    api.test_model(
        model,
        solver_timeout=1,
        exclusive="test_find_reactions_unbounded_flux_default_condition",
    )
    assert model.solver.configuration.timeout == 1


@pytest.mark.parametrize(
    "model",
    [
        "complete_failure",
    ],
    indirect=["model"],
)
def test_snapshot_report_file(model, tmpdir):
    filename = str(tmpdir.join("index.html"))
    _, results = api.test_model(model, results=True, pytest_args=["--tb", "no"])
    report = api.snapshot_report(results, html=True)
    assert report.startswith("<!doctype html>")
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


def test_validate_model(model_file):
    """Expect a valid returned model."""
    model, _, _ = api.validate_model(model_file)
    assert model.id == "e_coli_core"
    assert len(model.metabolites) == 72
    assert len(model.reactions) == 95


def _cache_lifecycle_model(solver):
    model = cobra.Model("cache_lifecycle")
    model.solver = solver
    a = cobra.Metabolite("a_c", compartment="c")
    b = cobra.Metabolite("b_c", compartment="c")
    conversion = cobra.Reaction("conversion")
    conversion.add_metabolites({a: -1, b: 1})
    model.add_reactions([conversion])
    branch = cobra.Reaction("branch")
    branch.add_metabolites({a: -1, b: 2})
    return model, branch


def _run_cache_lifecycle(model, selection="test_stoichiometric_consistency", extra=()):
    return api.test_model(
        model,
        results=True,
        pytest_args=[
            "-q",
            "--tb=short",
            "-o",
            "addopts=",
            "-p",
            "no:cacheprovider",
            "-k",
            selection,
        ]
        + list(extra),
    )


@pytest.mark.parametrize("initial_branch", [False, True])
def test_test_model_reaudits_added_and_removed_reaction(solver, initial_branch):
    """A new API run must test the current reaction set in either direction."""
    model, branch = _cache_lifecycle_model(solver)
    if initial_branch:
        model.add_reactions([branch])
    _, before = _run_cache_lifecycle(model)
    assert before.cases["test_stoichiometric_consistency"]["data"] is not initial_branch
    if initial_branch:
        model.remove_reactions([branch])
    else:
        model.add_reactions([branch])
    code, after = _run_cache_lifecycle(model)
    assert after.cases["test_stoichiometric_consistency"]["data"] is initial_branch
    assert code == (0 if initial_branch else 1)


def test_test_model_recollects_changed_biomass_annotation(solver, pytester):
    """Biomass parameters must refresh before pytest collection."""
    custom = pytester.makepyfile(
        """
        import pytest
        @pytest.mark.biomass
        def test_current_biomass(model, reaction_id):
            assert reaction_id == "branch"
        """
    )
    model, branch = _cache_lifecycle_model(solver)
    model.add_reactions([branch])
    selection = "test_stoichiometric_consistency or test_current_biomass"
    _, before = _run_cache_lifecycle(model, selection, [str(custom)])
    assert before.cases["test_stoichiometric_consistency"]["data"] is False
    branch.annotation["sbo"] = "SBO:0000629"
    code, after = _run_cache_lifecycle(model, selection, [str(custom)])
    assert code == 0
    assert after.cases["test_stoichiometric_consistency"]["data"] is True
    assert after.cases["test_current_biomass"]["result"] == {"branch": "passed"}


def test_test_model_reuses_classification_within_run(solver, pytester, monkeypatch):
    """Two tests still share one internal-reaction classification."""
    from memote.support import consistency_helpers

    custom = pytester.makepyfile(
        """
        from memote.support.consistency_helpers import get_internals
        def test_reuse_first(model):
            assert get_internals(model) is get_internals(model)
        def test_reuse_second(model):
            assert get_internals(model) is get_internals(model)
        """
    )
    original = consistency_helpers.find_biomass_reaction
    computations = []

    def counted(model):
        computations.append(model)
        return original(model)

    monkeypatch.setattr(consistency_helpers, "find_biomass_reaction", counted)
    model, _ = _cache_lifecycle_model(solver)
    code, _ = _run_cache_lifecycle(model, "test_reuse_", [str(custom)])
    assert code == 0
    assert computations == [model]


def test_test_model_retry_after_configuration_error(solver):
    """A failed entry must not poison the next sequential run."""
    from memote.support.consistency_helpers import get_internals

    class PlannedFailure(Exception):
        pass

    class FailingConfiguration:
        def load(self, model):
            get_internals(model)
            raise PlannedFailure("controlled configuration failure")

    model, branch = _cache_lifecycle_model(solver)
    with pytest.raises(PlannedFailure):
        api.test_model(model, experimental=FailingConfiguration())
    model.add_reactions([branch])
    code, result = _run_cache_lifecycle(model)
    assert code == 1
    assert result.cases["test_stoichiometric_consistency"]["data"] is False


def test_clear_support_caches_covers_existing_wrappers():
    """Keep the explicit reset complete when support caches are added."""
    from memote.support import basic, consistency_helpers, helpers
    from memote.support.cache import clear_support_caches

    wrappers = {
        function
        for module in (basic, consistency_helpers, helpers)
        for function in vars(module).values()
        if callable(function) and hasattr(function, "cache")
    }
    try:
        for function in wrappers:
            function.cache[("cache lifecycle regression",)] = object()
        clear_support_caches()
        assert all(len(function.cache) == 0 for function in wrappers)
    finally:
        clear_support_caches()
