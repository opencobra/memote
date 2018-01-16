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
from collections import defaultdict
import numpy as np
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", UserWarning)
    # ignore Gurobi warning
    from cobra.exceptions import Infeasible

from six import iteritems, itervalues
from sympy import expand

LOGGER = logging.getLogger(__name__)


def find_transported_elements(rxn):
    """
    Return a dictionary showing the amount of transported elements of a rxn.

    Collects the elements for each metabolite participating in a reaction,
    multiplies the amount by the metabolite's stoichiometry in the reaction and
    bins the result according to the compartment that metabolite is in. This
    produces a dictionary of dictionaries such as this
    ``{'p': {'C': -1, 'H': -4}, c: {'C': 1, 'H': 4}}`` which shows the
    transported entities. This dictionary is then simplified to only include
    the non-zero elements of one single compartment i.e. showing the precise
    elements that are transported.

    Parameters
    ----------
    rxn : cobra.Reaction
        Any cobra.Reaction containing metabolites.

    """
    element_dist = defaultdict()
    # Collecting elements for each metabolite.
    for met in rxn.metabolites:
        if met.compartment not in element_dist:
            # Multiplication by the metabolite stoichiometry.
            element_dist[met.compartment] = \
                {k: v * rxn.metabolites[met]
                 for (k, v) in iteritems(met.elements)}
        else:
            x = {k: v * rxn.metabolites[met] for (k, v) in
                 iteritems(met.elements)}
            y = element_dist[met.compartment]
            element_dist[met.compartment] = \
                {k: x.get(k, 0) + y.get(k, 0) for k in set(x) | set(y)}
    delta_dict = defaultdict()
    # Simplification of the resulting dictionary of dictionaries.
    for elements in itervalues(element_dist):
        delta_dict.update(elements)
    # Only non-zero values get included in the returned delta-dict.
    delta_dict = {k: abs(v) for (k, v) in iteritems(delta_dict) if v != 0}
    return delta_dict


def find_transport_reactions(model):
    """
    Return a list of all transport reactions.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Notes
    -----
    A transport reaction is defined as follows:
    1. It contains metabolites from at least 2 compartments and
    2. at least 1 metabolite undergoes no chemical reaction, i.e.,
    the formula stays the same on both sides of the equation.

    This function will not identify transport via the PTS System.

    """
    transport_reactions = []
    for rxn in model.reactions:
        # Collecting criteria to classify transporters by.
        rxn_reactants = set([met.formula for met in rxn.reactants])
        rxn_products = set([met.formula for met in rxn.products])
        # Looking for formulas that stay the same on both side of the reaction.
        transported_mets = \
            [formula for formula in rxn_reactants if formula in rxn_products]
        # Collect information on the elemental differences between
        # compartments in the reaction.
        delta_dicts = find_transported_elements(rxn)
        non_zero_array = [v for (k, v) in iteritems(delta_dicts) if v != 0]
        # Weeding out reactions such as oxidoreductases where no net
        # transport of Hydrogen is occurring, but rather just an exchange of
        # electrons or charges effecting a change in protonation.
        if set(transported_mets) != set('H') and list(
            delta_dicts.keys()
        ) == ['H']:
            pass
        # All other reactions for which the amount of transported elements is
        # not zero, which are not part of the model's exchange nor
        # biomass reactions, are defined as transport reactions.
        # This includes reactions where the transported metabolite reacts with
        # a carrier molecule.
        elif sum(non_zero_array) and rxn not in model.exchanges and \
                rxn not in find_biomass_reaction(model):
            transport_reactions.append(rxn)

    return transport_reactions


def find_converting_reactions(model, pair):
    """
    Find reactions which convert a given metabolite pair.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    pair: tuple or list
        A pair of metabolite identifiers without compartment suffix.

    Returns
    -------
    frozenset
        The set of reactions that have one of the pair on their left-hand
        side and the other on the right-hand side.

    """
    met_ids = [m.id for m in model.metabolites]
    first = set(model.metabolites.get_by_id(m)
                for m in met_ids if m.startswith(pair[0]))
    second = set(model.metabolites.get_by_id(m)
                 for m in met_ids if m.startswith(pair[1]))

    hits = list()
    for rxn in model.reactions:
        if len(first & set(rxn.reactants)) > 0 and len(
                second & set(rxn.products)) > 0:
            hits.append(rxn)
        elif len(first & set(rxn.products)) > 0 and len(
                second & set(rxn.reactants)) > 0:
            hits.append(rxn)
    return frozenset(hits)


