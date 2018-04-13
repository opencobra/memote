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

import memote.support.helpers as helpers

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
    Find un-tagged non-transport reactions.

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
    transport_rxns = helpers.find_transport_reactions(model)
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
    Find mis-tagged non-transport reactions.

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
    transport_rxns = set(helpers.find_transport_reactions(model))
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

    Make an exception for the ATP synthase reaction (ATPS) which a unique
    case for a transport reaction and thus does not get the tag.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    Notes
    -----
    A transport reaction is defined as follows:
    1. It contains metabolites from at least 2 compartments and
    2. at least 1 metabolite undergoes no chemical reaction, i.e.,
    the formula stays the same on both sides of the equation.

    Reactions that only transport protons ('H') across the membrane are
    excluded, as well as reactions with redox cofactors whose formula is
    either 'X' or 'XH2'

    """
    transport_rxns = helpers.find_transport_reactions(model)

    atp_adp_rxns = helpers.find_converting_reactions(
        model, ("MNXM3", "MNXM7")
    )
    gtp_gdp_rxns = helpers.find_converting_reactions(
        model, ("MNXM51", "MNXM30")
    )
    ctp_cdp_rxns = helpers.find_converting_reactions(
        model, ["MNXM63", "MNXM220"]
    )
    energy_requiring = set().union(atp_adp_rxns, gtp_gdp_rxns, ctp_cdp_rxns)

    non_abc_transporters = set(transport_rxns).difference(energy_requiring)

    return [rxn for rxn in non_abc_transporters
            if not re.match("[A-Z0-9]+\w*?t\w*?", rxn.id)
            if not rxn.id.startswith('ATPS')]


def find_abc_tag_transporter(model):
    """
    Find Atp-binding cassette transport rxns without 'abc' tag.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    Notes
    -----
    An ABC transport reaction is defined as follows:
    1. It contains metabolites from at least 2 compartments,
    2. at least 1 metabolite undergoes no chemical reaction, i.e.,
    the formula stays the same on both sides of the equation, and
    3. ATP is converted to ADP (+ Pi + H, yet this isn't checked for
    explicitly).

    Reactions that only transport protons ('H') across the membrane are
    excluded, as well as reactions with redox cofactors whose formula is
    either 'X' or 'XH2'

    """
    transport_rxns = helpers.find_transport_reactions(model)
    atp_adp_rxns = helpers.find_converting_reactions(
        model, ("MNXM3", "MNXM7")
    )
    gtp_gdp_rxns = helpers.find_converting_reactions(
        model, ("MNXM51", "MNXM30")
    )
    ctp_cdp_rxns = helpers.find_converting_reactions(
        model, ["MNXM63", "MNXM220"]
    )
    energy_requiring = set().union(atp_adp_rxns, gtp_gdp_rxns, ctp_cdp_rxns)

    abc_transporters = set(transport_rxns).intersection(energy_requiring)

    return [rxn for rxn in abc_transporters
            if not re.match("[A-Z0-9]+\w*?abc\w*?", rxn.id)]


def find_upper_case_mets(model):
    """
    Find metabolites whose ID roots contain uppercase characters.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    Notes
    -----
    In metabolite names, individual uppercase exceptions are allowed:
    -- Dextorotary prefix: 'D'
    -- Levorotary prefix: 'L'
    -- Prefixes for the absolute configuration of a stereocenter: 'R' and 'S'
    -- Prefixes for the absolute stereochemistry of double bonds 'E' and 'Z'
    -- Acyl carrier proteins can be labeled as 'ACP'

    """
    comp_pattern = "^([a-z0-9]|Z|E|L|D|ACP|S|R)+_\w+"
    return [met for met in model.metabolites
            if not re.match(comp_pattern, met.id)]


def find_untagged_demand_rxns(model):
    """
    Find demand reactions whose IDs do not begin with ``DM_``.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    """
    demand_rxns = helpers.find_demand_reactions(model)
    comp_pattern = "^DM_\w*?"
    return [rxn for rxn in demand_rxns
            if not re.match(comp_pattern, rxn.id)]


def find_false_demand_rxns(model):
    """
    Find reactions which are tagged with ``DM_`` but which are not demand rxns.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    """
    true_demand_rxns = helpers.find_demand_reactions(model)
    comp_pattern = "^DM_\w*?"
    all_rxns_tagged_DM = [rxn for rxn in model.reactions
                          if re.match(comp_pattern, rxn.id)]
    # false demand reactions
    return set(all_rxns_tagged_DM).difference(set(true_demand_rxns))


def find_untagged_sink_rxns(model):
    """
    Find demand reactions whose IDs do not begin with ``SK_``.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    """
    sink_rxns = helpers.find_sink_reactions(model)
    comp_pattern = "^SK_\w*?"
    return [rxn for rxn in sink_rxns
            if not re.match(comp_pattern, rxn.id)]


def find_false_sink_rxns(model):
    """
    Find reactions which are tagged with ``SK_`` but which are not sink rxns.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    """
    true_sink_rxns = helpers.find_sink_reactions(model)
    comp_pattern = "^SK_\w*?"
    all_rxns_tagged_SK = [rxn for rxn in model.reactions
                          if re.match(comp_pattern, rxn.id)]
    # false sink reactions
    return set(all_rxns_tagged_SK).difference(set(true_sink_rxns))


def find_untagged_exchange_rxns(model):
    """
    Find exchange reactions whose identifiers do not begin with ``EX_``.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    """
    exchange_rxns = helpers.find_exchange_rxns(model)
    comp_pattern = "^EX_\w*?"
    return [rxn for rxn in exchange_rxns
            if not re.match(comp_pattern, rxn.id)]


def find_false_exchange_rxns(model):
    """
    Find reactions that are tagged with ``EX_`` but are not exchange reactions.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    """
    true_exchange_rxns = helpers.find_exchange_rxns(model)
    comp_pattern = "^EX_\w*?"
    all_rxns_tagged_EX = [rxn for rxn in model.reactions
                          if re.match(comp_pattern, rxn.id)]
    # false exchange reactions
    return set(all_rxns_tagged_EX).difference(set(true_exchange_rxns))
