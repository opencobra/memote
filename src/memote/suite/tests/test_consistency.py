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
from cobra.flux_analysis import find_blocked_reactions

import memote.support.consistency as consistency
import memote.support.consistency_helpers as con_helpers
from memote.utils import annotate, get_ids, truncate, wrapper


@annotate(title="Stoichiometric Consistency", format_type="percent")
def test_stoichiometric_consistency(model):
    """
    Expect that the stoichiometry is consistent.

    Stoichiometric inconsistency violates universal constraints:
    1. Molecular masses are always positive, and
    2. On each side of a reaction the mass is conserved.
    A single incorrectly defined reaction can lead to stoichiometric
    inconsistency in the model, and consequently to unconserved metabolites.
    Similar to insufficient constraints, this may give rise to cycles which
    either produce mass from nothing or consume mass from the model.

    Implementation:
    This test uses an implementation of the algorithm presented in
    section 3.1 by Gevorgyan, A., M. G Poolman, and D. A Fell.
    "Detection of Stoichiometric Inconsistencies in Biomolecular Models."
    Bioinformatics 24, no. 19 (2008): 2245.
    doi: 10.1093/bioinformatics/btn425

    """
    ann = test_stoichiometric_consistency.annotation
    is_consistent = consistency.check_stoichiometric_consistency(model)
    ann["data"] = is_consistent
    ann["metric"] = 1.0 - float(is_consistent)
    ann["message"] = wrapper.fill(
        """This model's stoichiometry {}""".format(
            "consistent" if is_consistent else "inconsistent"
        )
    )
    assert is_consistent, ann["message"]


@annotate(title="Uncoserved Metabolites", format_type="count")
def test_unconserved_metabolites(model):
    """
    Report number all unconserved metabolites.

    The list of unconserved metabolites is computed using the algorithm described
    in section 3.2 of
    "Detection of Stoichiometric Inconsistencies in Biomolecular Models."
    Bioinformatics 24, no. 19 (2008): 2245.
    doi: 10.1093/bioinformatics/btn425.
    """
    ann = test_unconserved_metabolites.annotation
    is_consistent = consistency.check_stoichiometric_consistency(model)
    ann["data"] = []
    if not is_consistent:
        ann["data"] = get_ids(consistency.find_unconserved_metabolites(model))
    ann["metric"] = len(ann["data"])
    ann["message"] = wrapper.fill(
        """This model contains {} unconserved metabolites: {}""".format(
            ann["metric"],
            truncate(ann["data"]),
        )
    )
    assert ann["metric"] == 0, ann["message"]


@annotate(title="Minimal Inconsistent Net Stoichiometries", format_type="count")
def test_inconsistent_min_stoichiometry(model):
    """
    Report inconsistent min stoichiometries.

    Only 10 unconserved metabolites are reported and considered to
    avoid computing for too long.

    Implementation:
    Algorithm described in section 3.3 of
    "Detection of Stoichiometric Inconsistencies in Biomolecular Models."
    Bioinformatics 24, no. 19 (2008): 2245.
    doi: 10.1093/bioinformatics/btn425.
    """
    ann = test_inconsistent_min_stoichiometry.annotation
    is_consistent = consistency.check_stoichiometric_consistency(model)
    ann["data"] = []
    if not is_consistent:
        ann["data"] = [
            get_ids(mets)
            for mets in consistency.find_inconsistent_min_stoichiometry(model)
        ]
    ann["metric"] = len(ann["data"])
    ann["message"] = wrapper.fill(
        """This model contains {} minimal unconservable sets: {}""".format(
            ann["metric"] if ann["metric"] > 10 else "more than 10",
            truncate(ann["data"]),
        )
    )
    assert ann["metric"] == 0, ann["message"]


@pytest.mark.parametrize("met", [x for x in consistency.ENERGY_COUPLES])
@annotate(
    title="Erroneous Energy-generating Cycles",
    format_type="count",
    data=dict(),
    message=dict(),
    metric=dict(),
)
def test_detect_energy_generating_cycles(model, met):
    """
    Expect that no energy metabolite can be produced out of nothing.

    When a model is not sufficiently constrained to account for the
    thermodynamics of reactions, flux cycles may form which provide reduced
    metabolites to the model without requiring nutrient uptake. These cycles
    are referred to as erroneous energy-generating cycles. Their effect on the
    predicted growth rate in FBA may account for an increase of up to 25%,
    which makes studies involving the growth rates predicted from such models
    unreliable.

    Implementation:
    This test uses an implementation of the algorithm presented by:
    Fritzemeier, C. J., Hartleb, D., Szappanos, B., Papp, B., & Lercher,
    M. J. (2017). Erroneous energy-generating cycles in published genome scale
    metabolic networks: Identification and removal. PLoS Computational
    Biology, 13(4), 1–14. http://doi.org/10.1371/journal.pcbi.1005494

    First attempt to identify the main compartment (cytosol), then attempt to
    identify each metabolite of the referenced list of energy couples via an
    internal mapping table. Construct a dissipation reaction for each couple.
    Carry out FBA with each dissipation reaction as the objective and report
    those reactions that non-zero carry flux.

    """
    ann = test_detect_energy_generating_cycles.annotation
    if met not in model.metabolites:
        pytest.skip(
            "This test has been skipped since metabolite {} could "
            "not be found in the model.".format(met)
        )
    ann["data"][met] = consistency.detect_energy_generating_cycles(model, met)
    # Report the number of cycles scaled by the number of reactions.
    ann["metric"][met] = len(ann["data"][met]) / len(model.reactions)
    ann["message"][met] = wrapper.fill(
        """The model can produce '{}' without requiring resources. This is
        caused by improperly constrained reactions leading to erroneous
        energy-generating cycles. The following {} reactions are involved in
        those cycles: {}""".format(
            met, len(ann["data"][met]), truncate(ann["data"][met])
        )
    )
    assert len(ann["data"][met]) == 0, ann["message"][met]


