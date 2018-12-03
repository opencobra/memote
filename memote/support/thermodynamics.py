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
    from equilibrator_api import Reaction, CompoundMatcher
    compound_matcher = CompoundMatcher()


logger = logging.getLogger(__name__)


def get_smallest_compound_id(compounds_identifiers):
    """
    Return the smallest KEGG compound identifier from a list.

    KEGG identifiers may map to compounds, drugs or glycans prefixed
    respectively with "C", "D", and "G" followed by at least 5 digits.

    Parameters
    ----------
    compounds_identifiers : list
        A list of mixed KEGG identifiers.

    Returns
    -------
    str
        The KEGG compound identifier with the smallest number.

    """
    return min((c for c in compounds_identifiers if c.startswith("C")),
               key=lambda c: int(c[1:]))


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

    Returns
    -------
    str

    """
    kegg_annotation = metabolite.annotation.get("kegg.compound")
    if kegg_annotation is None:
        logger.warning("No kegg.compound annotation for metabolite %s.",
                       metabolite.id)
        return
    if isinstance(kegg_annotation, string_types) and \
            kegg_annotation.startswith("C"):
        return kegg_annotation
    elif isinstance(kegg_annotation, Iterable):
        try:
            return get_smallest_compound_id(kegg_annotation)
        except ValueError:
            return
    elif metabolite.name:
        try:
            df = compound_matcher.match(metabolite.name)
        # TODO: What kind of exception?
        except Exception:
            logger.warning(
                "Could not match the name %r to any kegg.compound "
                "annotation for metabolite %s.",
                metabolite.name, metabolite.id
            )
        else:
            # TODO: Table might not exist?
            return df['CID'].iloc[0]
    else:
        logger.warning(
            "No matching kegg.compound annotation for metabolite %s.",
            metabolite.id
        )
    return


def translate_reaction(reaction, metabolite_mapping):
    """
    Return a mapping from KEGG compound identifiers to coefficients.

    Parameters
    ----------
    reaction : cobra.Reaction
    metabolite_mapping : dict

    Returns
    -------
    dict
        The stoichiometry of a reaction given as a mapping from metabolite
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
    return stoichiometry


def find_incorrect_thermodynamic_reversibility(reactions, ln_gamma=3):
    u"""
    Return reactions whose reversibilities do not agree with thermodynamics.

    This function checks if the reversibility attribute of each reaction
    in a list of cobrapy reactions agrees with a thermodynamics-based
    calculation of the reversibility. To determine reversibility we calculate
    the reversibility index ln_gamma (see [1]_ section 3.5) of each reaction
    using the eQuilibrator API [2]_. The default cutoff for ln_gamma
    "corresponds to allowing concentrations to span three orders of magnitude
    around 100 μM (~3 μM—3 mM)" at "pH = 7, I = 0.1 M and T = 298 K" (see [1]_
    supplement section 3). Here pH denotes the negative base 10 logarithm of
    the activity of the hydrogen ion i.e. a measure of acidity/ basicity of an
    aqueous solution, I denotes the molar ionic strength which is a measure of
    the concentration of ions in a solution, lastly, T denotes the
    thermodynamic temperature also called absolute temperature measured in
    Kelvin.

    Parameters
    ----------
        reactions: list of cobra.Reactions
            A list of reactions to be checked for agreement with
            thermodynamics-based calculations of reversibility.
        ln_gamma: integer
            Log-scale, symmetric range of metabolite concentrations around the
            assumed average of 100 µM. A threshold of 3 means that a
            reaction is considered irreversible if the concentration of an
            individual metabolite would have to change more than three orders
            of magnitude i.e. from 3 µM to 3 mM to reverse the direction of
            flux.

    Returns
    -------
        incorrect_reversibility: list of cobra.Reactions
            A list of reactions whose reversibility does not agree
            with thermodynamic calculation.
        incomplete_mapping: list of cobra.Reactions
            A list of reactions which contain at least one metabolite that
            could not be mapped to KEGG on the basis of its annotation or name.
        problematic_calculation: list of cobra.Reactions
            A list of reactions for which it is not possible to calculate the
            standard change in Gibbs potential. Reasons of failure include that
            participating metabolites cannot be broken down with the group
            contribution method.
        unbalanced: list of cobra.Reactions
            A list of reactions that are not chemically or redox balanced.


    References
    ----------
    .. [1] Elad Noor, Arren Bar-Even, Avi Flamholz, Yaniv Lubling, Dan Davidi,
           Ron Milo; An integrated open framework for thermodynamics of
           reactions that combines accuracy and coverage, Bioinformatics,
           Volume 28, Issue 15, 1 August 2012, Pages 2037–2044,
           https://doi.org/10.1093/bioinformatics/bts317
    .. [2] https://gitlab.com/elad.noor/equilibrator-api/tree/master

    """
    incomplete_mapping = []
    problematic_calculation = []
    incorrect_reversibility = []
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
            # TODO: Which exceptions can we expect here?
            except Exception:
                problematic_calculation.append(rxn)
                continue
            if (ln_rev_index < ln_gamma) != rxn.reversibility:
                incorrect_reversibility.append(rxn)
            else:
                continue
        else:
            unbalanced.append(rxn)

    return(incorrect_reversibility, incomplete_mapping,
           problematic_calculation, unbalanced)
