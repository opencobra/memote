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

"""Supporting functions for biomass consistency checks."""

from __future__ import absolute_import

import logging
import re

import numpy as np
import pandas as pd

from six import iteritems
from cobra.exceptions import Infeasible

from memote.utils import get_ids
import memote.support.helpers as helpers

__all__ = (
    "sum_biomass_weight", "find_biomass_precursors",
    "find_blocked_biomass_precursors")

LOGGER = logging.getLogger(__name__)


# 20 Amino Acids, 4 Deoxyribonucleotides, 4 Ribonucleotides,
# 8 Cofactors, and H2O
ESSENTIAL_PRECURSOR_IDS = \
    ['MNXM94', 'MNXM55', 'MNXM134', 'MNXM76', 'MNXM61',
     'MNXM97', 'MNXM53', 'MNXM114', 'MNXM42', 'MNXM142',
     'MNXM37', 'MNXM89557', 'MNXM231', 'MNXM70', 'MNXM78',
     'MNXM199', 'MNXM140', 'MNXM32', 'MNXM29', 'MNXM147',
     'MNXM286', 'MNXM360', 'MNXM394', 'MNXM344',
     'MNXM3', 'MNXM51', 'MNXM63', 'MNXM121',
     'MNXM8', 'MNXM5', 'MNXM16', 'MNXM33', 'MNXM161',
     'MNXM12', 'MNXM256', 'MNXM119', 'MNXM2']


def sum_biomass_weight(reaction):
    """
    Compute the sum of all reaction compounds.

    Parameters
    ----------
    reaction : cobra.core.reaction.Reaction
        The biomass reaction of the model under investigation.

    """
    return sum(-coef * met.formula_weight
               for (met, coef) in iteritems(reaction.metabolites)) / 1000.0


def find_biomass_precursors(model, reaction):
    """
    Return a list of all biomass precursors excluding ATP and H2O.

    Parameters
    ----------
    reaction : cobra.core.reaction.Reaction
        The biomass reaction of the model under investigation.

    """
    id_of_main_compartment = helpers.find_compartment_id_in_model(model, 'c')
    gam_reactants = set()
    try:
        gam_reactants.update([
            helpers.find_met_in_model(
                model, "MNXM3", id_of_main_compartment)[0]])
    except RuntimeError:
        pass
    try:
        gam_reactants.update([
            helpers.find_met_in_model(
                model, "MNXM2", id_of_main_compartment)[0]])
    except RuntimeError:
        pass

    biomass_precursors = set(reaction.reactants) - gam_reactants

    return list(biomass_precursors)


def find_blocked_biomass_precursors(reaction, model):
    """
    Return a list of all biomass precursors that cannot be produced.

    Parameters
    ----------
    reaction : cobra.core.reaction.Reaction
        The biomass reaction of the model under investigation.

    model : cobra.Model
        The metabolic model under investigation.

    """
    LOGGER.debug("Finding blocked biomass precursors")
    precursors = find_biomass_precursors(model, reaction)
    blocked_precursors = list()
    for precursor in precursors:
        with model:
            dm_rxn = model.add_boundary(precursor, type="demand")
            model.objective = dm_rxn
            try:
                solution = model.optimize()
                LOGGER.debug(
                    "%s: demand flux is '%g' and solver status is '%s'",
                    str(precursor), solution.objective_value, solution.status)
                if solution.objective_value <= 0.0:
                    blocked_precursors.append(precursor)
            except Infeasible:
                blocked_precursors.append(precursor)
    return blocked_precursors


def gam_in_biomass(model, reaction):
    """
    Return boolean if biomass reaction includes growth-associated maintenance.

    Parameters
    ----------
    reaction : cobra.core.reaction.Reaction
        The biomass reaction of the model under investigation.

    """
    id_of_main_compartment = helpers.find_compartment_id_in_model(model, 'c')

    try:
        left = {
            helpers.find_met_in_model(
                model, "MNXM3", id_of_main_compartment)[0],
            helpers.find_met_in_model(
                model, "MNXM2", id_of_main_compartment)[0]
        }
        right = {
            helpers.find_met_in_model(
                model, "MNXM7", id_of_main_compartment)[0],
            helpers.find_met_in_model(
                model, "MNXM1", id_of_main_compartment)[0],
            helpers.find_met_in_model(
                model, "MNXM9", id_of_main_compartment)[0]
        }
    except RuntimeError:
        return False

    return (
        left.issubset(set(reaction.reactants)) and
        right.issubset(set(reaction.products)))


