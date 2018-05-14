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

"""
Biomass tests performed on an instance of ``cobra.Model``.

N.B.: We parametrize each function here with the identified biomass reactions.
In the storage of test results we rely on the order of the biomass fixtures
to remain the same as the parametrized test cases.
"""

from __future__ import absolute_import, division

import logging

import pytest
from cobra.exceptions import OptimizationError

import memote.support.biomass as biomass
import memote.support.helpers as helpers
from memote.utils import annotate, truncate, get_ids, wrapper


LOGGER = logging.getLogger(__name__)
BIOMASS_IDS = pytest.memote.biomass_ids


@annotate(title="Amount of Biomass Reactions", format_type="count")
def test_biomass_presence():
    """
    Expect the model to contain at least one biomass reaction.

    The biomass composition aka biomass formulation aka biomass reaction
    is a common pseudo-reaction accounting for biomass synthesis in
    constraints-based modelling. It describes the stoichiometry of
    intracellular compounds that are required for cell growth. While this
    reaction may not be relevant to modeling the metabolism of higher
    organisms, it is essential for single-cell modeling.

    This test checks if at least one biomass reaction is present. Currently,
    the biomass reaction is identified by looking for the word 'biomass' in
    the reaction ID. The heuristics of identification will be improved in the
    future.
    """
    ann = test_biomass_presence.annotation
    ann["data"] = BIOMASS_IDS
    ann["message"] = wrapper.fill(
        """In this model {} the following biomass reactions were
        identified: {}""".format(
            len(ann["data"]), truncate(ann["data"])))
    assert len(ann["data"]) > 0, ann["message"]


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
@annotate(title="Biomass Consistency", format_type="number", data=dict(),
          message=dict(), metric=dict())
def test_biomass_consistency(read_only_model, reaction_id):
    """
    Expect biomass components to sum up to 1 g[CDW].

    The molecular weight of the biomass reaction in metabolic models is
    defined to be equal to 1 g/mmol. Conforming to this is essential in order
    to be able to reliably calculate growth yields, to cross-compare models,
    and to obtain valid predictions when simulating microbial consortia. A
    deviation by 1e-03 is accepted.
    """
    ann = test_biomass_consistency.annotation
    reaction = read_only_model.reactions.get_by_id(reaction_id)
    ann["data"][reaction_id] = biomass.sum_biomass_weight(reaction)
    ann["metric"][reaction_id] = 1.0  # Placeholder value.
    ann["message"][reaction_id] = wrapper.fill(
        """The component molar mass of the biomass reaction {} sums up to {}
        which is outside of the 1e-03 margin from 1 mmol / g[CDW] / h.
        """.format(reaction_id, ann["data"][reaction_id]))
    # To account for numerical innacuracies, a range from 1-1e0-3 to 1+1e-06
    # is implemented in the assertion check
    assert (1 - 1e-03) < ann["data"][reaction_id] < (1 + 1e-06), \
        ann["message"][reaction_id]


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
@annotate(title="Biomass Production At Default State", format_type="number",
          data=dict(), message=dict(), metric=dict())
def test_biomass_default_production(model, reaction_id):
    """
    Expect biomass production in default medium.

    Using flux balance analysis this test optimizes the model for growth in
    the medium that is set by default. Any non-zero growth rate is accepted to
    pass this test.
    """
    ann = test_biomass_default_production.annotation
    ann["data"][reaction_id] = helpers.run_fba(model, reaction_id)
    ann["metric"][reaction_id] = 1.0  # Placeholder value.
    ann["message"][reaction_id] = wrapper.fill(
        """Using the biomass reaction {} this is the growth rate (1/h) that
        can be achieved when the model is simulated on the provided
        default medium: {}
        """.format(reaction_id, ann["data"][reaction_id]))
    assert ann["data"][reaction_id] > 0.0, ann["message"][reaction_id]


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
@annotate(title="Biomass Production In Complete Medium", format_type="number",
          data=dict(), message=dict(), metric=dict())
def test_biomass_open_production(model, reaction_id):
    """
    Expect biomass production in complete medium.

    Using flux balance analysis this test optimizes the model for growth using
    a complete medium i.e. unconstrained boundary reactions. Any non-zero
    growth rate is accepted to pass this test.
    """
    ann = test_biomass_open_production.annotation
    helpers.open_boundaries(model)
    ann["data"][reaction_id] = helpers.run_fba(model, reaction_id)
    ann["metric"][reaction_id] = 1.0  # Placeholder value.
    ann["message"][reaction_id] = wrapper.fill(
        """Using the biomass reaction {} this is the growth rate that can be
        achieved when the model is simulated on a complete medium i.e.
        with all the boundary reactions unconstrained: {}
        """.format(reaction_id, ann["data"][reaction_id]))
    assert ann["data"][reaction_id] > 0.0, ann["message"][reaction_id]


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
@annotate(title="Blocked Biomass Precursors At Default State",
          format_type="count", data=dict(), metric=dict(), message=dict())
