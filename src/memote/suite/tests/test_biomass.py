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
from memote.utils import annotate, get_ids, truncate, wrapper


LOGGER = logging.getLogger(__name__)


@annotate(title="Biomass Reactions Identified", format_type="count")
def test_biomass_presence(model):
    """
    Expect the model to contain at least one biomass reaction.

    The biomass composition aka biomass formulation aka biomass reaction
    is a common pseudo-reaction accounting for biomass synthesis in
    constraints-based modelling. It describes the stoichiometry of
    intracellular compounds that are required for cell growth. While this
    reaction may not be relevant to modeling the metabolism of higher
    organisms, it is essential for single-cell modeling.

    Implementation:
    Identifies possible biomass reactions using two principal steps:
        1. Return reactions that include the SBO annotation "SBO:0000629" for
        biomass.
    If no reactions can be identifies this way:
        1. Look for the ``buzzwords`` "biomass", "growth" and "bof" in reaction
        IDs.
        2. Look for metabolite IDs or names that contain the ``buzzword``
        "biomass" and obtain the set of reactions they are involved in.
        3. Remove boundary reactions from this set.
        4. Return the union of reactions that match the buzzwords and of the
        reactions that metabolites are involved in that match the buzzword.
    This test checks if at least one biomass reaction is present.

    """
    ann = test_biomass_presence.annotation
    ann["data"] = [rxn.id for rxn in helpers.find_biomass_reaction(model)]
    outcome = len(ann["data"]) > 0
    ann["metric"] = 1.0 - float(outcome)
    ann["message"] = wrapper.fill(
        """In this model {} the following biomass reactions were
        identified: {}""".format(
            len(ann["data"]), truncate(ann["data"])
        )
    )
    assert outcome, ann["message"]


@pytest.mark.biomass
@annotate(
    title="Biomass Consistency",
    format_type="number",
    data=dict(),
    message=dict(),
    metric=dict(),
)
def test_biomass_consistency(model, reaction_id):
    """
    Expect biomass components to sum up to 1 g[CDW].

    This test only yields sensible results if all biomass precursor
    metabolites have chemical formulas assigned to them.
    The molecular weight of the biomass reaction in metabolic models is
    defined to be equal to 1 g/mmol. Conforming to this is essential in order
    to be able to reliably calculate growth yields, to cross-compare models,
    and to obtain valid predictions when simulating microbial consortia. A
    deviation from 1 - 1E-03 to 1 + 1E-06 is accepted.

    Implementation:
    Multiplies the coefficient of each metabolite of the biomass reaction with
    its molecular weight calculated from the formula, then divides the overall
    sum of all the products by 1000.

    """
    ann = test_biomass_consistency.annotation
    reaction = model.reactions.get_by_id(reaction_id)
    try:
        ann["data"][reaction_id] = biomass.sum_biomass_weight(reaction)
    except TypeError:
        ann["data"][reaction_id] = None
        ann["message"][reaction_id] = wrapper.fill(
            """One or more of the biomass components do not have a defined
            formula or contain unspecified chemical groups."""
        )
    else:
        ann["message"][reaction_id] = wrapper.fill(
            """The component molar mass of the biomass reaction {} sums up to {}
            which is outside of the 1e-03 margin from 1 mmol / g[CDW] / h.
            """.format(
                reaction_id, ann["data"][reaction_id]
            )
        )
    outcome = (1 - 1e-03) < ann["data"][reaction_id] < (1 + 1e-06)
    ann["metric"][reaction_id] = 1.0 - float(outcome)
    # To account for numerical inaccuracies, a range from 1-1e0-3 to 1+1e-06
    # is implemented in the assertion check
    assert outcome, ann["message"][reaction_id]


@pytest.mark.biomass
@annotate(
    title="Biomass Production In Default Medium",
    format_type="number",
    data=dict(),
    message=dict(),
    metric=dict(),
)
def test_biomass_default_production(model, reaction_id):
    """
    Expect biomass production in default medium.

    Using flux balance analysis this test optimizes the model for growth in
    the medium that is set by default. Any non-zero growth rate is accepted to
    pass this test.

    Implementation:
    Calculate the solution of FBA with the biomass reaction set as objective
    function and the model's default constraints.

    """
    ann = test_biomass_default_production.annotation
    ann["data"][reaction_id] = helpers.get_biomass_flux(model, reaction_id)
    outcome = ann["data"][reaction_id] > model.tolerance
    ann["metric"][reaction_id] = 1.0 - float(outcome)
    ann["message"][reaction_id] = wrapper.fill(
        """Using the biomass reaction {} this is the growth rate (1/h) that
        can be achieved when the model is simulated on the provided
        default medium: {}
        """.format(
            reaction_id, ann["data"][reaction_id]
        )
    )
    assert outcome, ann["message"][reaction_id]


