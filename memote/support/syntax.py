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
    find_atp_adp_converting_reactions, find_transport_reactions)

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
    model : cobra.Model
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
    transport_rxns = set(find_transport_reactions(model))
    exchange_demand_rxns = set(model.exchanges)

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


def find_rxn_id_suffix_compartment(model, suffix):
    """
    Find incorrectly tagged non-transport reactions.

    Find non-transport reactions whose ID bear a compartment tag but which do
    not contain any metabolites in the given compartment.

    Parameters
    ----------
    model : cobra.Model
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
    transport_rxns = set(find_transport_reactions(model))
    exchange_demand_rxns = set(model.exchanges)

    comp_pattern = re.compile(
        "[A-Z0-9]+\w*?{}\w*?".format(SUFFIX_MAP[suffix])
    )

    rxns = []

    for rxn in model.reactions:
        if comp_pattern.match(rxn.id):
            if ('biomass' not in rxn.id.lower()) and (
                    rxn not in transport_rxns and
                    rxn not in exchange_demand_rxns):
                rxns.append(rxn)

    return [rxn for rxn in rxns if suffix not in rxn.compartments]


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
    model : cobra.Model
            A cobrapy metabolic model

    """
    transport_rxns = find_transport_reactions(model)
    atp_adp_rxns = find_atp_adp_converting_reactions(model)

    non_abc_transporters = set(transport_rxns).difference(set(atp_adp_rxns))

    return [rxn for rxn in non_abc_transporters
            if not re.match("[A-Z0-9]+\w*?t\w*?", rxn.id)]


def find_abc_tag_transporter(model):
    """
    Find Atp-binding cassette transport rxns without 'abc' tag.

    An ABC transport reaction is defined as follows:
       -- It contains metabolites from at least 2 compartments
       -- At least 1 metabolite undergoes no chemical reaction
          i.e. the formula stays the same on both sides of the equation
       -- ATP is converted to ADP (+ Pi + H,
          yet this isn't checked for explicitly)

    Reactions that only transport protons ('H') across the membrane are
    excluded, as well as reactions with redox cofactors whose formula is
    either 'X' or 'XH2'

    Parameters
    ----------
    model : cobra.Model
            A cobrapy metabolic model

    """
    transport_rxns = find_transport_reactions(model)
    atp_adp_rxns = find_atp_adp_converting_reactions(model)

    abc_transporters = set(transport_rxns).intersection(set(atp_adp_rxns))

    return [rxn for rxn in abc_transporters
            if not re.match("[A-Z0-9]+\w*?abc\w*?", rxn.id)]


def find_upper_case_mets(model):
    """
    Find metabolites whose ID roots contain uppercase characters.

    In metabolite names, individual uppercase exceptions are allowed:
    -- Dextorotary prefix: 'D'
    -- Levorotary prefix: 'L'
    -- Prefixes for the absolute configuration of a stereocenter: 'R' and 'S'
    -- Prefixes for the absolute stereochemistry of double bonds 'E' and 'Z'
    -- Acyl carrier proteins can be labeled as 'ACP'

    Parameters
    ----------
    model : cobra.Model
            A cobrapy metabolic model

    """
    comp_pattern = "^([a-z0-9]|Z|E|L|D|ACP|S|R)+_\w+"
    return [met for met in model.metabolites
            if not re.match(comp_pattern, met.id)]


def find_untagged_demand_rxns(model):
    """
    Find demand reactions whose IDs do not begin with 'DM_'.

    [1] defines demand reactions as:
    -- 'unbalanced network reactions that allow the accumulation of a compound'
    -- reactions that are chiefly added during the gap-filling process
    -- as a means of dealing with 'compounds that are known to be produced by
    the organism [..] (i) for which no information is available about their
    fractional distribution to the biomass or (ii) which may only be produced
    in some environmental conditions
    -- reactions with a formula such as: 'met_c -> '

    Demand reactions differ from exchange reactions in that the metabolites
    are not removed from the extracellular environment, but from any of the
    organism's compartments.

    Parameters
    ----------
    model : cobra.Model
            A cobrapy metabolic model

    References
    ----------
    [1] Thiele, I., & Palsson, B. Ø. (2010, January). A protocol for generating
    a high-quality genome-scale metabolic reconstruction. Nature protocols.
    Nature Publishing Group. http://doi.org/10.1038/nprot.2009.203

    """
    demand_and_exchange_rxns = set(model.exchanges)
    demand_rxns = [rxn for rxn in demand_and_exchange_rxns
                   if not rxn.reversibility and
                   rxn.get_compartments() not in ['e']]

    comp_pattern = "^DM_\w*?"
    return [rxn for rxn in demand_rxns
            if not re.match(comp_pattern, rxn.id)]


def find_untagged_sink_rxns(model):
    """
    Find demand reactions whose IDs do not begin with 'SK_'.

    [1] defines sink reactions as:
    -- 'similar to demand reactions' but reversible, thus able to supply the
    model with metabolites
    -- reactions that are chiefly added during the gap-filling process
    -- as a means of dealing with 'compounds that are produced by nonmetabolic
    cellular processes but that need to be metabolized'
    -- reactions with a formula such as: 'met_c <-> '

    Sink reactions differ from exchange reactions in that the metabolites
    are not removed from the extracellular environment, but from any of the
    organism's compartments.

    Parameters
    ----------
    model : cobra.Model
            A cobrapy metabolic model

    References
    ----------
    [1] Thiele, I., & Palsson, B. Ø. (2010, January). A protocol for generating
    a high-quality genome-scale metabolic reconstruction. Nature protocols.
    Nature Publishing Group. http://doi.org/10.1038/nprot.2009.203

    """
    demand_and_exchange_rxns = set(model.exchanges)
    sink_rxns = [rxn for rxn in demand_and_exchange_rxns
                   if rxn.reversibility and
                   rxn.get_compartments() not in ['e']]

    comp_pattern = "^SK_\w*?"
    return [rxn for rxn in sink_rxns
            if not re.match(comp_pattern, rxn.id)]


def find_untagged_exchange_rxns(model):
    """
    Find exchange reactions whose IDs do not begin with 'EX_'.

    [1] defines exchange reactions as:
    -- reactions that 'define the extracellular environment'
    -- 'unbalanced, extra-organism reactions that represent the supply to or
    removal of metabolites from the extra-organism "space"'
    -- reactions with a formula such as: 'met_e -> ' or ' -> met_e' or
    'met_e <=> '

    Exchange reactions differ from demand reactions in that the metabolites
    are removed from or added to the extracellular environment only. With this
    the uptake or secretion of a metabolite is modeled, respectively.

    Parameters
    ----------
    model : cobra.Model
            A cobrapy metabolic model

    References
    ----------
    [1] Thiele, I., & Palsson, B. Ø. (2010, January). A protocol for generating
    a high-quality genome-scale metabolic reconstruction. Nature protocols.
    Nature Publishing Group. http://doi.org/10.1038/nprot.2009.203

    """
    demand_and_exchange_rxns = set(model.exchanges)
    exchange_rxns = [rxn for rxn in demand_and_exchange_rxns
                     if rxn.get_compartments() == ['e']]

    comp_pattern = "^EX_\w*?"
    return [rxn for rxn in exchange_rxns
            if not re.match(comp_pattern, rxn.id)]