@annotate(title="Charge Balance", format_type="count")
def test_reaction_charge_balance(model):
    """
    Expect all reactions to be charge balanced.

    This will exclude biomass, exchange and demand reactions as they are
    unbalanced by definition. It will also fail all reactions where at
    least one metabolite does not have a charge defined.

    In steady state, for each metabolite the sum of influx equals the sum
    of efflux. Hence the net charges of both sides of any model reaction have
    to be equal. Reactions where at least one metabolite does not have a
    charge are not considered to be balanced, even though the remaining
    metabolites participating in the reaction might be.

    Implementation:
    For each reaction that isn't a boundary or biomass reaction check if each
    metabolite has a non-zero charge attribute and if so calculate if the
    overall sum of charges of reactants and products is equal to zero.

    """
    ann = test_reaction_charge_balance.annotation
    internal_rxns = con_helpers.get_internals(model)
    ann["data"] = get_ids(consistency.find_charge_unbalanced_reactions(internal_rxns))
    ann["metric"] = len(ann["data"]) / len(internal_rxns)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) reactions are charge unbalanced with at
        least one of the metabolites not having a charge or the overall
        charge not equal to 0: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Mass Balance", format_type="count")
def test_reaction_mass_balance(model):
    """
    Expect all reactions to be mass balanced.

    This will exclude biomass, exchange and demand reactions as they are
    unbalanced by definition. It will also fail all reactions where at
    least one metabolite does not have a formula defined.

    In steady state, for each metabolite the sum of influx equals the sum
    of efflux. Hence the net masses of both sides of any model reaction have
    to be equal. Reactions where at least one metabolite does not have a
    formula are not considered to be balanced, even though the remaining
    metabolites participating in the reaction might be.

    Implementation:
    For each reaction that isn't a boundary or biomass reaction check if each
    metabolite has a non-zero elements attribute and if so calculate if the
    overall element balance of reactants and products is equal to zero.

    """
    ann = test_reaction_mass_balance.annotation
    internal_rxns = con_helpers.get_internals(model)
    ann["data"] = get_ids(consistency.find_mass_unbalanced_reactions(internal_rxns))
    ann["metric"] = len(ann["data"]) / len(internal_rxns)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) reactions are mass unbalanced with at least
        one of the metabolites not having a formula or the overall mass not
        equal to 0: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Universally Blocked Reactions", format_type="count")
