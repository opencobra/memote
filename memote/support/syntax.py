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

"""Supporting functions for syntax checks performed on the model object."""

from __future__ import absolute_import

import logging
import re
from builtins import dict

from memote.support.helpers import (
    find_atp_adp_converting_reactions, find_demand_and_exchange_reactions,
    find_transport_reactions)

LOGGER = logging.getLogger(__name__)

SUFFIX_MAP = dict({
    'p': 'pp',
    'c': 'c',
    'e': 'e',
    'er': 'er',
    'g': 'g',
    'l': 'l',
    'm': 'm',
    'n': 'n',
    'x': 'x',
    'v': 'v'})


def find_rxn_id_compartment_suffix(model, suffix):
    """
    Find incorrectly tagged IDs.

    Find non-transport reactions with metabolites in the given compartment
    whose ID is not tagged accordingly.

    Parameters
    ----------
    model : cobra.core.Model.Model
        A cobrapy metabolic model.
    suffix : str
        The suffix of the compartment to be checked.

    Returns
    -------
    list
        Non-transport reactions that have at least one metabolite in the
        compartment given by `suffix` but whose IDs do not have
        the `suffix` appended.
    """
    transport_rxns = find_transport_reactions(model)
    exchange_demand_rxns = find_demand_and_exchange_reactions(model)

    comp_pattern = re.compile(
        "[A-Z0-9]+\w*?{}\w*?".format(SUFFIX_MAP[suffix])
    )

    rxns = []
    for rxn in model.reactions:
        if suffix in rxn.compartments:
            if ('biomass' not in rxn.id.lower()) and (
                    rxn not in transport_rxns and
                    rxn not in exchange_demand_rxns):
                rxns.append(rxn)

    return [rxn for rxn in rxns if not comp_pattern.match(rxn.id)]


def find_reaction_tag_transporter(model):
    """
    Return incorrectly tagged transport reactions.

    A transport reaction is defined as follows:
       -- It contains metabolites from at least 2 compartments
       -- At least 1 metabolite undergoes no chemical reaction
          i.e. the formula stays the same on both sides of the equation

    Reactions that only transport protons ('H') across the membrane are
    excluded, as well as reactions with redox cofactors whose formula is
    either 'X' or 'XH2'

    Parameters
    ----------
    model : model: cobra.core.Model.Model
            A cobrapy metabolic model
    """
    transport_rxns = find_transport_reactions(model)
    atp_adp_rxns = find_atp_adp_converting_reactions(model)

    non_abc_transporters = set(transport_rxns).difference(set(atp_adp_rxns))

    return [rxn for rxn in non_abc_transporters
            if not re.match("[A-Z0-9]+\w*?t\w*?", rxn.id)]
