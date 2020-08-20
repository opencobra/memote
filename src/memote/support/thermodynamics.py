# -*- coding: utf-8 -*-

# Copyright 2018 Novo Nordisk Foundation Center for Biosustainability,
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

"""Supporting functions for checks requiring the eQuilibrator API."""

from __future__ import absolute_import

import logging
from collections import Iterable, defaultdict
from sys import version_info

from six import iteritems, string_types


if version_info[:2] >= (3, 5):
    from equilibrator_api import CompoundMatcher, Reaction

    compound_matcher = CompoundMatcher()


logger = logging.getLogger(__name__)


def get_smallest_compound_id(compounds_identifiers):
    """
    Return the smallest KEGG compound identifier from a list.

    KEGG identifiers may map to compounds, drugs or glycans prefixed
    respectively with "C", "D", and "G" followed by at least 5 digits. We
    choose the lowest KEGG identifier with the assumption that several
    identifiers are due to chirality and that the lower one represents the
    more common form.

    Parameters
    ----------
    compounds_identifiers : list
        A list of mixed KEGG identifiers.

    Returns
    -------
    str
        The KEGG compound identifier with the smallest number.

    Raises
    ------
    ValueError
        When compound_identifiers contains no KEGG compound identifiers.

    """
    return min(
        (c for c in compounds_identifiers if c.startswith("C")),
        key=lambda c: int(c[1:]),
    )


def map_metabolite2kegg(metabolite):
    """
    Return a KEGG compound identifier for the metabolite if it exists.

    First see if there is an unambiguous mapping to a single KEGG compound ID
    provided with the model. If not, check if there is any KEGG compound ID in
    a list of mappings. KEGG IDs may map to compounds, drugs and glycans. KEGG
    compound IDs are sorted so we keep the lowest that is there. If none of
    this works try mapping to KEGG via the CompoundMatcher by the name of the
    metabolite. If the metabolite cannot be mapped at all we simply map it back
    to its own ID.

    Parameters
    ----------
    metabolite : cobra.Metabolite
        The metabolite to be mapped to its KEGG compound identifier.

    Returns
    -------
    None
        If the metabolite could not be mapped.
    str
        The smallest KEGG compound identifier that was found.

    """
    logger.debug("Looking for KEGG compound identifier for %s.", metabolite.id)
    kegg_annotation = metabolite.annotation.get("kegg.compound")
    if kegg_annotation is None:
        # TODO (Moritz Beber): Currently name matching is very slow and
        #  inaccurate. We disable it until there is a better solution.
        # if metabolite.name:
        #     # The compound matcher uses regular expression and chokes
        #     # with a low level error on `[` in the name, for example.
        #     df = compound_matcher.match(metabolite.name)
        #     try:
        #         return df.loc[df["score"] > threshold, "CID"].iat[0]
        #     except (IndexError, AttributeError):
        #         logger.warning(
        #             "Could not match the name %r to any kegg.compound "
        #             "annotation for metabolite %s.",
        #             metabolite.name, metabolite.id
        #         )
        #         return
        # else:
        logger.warning("No kegg.compound annotation for metabolite %s.", metabolite.id)
        return
    if isinstance(kegg_annotation, string_types) and kegg_annotation.startswith("C"):
        return kegg_annotation
    elif isinstance(kegg_annotation, Iterable):
        try:
            return get_smallest_compound_id(kegg_annotation)
        except ValueError:
            return
    logger.warning(
        "No matching kegg.compound annotation for metabolite %s.", metabolite.id
    )
    return


def translate_reaction(reaction, metabolite_mapping):
    """
    Return a mapping from KEGG compound identifiers to coefficients.

    Parameters
    ----------
    reaction : cobra.Reaction
        The reaction whose metabolites are to be translated.
    metabolite_mapping : dict
        An existing mapping from cobra.Metabolite to KEGG compound identifier
        that may already contain the metabolites in question or will have to be
        extended.

    Returns
    -------
    dict
        The stoichiometry of the reaction given as a mapping from metabolite
        KEGG identifier to coefficient.

    """
    # Transport reactions where the same metabolite occurs in different
    # compartments should have been filtered out but just to be sure, we add
    # coefficients in the mapping.
    stoichiometry = defaultdict(float)
    for met, coef in iteritems(reaction.metabolites):
        kegg_id = metabolite_mapping.setdefault(met, map_metabolite2kegg(met))
        if kegg_id is None:
            continue
        stoichiometry[kegg_id] += coef
    return dict(stoichiometry)


def find_thermodynamic_reversibility_index(reactions):
    u"""
    Return the reversibility index of the given reactions.

    To determine the reversibility index, we calculate
    the reversibility index ln_gamma (see [1]_ section 3.5) of each reaction
    using the eQuilibrator API [2]_.

    Parameters
    ----------
        reactions: list of cobra.Reaction
            A list of reactions for which to calculate the reversibility index.

    Returns
    -------
    tuple
        list of cobra.Reaction, index pairs
            A list of pairs of reactions and their reversibility indexes.
        list of cobra.Reaction
            A list of reactions which contain at least one metabolite that
            could not be mapped to KEGG on the basis of its annotation.
        list of cobra.Reaction
            A list of reactions for which it is not possible to calculate the
            standard change in Gibbs free energy potential. Reasons of failure
            include that participating metabolites cannot be broken down with
            the group contribution method.
        list of cobra.Reaction
            A list of reactions that are not chemically or redox balanced.


    References
    ----------
    .. [1] Elad Noor, Arren Bar-Even, Avi Flamholz, Yaniv Lubling, Dan Davidi,
           Ron Milo; An integrated open framework for thermodynamics of
           reactions that combines accuracy and coverage, Bioinformatics,
           Volume 28, Issue 15, 1 August 2012, Pages 2037–2044,
           https://doi.org/10.1093/bioinformatics/bts317
    .. [2] https://pypi.org/project/equilibrator-api/

    """
    incomplete_mapping = []
    problematic_calculation = []
    reversibility_indexes = []
    unbalanced = []
    metabolite_mapping = {}

    for rxn in reactions:
        stoich = translate_reaction(rxn, metabolite_mapping)
        if len(stoich) < len(rxn.metabolites):
            incomplete_mapping.append(rxn)
            continue
        try:
            # Remove protons from stoichiometry.
            if "C00080" in stoich:
                del stoich["C00080"]
            eq_rxn = Reaction(stoich, rxn.id)
        except KeyError:
            incomplete_mapping.append(rxn)
            continue
        if eq_rxn.check_full_reaction_balancing():
            try:
                ln_rev_index = eq_rxn.reversibility_index()
            # TODO (Moritz Beber): Which exceptions can we expect here?
            except Exception:
                problematic_calculation.append(rxn)
                continue
            reversibility_indexes.append((rxn, ln_rev_index))
        else:
            unbalanced.append(rxn)
    reversibility_indexes.sort(key=lambda p: abs(p[1]), reverse=True)
    return (
        reversibility_indexes,
        incomplete_mapping,
        problematic_calculation,
        unbalanced,
    )