@pytest.mark.biomass
@annotate(
    title="Biomass Production In Complete Medium",
    format_type="number",
    data=dict(),
    message=dict(),
    metric=dict(),
)
def test_biomass_open_production(model, reaction_id):
    """
    Expect biomass production in complete medium.

    Using flux balance analysis this test optimizes the model for growth using
    a complete medium i.e. unconstrained boundary reactions. Any non-zero
    growth rate is accepted to pass this test.

    Implementation:
    Calculate the solution of FBA with the biomass reaction set as objective
    function and after removing any constraints from all boundary reactions.

    """
    ann = test_biomass_open_production.annotation
    helpers.open_boundaries(model)
    ann["data"][reaction_id] = helpers.get_biomass_flux(model, reaction_id)
    outcome = ann["data"][reaction_id] > model.tolerance
    ann["metric"][reaction_id] = 1.0 - float(outcome)
    ann["message"][reaction_id] = wrapper.fill(
        """Using the biomass reaction {} this is the growth rate that can be
        achieved when the model is simulated on a complete medium i.e.
        with all the boundary reactions unconstrained: {}
        """.format(
            reaction_id, ann["data"][reaction_id]
        )
    )
    assert outcome, ann["message"][reaction_id]


@pytest.mark.biomass
@annotate(
    title="Blocked Biomass Precursors In Default Medium",
    format_type="count",
    data=dict(),
    metric=dict(),
    message=dict(),
)
def test_biomass_precursors_default_production(model, reaction_id):
    """
    Expect production of all biomass precursors in default medium.

    Using flux balance analysis this test optimizes for the production of each
    metabolite that is a substrate of the biomass reaction with the exception
    of atp and h2o. Optimizations are carried out using the default
    conditions. This is useful when reconstructing the precursor biosynthesis
    pathways of a metabolic model. To pass this test, the model should be able
    to synthesis all the precursors.

    Implementation:
    For each biomass precursor (except ATP and H2O) add a temporary demand
    reaction, then carry out FBA with this reaction as the objective. Collect
    all metabolites for which this optimization is equal to zero or
    infeasible.

    """
    ann = test_biomass_precursors_default_production.annotation
    reaction = model.reactions.get_by_id(reaction_id)
    ann["data"][reaction_id] = get_ids(
        biomass.find_blocked_biomass_precursors(reaction, model)
    )
    ann["metric"][reaction_id] = len(ann["data"][reaction_id]) / len(
        biomass.find_biomass_precursors(model, reaction)
    )
    ann["message"][reaction_id] = wrapper.fill(
        """Using the biomass reaction {} and when the model is simulated on the
        provided default medium a total of {} precursors
        ({:.2%} of all precursors except h2o and atp) cannot be produced: {}
        """.format(
            reaction_id,
            len(ann["data"][reaction_id]),
            ann["metric"][reaction_id],
            ann["data"][reaction_id],
        )
    )
    assert len(ann["data"][reaction_id]) == 0, ann["message"][reaction_id]