def test_biomass_precursors_default_production(read_only_model, reaction_id):
    """
    Expect production of all biomass precursors in default medium.

    Using flux balance analysis this test optimizes for the production of each
    metabolite that is a substrate of the biomass reaction with the exception
    of atp and h2o. Optimizations are carried out using the default
    conditions. This is useful when reconstructing the precursor biosynthesis
    pathways of a metabolic model. To pass this test, the model should be able
    to synthesis all the precursors.
    """
    ann = test_biomass_precursors_default_production.annotation
    reaction = read_only_model.reactions.get_by_id(reaction_id)
    ann["data"][reaction_id] = get_ids(
        biomass.find_blocked_biomass_precursors(reaction, read_only_model)
    )
    ann["metric"][reaction_id] = len(ann["data"][reaction_id]) / \
        len(biomass.find_biomass_precursors(read_only_model, reaction))
    ann["message"][reaction_id] = wrapper.fill(
        """Using the biomass reaction {} and when the model is simulated on the
        provided default medium a total of {} precursors
        ({:.2%} of all precursors except h2o and atp) cannot be produced: {}
        """.format(reaction_id,
                   len(ann["data"][reaction_id]),
                   ann["metric"][reaction_id],
                   ann["data"][reaction_id]
                   ))
    assert len(ann["data"][reaction_id]) == 0, ann["message"][reaction_id]


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
@annotate(title="Blocked Biomass Precursors In Complete Medium",
          format_type="count", data=dict(), metric=dict(), message=dict())
def test_biomass_precursors_open_production(model, reaction_id):
    """
    Expect precursor production in complete medium.

    Using flux balance analysis this test optimizes for the production of each
    metabolite that is a substrate of the biomass reaction with the exception
    of atp and h2o. Optimizations are carried out using a complete
    medium i.e. unconstrained boundary reactions. This is useful when
    reconstructing the precursor biosynthesis pathways of a metabolic model.
    To pass this test, the model should be able to synthesis all the
    precursors.
    """
    ann = test_biomass_precursors_open_production.annotation
    helpers.open_boundaries(model)
    reaction = model.reactions.get_by_id(reaction_id)
    ann["data"][reaction_id] = get_ids(
        biomass.find_blocked_biomass_precursors(reaction, model))
    ann["metric"][reaction_id] = len(ann["data"][reaction_id]) / \
        len(biomass.find_biomass_precursors(model, reaction))
    ann["message"][reaction_id] = wrapper.fill(
        """Using the biomass reaction {} and when the model is simulated in
        complete medium a total of {} precursors
        ({:.2%} of all precursors except h2o and atp) cannot be produced: {}
        """.format(reaction_id,
                   len(ann["data"][reaction_id]),
                   ann["metric"][reaction_id],
                   ann["data"][reaction_id]
                   ))
    assert len(ann["data"][reaction_id]) == 0, ann["message"][reaction_id]


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
@annotate(title="Growth-associated Maintenance in Biomass Reaction",
          format_type="raw", data=dict(), message=dict(), metric=dict())
def test_gam_in_biomass(model, reaction_id):
    """
    Expect the biomass reactions to contain atp and adp.

    The growth-associated maintenance (GAM) term accounts for the energy in
    the form of ATP that is required to synthesize macromolecules such as
    Proteins, DNA and RNA, and other processes during growth. This test checks
    if a biomass reaction contains this term.
    """
    ann = test_gam_in_biomass.annotation
    reaction = model.reactions.get_by_id(reaction_id)
    ann["data"][reaction_id] = biomass.gam_in_biomass(model, reaction)
    ann["metric"][reaction_id] = 1.0  # Placeholder value.
    ann["message"][reaction_id] = wrapper.fill(
        """{} does not contain a term for growth-associated maintenance.
        """.format(reaction_id))
    assert ann["data"][reaction_id], ann["message"][reaction_id]


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
@annotate(title="Unrealistic Growth Rate In Default Condition",
          format_type="raw", data=dict(), message=dict(), metric=dict())
