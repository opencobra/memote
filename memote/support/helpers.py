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

"""Helper functions that are used all over the memote package."""

from __future__ import absolute_import

import logging
import re

LOGGER = logging.getLogger(__name__)


def find_transport_reactions(model):
    """
    Return a list of all transport reactions.

       A transport reaction is defined as follows:
       -- It contains metabolites from at least 2 compartments
       -- At least 1 metabolite undergoes no chemical reaction
          i.e. the formula stays the same on both sides of the equation

       Will not identify transport via the PTS System.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    compartment_spanning_rxns = \
        [rxn for rxn in model.reactions if len(rxn.get_compartments()) >= 2]

    transport_reactions = []
    for rxn in compartment_spanning_rxns:
        rxn_reactants = set([met.formula for met in rxn.reactants])
        rxn_products = set([met.formula for met in rxn.products])

        transported_mets = \
            [formula for formula in rxn_reactants if formula in rxn_products]
        # Excluding H-pumping reactions for now.
        if set(transported_mets).issubset(set('H')):
            pass
        # Excluding redox-reactions which only transport electrons
        elif set(transported_mets).issubset(set(['X', 'XH2'])):
            pass

        elif len(transported_mets) >= 1:
            transport_reactions.append(rxn)

    return transport_reactions


def find_atp_adp_converting_reactions(model):
    """
    Find reactions which interact with ATP and ADP.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    atp_all_comp_rxn_list = []
    for met in model.metabolites:
        if re.match('^atp_.*', met.id):
            atp_all_comp_rxn_list.append(met.reactions)

    adp_all_comp_rxn_list = []
    for met in model.metabolites:
        if re.match('^adp_.*', met.id):
            adp_all_comp_rxn_list.append(met.reactions)

    atp_union = set().union(*atp_all_comp_rxn_list)
    adp_union = set().union(*adp_all_comp_rxn_list)

    return atp_union.intersection(adp_union)


def find_biomass_reaction(model):
    """
    Return a list of the biomass reaction(s) of the model.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    return [rxn for rxn in model.reactions if "biomass" in rxn.id.lower()]


def get_difference(subset, model, type):
    """
    Return difference between a given subset and the full set.

    Providing that all metabolites or reactions in subset have a certain
    attribute, this function returns the 'leftover' list of the metabolites or
    reactions from the total amount of metabolites or reactions, i.e. those
    that do not have this attribute.

    Parameters
    ----------
    subset: list
        A list of either reactions or metabolites with a certain attribute.

    model : cobra.Model
        The metabolic model under investigation.

    """
    if type == 'met':
        diff_subset = set(model.metabolites).difference(set(subset))
    if type == 'rxn':
        diff_subset = set(model.reactions).difference(set(subset))
    else:
        pass
    return list(diff_subset)