# TODO: Improve the heuristics of identifying the biomass reaction(s)!!!
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
    u"""
    Return a list of demand reactions.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    Notes
    -----
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

    References
    ----------
    .. [1] Thiele, I., & Palsson, B. Ø. (2010, January). A protocol for
           generating a high-quality genome-scale metabolic reconstruction.
           Nature protocols. Nature Publishing Group.
           http://doi.org/10.1038/nprot.2009.203

    """
    demand_and_exchange_rxns = set(model.exchanges)
    return [rxn for rxn in demand_and_exchange_rxns
            if not rxn.reversibility and not
            any(c in rxn.get_compartments() for c in ['e'])]


def find_sink_reactions(model):
    u"""
    Return a list of sink reactions.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    Notes
    -----
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

    References
    ----------
    .. [1] Thiele, I., & Palsson, B. Ø. (2010, January). A protocol for
           generating a high-quality genome-scale metabolic reconstruction.
           Nature protocols. Nature Publishing Group.
           http://doi.org/10.1038/nprot.2009.203

    """
    demand_and_exchange_rxns = set(model.exchanges)
    return [rxn for rxn in demand_and_exchange_rxns
            if rxn.reversibility and not
            any(c in rxn.get_compartments() for c in ['e'])]


def find_exchange_rxns(model):
    u"""
    Return a list of exchange reactions.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    Notes
    -----
    [1] defines exchange reactions as:
    -- reactions that 'define the extracellular environment'
    -- 'unbalanced, extra-organism reactions that represent the supply to or
    removal of metabolites from the extra-organism "space"'
    -- reactions with a formula such as: 'met_e -> ' or ' -> met_e' or
    'met_e <=> '

    Exchange reactions differ from demand reactions in that the metabolites
    are removed from or added to the extracellular environment only. With this
    the uptake or secretion of a metabolite is modeled, respectively.

    References
    ----------
    .. [1] Thiele, I., & Palsson, B. Ø. (2010, January). A protocol for
           generating a high-quality genome-scale metabolic reconstruction.
           Nature protocols. Nature Publishing Group.
           http://doi.org/10.1038/nprot.2009.203

    """
    demand_and_exchange_rxns = set(model.exchanges)
    return [rxn for rxn in demand_and_exchange_rxns
            if any(c in rxn.get_compartments() for c in ['e'])]


def find_functional_units(gpr_str):
    """
    Return an iterator of gene IDs grouped by boolean rules from the gpr_str.

    The gpr_str is first transformed into an algebraic expression, replacing
    the boolean operators 'or' with '+' and 'and' with '*'. Treating the
    gene IDs as sympy.symbols this allows a mathematical expansion of the
    algebraic expression. The expanded form is then split again producing sets
    of gene IDs that in the gpr_str had an 'and' relationship.

    Parameters
    ----------
    gpr_str : string
            A string consisting of gene ids and the boolean expressions 'and'
            and 'or'

    """
    algebraic_form = re.sub('[Oo]r', '+', re.sub('[Aa]nd', '*', gpr_str))
    expanded = str(expand(algebraic_form))
    for unit in expanded.replace('+', ',').split(' , '):
        yield unit.split('*')


def run_fba(model, rxn_id, direction="max", single_value=True):
    """
    Return the solution of an FBA to a set objective function.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model
    rxn_id : string
        A string containing the reaction ID of the desired FBA objective
    direction: string
        A string containing either "max" or "min" to specify the direction
        of the desired FBA objective function
    single_value: boolean
        Indicates whether the results for all reactions are gathered from the
        solver, or only the result for the objective value.

    Returns
    -------
    cobra.solution
        The cobra solution object for the corresponding FBA problem

    """
    model.objective = model.reactions.get_by_id(rxn_id)
    model.objective_direction = direction
    if single_value:
        try:
            return model.slim_optimize()
        except Infeasible:
            return np.nan
    else:
        try:
            solution = model.optimize()
            return solution
        except Infeasible:
            return np.nan


def close_boundaries_sensibly(model):
    """
    Return a cobra model with all boundaries closed and changed constraints.

    In the returned model previously fixed reactions are no longer constrained
    as such. Instead reactions are constrained according to their
    reversibility. This is to prevent the FBA from becoming infeasible when
    trying to solve a model with closed exchanges and one fixed reaction.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    Returns
    -------
    cobra.Model
        A cobra model with all boundary reactions closed and the constraints
        of each reaction set according to their reversibility.

    """
    with model:
        for rxn in model.reactions:
            if rxn.reversibility:
                rxn.bounds = -1, 1
            else:
                rxn.bounds = 0, 1
        for exchange in model.exchanges:
            exchange.bounds = (0, 0)
        return model.copy()