def test_fast_growth_default(model, reaction_id):
    """
    Expect the predicted growth rate for each BOF to be below 10.3972.

    The growth rate of a metabolic model should not be faster than that of the
    fastest growing organism. This is based on lowest doubling time reported
    here:
    http://www.pnnl.gov/science/highlights/highlight.asp?id=879
    """
    ann = test_fast_growth_default.annotation
    ann["data"][reaction_id] = helpers.run_fba(model, reaction_id) <= 10.3972
    ann["metric"][reaction_id] = 1.0  # Placeholder value.
    ann["message"][reaction_id] = wrapper.fill(
        """Using the biomass reaction {} and when the model is simulated on
        the provided default medium the growth rate amounts to {}""".format(
            reaction_id, ann["data"][reaction_id]))
    assert ann["data"][reaction_id] <= 10.3972, ann["message"][reaction_id]


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
@annotate(title="Ratio of Direct Metabolites in Biomass Reaction",
          format_type="percent", data=dict(), message=dict(), metric=dict())
def test_direct_metabolites_in_biomass(model, reaction_id):
    """
    Expect the biomass reactions to contain atp and adp.

    Some biomass precursors are taken from the media and directly consumed by
    the biomass reaction. It might not be a problem for ions or
    metabolites for which the organism in question is auxotrophic. However,
    too many of these metabolites may be artifacts of automated gap-filling
    procedures. Many gap-filling algorithms attempt to minimise the number of
    added reactions. This can lead to many biomass precursors being
    "direct metabolites".

    This test reports the ratio of direct metabolites to the total amount of
    precursors to a given biomass reaction. It specifically looks for
    metabolites that are only in either exchange, transport or biomass
    reactions. Bear in mind that this may lead to false positives in heavily
    compartimentalized models.

    To pass this test, the ratio of direct metabolites should be less than 50%
    of all biomass precursors. This is an arbitrary threshold but it takes
    into account that while certain ions do not serve a relevant metabolic
    function, it may still be important to include them in the biomass
    reaction to account for the impact of their uptake energy costs.

    This threshold is subject to change in the future.
    """
    # TODO: Update the threshold as soon as we have an overview of the average!
    ann = test_direct_metabolites_in_biomass.annotation
    reaction = model.reactions.get_by_id(reaction_id)
    try:
        ann["data"][reaction_id] = get_ids(
            biomass.find_direct_metabolites(model, reaction))
    except OptimizationError:
        ann["data"][reaction_id] = []
        ann["metric"][reaction_id] = 1.0
        ann["message"][reaction_id] = "This model does not grow."
        pytest.skip(ann["message"])
    ann["metric"][reaction_id] = len(ann["data"][reaction_id]) / \
        len(biomass.find_biomass_precursors(model, reaction))
    ann["message"][reaction_id] = wrapper.fill(
        """{} contains a total of {} direct metabolites ({:.2%}).
        Specifically these are: {}.
        """.format(reaction_id,
                   len(ann["data"][reaction_id]),
                   ann["metric"][reaction_id],
                   ann["data"][reaction_id]))
    assert ann["metric"][reaction_id] < 0.5, ann["message"][reaction_id]


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
@annotate(title="Number of Missing Essential Biomass Precursors",
          format_type="count", data=dict(), message=dict(), metric=dict())
def test_essential_precursors_not_in_biomass(model, reaction_id):
    """
    Expect the biomass reaction to contain all essential precursors.

    There are universal components of life that make up the biomass of all
    known organisms. These include all proteinogenic amino acids, deoxy- and
    ribonucleotides, water and a range of metabolic cofactors.

    This test reports the amount of biomass precursors that have been reported
    to be essential constituents of the biomass equation. All of the following
    precursors need to be included in the biomass reaction to pass the test:

    Aminoacids:
    trp__L, cys__L, his__L, tyr__L, met__L, phe__L, ser__L, pro__L, asp__L,
    thr__L, gln__L, glu__L, ile__L, arg__L, lys__L, val__L, leu__L, ala__L,
    gly, asn__L
    DNA: datp, dctp, dttp, dgtp
    RNA: atp, ctp, utp, gtp
    Cofactors: nad, nadp, amet, fad, pydx5p, coa, thmpp, fmn and h2o

    These metabolties were selected based on the results presented by
    DOI:10.1016/j.ymben.2016.12.002
    """
    ann = test_essential_precursors_not_in_biomass.annotation
    reaction = model.reactions.get_by_id(reaction_id)
    ann["data"][reaction_id] = [
        m for m in biomass.essential_precursors_not_in_biomass(
            model, reaction
        )]
    ann["metric"][reaction_id] = len(ann["data"][reaction_id]) / \
        len(biomass.find_biomass_precursors(model, reaction))
    ann["message"][reaction_id] = wrapper.fill(
        """{} lacks a total of {} essential metabolites
        ({:.2%} of all biomass precursors). Specifically
        these are: {}.""".format(reaction_id,
                                 len(ann["data"][reaction_id]),
                                 ann["metric"][reaction_id],
                                 ann["data"][reaction_id]
                                 )
    )
    assert len(ann["data"][reaction_id]) == 0, ann["message"][reaction_id]
