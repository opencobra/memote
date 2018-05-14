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
from collections import defaultdict
from operator import itemgetter


import numpy as np
import pandas as pd
from six import iteritems, itervalues
from sympy import expand
from importlib_resources import open_text
from cobra.exceptions import Infeasible
from pylru import lrudecorator

import memote.utils as utils
import memote.support.data

LOGGER = logging.getLogger(__name__)

TRANSPORT_RXN_SBO_TERMS = ['SBO:0000185', 'SBO:0000588', 'SBO:0000587',
                           'SBO:0000655', 'SBO:0000654', 'SBO:0000660',
                           'SBO:0000659', 'SBO:0000657', 'SBO:0000658']


# Read the MetaNetX shortlist to identify specific metabolite IDs across
# different namespaces.
with open_text(memote.support.data, "met_id_shortlist.json",
               encoding="utf-8") as file_handle:
    METANETX_SHORTLIST = pd.read_json(file_handle)

# Provide a compartment shortlist to identify specfic compartments whenever
# necessary.
COMPARTMENT_SHORTLIST = {
    'ce': ['cell envelope'],
    'c': ['cytoplasm', 'cytosol', 'default', 'in', 'intra cellular',
          'intracellular', 'intracellular region', 'intracellular space'],
    'er': ['endoplasmic reticulum'],
    'erm': ['endoplasmic reticulum membrane'],
    'e': ['extracellular', 'extraorganism', 'out', 'extracellular space',
          'extra organism', 'extra cellular', 'extra-organism'],
    'f': ['flagellum', 'bacterial-type flagellum'],
    'g': ['golgi', 'golgi apparatus'],
    'gm': ['golgi membrane'],
    'h': ['chloroplast'],
    'l': ['lysosome'],
    'im': ['mitochondrial intermembrane space'],
    'mm': ['mitochondrial membrane'],
    'm': ['mitochondrion', 'mitochondria'],
    'n': ['nucleus'],
    'p': ['periplasm', 'periplasmic space'],
    'x': ['peroxisome', 'glyoxysome'],
    'u': ['thylakoid'],
    'vm': ['vacuolar membrane'],
    'v': ['vacuole'],
    'w': ['cell wall'],
    's': ['eyespot', 'eyespot apparatus', 'stigma']}


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