def test_blocked_reactions(model):
    """
    Expect all reactions to be able to carry flux in complete medium.

    Universally blocked reactions are reactions that during Flux Variability
    Analysis cannot carry any flux while all model boundaries are open.
    Generally blocked reactions are caused by network gaps, which can be
    attributed to scope or knowledge gaps.

    Implementation:
    Use flux variability analysis (FVA) implemented in
    cobra.flux_analysis.find_blocked_reactions with open_exchanges=True.
    Please refer to the cobrapy documentation for more information:
    https://cobrapy.readthedocs.io/en/stable/autoapi/cobra/flux_analysis/
    variability/index.html#cobra.flux_analysis.variability.
    find_blocked_reactions

    """
    ann = test_blocked_reactions.annotation
    ann["data"] = find_blocked_reactions(model, open_exchanges=True)
    ann["metric"] = len(ann["data"]) / len(model.reactions)
    ann["message"] = wrapper.fill(
        """There are {} ({:.2%}) blocked reactions in
        the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Stoichiometrically Balanced Cycles", format_type="count")
def test_find_stoichiometrically_balanced_cycles(model):
    """
    Expect no stoichiometrically balanced loops to be present.

    Stoichiometrically Balanced Cycles are artifacts of insufficiently
    constrained networks resulting in reactions that can carry flux when
    all the boundaries have been closed.

    Implementation:
    Close all model boundary reactions and then use flux variability analysis
    (FVA) to identify reactions that carry flux.

    """
    ann = test_find_stoichiometrically_balanced_cycles.annotation
    ann["data"] = consistency.find_stoichiometrically_balanced_cycles(model)
    ann["metric"] = len(ann["data"]) / len(model.reactions)
    ann["message"] = wrapper.fill(
        """There are {} ({:.2%}) reactions
        which participate in SBC in the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Orphan Metabolites", format_type="count")
def test_find_orphans(model):
    """
    Expect no orphans to be present.

    Orphans are metabolites that are only consumed but not produced by
    reactions in the model. They may indicate the presence of network and
    knowledge gaps.

    Implementation:
    Find orphan metabolites structurally by considering only reaction
    equations and bounds. FBA is not carried out.


    """
    ann = test_find_orphans.annotation
    ann["data"] = get_ids(consistency.find_orphans(model))
    ann["metric"] = len(ann["data"]) / len(model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites are not produced by any reaction
        of the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Dead-end Metabolites", format_type="count")
def test_find_deadends(model):
    """
    Expect no dead-ends to be present.

    Dead-ends are metabolites that can only be produced but not consumed by
    reactions in the model. They may indicate the presence of network and
    knowledge gaps.

    Implementation:
    Find dead-end metabolites structurally by considering only reaction
    equations and bounds. FBA is not carried out.

    """
    ann = test_find_deadends.annotation
    ann["data"] = get_ids(consistency.find_deadends(model))
    ann["metric"] = len(ann["data"]) / len(model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites are not consumed by any reaction
        of the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert ann["data"] == 0, ann["message"]


@annotate(title="Metabolite Connectivity", format_type="count")
def test_find_disconnected(model):
    """
    Expect no disconnected metabolites to be present.

    Disconnected metabolites are not part of any reaction in the model. They
    are most likely left-over from the reconstruction process, but may also
    point to network and knowledge gaps.

    Implementation:
    Check for any metabolites of the cobra.Model object with emtpy reaction
    attribute.

    """
    ann = test_find_disconnected.annotation
    ann["data"] = get_ids(consistency.find_disconnected(model))
    ann["metric"] = len(ann["data"]) / len(model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites are not associated with any
        reaction of the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Metabolite Production In Complete Medium", format_type="count")
def test_find_metabolites_not_produced_with_open_bounds(model):
    """
    Expect metabolites to be producible in complete medium.

    In complete medium, a model should be able to divert flux to every
    metabolite. This test opens all the boundary reactions i.e. simulates a
    complete medium and checks if any metabolite cannot be produced
    individually using flux balance analysis. Metabolites that cannot be
    produced this way are likely orphan metabolites, downstream of reactions
    with fixed constraints, or blocked by a cofactor imbalance. To pass this
    test all metabolites should be producible.

    Implementation:
    Open all model boundary reactions, then for each metabolite in the model
    add a boundary reaction and maximize it with FBA.

    """
    ann = test_find_metabolites_not_produced_with_open_bounds.annotation
    ann["data"] = consistency.find_metabolites_not_produced_with_open_bounds(model)
    ann["metric"] = len(ann["data"]) / len(model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites cannot be produced in complete
        medium: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Metabolite Consumption In Complete Medium", format_type="count")
def test_find_metabolites_not_consumed_with_open_bounds(model):
    """
    Expect metabolites to be consumable in complete medium.

    In complete medium, a model should be able to divert flux from every
    metabolite. This test opens all the boundary reactions i.e. simulates a
    complete medium and checks if any metabolite cannot be consumed
    individually using flux balance analysis. Metabolites that cannot be
    consumed this way are likely dead-end metabolites or upstream of reactions
    with fixed constraints. To pass this test all metabolites should be
    consumable.

    Implementation:
    Open all model boundary reactions, then for each metabolite in the model
    add a boundary reaction and minimize it with FBA.

    """
    ann = test_find_metabolites_not_consumed_with_open_bounds.annotation
    ann["data"] = consistency.find_metabolites_not_consumed_with_open_bounds(model)
    ann["metric"] = len(ann["data"]) / len(model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} ({:.2%}) metabolites cannot be consumed in complete
        medium: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Unbounded Flux In Default Medium", format_type="percent")
def test_find_reactions_unbounded_flux_default_condition(model):
    """
    Expect the fraction of unbounded reactions to be low.

    A large fraction of model reactions able to carry unlimited flux under
    default conditions indicates problems with reaction directionality,
    missing cofactors, incorrectly defined transport reactions and more.

    Implementation:
    Without changing the default constraints run flux variability analysis.
    From the FVA results identify those reactions that carry flux equal to the
    model's maximal or minimal flux.

    """
    ann = test_find_reactions_unbounded_flux_default_condition.annotation
    (
        unbounded_rxn_ids,
        fraction,
        _,
    ) = consistency.find_reactions_with_unbounded_flux_default_condition(model)
    ann["data"] = unbounded_rxn_ids
    ann["metric"] = fraction
    ann["message"] = wrapper.fill(
        """ A fraction of {:.2%} of the non-blocked reactions (in total {}
        reactions) can carry unbounded flux in the default model
        condition. Unbounded reactions may be involved in
        thermodynamically infeasible cycles: {}""".format(
            ann["metric"], len(ann["data"]), truncate(ann["data"])
        )
    )
    # TODO: Arbitrary threshold right now! Update after meta study!
    assert ann["metric"] <= 0.1, ann["message"]
