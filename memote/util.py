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

"""
The module provides recurring functions useful for both hard and soft checks.
"""

from __future__ import absolute_import
import re

__all__ = ("find_demand_and_exchange_reactions",)

import logging

LOGGER = logging.getLogger(__name__)


def find_demand_and_exchange_reactions(model):
    """Return a list containing demand and exchange reactions of model

    :param model: A cobrapy metabolic model
    :type model: cobra.core.Model.Model
    """
    return [rxn for rxn in model.reactions if len(rxn.metabolites.keys()) == 1]


def find_transport_reactions(model):
    """Return a list of all transport reactions.

       A transport reaction is defined as follows:
       -- It contains metabolites from at least 2 compartments
       -- At least 1 metabolite undergoes no chemical reaction
          i.e. the formula stays the same on both sides of the equation

       Will not identify transport via the PTS System.

    Parameters
    ----------
    model : model: cobra.core.Model.Model
            A cobrapy metabolic model
    """
    compartment_spanning_rxns = \
        [rxn for rxn in model.reactions if len(rxn.get_compartments()) >= 2]

    transport_reactions = []
    for rxn in compartment_spanning_rxns:
        rxn_reactants = {met.formula for met in rxn.reactants}
        rxn_products = {met.formula for met in rxn.products}

        transported_mets = \
            [formula for formula in rxn_reactants if formula in rxn_products]

        if len(transported_mets) == 1 and set(transported_mets).union({'H'}):
            pass

        elif not (
            not (len(transported_mets) > 1) or not set(transported_mets).union(
                {'X', 'XH2'})):
            pass

        elif len(transported_mets) > 1:
            transport_reactions.append(rxn)

    return transport_reactions


def find_atp_adp_converting_reactions(model):
    """
    Return a list of all reactions in which interact with both
    atp and adp in all compartments.

    Parameters
    ----------
    model : model: cobra.core.Model.Model
            A cobrapy metabolic model
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
