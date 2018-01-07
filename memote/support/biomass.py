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

from six import iteritems
from cobra.exceptions import Infeasible

import memote.support.helpers as helpers

__all__ = (
    "sum_biomass_weight", "find_biomass_precursors",
    "find_blocked_biomass_precursors")

LOGGER = logging.getLogger(__name__)


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


def find_biomass_precursors(reaction):
    """
    Return a list of all biomass precursors excluding ATP and H2O.

    Parameters
    ----------
    reaction : cobra.core.reaction.Reaction
        The biomass reaction of the model under investigation.

    """
    return [met for met in reaction.reactants
            if met.id != 'atp_c' or met.id != 'h2o_c']


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
    precursors = find_biomass_precursors(reaction)
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


def gam_in_biomass(reaction):
    """
    Return boolean if biomass reaction includes growth-associated maintenance.

    Parameters
    ----------
    reaction : cobra.core.reaction.Reaction
        The biomass reaction of the model under investigation.

    """
    left = set(["atp_c", "h2o_c"])
    right = set(["adp_c", "pi_c", "h_c"])
    return (
        left.issubset(met.id for met in reaction.reactants) and
        right.issubset(met.id for met in reaction.products))


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
    precursors = find_biomass_precursors(reaction)

    return [met for met in precursors if met.reactions.issubset(combined_set)]
