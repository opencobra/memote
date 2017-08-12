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
from builtins import dict

LOGGER = logging.getLogger(__name__)


def find_transport_reactions(model):
    """
    Return a list of all transport reactions.

    A transport reaction is defined as follows:
    1. It contains metabolites from at least 2 compartments and
    2. at least 1 metabolite undergoes no chemical reaction, i.e.,
    the formula stays the same on both sides of the equation.

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


def df2dict(df):
    """Turn a `pandas.DataFrame` into a `dict` of lists."""
    blob = dict((key, df[key].tolist()) for key in df.columns)
    blob["index"] = df.index.tolist()
    return blob


def find_demand_reactions(model):
    """
    Return a list of demand reactions.

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
    return [rxn for rxn in demand_and_exchange_rxns
            if not rxn.reversibility and not
            any(c in rxn.get_compartments() for c in ['e'])]


def find_sink_reactions(model):
    """
    Return a list of sink reactions.

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
    return [rxn for rxn in demand_and_exchange_rxns
            if rxn.reversibility and not
            any(c in rxn.get_compartments() for c in ['e'])]


def find_exchange_rxns(model):
    """
    Return a list of exchange reactions.

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
    return [rxn for rxn in demand_and_exchange_rxns
            if any(c in rxn.get_compartments() for c in ['e'])]
