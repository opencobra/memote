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
from operator import attrgetter, itemgetter

import cobra
import numpy as np
import pandas as pd
from cobra.exceptions import Infeasible
from cobra.medium.boundary_types import find_boundary_types
from importlib_resources import open_text
from pylru import lrudecorator
from six import iteritems, itervalues

import memote.support.data
import memote.utils as utils


LOGGER = logging.getLogger(__name__)

TRANSPORT_RXN_SBO_TERMS = [
    "SBO:0000185",
    "SBO:0000588",
    "SBO:0000587",
    "SBO:0000655",
    "SBO:0000654",
    "SBO:0000660",
    "SBO:0000659",
    "SBO:0000657",
    "SBO:0000658",
]


# Read the MetaNetX shortlist to identify specific metabolite IDs across
# different namespaces.
with open_text(
    memote.support.data, "met_id_shortlist.json", encoding="utf-8"
) as file_handle:
    METANETX_SHORTLIST = pd.read_json(file_handle)


# Provide a compartment shortlist to identify specific compartments whenever
# necessary.
COMPARTMENT_SHORTLIST = {
    "ce": ["cell envelope"],
    "c": [
        "cytoplasm",
        "cytosol",
        "default",
        "in",
        "intra cellular",
        "intracellular",
        "intracellular region",
        "intracellular space",
    ],
    "er": ["endoplasmic reticulum"],
    "erm": ["endoplasmic reticulum membrane"],
    "e": [
        "extracellular",
        "extraorganism",
        "out",
        "extracellular space",
        "extra organism",
        "extra cellular",
        "extra-organism",
    ],
    "f": ["flagellum", "bacterial-type flagellum"],
    "g": ["golgi", "golgi apparatus"],
    "gm": ["golgi membrane"],
    "h": ["chloroplast"],
    "l": ["lysosome"],
    "im": ["mitochondrial intermembrane space"],
    "mm": ["mitochondrial membrane"],
    "m": ["mitochondrion", "mitochondria"],
    "n": ["nucleus"],
    "p": ["periplasm", "periplasmic space"],
    "x": ["peroxisome", "glyoxysome"],
    "u": ["thylakoid"],
    "vm": ["vacuolar membrane"],
    "v": ["vacuole"],
    "w": ["cell wall"],
    "s": ["eyespot", "eyespot apparatus", "stigma"],
}


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
            element_dist[met.compartment] = {
                k: v * rxn.metabolites[met] for (k, v) in iteritems(met.elements)
            }
        else:
            x = {k: v * rxn.metabolites[met] for (k, v) in iteritems(met.elements)}
            y = element_dist[met.compartment]
            element_dist[met.compartment] = {
                k: x.get(k, 0) + y.get(k, 0) for k in set(x) | set(y)
            }
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
    the exchange of a phosphate group.

    An example of transport via PTS would be
    pep(c) + glucose(e) -> glucose-6-phosphate(c) + pyr(c)

    Reactions similar to transport via PTS (referred to as "modified transport
    reactions") follow a similar pattern:
    A(x) + B-R(y) -> A-R(y) + B(y)

    Such modified transport reactions can be detected, but only when a formula
    field exists for all metabolites in a particular reaction. If this is not
    the case, transport reactions are identified through annotations, which
    cannot detect modified transport reactions.

    """
    transport_reactions = []
    transport_rxn_candidates = (
        set(model.reactions) - set(model.boundary) - set(find_biomass_reaction(model))
    )
    transport_rxn_candidates = set(
        [rxn for rxn in transport_rxn_candidates if len(rxn.compartments) >= 2]
    )
    # Add all labeled transport reactions
    sbo_matches = set(
        [
            rxn
            for rxn in transport_rxn_candidates
            if rxn.annotation is not None
            and "sbo" in rxn.annotation
            and rxn.annotation["sbo"] in TRANSPORT_RXN_SBO_TERMS
        ]
    )
    if len(sbo_matches) > 0:
        transport_reactions += list(sbo_matches)
    # Find unlabeled transport reactions via formula or annotation checks
    for rxn in transport_rxn_candidates:
        # Check if metabolites have formula field
        rxn_mets = set([met.formula for met in rxn.metabolites])
        if (None not in rxn_mets) and (len(rxn_mets) != 0):
            if is_transport_reaction_formulae(rxn):
                transport_reactions.append(rxn)
        elif is_transport_reaction_annotations(rxn):
            transport_reactions.append(rxn)

    return set(transport_reactions)


def is_transport_reaction_formulae(rxn):
    """
    Return boolean if a reaction is a transport reaction (from formulae).

    Parameters
    ----------
    rxn: cobra.Reaction
        The metabolic reaction under investigation.

    """
    # Collecting criteria to classify transporters by.
    rxn_reactants = set([met.formula for met in rxn.reactants])
    rxn_products = set([met.formula for met in rxn.products])
    # Looking for formulas that stay the same on both side of the reaction.
    transported_mets = [formula for formula in rxn_reactants if formula in rxn_products]
    # Collect information on the elemental differences between
    # compartments in the reaction.
    delta_dicts = find_transported_elements(rxn)
    non_zero_array = [v for (k, v) in iteritems(delta_dicts) if v != 0]
    # Excluding reactions such as oxidoreductases where no net
    # transport of Hydrogen is occurring, but rather just an exchange of
    # electrons or charges effecting a change in protonation.
    if set(transported_mets) != set("H") and list(delta_dicts.keys()) == ["H"]:
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
    Return boolean if a reaction is a transport reaction (from annotations).

    Parameters
    ----------
    rxn: cobra.Reaction
        The metabolic reaction under investigation.

    """
    reactants = set(
        [
            (k, tuple(v))
            for met in rxn.reactants
            for k, v in iteritems(met.annotation)
            if met.id != "H" and k is not None and k != "sbo" and v is not None
        ]
    )
    products = set(
        [
            (k, tuple(v))
            for met in rxn.products
            for k, v in iteritems(met.annotation)
            if met.id != "H" and k is not None and k != "sbo" and v is not None
        ]
    )
    # Find intersection between reactant annotations and
    # product annotations to find common metabolites between them,
    # satisfying the requirements for a transport reaction. Reactions such
    # as those involving oxidoreductases (where no net transport of
    # Hydrogen is occurring, but rather just an exchange of electrons or
    # charges effecting a change in protonation) are excluded.
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
        if len(first & set(rxn.reactants)) > 0 and len(second & set(rxn.products)) > 0:
            hits.append(rxn)
        elif (
            len(first & set(rxn.products)) > 0 and len(second & set(rxn.reactants)) > 0
        ):
            hits.append(rxn)
    return frozenset(hits)


def filter_sbo_term(component, sbo_term):
    """
    Return true if the component is annotated with the given SBO term.

    Parameters
    ----------
    component : cobra.Reaction or cobra.Metabolite
        Either a reaction or a metabolite instance.
    sbo_term : str
        The term for either biomass production or biomass.

    """
    return component.annotation.get("sbo", "") == sbo_term


def filter_match_name(component, buzzwords):
    """
    Return whether the component's name matches a biomass description.

    Notes
    -----
    Regex patterns are necessary here to prevent, for example, 'non-growth' from
    matching.

    Parameters
    ----------
    component : cobra.Reaction or cobra.Metabolite
        Either a reaction or a metabolite instance.
    buzzwords : collection of regex patterns
        One or more regular expression patterns to match against the name of the
        component.

    Returns
    -------
    bool
        True if there was any match at all.

    """
    if component.name is None:
        return False
    name = component.name.lower()
    return any(b.match(name) for b in buzzwords)


def filter_identifier(component, buzzwords):
    """
    Return whether the component's identifier contains a biomass description.

    Notes
    -----
    We check substring presence here because identifiers are often prefixed with
    ``M_`` or ``R_``.

    Parameters
    ----------
    component : cobra.Reaction or cobra.Metabolite
        Either a reaction or a metabolite instance.
    buzzwords : iterable of str
        One or more buzzwords that the identifier should contain.

    Returns
    -------
    bool
        True if there was any match at all.

    """
    identifier = component.id.lower()
    return any(b in identifier for b in buzzwords)


@lrudecorator(size=2)
def find_biomass_reaction(model):
    """
    Return a list of the biomass reaction(s) of the model.

    Identifiy possible biomass reactions using multiple steps:
    1. Look for candidate reactions that include the SBO term ``SBO:0000629``
    for biomass production,
    2. the 'buzzwords' biomass, growth, and bof in reaction names
    and identifiers,
    3. reactions that involve a metabolite with the SBO term ``SBO:0000649``
    for biomass,
    4. or reactions that involve a metabolite whose name or identifier
    contains the 'buzzword' biomass.
    Return identified reactions excluding any boundary reactions.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns
    -------
    list
        Identified biomass reactions (if any).

    """
    boundary = frozenset(model.boundary)

    # 1.
    candidates = {r for r in model.reactions if filter_sbo_term(r, "SBO:0000629")}
    candidates.difference_update(boundary)
    if candidates:
        return sorted(candidates, key=attrgetter("id"))

    # 2.
    name_buzzwords = (
        re.compile(r"\bbiomass"),
        re.compile(r"\bgrowth"),
        re.compile(r"bof"),
    )
    id_buzzwords = ("biomass",)
    candidates = {
        r
        for r in model.reactions
        if filter_match_name(r, name_buzzwords) or filter_identifier(r, id_buzzwords)
    }
    candidates.difference_update(boundary)
    if candidates:
        return sorted(candidates, key=attrgetter("id"))

    # 3.
    name_buzzwords = (re.compile(r"\bbiomass"),)
    id_buzzwords = ("biomass",)
    sbo_metabolites = {
        m for m in model.metabolites if filter_sbo_term(m, "SBO:0000649")
    }
    metabolites = {
        m
        for m in model.metabolites
        if filter_match_name(m, name_buzzwords) or filter_identifier(m, id_buzzwords)
    }
    # Many metabolites may match 'SBO:0000649', we filter those further by name
    # and ID.
    sbo_metabolites.intersection_update(metabolites)
    if sbo_metabolites:
        candidates = {r for m in sbo_metabolites for r in m.reactions}
        candidates.difference_update(boundary)
        if candidates:
            return sorted(candidates, key=attrgetter("id"))

    # 4.
    candidates = {r for m in metabolites for r in m.reactions}
    candidates.difference_update(boundary)
    if candidates:
        return sorted(candidates, key=attrgetter("id"))

    return []


@lrudecorator(size=2)
def find_demand_reactions(model):
    u"""
    Return a list of demand reactions.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

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
        extracellular = find_compartment_id_in_model(model, "e")
    except KeyError:
        extracellular = None
    return find_boundary_types(model, "demand", extracellular)


@lrudecorator(size=2)
def find_sink_reactions(model):
    u"""
    Return a list of sink reactions.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

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
        extracellular = find_compartment_id_in_model(model, "e")
    except KeyError:
        extracellular = None
    return find_boundary_types(model, "sink", extracellular)


@lrudecorator(size=2)
def find_exchange_rxns(model):
    u"""
    Return a list of exchange reactions.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

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
        extracellular = find_compartment_id_in_model(model, "e")
    except KeyError:
        extracellular = None
    return find_boundary_types(model, "exchange", extracellular)


def find_interchange_biomass_reactions(model, biomass=None):
    """
    Return the set of all transport, boundary, and biomass reactions.

    These reactions are either pseudo-reactions, or incorporated to allow
    metabolites to pass between compartments. Some tests focus on purely
    metabolic reactions and hence exclude this set.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    biomass : list or cobra.Reaction, optional
        A list of cobrapy biomass reactions.

    """
    boundary = set(model.boundary)
    transporters = find_transport_reactions(model)
    if biomass is None:
        biomass = set(find_biomass_reaction(model))
    return boundary | transporters | biomass


def run_fba(model, rxn_id, direction="max", single_value=True):
    """
    Return the solution of an FBA to a set objective function.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    rxn_id : string
        A string containing the reaction ID of the desired FBA objective.
    direction: string
        A string containing either "max" or "min" to specify the direction
        of the desired FBA objective function.
    single_value: boolean
        Indicates whether the results for all reactions are gathered from the
        solver, or only the result for the objective value.

    Returns
    -------
    cobra.solution
        The cobra solution object for the corresponding FBA problem.

    """
    model.objective = model.reactions.get_by_id(rxn_id)
    model.objective_direction = direction
    if single_value:
        return model.slim_optimize()
    else:
        try:
            solution = model.optimize()
            return solution
        except Infeasible:
            return np.nan


def get_biomass_flux(model: cobra.Model, rxn_id: str) -> float:
    """
    Compute the maximal objective value.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    rxn_id : string
        A string containing the reaction ID of the desired FBA objective.

    Returns
    -------
    float
        The objective value which takes infeasibility and solver tolerances into
        account.

    """
    model.objective = model.reactions.get_by_id(rxn_id)
    model.objective_direction = "max"
    flux = model.slim_optimize(error_value=0.0)
    if abs(flux) < model.tolerance:
        return 0.0
    else:
        return flux


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
        The metabolic model under investigation.

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
    for boundary in model.boundary:
        boundary.bounds = (0, 0)


def open_exchanges(model):
    """
    Open all exchange reactions.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    for rxn in model.exchanges:
        rxn.bounds = (-1000, 1000)


def open_boundaries(model):
    """
    Open all boundary reactions.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    for boundary in model.boundary:
        boundary.bounds = (-1000, 1000)


def metabolites_per_compartment(model, compartment_id):
    """
    Identify all metabolites that belong to a given compartment.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    compartment_id : string
        Model specific compartment identifier.

    Returns
    -------
    list
        List of metabolites belonging to a given compartment.

    """
    return [met for met in model.metabolites if met.compartment == compartment_id]


def largest_compartment_id_met(model):
    """
    Return the ID of the compartment with the most metabolites.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns
    -------
    string
        Compartment ID of the compartment with the most metabolites.

    """
    # Sort compartments by decreasing size and extract the largest two.
    candidate, second = sorted(
        ((c, len(metabolites_per_compartment(model, c))) for c in model.compartments),
        reverse=True,
        key=itemgetter(1),
    )[:2]
    # Compare the size of the compartments.
    if candidate[1] == second[1]:
        raise RuntimeError(
            "There is a tie for the largest compartment. "
            "Compartment {} and {} have equal amounts of "
            "metabolites.".format(candidate[0], second[0])
        )
    else:
        return candidate[0]


def find_compartment_id_in_model(model, compartment_id):
    """
    Identify a model compartment by looking up names in COMPARTMENT_SHORTLIST.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    compartment_id : string
        Memote internal compartment identifier used to access compartment name
        shortlist to look up potential compartment names.

    Returns
    -------
    string
        Compartment identifier in the model corresponding to compartment_id.

    """
    if compartment_id not in COMPARTMENT_SHORTLIST.keys():
        raise KeyError(
            "{} is not in the COMPARTMENT_SHORTLIST! Make sure "
            "you typed the ID correctly, if yes, update the "
            "shortlist manually.".format(compartment_id)
        )

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

    if compartment_id == "c":
        return largest_compartment_id_met(model)


def find_met_in_model(model, mnx_id, compartment_id=None):
    """
    Return specific metabolites by looking up IDs in METANETX_SHORTLIST.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    mnx_id : string
        Memote internal MetaNetX metabolite identifier used to map between
        cross-references in the METANETX_SHORTLIST.
    compartment_id : string, optional
        ID of the specific compartment where the metabolites should be found.
        Defaults to returning matching metabolites from all compartments.

    Returns
    -------
    list
        cobra.Metabolite(s) matching the mnx_id.

    """

    def compare_annotation(annotation):
        """
        Return annotation IDs that match to METANETX_SHORTLIST references.

        Compares the set of METANETX_SHORTLIST references for a given mnx_id
        and the annotation IDs stored in a given annotation dictionary.
        """
        query_values = set(utils.flatten(annotation.values()))
        ref_values = set(utils.flatten(METANETX_SHORTLIST[mnx_id]))
        return query_values & ref_values

    # Make sure that the MNX ID we're looking up exists in the metabolite
    # shortlist.
    if mnx_id not in METANETX_SHORTLIST.columns:
        raise ValueError(
            "{} is not in the MetaNetX Shortlist! Make sure "
            "you typed the ID correctly, if yes, update the "
            "shortlist by updating and re-running the script "
            "generate_mnx_shortlists.py.".format(mnx_id)
        )
    candidates = []
    # The MNX ID used in the model may or may not be tagged with a compartment
    # tag e.g. `MNXM23141_c` vs. `MNXM23141`, which is tested with the
    # following regex.
    # If the MNX ID itself cannot be found as an ID, we try all other
    # identifiers that are provided by our shortlist of MetaNetX' mapping
    # table.
    regex = re.compile("^{}(_[a-zA-Z0-9]+)?$".format(mnx_id))
    if model.metabolites.query(regex):
        candidates = model.metabolites.query(regex)
    elif model.metabolites.query(compare_annotation, attribute="annotation"):
        candidates = model.metabolites.query(compare_annotation, attribute="annotation")
    else:
        for value in METANETX_SHORTLIST[mnx_id]:
            if value:
                for ident in value:
                    regex = re.compile("^{}(_[a-zA-Z0-9]+)?$".format(ident))
                    if model.metabolites.query(regex, attribute="id"):
                        candidates.extend(
                            model.metabolites.query(regex, attribute="id")
                        )

    # Return a list of all possible candidates if no specific compartment ID
    # is provided.
    # Otherwise, just return the candidate in one specific compartment. Raise
    # an exception if there are more than one possible candidates for a given
    # compartment.
    if compartment_id is None:
        print("compartment_id = None?")
        return candidates
    else:
        candidates_in_compartment = [
            cand for cand in candidates if cand.compartment == compartment_id
        ]

    if len(candidates_in_compartment) == 0:
        raise RuntimeError(
            "It was not possible to identify "
            "any metabolite in compartment {} corresponding to "
            "the following MetaNetX identifier: {}."
            "Make sure that a cross-reference to this ID in "
            "the MetaNetX Database exists for your "
            "identifier "
            "namespace.".format(compartment_id, mnx_id)
        )
    elif len(candidates_in_compartment) > 1:
        raise RuntimeError(
            "It was not possible to uniquely identify "
            "a single metabolite in compartment {} that "
            "corresponds to the following MetaNetX "
            "identifier: {}."
            "Instead these candidates were found: {}."
            "Check that metabolite compartment tags are "
            "correct. Consider switching to a namespace scheme "
            "where identifiers are truly "
            "unique.".format(
                compartment_id, mnx_id, utils.get_ids(candidates_in_compartment)
            )
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


@lrudecorator(size=2)
def find_bounds(model):
    """
    Return the median upper and lower bound of the metabolic model.

    Bounds can vary from model to model. Cobrapy defaults to (-1000, 1000) but
    this may not be the case for merged or autogenerated models. In these
    cases, this function is used to iterate over all the bounds of all the
    reactions and find the median bound values in the model, which are
    then used as the 'most common' bounds.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    lower_bounds = np.asarray([rxn.lower_bound for rxn in model.reactions], dtype=float)
    upper_bounds = np.asarray([rxn.upper_bound for rxn in model.reactions], dtype=float)
    lower_bound = np.nanmedian(lower_bounds[lower_bounds != 0.0])
    upper_bound = np.nanmedian(upper_bounds[upper_bounds != 0.0])
    if np.isnan(lower_bound):
        LOGGER.warning("Could not identify a median lower bound.")
        lower_bound = -1000.0
    if np.isnan(upper_bound):
        LOGGER.warning("Could not identify a median upper bound.")
        upper_bound = 1000.0
    return lower_bound, upper_bound
