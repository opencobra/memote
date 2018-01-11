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

"""Stoichiometric consistency tests for an instance of ``cobra.Model``."""

from __future__ import absolute_import

import pytest

import memote.support.consistency as consistency
from memote.utils import annotate, truncate, get_ids, wrapper


@annotate(title="Stoichiometric Consistency", type="length")
def test_stoichiometric_consistency(read_only_model):
    """
    Expect that the stoichiometry is consistent.

    Stoichiometric inconsistency violates universal constraints:
    1. Molecular masses are always positive, and
    2. On each side of a reaction the mass is conserved.
    A single incorrectly defined reaction can lead to stoichiometric
    inconsistency in the model, and consequently to unconserved metabolites.
    Similar to insufficient constraints, this may give rise to cycles which
    either produce mass from nothing or consume mass from the model.

    This test uses an implementation of the algorithm presented by
    Gevorgyan, A., M. G Poolman, and D. A Fell.
    "Detection of Stoichiometric Inconsistencies in Biomolecular Models."
    Bioinformatics 24, no. 19 (2008): 2245.
    doi: 10.1093/bioinformatics/btn425
    """
    ann = test_stoichiometric_consistency.annotation
    is_consistent = consistency.check_stoichiometric_consistency(
        read_only_model)
    ann["data"] = [] if is_consistent else get_ids(
        consistency.find_unconserved_metabolites(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """This model contains {} ({:.2%}) unconserved
        metabolites: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert is_consistent, ann["message"]


@pytest.mark.parametrize("met", [x for x in consistency.ENERGY_COUPLES])
@annotate(title="Erroneous Energy-generating Cycles", type="object",
          data=dict(), message=dict())
def test_detect_energy_generating_cycles(read_only_model, met):
    """
    Expect that no energy metabolite can be produced out of nothing.

    When a model is not sufficiently constrained to account for the
    thermodynamics of reactions, flux cycles may form which provide reduced
    metabolites to the model without requiring nutrient uptake. These cycles
    are referred to as erroneous energy-generating cycles. Their effect on the
    predicted growth rate in FBA may account for an increase of up to 25%,
    which makes studies involving the growth rates predicted from such models
    unreliable.

    This test uses an implementation of the algorithm presented by:
    Fritzemeier, C. J., Hartleb, D., Szappanos, B., Papp, B., & Lercher,
    M. J. (2017). Erroneous energy-generating cycles in published genome scale
    metabolic networks: Identification and removal. PLoS Computational
    Biology, 13(4), 1–14. http://doi.org/10.1371/journal.pcbi.1005494
    """
    ann = test_detect_energy_generating_cycles.annotation
    if met not in read_only_model.metabolites:
        pytest.skip("This test has been skipped since metabolite {} could "
                    "not be found in the model.".format(met))
    ann["data"][met] = consistency.detect_energy_generating_cycles(
        read_only_model, met)
    ann["message"][met] = wrapper.fill(
        """The model can produce '{}' without requiring resources. This is
        caused by improperly constrained reactions leading to erroneous
        energy-generating cycles. The following {} reactions are involved in
        those cycles: {}""".format(
            met, len(ann["data"][met]), truncate(ann["data"][met])))
    assert len(ann["data"][met]) == 0, ann["message"][met]


@annotate(title="Number of Charge-Imbalanced Reactions", type="length")
def test_reaction_charge_balance(read_only_model):
    """
    Expect all reactions to be charge balanced.

    In steady state, for each metabolite the sum of influx equals the sum
    of outflux. Hence the net charges of both sides of any model reaction have
    to be equal.
    """
    ann = test_reaction_charge_balance.annotation
    ann["data"] = get_ids(
        consistency.find_charge_imbalanced_reactions(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) reactions are charge imbalanced with at least
        one of the metabolites not having a charge or the overall charge not
        equal to 0: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Number of Mass-Unbalanced Reactions", type="length")
def test_reaction_mass_balance(read_only_model):
    """
    Expect all reactions to be mass balanced.

    In steady state, for each metabolite the sum of influx equals the sum
    of outflux. Hence the net masses of both sides of any model reaction have
    to be equal.
    """
    ann = test_reaction_mass_balance.annotation
    ann["data"] = get_ids(
        consistency.find_mass_imbalanced_reactions(read_only_model)
    )
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) reactions are mass imbalanced with at least
        one of the metabolites not having a formula or the overall mass not
        equal to 0: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Number of Universally Blocked Reactions", type="length")
def test_blocked_reactions(read_only_model):
    """
    Expect all reactions to be able to carry flux in complete medium.

    Universally blocked reactions are reactions that during Flux Variability
    Analysis cannot carry any flux while all model boundaries are open.
    Generally blocked reactions are caused by network gaps, which can be
    attributed to scope or knowledge gaps.
    """
    ann = test_blocked_reactions.annotation
    ann["data"] = get_ids(consistency.find_blocked_reactions(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """There are {} ({:.2%}) blocked reactions in
        the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Stoichiometrically Balanced Cycles", type="length")
def test_find_stoichiometrically_balanced_cycles(read_only_model):
    """
    Expect no stoichiometrically balanced loops to be present.

    Stoichiometrically Balanced Cycles are artifacts of insufficiently
    constrained networks resulting in reactions that can carry flux when
    all the boundaries have been closed.
    """
    # Skip inside function so it happens during call and not during setup.
    # TODO: Consider using a timeout on the solver in future instead.
    pytest.skip("Loopless FVA currently runs too slowly for large models.")
    ann = test_find_stoichiometrically_balanced_cycles.annotation
    ann["data"] = get_ids(
        consistency.find_stoichiometrically_balanced_cycles(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """There are {} ({:.2%}) reactions
        which participate in SBC in the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Number of Orphan Metabolites", type="length")
def test_find_orphans(read_only_model):
    """
    Expect no orphans to be present.

    Orphans are metabolites that are only consumed in reactions. The may
    indicate the presence of network gaps.
    """
    ann = test_find_orphans.annotation
    ann["data"] = get_ids(consistency.find_orphans(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites are not produced by any reaction
        of the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Number of Dead-end Metabolites", type="length")
def test_find_deadends(read_only_model):
    """
    Expect no deadends to be present.

    Deadends are metabolites that are only produced in reactions. The may
    indicate the presence of network gaps.
    """
    ann = test_find_deadends.annotation
    ann["data"] = get_ids(consistency.find_deadends(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites are not consumed by any reaction
        of the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert ann["data"] == 0, ann["message"]


@annotate(title="Number of Disconnected Metabolites", type="length")
def test_find_disconnected(read_only_model):
    """
    Expect no disconnected metabolites to be present.

    Disconnected metabolites are not part of any model reactions. They are
    most likely left-over from the reconstruction process, but may also point
    to network gaps.
    """
    ann = test_find_disconnected.annotation
    ann["data"] = get_ids(consistency.find_disconnected(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites are not associated with any
        reaction of the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]