def find_direct_metabolites(model, reaction):
    """
    Return list of possible direct biomass precursor metabolites.

    Direct metabolites are metabolites that are involved only in transport
    and/or boundary reactions, as well as the biomass reaction(s).
    This function detects and excludes false positives from being part of the
    count of direct metabolites. A false positive is specifically defined as
    a metabolite that is taken up by the biomass reaction, and only involved
    in tranposrt and/or boundary reactions, but is transported from the cytosol
    into the extracellular space where it isomerizes and is taken up by the
    biomass reaction. Oftentimes, the isomerization reaction is not part of the
    model, and so such a metabolite is wrongly identified as a direct
    metabolite. The most common examples of this occur in various E. coli
    models.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    reaction : cobra.core.reaction.Reaction
        The biomass reaction of the model under investigation.

    Returns
    -------
    list
        Metabolites that qualify as direct metabolites i.e. biomass precursors
        that are taken up to be consumed by the biomass reaction only.

    """
    biomass_rxns = set(helpers.find_biomass_reaction(model))
    tra_bou_bio_rxns = helpers.find_tra_bou_bio_reactions(model, biomass_rxns)
    precursors = find_biomass_precursors(model, reaction)
    tra_bou_bio_mets = [met for met in precursors if
                        met.reactions.issubset(tra_bou_bio_rxns)]
    rxns_of_interest = set([rxn for met in tra_bou_bio_mets
                            for rxn in met.reactions
                            if rxn not in biomass_rxns])

    solution = model.optimize()
    if solution.objective_value == 0:
        LOGGER.error("Failed to generate a non-zero objective value with "
                     "flux balance analysis. This may be a bug.")
        raise ValueError("The flux balance analysis on this model returned an "
                         "objective value of zero. Make sure the model can "
                         "grow! Check if the constraints are not too strict!")

    tra_bou_bio_fluxes = solution.fluxes[get_ids(rxns_of_interest)]
    flux_sum = pd.DataFrame(index=tra_bou_bio_mets, columns=["sum"], data=0).T

    # The following is to detect false positives.
    # As mentioned previously, these false positives exists in the "e"
    # compartment with flux from the "c" compartment and are part of the
    # biomass reaction(s). It sums fluxes positively or negatively depending
    # on if direct metabolites in the "e" compartment are defined as reactants
    # or products in various reactions.
    main_comp = helpers.find_compartment_id_in_model(model, 'c')
    ext_space = helpers.find_compartment_id_in_model(model, 'e')
    for met in tra_bou_bio_mets:
        for rxn in met.reactions:
            not_biomass_rxn = rxn not in biomass_rxns
            extracellular = met.compartment == ext_space
            # if the metabolite is in the "e" compartment and a reactant,
            # sum the fluxes accordingly (outward=negative, inward=positive)
            if met in rxn.reactants and not_biomass_rxn and extracellular:
                product_comps = set([p.compartment for p in rxn.products])
                # if the reaction has no product (outward flux)
                if len(product_comps) == 0:
                    flux_sum[met] += -float(
                        tra_bou_bio_fluxes[get_ids([rxn])])
                # if the reaction has a product in "c" (inward flux)
                elif main_comp in product_comps:
                    flux_sum[met] += float(
                        tra_bou_bio_fluxes[get_ids([rxn])])
            # if the metabolite is in the "e" compartment and a product,
            # sum the fluxes accordingly (outward=negative, inward=positive)
            elif met in rxn.products and not_biomass_rxn and extracellular:
                reactant_comps = set([p.compartment for p in rxn.reactants])
                # if the reaction has no reactant (inward flux)
                if len(reactant_comps) == 0:
                    flux_sum[met] += float(
                        tra_bou_bio_fluxes[get_ids([rxn])])
                # if the reaction has a reactant in "c" (outward flux)
                elif main_comp in reactant_comps:
                    flux_sum[met] += -float(
                        tra_bou_bio_fluxes[get_ids([rxn])])
            # for all non-e metabolites (cannot be false positives, flux is
            # automatically non-negative)
            elif not_biomass_rxn and not extracellular:
                flux_sum[met] += np.abs(
                    float(tra_bou_bio_fluxes[get_ids([rxn])]))

    return [met for met in flux_sum.T.loc[flux_sum.T['sum'] > 0].index]


