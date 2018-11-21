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

from sys import version_info

from six import string_types


if version_info[:2] >= (3, 5):
    from equilibrator_api import Reaction, CompoundMatcher
    COMPOUND_MATCHER = CompoundMatcher()


def smallest_compound_id(kegg_ann_list):
    """
    Return an ascending list filtered to contain only KEGG compound IDs.

    KEGG IDs may map to compounds, drugs and glycans prefixed respectively
    with "C", "D", and "G" followed by at least 5 digits.

    Parameters
    ----------
    kegg_ann_list: list
        A list of mixed KEGG IDs.

    """
    only_compound_ids = [x for x in kegg_ann_list if x.startswith("C")]
    only_compound_ids.sort(key=lambda x: int(x.lstrip('C')))
    return only_compound_ids


def get_metabolite_mapping(reactions):
    """
    Return dictionary that maps model IDs to KEGG compound IDs if available.

    First see if there is an unambiguous mapping to a single KEGG compound ID
    provided with the model. If not, check if there is any KEGG compound ID in
    a list of mappings. KEGG IDs may map to compounds, drugs and glycans. KEGG
    compound IDs are sorted so we keep the lowest that is there. If none of
    this works try mapping to KEGG via the CompoundMatcher by the name of the
    metabolite. If the metabolite cannot be mapped at all we simply map it back
    to its own ID.
    """
    mets = set([met for rxn in reactions for met in rxn.metabolites])
    kegg_mapping_dict = {}
    for met in mets:
        kegg_ann_id = met.annotation.get("kegg.compound")
        if isinstance(kegg_ann_id, string_types) and "C" in kegg_ann_id:
            kegg_mapping_dict[met.id] = kegg_ann_id
        elif type(kegg_ann_id) is list and any("C" in s for s in kegg_ann_id):
            kegg_mapping_dict[met.id] = smallest_compound_id(kegg_ann_id)[0]
        elif not met.name:
            kegg_mapping_dict[met.id] = met.id
        else:
            try:
                df = COMPOUND_MATCHER.match(getattr(met, "name", None))
                kegg_match_id = df['CID'].iloc[0]
                kegg_mapping_dict[met.id] = kegg_match_id
            except Exception:
                kegg_mapping_dict[met.id] = met.id
    return kegg_mapping_dict


def get_equilibrator_reaction_string(reaction, mapping_dict):
    """
    Return a reaction string with at least a partial mapping to KEGG IDs.

    Parameters
    ----------
    reaction: cobra.Reaction
        The metabolic reaction under investigation.
    mapping_dict: dict
        A simple dictionary which provides a 1:1 mapping of metabolite IDs in
        the model to KEGG compound IDs if available.

    """
    kegg_rxn_list = reaction.reaction.split(" ")

    for index, met_id in enumerate(kegg_rxn_list):
        try:
            kegg_rxn_list[index] = mapping_dict[met_id]
        except KeyError:
            pass
    kegg_rxn = ' '.join(kegg_rxn_list)
    # COBRApy reaction strings seem to use slightly different arrows which
    # are not recognized by the eQuilibrator-API
    return kegg_rxn.replace('-->', '->').replace('<--', '<-')


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
    incomplete_mapping = list()
    problematic_calculation = list()
    incorrect_reversibility = list()
    unbalanced = list()
    mapping_dict = get_metabolite_mapping(reactions)

    for rxn in reactions:
        try:
            eq_rxn = Reaction.parse_formula(
                get_equilibrator_reaction_string(rxn, mapping_dict)
            )
        except Exception:
            incomplete_mapping.append(rxn)
            continue
        if eq_rxn.check_full_reaction_balancing():
            try:
                ln_rev_index = eq_rxn.reversibility_index()
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
