# -*- coding: utf-8 -*-

# Copyright 2016 Novo Nordisk Foundation Center for Biosustainability,
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

from __future__ import absolute_import

import cobra
import pytest

import memote.support.basic as basic


"""
Tests ensuring that the functions in `memote.support.basic` work as expected.
"""


def three_missing(base):
    base.add_metabolites([cobra.Metabolite(id="M{0:d}".format(i))
                          for i in range(1, 4)])
    return base


def three_present(base):
    base.add_metabolites(
        [cobra.Metabolite(id="M{0:d}".format(i), formula="CH4")
         for i in range(1, 4)]
    )
    return base


def model_builder(name):
    choices = {
        "three-missing": three_missing,
        "three-present": three_present,
    }
    model = cobra.Model(id_or_model=name, name=name)
    return choices[name](model)


@pytest.fixture(scope="function")
def gpr_present():
    """Provide a model with reactions that all have GPR"""
    model = cobra.Model(id_or_model="gpr_present", name="gpr_present")
    rxn_1 = cobra.Reaction("RXN1")
    rxn_1.gene_reaction_rule = 'gene1 or gene2'
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    model.add_reactions([rxn_1])
    return model


@pytest.fixture(scope="function")
def gpr_missing():
    """Provide a model reactions that lack GPR"""
    model = cobra.Model(id_or_model="gpr_missing", name="gpr_missing")
    rxn_1 = cobra.Reaction("RXN1")
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    model.add_reactions([rxn_1])
    return model


@pytest.fixture(scope="function")
def gpr_missing_with_exchange():
    """Provide a model reactions that lack GPR"""
    model = cobra.Model(
        id_or_model="gpr_missing_with_exchange",
        name="gpr_missing_with_exchange"
    )
    rxn_1 = cobra.Reaction("RXN1")
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    rxn_2 = cobra.Reaction("EX_met1_c")
    met_1 = cobra.Metabolite("met1")
    rxn_2.add_metabolites({met_1: 1})
    model.add_reactions([rxn_1, rxn_2])
    return model


@pytest.fixture(scope="function")
def gpr_present_not_lumped():
    """Provide a model with reactions that all have GPR"""
    model = cobra.Model(id_or_model="gpr_present", name="gpr_present")
    rxn_1 = cobra.Reaction("RXN1")
    rxn_1.gene_reaction_rule = 'gene1'
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    model.add_reactions([rxn_1])
    return model


@pytest.fixture(scope="function")
def unconstrained_rxn():
    """Provide a model with one unconstrained reaction"""
    model = cobra.Model(id_or_model="unconstrained", name="unconstrained")
    rxn_1 = cobra.Reaction("RXN1")
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    rxn_1.bounds = -1000, 1000
    model.add_reactions([rxn_1])
    return model


@pytest.fixture(scope="function")
def irreversible_rxn():
    """Provide a model with one irreversible reaction"""
    model = cobra.Model(id_or_model="irreversible", name="irreversible")
    rxn_1 = cobra.Reaction("RXN1")
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    rxn_1.bounds = 0, 1000
    model.add_reactions([rxn_1])
    return model


@pytest.fixture(scope="function")
def zero_constrained_rxn():
    """Provide a model with one zero-constrained reaction"""
    model = cobra.Model(
        id_or_model="zero_constrained", name="zero_constrained"
    )
    rxn_1 = cobra.Reaction("RXN1")
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    rxn_1.bounds = 0, 0
    model.add_reactions([rxn_1])
    return model


@pytest.fixture(scope="function")
def nonzero_constrained_rxn():
    """Provide a model with one nonzero-constrained reaction"""
    model = cobra.Model(
        id_or_model="nonzero_constrained", name="nonzero_constrained"
    )
    rxn_1 = cobra.Reaction("RXN1")
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    rxn_2 = cobra.Reaction("RXN2")
    rxn_2.add_metabolites({met_1: -1, met_2: 1})
    rxn_1.bounds = 0, 5
    rxn_2.bounds = -5, 0
    model.add_reactions([rxn_1, rxn_2])
    return model


@pytest.mark.parametrize("model, num", [
    ("empty", 0),
    ("three-missing", 3),
    ("three-present", 0)
], indirect=["model"])
def test_metabolites_formula_presence(model, num):
    """Expect all metabolites to have a formula."""
    assert len(basic.check_metabolites_formula_presence(model)) == num


@pytest.mark.parametrize("model, num", [
    ("empty", 0),
    ("three-missing", 3),
    ("three-present", 0)
], indirect=["model"])
def test_metabolites_charge_presence(model, num):
    """Expect all metabolites to have a charge."""
    assert len(basic.check_metabolites_charge_presence(model)) == num


@pytest.mark.parametrize("model, num", [
    (gpr_present(), 0),
    (gpr_missing(), 1),
    (gpr_missing_with_exchange(), 1),
])
def test_gene_protein_reaction_rule_presence(model, num):
    """Expect all non-exchange reactions to have a GPR."""
    missing_gpr_metabolic_rxns = \
        set(
            basic.check_gene_protein_reaction_rule_presence(
                model
            )
        ).difference(set(model.exchanges))
    assert len(missing_gpr_metabolic_rxns) == num


@pytest.mark.parametrize("model, coverage", [
    (gpr_present(), 0.5),
    (gpr_present_not_lumped(), 1),
])
def test_metabolic_coverage(model, coverage):
    """Expect a model to have high metabolic coverage."""
    metabolic_coverage = basic.calculate_metabolic_coverage(model)
    assert metabolic_coverage >= coverage


@pytest.mark.parametrize("model, num", [
    (unconstrained_rxn(), 0),
    (nonzero_constrained_rxn(), 2),
])
def test_find_nonzero_constrained_reactions(model, num):
    """Expect amount of non-zero rxns to be identified correctly."""
    nonzero_constrained_rxns = basic.find_nonzero_constrained_reactions(model)
    assert len(nonzero_constrained_rxns) == num


@pytest.mark.parametrize("model, num", [
    (unconstrained_rxn(), 0),
    (zero_constrained_rxn(), 1),
])
def test_find_zero_constrained_reactions(model, num):
    """Expect amount of zero-constrained rxns to be identified correctly."""
    zero_constrained_rxns = basic.find_zero_constrained_reactions(model)
    assert len(zero_constrained_rxns) == num


@pytest.mark.parametrize("model, num", [
    (unconstrained_rxn(), 0),
    (irreversible_rxn(), 1),
])
def test_find_irreversible_reactions(model, num):
    """Expect amount of irreversible rxns to be identified correctly."""
    irreversible_rxns = basic.find_irreversible_reactions(model)
    assert len(irreversible_rxns) == num


@pytest.mark.parametrize("model, num", [
    (unconstrained_rxn(), 1),
    (zero_constrained_rxn(), 0),
])
def test_find_unconstrained_reactions(model, num):
    """Expect amount of unconstrained rxns to be identified correctly."""
    unconstrained_rxns = basic.find_unconstrained_reactions(model)
    assert len(unconstrained_rxns) == num