def bundle_biomass_components(model, reaction):
    """
    Return bundle biomass component reactions if it is not one lumped reaction.

    There are two basic ways of specifying the biomass composition. The most
    common is a single lumped reaction containing all biomass precursors.
    Alternatively, the biomass equation can be split into several reactions
    each focusing on a different macromolecular component for instance
    a (1 gDW ash) + b (1 gDW phospholipids) + c (free fatty acids)+
    d (1 gDW carbs) + e (1 gDW protein) + f (1 gDW RNA) + g (1 gDW DNA) +
    h (vitamins/cofactors) + xATP + xH2O-> 1 gDCW biomass + xADP + xH + xPi.
    This function aims to identify if the given biomass reaction 'reaction',
    is a lumped all-in-one reaction, or whether it is just the final
    composing reaction of all macromolecular components. It is important to
    identify which other reaction belong to a given biomass reaction to be
    able to identify universal biomass components or calculate detailed
    precursor stoichiometries.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    reaction : cobra.core.reaction.Reaction
        The biomass reaction of the model under investigation.

    Returns
    -------
    list
        One or more reactions that qualify as THE biomass equation together.

    Notes
    -----
    Counting H2O, ADP, Pi, H, and ATP, the amount of metabolites in a split
    reaction is comparatively low:
    Any reaction with less or equal to 15 metabolites can
    probably be counted as a split reaction containing Ash, Phospholipids,
    Fatty Acids, Carbohydrates (i.e. cell wall components), Protein, RNA,
    DNA, Cofactors and Vitamins, and Small Molecules. Any reaction with more
    than or equal to 28 metabolites, however, (21 AA + 3 Nucleotides (4-ATP)
    + 4 Deoxy-Nucleotides) can be considered a lumped reaction.
    Anything in between will be treated conservatively as a lumped reaction.
    For split reactions, after removing any of the metabolites associated with
    growth-associated energy expenditure (H2O, ADP, Pi, H, and ATP), the
    only remaining metabolites should be generalized macromolecule precursors
    e.g. Protein, Phospholipids etc. Each of these have their own composing
    reactions. Hence we include the reactions of these metabolites in the
    set that ultimately makes up the returned list of reactions that together
    make up the biomass equation.

    """
    if len(reaction.metabolites) >= 16:
        return [reaction]

    id_of_main_compartment = helpers.find_compartment_id_in_model(model,
                                                                  'c')
    gam_mets = ["MNXM3", "MNXM2", "MNXM7", "MNXM1", 'MNXM9']
    try:
        gam = set([helpers.find_met_in_model(
            model, met, id_of_main_compartment)[0] for met in gam_mets])
    except RuntimeError:
        gam = set()
    regex = re.compile('^{}(_[a-zA-Z]+?)*?$'.format('biomass'),
                       re.IGNORECASE)
    biomass_metabolite = set(model.metabolites.query(regex))

    macromolecules = set(reaction.metabolites) - gam - biomass_metabolite

    bundled_reactions = set()
    for met in macromolecules:
        bundled_reactions = bundled_reactions | set(met.reactions)

    return list(bundled_reactions)


def essential_precursors_not_in_biomass(model, reaction):
    u"""
    Return a list of essential precursors missing from the biomass reaction.

    There are universal components of life that make up the biomass of all
    known organisms. These include all proteinogenic amino acids, deoxy- and
    ribonucleotides, water and a range of metabolic cofactors.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    reaction : cobra.core.reaction.Reaction
        The biomass reaction of the model under investigation.

    Returns
    -------
    list
        IDs of essential metabolites missing from the biomass reaction. The
        IDS will appear in the models namespace if the metabolite exists, but
        will be using the MetaNetX namespace if the metabolite does not exist
        in the model.

    Notes
    -----
    "Answering the question of what to include in the core of a biomass
    objective function is not always straightforward. One example is different
    nucleotide forms, which, although inter-convertible, are essential for
    cellular chemistry. We propose here that all essential and irreplaceable
    molecules for metabolism should be included in the biomass functions of
    genome scale metabolic models. In the special case of cofactors, when two
    forms of the same cofactor take part in the same reactions (such as NAD
    and NADH), only one form could be included for the sake of simplicity.
    When a class of cofactors includes active and non-active interconvertible
    forms, the active forms should be preferred. [1]_."

    References
    ----------
    .. [1] Xavier, J. C., Patil, K. R., & Rocha, I. (2017). Integration of
    Biomass Formulations of Genome-Scale Metabolic Models with Experimental
    Data Reveals Universally Essential Cofactors in Prokaryotes. Metabolic
    Engineering, 39(October 2016), 200–208.
    http://doi.org/10.1016/j.ymben.2016.12.002

    """
    main_comp = helpers.find_compartment_id_in_model(model, 'c')
    biomass_eq = bundle_biomass_components(model, reaction)
    pooled_precursors = set(
        [met for rxn in biomass_eq for met in rxn.metabolites])

    missing_essential_precursors = []
    for mnx_id in ESSENTIAL_PRECURSOR_IDS:
        try:
            met = helpers.find_met_in_model(model, mnx_id, main_comp)[0]
            if met not in pooled_precursors:
                missing_essential_precursors.append(met.id)
        except RuntimeError:
            missing_essential_precursors.append(mnx_id)

    return missing_essential_precursors
