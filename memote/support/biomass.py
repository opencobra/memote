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

from six import iteritems
from cobra.exceptions import Infeasible

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
    transport_reactions = set(helpers.find_transport_reactions(model))
    exchange_reactions = set(model.exchanges)
    biomass_reactions = set(helpers.find_biomass_reaction(model))

    combined_set = transport_reactions | exchange_reactions | biomass_reactions
    precursors = find_biomass_precursors(model, reaction)

    return [met for met in precursors if met.reactions.issubset(combined_set)]


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
