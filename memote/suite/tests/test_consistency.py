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

from __future__ import absolute_import, division

import pytest

import memote.support.consistency as consistency
from memote.utils import annotate, truncate, get_ids, wrapper
import memote.support.consistency_helpers as con_helpers


@annotate(title="Stoichiometric Consistency", format_type="count")
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
@annotate(title="Erroneous Energy-generating Cycles", format_type="count",
          data=dict(), message=dict())
def test_detect_energy_generating_cycles(read_only_model, met):
    u"""
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


@annotate(title="Number of Charge-Imbalanced Reactions", format_type="count")
def test_reaction_charge_balance(read_only_model):
    """
    Expect all reactions to be charge balanced.

    This will exclude biomass, exchange and demand reactions as they are
    unbalanced by definition. It will also fail all reactions where at
    least one metabolite does not have a charge defined.

    In steady state, for each metabolite the sum of influx equals the sum
    of outflux. Hence the net charges of both sides of any model reaction have
    to be equal. Reactions where at least one metabolite does not have a
    formula are not considered to be balanced, even though the remaining
    metabolites participating in the reaction might be.
    """
    ann = test_reaction_charge_balance.annotation
    internal_rxns = con_helpers.get_internals(read_only_model)
    ann["data"] = get_ids(
        consistency.find_charge_unbalanced_reactions(internal_rxns))
    ann["metric"] = len(ann["data"]) / len(internal_rxns)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) reactions are charge unbalanced with at
        least one of the metabolites not having a charge or the overall
        charge not equal to 0: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Number of Mass-Unbalanced Reactions", format_type="count")
def test_reaction_mass_balance(read_only_model):
    """
    Expect all reactions to be mass balanced.

    This will exclude biomass, exchange and demand reactions as they are
    unbalanced by definition. It will also fail all reactions where at
    least one metabolite does not have a formula defined.

    In steady state, for each metabolite the sum of influx equals the sum
    of outflux. Hence the net masses of both sides of any model reaction have
    to be equal. Reactions where at least one metabolite does not have a
    charge are not considered to be balanced, even though the remaining
    metabolites participating in the reaction might be.
    """
    ann = test_reaction_mass_balance.annotation
    internal_rxns = con_helpers.get_internals(read_only_model)
    ann["data"] = get_ids(
        consistency.find_mass_unbalanced_reactions(internal_rxns)
    )
    ann["metric"] = len(ann["data"]) / len(internal_rxns)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) reactions are mass unbalanced with at least
        one of the metabolites not having a formula or the overall mass not
        equal to 0: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Number of Universally Blocked Reactions", format_type="count")
def test_blocked_reactions(read_only_model):
    """
    Expect all reactions to be able to carry flux in complete medium.

    Universally blocked reactions are reactions that during Flux Variability
    Analysis cannot carry any flux while all model boundaries are open.
    Generally blocked reactions are caused by network gaps, which can be
    attributed to scope or knowledge gaps.
    """
    ann = test_blocked_reactions.annotation
    ann["data"] = get_ids(
        consistency.find_universally_blocked_reactions(read_only_model)
    )
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """There are {} ({:.2%}) blocked reactions in
        the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Stoichiometrically Balanced Cycles", format_type="count")
