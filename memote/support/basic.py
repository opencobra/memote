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

"""Supporting functions for basic checks performed on the model object."""

from __future__ import absolute_import

import logging

import memote.support.helpers as helpers

__all__ = ("check_metabolites_formula_presence",)


LOGGER = logging.getLogger(__name__)


def check_metabolites_formula_presence(model):
    """Return the list of model metabolites that have no associated formula."""
    return [met for met in model.metabolites if met.formula is None]


def check_metabolites_charge_presence(model):
    """Return the list of model metabolites that have no associated charge."""
    return [met for met in model.metabolites if met.charge is None]


def check_gene_protein_reaction_rule_presence(model):
    """Return the list of model reactions that have no associated gene rule."""
    return [rxn for rxn in model.reactions if not rxn.gene_reaction_rule]


def find_nonzero_constrained_reactions(model):
    """Return list of reactions with non-zero, non-maximal bounds."""
    return [rxn for rxn in model.reactions if
            0 > rxn.lower_bound > -1000 or
            0 < rxn.upper_bound < 1000]


def find_zero_constrained_reactions(model):
    """Return list of reactions that are constrained to zero flux."""
    return [rxn for rxn in model.reactions if
            rxn.lower_bound == 0 and
            rxn.upper_bound == 0]


def find_irreversible_reactions(model):
    """Return list of reactions that are irreversible."""
    return [rxn for rxn in model.reactions if rxn.reversibility is False]


def find_unconstrained_reactions(model):
    """Return list of reactions that are not constrained at all."""
    return [rxn for rxn in model.reactions if
            rxn.lower_bound <= -1000 and
            rxn.upper_bound >= 1000]


def find_ngam(model):
    u"""
    Return all potential non growth-associated maintenance reactions.

    From the list of all reactions that convert ATP to ADP select the reactions
    that match a defined reaction string and whose metabolites are situated
    within the main model compartment. The main model compartment is the
    cytosol, and if that cannot be identified, the compartment with the most
    metabolites.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns
    -------
    list
        Reactions that qualify as non-growth associated maintenance reactions.

    Notes
    -----
    [1]_ define the non-growth associated maintenance (NGAM) as the energy
    required to maintain all constant processes such as turgor pressure and
    other housekeeping activities. In metabolic models this is expressed by
    requiring a simple ATP hydrolysis reaction to always have a fixed minimal
    amount of flux. This value can be measured as described by [1]_ .

    References
    ----------
    .. [1] Thiele, I., & Palsson, B. Ø. (2010, January). A protocol for
          generating a high-quality genome-scale metabolic reconstruction.
          Nature protocols. Nature Publishing Group.
          http://doi.org/10.1038/nprot.2009.203

    """
    atp_adp_conv_rxns = helpers.find_converting_reactions(
        model, ("MNXM3", "MNXM7")
    )
    id_of_main_compartment = helpers.find_compartment_id_in_model(model, 'c')

    reactants = {
        helpers.find_met_in_model(model, "MNXM3", id_of_main_compartment)[0],
        helpers.find_met_in_model(model, "MNXM2", id_of_main_compartment)[0]
    }

    products = {
        helpers.find_met_in_model(model, "MNXM7", id_of_main_compartment)[0],
        helpers.find_met_in_model(model, "MNXM1", id_of_main_compartment)[0],
        helpers.find_met_in_model(model, "MNXM9", id_of_main_compartment)[0]
    }

    candidates = [rxn for rxn in atp_adp_conv_rxns
                  if rxn.reversibility is False and
                  set(rxn.reactants) == reactants and
                  set(rxn.products) == products]

    buzzwords = ['maintenance', 'atpm', 'requirement',
                 'ngam', 'non-growth', 'associated']

    refined_candidates = [rxn for rxn in candidates if any(
        string in rxn.name.lower() for string in buzzwords
    )]

    if refined_candidates:
        return refined_candidates
    else:
        return candidates


def calculate_metabolic_coverage(model):
    u"""
    Return the ratio of reactions and genes included in the model.

    Determine whether the amount of reactions and genes in model not equal to
    zero, then return the ratio.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns
    -------
    float
        The ratio of reactions to genes also called metabolic coverage.

    Raises
    ------
    ValueError
        If the model does not contain either reactions or genes.

    Notes
    -----
    According to [1]_ this is a good quality indicator expressing the degree of
    metabolic coverage i.e. modeling detail of a given reconstruction. The
    authors explain that models with a 'high level of modeling detail have
    ratios >1, and [models] with low level of detail have ratios <1'. They
    explain that 'this difference arises because [models] with basic or
    intermediate levels of detail often include many reactions in which several
    gene products and their enzymatic transformations are ‘lumped’'.

    References
    ----------
    .. [1] Monk, J., Nogales, J., & Palsson, B. O. (2014). Optimizing
          genome-scale network reconstructions. Nature Biotechnology, 32(5),
          447–452. http://doi.org/10.1038/nbt.2870

    """
    if len(model.reactions) == 0 or len(model.genes) == 0:
        raise ValueError("The model contains no reactions or genes.")
    return float(len(model.reactions)) / float(len(model.genes))


def find_protein_complexes(model):
    """
    Find tuples of gene identifiers that constitute functional enzyme complexes.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    protein_complexes = set()
    for rxn in model.reactions:
        if rxn.gene_reaction_rule:
            for candidate in helpers.find_functional_units(
                    rxn.gene_reaction_rule):
                if len(candidate) >= 2:
                    protein_complexes.add(tuple(candidate))
    return protein_complexes


def find_pure_metabolic_reactions(model):
    """
    Return reactions that are neither transporters, exchanges, nor pseudo.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    exchanges = set(model.exchanges)
    transporters = set(helpers.find_transport_reactions(model))
    biomass = set(helpers.find_biomass_reaction(model))
    return set(model.reactions) - (exchanges | transporters | biomass)


def find_unique_metabolites(model):
    """Return set of metabolite IDs without duplicates from compartments."""
    # TODO: BiGG specific (met_c).
    return set(met.id.split("_", 1)[0] for met in model.metabolites)


def check_transport_reaction_gpr_presence(model):
    """Return the list of transport reactions that have no associated gpr."""
    return [rxn for rxn in helpers.find_transport_reactions(model)
            if not rxn.gene_reaction_rule]