@pytest.mark.biomass
@annotate(
    title="Blocked Biomass Precursors In Complete Medium",
    format_type="count",
    data=dict(),
    metric=dict(),
    message=dict(),
)
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

    Implementation:
    First remove any constraints from all boundary reactions, then for each
    biomass precursor (except ATP and H2O) add a temporary demand
    reaction, then carry out FBA with this reaction as the objective. Collect
    all metabolites for which this optimization is below or equal to zero or is
    infeasible.

    """
    ann = test_biomass_precursors_open_production.annotation
    helpers.open_boundaries(model)
    reaction = model.reactions.get_by_id(reaction_id)
    ann["data"][reaction_id] = get_ids(
        biomass.find_blocked_biomass_precursors(reaction, model)
    )
    ann["metric"][reaction_id] = len(ann["data"][reaction_id]) / len(
        biomass.find_biomass_precursors(model, reaction)
    )
    ann["message"][reaction_id] = wrapper.fill(
        """Using the biomass reaction {} and when the model is simulated in
        complete medium a total of {} precursors
        ({:.2%} of all precursors except h2o and atp) cannot be produced: {}
        """.format(
            reaction_id,
            len(ann["data"][reaction_id]),
            ann["metric"][reaction_id],
            ann["data"][reaction_id],
        )
    )
    assert len(ann["data"][reaction_id]) == 0, ann["message"][reaction_id]


@pytest.mark.biomass
@annotate(
    title="Growth-associated Maintenance in Biomass Reaction",
    format_type="raw",
    data=dict(),
    message=dict(),
    metric=dict(),
)
def test_gam_in_biomass(model, reaction_id):
    u"""
    Expect the biomass reactions to contain  ATP and ADP.

    The growth-associated maintenance (GAM) term accounts for the energy in
    the form of ATP that is required to synthesize macromolecules such as
    Proteins, DNA and RNA, and other processes during growth. A GAM term is
    therefore a requirement for any well-defined biomass reaction. There are
    different ways to implement this term depending on
    what kind of experimental data is available and the preferred
    way of implementing the biomass reaction:
    - Chemostat growth experiments yield a single GAM value representing the
      required energy per gram of biomass (Figure 6 of [1]_). This can be
      implemented in a lumped biomass reaction or in the final term of a split
      biomass reaction.
    - Experimentally delineating or estimating the GAM requirements
      for each macromolecule separately is possible, yet requires either
      data from multi-omics experiments [2]_ or detailed resources [1]_ ,
      respectively. Individual energy requirements can either be implemented
      in a split biomass equation on the term for each macromolecule, or, on
      the basis of the biomass composition, they can be summed into a single
      GAM value for growth and treated as mentioned above.

    This test is only able to detect if a lumped biomass reaction or the final
    term of a split biomass reaction contains this term. Hence, it will
    only detect the use of a single GAM value as opposed to individual energy
    requirements of each macromolecule. Both approaches, however, have
    its merits.

    Implementation:
    Determines the metabolite identifiers of ATP, ADP, H2O, HO4P and H+ based
    on an internal mapping table. Checks if ATP and H2O are a subset of the
    reactants and ADP, HO4P and H+ a subset of the products of the biomass
    reaction.

    References:
    .. [1] Thiele, I., & Palsson, B. Ø. (2010, January). A protocol for
           generating a high-quality genome-scale metabolic reconstruction.
           Nature protocols. Nature Publishing Group.
           http://doi.org/10.1038/nprot.2009.203
    .. [2] Hackett, S. R., Zanotelli, V. R. T., Xu, W., Goya, J., Park, J. O.,
           Perlman, D. H., Gibney, P. A., Botstein, D., Storey, J. D.,
           Rabinowitz, J. D.  (2010, January). Systems-level analysis of
           mechanisms regulating yeast metabolic flux
           Science
           http://doi.org/10.1126/science.aaf2786

    """
    ann = test_gam_in_biomass.annotation
    reaction = model.reactions.get_by_id(reaction_id)
    outcome = biomass.gam_in_biomass(model, reaction)
    ann["data"][reaction_id] = outcome
    ann["metric"][reaction_id] = 1.0 - float(outcome)
    if outcome:
        ann["message"][reaction_id] = wrapper.fill(
            """Yes, {} contains a term for growth-associated maintenance.
            """.format(
                reaction_id
            )
        )
    else:
        ann["message"][reaction_id] = wrapper.fill(
            """No, {} does not contain a term for growth-associated
            maintenance.""".format(
                reaction_id
            )
        )
    assert outcome, ann["message"][reaction_id]


@pytest.mark.biomass
@annotate(
    title="Unrealistic Growth Rate In Default Medium",
    format_type="raw",
    data=dict(),
    message=dict(),
    metric=dict(),
)
def test_fast_growth_default(model, reaction_id):
    u"""
    Expect the predicted growth rate for each BOF to be below 2.81.

    The growth rate of a metabolic model should not be faster than that of the
    fastest growing organism. This is based on a doubling time of Vibrio
    natriegens which was reported to be 14.8 minutes by: Henry H. Lee, Nili
    Ostrov, Brandon G. Wong, Michaela A. Gold, Ahmad S. Khalil,
    George M. Church
    in https://www.biorxiv.org/content/biorxiv/early/2016/06/12/058487.full.pdf

    The calculation ln(2)/(14.8/60) ~ 2.81 yields the corresponding growth
    rate.

    Implementation:
    Calculate the solution of FBA with the biomass reaction set as objective
    function and a model's default constraints. Then check if the objective
    value is higher than 2.81.

    """
    ann = test_fast_growth_default.annotation
    outcome = helpers.get_biomass_flux(model, reaction_id) > 2.81
    ann["data"][reaction_id] = outcome
    ann["metric"][reaction_id] = 1.0 - float(outcome)
    if ann["data"][reaction_id]:
        ann["message"][reaction_id] = wrapper.fill(
            """Using the biomass reaction {} and when the model is simulated on
            the provided default medium the growth rate is *higher* than that
            of the fastest bacteria.
            This could be due to inconsistencies in the network or missing
            constraints.""".format(
                reaction_id
            )
        )
    else:
        ann["message"][reaction_id] = wrapper.fill(
            """Using the biomass reaction {} and when the model is simulated on
            the provided default medium the growth rate is *lower* than that
            of the fastest bacteria. This is to be expected for
            a majority of organisms.""".format(
                reaction_id
            )
        )
    assert outcome, ann["message"][reaction_id]


@pytest.mark.biomass
@annotate(
    title="Ratio of Direct Metabolites in Biomass Reaction",
    format_type="percent",
    data=dict(),
    message=dict(),
    metric=dict(),
)
def test_direct_metabolites_in_biomass(model, reaction_id):
    """
    Expect the ratio of direct metabolites to be below 0.5.

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

    Implementation:
    Identify biomass precursors (excluding ATP and H+), identify cytosol
    and extracellular compartment from an internal mapping table. Then,
    determine which precursors is only involved in transport, boundary and
    biomass reactions. Using FBA with the biomass function as the objective
    then determine whether the metabolite is taken up only to be consumed by
    the biomass reaction.

    """
    # TODO: Update the threshold as soon as we have an overview of the average!
    ann = test_direct_metabolites_in_biomass.annotation
    reaction = model.reactions.get_by_id(reaction_id)
    try:
        ann["data"][reaction_id] = get_ids(
            biomass.find_direct_metabolites(model, reaction)
        )
    except OptimizationError:
        ann["data"][reaction_id] = []
        ann["metric"][reaction_id] = 1.0
        ann["message"][reaction_id] = "This model does not grow."
        pytest.skip(ann["message"])
    ann["metric"][reaction_id] = len(ann["data"][reaction_id]) / len(
        biomass.find_biomass_precursors(model, reaction)
    )
    ann["message"][reaction_id] = wrapper.fill(
        """{} contains a total of {} direct metabolites ({:.2%}).
        Specifically these are: {}.
        """.format(
            reaction_id,
            len(ann["data"][reaction_id]),
            ann["metric"][reaction_id],
            ann["data"][reaction_id],
        )
    )
    assert ann["metric"][reaction_id] < 0.5, ann["message"][reaction_id]


@pytest.mark.biomass
@annotate(
    title="Number of Missing Essential Biomass Precursors",
    format_type="count",
    data=dict(),
    message=dict(),
    metric=dict(),
)
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

    These metabolites were selected based on the results presented by
    DOI:10.1016/j.ymben.2016.12.002

    Please note, that the authors also suggest to count C1 carriers
    (derivatives of tetrahydrofolate(B9) or tetrahydromethanopterin) as
    universal cofactors. We have omitted these from this check because there
    are many individual compounds that classify as C1 carriers, and it is not
    clear a priori which one should be preferred. In a future update, we may
    consider identifying these using a chemical ontology.

    Implementation:
    Determine whether the model employs a lumped or split biomass reaction.
    Then, using an internal mapping table, try to identify the above list of
    essential precursors in list of precursor metabolites of either type of
    biomass reaction. List IDs in the models namespace if the metabolite
    exists, else use the MetaNetX namespace if the metabolite does not exist
    in the model. Identifies the cytosol from an internal mapping
    table, and assumes that all precursors exist in that compartment.

    """
    ann = test_essential_precursors_not_in_biomass.annotation
    reaction = model.reactions.get_by_id(reaction_id)
    ann["data"][reaction_id] = [
        m for m in biomass.essential_precursors_not_in_biomass(model, reaction)
    ]
    ann["metric"][reaction_id] = len(ann["data"][reaction_id]) / len(
        biomass.find_biomass_precursors(model, reaction)
    )
    ann["message"][reaction_id] = wrapper.fill(
        """{} lacks a total of {} essential metabolites
        ({:.2%} of all biomass precursors). Specifically
        these are: {}.""".format(
            reaction_id,
            len(ann["data"][reaction_id]),
            ann["metric"][reaction_id],
            ann["data"][reaction_id],
        )
    )
    assert len(ann["data"][reaction_id]) == 0, ann["message"][reaction_id]