def test_find_stoichiometrically_balanced_cycles(read_only_model):
    """
    Expect no stoichiometrically balanced loops to be present.

    Stoichiometrically Balanced Cycles are artifacts of insufficiently
    constrained networks resulting in reactions that can carry flux when
    all the boundaries have been closed.
    """
    ann = test_find_stoichiometrically_balanced_cycles.annotation
    ann["data"] = consistency.find_stoichiometrically_balanced_cycles(
        read_only_model)
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """There are {} ({:.2%}) reactions
        which participate in SBC in the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Number of Orphan Metabolites", format_type="count")
def test_find_orphans(read_only_model):
    """
    Expect no orphans to be present.

    Orphans are metabolites that are only consumed but not produced by
    reactions in the model. They may indicate the presence of network gaps.
    """
    ann = test_find_orphans.annotation
    ann["data"] = get_ids(consistency.find_orphans(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites are not produced by any reaction
        of the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Number of Dead-end Metabolites", format_type="count")
def test_find_deadends(read_only_model):
    """
    Expect no dead-ends to be present.

    Dead-ends are metabolites that can only be produced but not consumed by
    reactions in the model. They may indicate the presence of network gaps.
    """
    ann = test_find_deadends.annotation
    ann["data"] = get_ids(consistency.find_deadends(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites are not consumed by any reaction
        of the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert ann["data"] == 0, ann["message"]


@annotate(title="Number of Disconnected Metabolites", format_type="count")
def test_find_disconnected(read_only_model):
    """
    Expect no disconnected metabolites to be present.

    Disconnected metabolites are not part of any reaction in the model. They
    are most likely left-over from the reconstruction process, but may also
    point to network gaps.
    """
    ann = test_find_disconnected.annotation
    ann["data"] = get_ids(consistency.find_disconnected(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites are not associated with any
        reaction of the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Number of Metabolites Produced Without Substrate Consumption",
          format_type="count")
def test_find_metabolites_produced_with_closed_bounds(read_only_model):
    """
    Expect no metabolites to be produced without substrate consumption.

    It should not be possible for the model to produce metabolites without
    consuming substrate from the medium. This test disables all the boundary
    reactions and checks if each metabolite can be produced individually
    using flux balance analysis. To pass this test no metabolite outside of
    specific boundary reactions should be produced without the consumption of
    substrate.
    """
    ann = test_find_metabolites_produced_with_closed_bounds.annotation
    ann["data"] = get_ids(
        consistency.find_metabolites_produced_with_closed_bounds(
            read_only_model
        )
    )
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites can be produced without the model
        needing to consume any substrate: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Number of Metabolites Consumed Without Product Removal",
          format_type="count")
def test_find_metabolites_consumed_with_closed_bounds(read_only_model):
    """
    Expect no metabolites to be consumed without product removal.

    Just like metabolites should not be produced from nothing, mass should
    not simply be removed from the model. This test disables all the
    boundary reactions and checks if each metabolite can be consumed
    individually using flux balance analysis. To pass this test no
    metabolite outside of specific boundary reactions should be consumed
    without product leaving the system.
    """
    ann = test_find_metabolites_consumed_with_closed_bounds.annotation
    ann["data"] = get_ids(
        consistency.find_metabolites_consumed_with_closed_bounds(
            read_only_model
        )
    )
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites can be consumed without
        using the system's boundary reactions: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Number of Metabolites Not Produced In Complete Medium",
          format_type="count")
def test_find_metabolites_not_produced_with_open_bounds(read_only_model):
    """
    Expect no metabolites to be unproducible in complete medium.

    It should not be possible for the model to not produce metabolites in
    complete medium. This test enables all the boundary reactions and checks
    if each metabolite is incapable of being produced individually using flux
    balance analysis. To pass this test no metabolite outside of
    specific boundary reactions should be unproducible in complete medium.
    """
    ann = test_find_metabolites_not_produced_with_open_bounds.annotation
    ann["data"] = get_ids(
        consistency.find_metabolites_not_produced_with_open_bounds(
            read_only_model
        )
    )
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites cannot be produced in complete
        medium: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Number of Metabolites Not Consumed In Complete Medium",
          format_type="count")
def test_find_metabolites_not_consumed_with_open_bounds(read_only_model):
    """
    Expect no metabolites to be inconsumable in complete medium.

    Just like metabolites should not be unproducible in complete medium,
    they also should not be incapable of being consumed in complete medium.
    This test enables all the boundary reactions and checks if each metabolite
    is incapble of being consumed individually using flux balance analysis. To
    pass this test no metabolite outside of specific boundary reactions should
    be inconsumable in complete medium.
    """
    ann = test_find_metabolites_not_consumed_with_open_bounds.annotation
    ann["data"] = get_ids(
        consistency.find_metabolites_not_consumed_with_open_bounds(
            read_only_model
        )
    )
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites cannot be consumed in complete
        medium: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(
    title="Fraction of Unbounded Reactions in the Default Condition",
    format_type="percent")
def test_find_reactions_unbounded_flux_default_condition(read_only_model):
    """
    Expect the fraction of unbounded reactions to be low.

    A large fraction of model reactions able to carry unlimited flux under
    default conditions indicates problems with reaction directionality,
    missing cofactors, incorrectly defined transport reactions and more.
    """
    # TODO: Arbitrary threshold right now! Update after meta study!
    ann = test_find_reactions_unbounded_flux_default_condition.annotation
    unbounded_rxns, fraction, _ = \
        consistency.find_reactions_with_unbounded_flux_default_condition(
            read_only_model
        )
    ann["data"] = get_ids(unbounded_rxns)
    ann["metric"] = fraction
    ann["message"] = wrapper.fill(
        """ A fraction of {:.2%} of the non-blocked reactions (in total {}
        reactions) can carry unbounded flux in the default model
        condition. Unbounded reactions may be involved in
        thermodynamically infeasible cycles: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert ann["metric"] <= 0.1, ann["message"]