@lrudecorator(size=2)
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
    the formula and/or annotation stays the same on both sides of the equation.

    A notable exception is transport via PTS, which also contains the following
    restriction:
    3. The transported metabolite(s) are transported into a compartment through
    the exchange of a phosphate.

    An example of tranport via PTS would be
    pep(c) + glucose(e) -> glucose-6-phosphate(c) + pyr(c)

    Reactions similar to transport via PTS (referred to as "modified transport
    reactions") follow a similar pattern:
    A(x) + B-R(y) -> A-R(y) + B(y)

    Such modified transport reactions can be detected, but only when a formula
    field exists for all metabolites in a particular reaction. If this is not
    the case, transport reactions are identified through annotations, which
    cannot detect modified tranport reactions.

    """
    transport_reactions = []
    transport_rxn_candidates = set(model.reactions) - set(model.exchanges) \
        - set(find_biomass_reaction(model))
    # Add all labeled transport reactions
    sbo_matches = set([rxn for rxn in transport_rxn_candidates if
                       rxn.annotation is not None and
                       'SBO' in rxn.annotation and
                       rxn.annotation['SBO'] in TRANSPORT_RXN_SBO_TERMS])
    if len(sbo_matches) > 0:
        transport_reactions += list(sbo_matches)
    # Find unlabeled transport reactions via formula or annotation checks
    for rxn in transport_rxn_candidates:
        # Check if metabolites have formula field
        rxn_mets = set([met.formula for met in rxn.metabolites])
        if (None not in rxn_mets) and (len(rxn_mets) != 0):
            if is_transport_reaction_formulae(rxn):
                transport_reactions.append(rxn)
        if is_transport_reaction_annotations(rxn):
            transport_reactions.append(rxn)

    return set(transport_reactions)


def is_transport_reaction_formulae(rxn):
    """
    Return boolean given if rxn is a transport reaction (from formulae).

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    rxn: cobra.Reaction
        The metabolic reaction under investigation.

    transport_reactions: list
        A list of all transport reactions.

    """
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
    elif sum(non_zero_array):
        return True


def is_transport_reaction_annotations(rxn):
    """
    Return boolean given if rxn is a transport reaction (from annotations).

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    rxn: cobra.Reaction
        The metabolic reaction under investigation.

    transport_reactions: list
        A list of all transport reactions.

    """
    reactants = set([(k, tuple(v)) for met in rxn.reactants
                     for k, v in iteritems(met.annotation)
                     if met.id is not "H" and k is not None and v is not None])
    products = set([(k, tuple(v)) for met in rxn.products
                    for k, v in iteritems(met.annotation)
                    if met.id is not "H" and k is not None and v is not None])
    # Find intersection between reactant annotations and
    # product annotations to find common metabolites between them,
    # satisfying the requirements for a transport reaction. Reactions such
    # as those involving oxidoreductases (where no net transport of
    # Hydrogen is occurring, but rather just an exchange of electrons or
    # charges effecting a change in protonation) are weeded out.
    transported_mets = reactants & products
    if len(transported_mets) > 0:
        return True


def find_converting_reactions(model, pair):
    """
    Find all reactions which convert a given metabolite pair.

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
    first = set(find_met_in_model(model, pair[0]))
    second = set(find_met_in_model(model, pair[1]))
    hits = list()
    for rxn in model.reactions:
        # FIXME: Use `set.issubset` much more idiomatic.
        if len(first & set(rxn.reactants)) > 0 and len(
                second & set(rxn.products)) > 0:
            hits.append(rxn)
        elif len(first & set(rxn.products)) > 0 and len(
                second & set(rxn.reactants)) > 0:
            hits.append(rxn)
    return frozenset(hits)


@lrudecorator(size=2)
def find_biomass_reaction(model):
    """
    Return a list of the biomass reaction(s) of the model.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns
    -------
    list of biomass reactions

    """
    sbo_matches = set([rxn for rxn in model.reactions if
                       rxn.annotation is not None and
                       'SBO' in rxn.annotation and
                       rxn.annotation['SBO'] == 'SBO:0000629'])

    if len(sbo_matches) > 0:
        return list(sbo_matches)

    buzzwords = ['biomass', 'growth', 'bof']

    buzzword_matches = set([rxn for rxn in model.reactions if any(
        string in rxn.id.lower() for string in buzzwords)])

    biomass_met = []
    for met in model.metabolites:
        if met.id.lower().startswith('biomass') or met.name.lower().startswith(
            'biomass'
        ):
            biomass_met.append(met)
    if biomass_met == 1:
        biomass_met_matches = set(
            biomass_met.reactions
        ) - set(model.exchanges)
    else:
        biomass_met_matches = set()

    return list(buzzword_matches | biomass_met_matches)


@lrudecorator(size=2)
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
    try:
        extracellular = find_compartment_id_in_model(model, 'e')
    except KeyError:
        extracellular = None
    demand_and_exchange_rxns = set(model.exchanges)
    return [rxn for rxn in demand_and_exchange_rxns
            if not rxn.reversibility and
            extracellular not in rxn.get_compartments()]


@lrudecorator(size=2)
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
    try:
        extracellular = find_compartment_id_in_model(model, 'e')
    except KeyError:
        extracellular = None
    demand_and_exchange_rxns = set(model.exchanges)
    return [rxn for rxn in demand_and_exchange_rxns
            if rxn.reversibility and
            extracellular not in rxn.get_compartments()]


@lrudecorator(size=2)
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
    try:
        extracellular = find_compartment_id_in_model(model, 'e')
    except KeyError:
        extracellular = None
    demand_and_exchange_rxns = set(model.exchanges)
    return [rxn for rxn in demand_and_exchange_rxns
            if extracellular in rxn.get_compartments()]


def find_interchange_biomass_reactions(model, biomass=None):
    """
    Return the set of all transport, boundary, and biomass reactions in a model.

    These reactions are incorporated in models simply for to allow
    metabolites into the correct compartments for vital system reactions to
    occur. As such, many tests do not look at these reactions.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    biomass : list or cobra.Reaction, optional
        A list of cobrapy biomass reactions

    """
    # exchanges in this case also refer to sink and demand reactions
    exchanges = set(model.exchanges)
    transporters = find_transport_reactions(model)
    if biomass is None:
        biomass = set(find_biomass_reaction(model))
    return exchanges | transporters | biomass


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
    for rxn in model.reactions:
        if rxn.reversibility:
            rxn.bounds = -1, 1
        else:
            rxn.bounds = 0, 1
    for exchange in model.exchanges:
        exchange.bounds = (0, 0)


def open_boundaries(model):
    """
    Return a copy of cobra model with all boundaries opened.

    Parameters
    ----------
    cobra.Model
        A cobra model with all boundary reactions opened.

    """
    for exchange in model.exchanges:
        exchange.bounds = (-1000, 1000)


def metabolites_per_compartment(model, compartment_id):
    """
    Identify all metabolites that belong to a given compartment.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model
    compartment_id : string
        Model specific compartment identifier.

    Returns
    -------
    list
        List of metabolites belonging to a given compartment.

    """
    return [met for met in model.metabolites
            if met.compartment == compartment_id]


def largest_compartment_id_met(model):
    """
    Return the ID of the compartment with the most metabolites.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model

    Returns
    -------
    string
        Compartment ID of the compartment with the most metabolites.

    """
    # Sort compartments by decreasing size and extract the largest two.
    candidate, second = sorted(
        ((c, len(metabolites_per_compartment(model, c)))
         for c in model.compartments), reverse=True, key=itemgetter(1))[:2]
    # Compare the size of the compartments.
    if candidate[1] == second[1]:
        raise RuntimeError("There is a tie for the largest compartment. "
                           "Compartment {} and {} have equal amounts of "
                           "metabolites.".format(candidate[0], second[0]))
    else:
        return candidate[0]


def find_compartment_id_in_model(model, compartment_id):
    """
    Identify a model compartment by looking up names in COMPARTMENT_SHORTLIST.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model
    compartment_id : string
        Memote internal compartment identifier used to access compartment name
        shortlist to look up potential compartment names.

    Returns
    -------
    string
        Compartment identifier in the model corresponding to compartment_id

    """
    if compartment_id not in COMPARTMENT_SHORTLIST.keys():
        raise KeyError("{} is not in the COMPARTMENT_SHORTLIST! Make sure "
                       "you typed the ID correctly, if yes, update the "
                       "shortlist manually.".format(compartment_id))

    if len(model.compartments) == 0:
        raise KeyError(
            "It was not possible to identify the "
            "compartment {}, since the "
            "model has no compartments at "
            "all.".format(COMPARTMENT_SHORTLIST[compartment_id][0])
        )

    if compartment_id in model.compartments.keys():
        return compartment_id

    for name in COMPARTMENT_SHORTLIST[compartment_id]:
        for c_id, c_name in model.compartments.items():
            if c_name.lower() == name:
                return c_id

    if compartment_id == 'c':
        return largest_compartment_id_met(model)


def find_met_in_model(model, mnx_id, compartment_id=None):
    """
    Identify metabolites in the model by looking up IDs in METANETX_SHORTLIST.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model
    mnx_id : string
        Memote internal MetaNetX metabolite identifier used to map between
        cross-references in the METANETX_SHORTLIST.
    compartment_id : string, optional
        ID of the specific compartment where the metabolites should be found.
        Defaults to returning matching metabolites from all compartments.

    Returns
    -------
    list of cobra.Metabolite

    """
    if mnx_id not in METANETX_SHORTLIST.columns:
        raise RuntimeError("{} is not in the MetaNetX Shortlist! Make sure "
                           "you typed the ID correctly, if yes, update the "
                           "shortlist by updating and re-running the script "
                           "generate_mnx_shortlists.py.".format(mnx_id))

    candidates = []
    regex = re.compile('^{}(_[a-zA-Z]+?)*?$'.format(mnx_id))
    if model.metabolites.query(regex):
        candidates = model.metabolites.query(regex)
    else:
        for value in METANETX_SHORTLIST[mnx_id]:
            if value:
                for ident in value:
                    regex = re.compile('^{}(_[a-zA-Z]+?)*?$'.format(ident))
                    if model.metabolites.query(regex, attribute='id'):
                        candidates.extend(
                            model.metabolites.query(regex, attribute='id'))

    if compartment_id is None:
        return candidates

    else:
        candidates_in_compartment = \
            [cand for cand in candidates if cand.compartment == compartment_id]

    if len(candidates_in_compartment) == 0:
        raise RuntimeError("It was not possible to identify "
                           "any metabolite in compartment {} corresponding to "
                           "the following MetaNetX identifier: {}."
                           "Make sure that a cross-reference to this ID in "
                           "the MetaNetX Database exists for your "
                           "identifier "
                           "namespace.".format(compartment_id, mnx_id))
    elif len(candidates_in_compartment) > 1:
        raise RuntimeError("It was not possible to uniquely identify "
                           "a single metabolite in compartment {} that "
                           "corresponds to the following MetaNetX "
                           "identifier: {}."
                           "Instead these candidates were found: {}."
                           "Check that metabolite compartment tags are "
                           "correct. Consider switching to a namespace scheme "
                           "where identifiers are truly "
                           "unique.".format(compartment_id,
                                            mnx_id,
                                            utils.get_ids(
                                                candidates_in_compartment
                                            ))
                           )
    else:
        return candidates_in_compartment


def find_objective_function(model):
    """
    Return reactions that are part of the objective function.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    return [rxn for rxn in model.reactions if rxn.objective_coefficient != 0]


def find_bounds(model):
    """
    Return the maximal and minimal bounds of the reactions of the model.

    Bounds can vary from model to model. Cobrapy defaults to (-1000, 1000) but
    this may not be the case for merged or autogenerated models. In these
    cases, this function is used to iterate over all the bounds of all the
    reactions and find the most extreme bound values in the model, which are
    then used as its default max and min bound values.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    bounds = [bound for rxn in model.reactions for bound in rxn.bounds]
    try:
        lower_bound = np.array(bounds[0::2]).min()
        upper_bound = np.array(bounds[1::2]).max()
        lower_bound = -np.amax([np.abs(lower_bound), np.abs(upper_bound)])
        upper_bound = np.amax([np.abs(lower_bound), np.abs(upper_bound)])
    except ValueError:
        lower_bound = -1000
        upper_bound = 1000

    if lower_bound != 0 and upper_bound != 0:
        return lower_bound, upper_bound
    else:
        return -1000, 1000
