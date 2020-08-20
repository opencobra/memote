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

"""Supporting functions for basic checks performed on the model object."""

from __future__ import absolute_import, division

import logging
from itertools import combinations

from cobra.medium import find_external_compartment
from pylru import lrudecorator

import memote.support.helpers as helpers
from memote.support.gpr_helpers import find_top_level_complex
from memote.utils import filter_none


__all__ = ("check_metabolites_formula_presence",)


LOGGER = logging.getLogger(__name__)


def check_metabolites_formula_presence(model):
    """Return the list of model metabolites that have no associated formula."""
    return [met for met in model.metabolites if met.formula is None]


def check_metabolites_charge_presence(model):
    """Return the list of model metabolites that have no associated charge."""
    return [met for met in model.metabolites if met.charge is None]


def check_gene_protein_reaction_rule_presence(model):
    """Return the list of model reactions that have no associated gene rule."""
    return [rxn for rxn in model.reactions if not rxn.gene_reaction_rule]


def find_nonzero_constrained_reactions(model):
    """Return list of reactions with non-zero, non-maximal bounds."""
    lower_bound, upper_bound = helpers.find_bounds(model)
    return [
        rxn
        for rxn in model.reactions
        if 0 > rxn.lower_bound > lower_bound or 0 < rxn.upper_bound < upper_bound
    ]


def find_zero_constrained_reactions(model):
    """Return list of reactions that are constrained to zero flux."""
    return [
        rxn for rxn in model.reactions if rxn.lower_bound == 0 and rxn.upper_bound == 0
    ]


def find_irreversible_reactions(model):
    """Return list of reactions that are irreversible."""
    return [rxn for rxn in model.reactions if rxn.reversibility is False]


def find_unconstrained_reactions(model):
    """Return list of reactions that are not constrained at all."""
    lower_bound, upper_bound = helpers.find_bounds(model)
    return [
        rxn
        for rxn in model.reactions
        if rxn.lower_bound <= lower_bound and rxn.upper_bound >= upper_bound
    ]


def find_ngam(model):
    u"""
    Return all potential non growth-associated maintenance reactions.

    From the list of all reactions that convert ATP to ADP select the reactions
    that match a defined reaction string and whose metabolites are situated
    within the main model compartment. The main model compartment is the
    cytosol, and if that cannot be identified, the compartment with the most
    metabolites.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns
    -------
    list
        Reactions that qualify as non-growth associated maintenance reactions.

    Notes
    -----
    [1]_ define the non-growth associated maintenance (NGAM) as the energy
    required to maintain all constant processes such as turgor pressure and
    other housekeeping activities. In metabolic models this is expressed by
    requiring a simple ATP hydrolysis reaction to always have a fixed minimal
    amount of flux. This value can be measured as described by [1]_ .

    References
    ----------
    .. [1] Thiele, I., & Palsson, B. Ø. (2010, January). A protocol for
          generating a high-quality genome-scale metabolic reconstruction.
          Nature protocols. Nature Publishing Group.
          http://doi.org/10.1038/nprot.2009.203

    """
    atp_adp_conv_rxns = helpers.find_converting_reactions(model, ("MNXM3", "MNXM7"))
    id_of_main_compartment = helpers.find_compartment_id_in_model(model, "c")

    reactants = {
        helpers.find_met_in_model(model, "MNXM3", id_of_main_compartment)[0],
        helpers.find_met_in_model(model, "MNXM2", id_of_main_compartment)[0],
    }

    products = {
        helpers.find_met_in_model(model, "MNXM7", id_of_main_compartment)[0],
        helpers.find_met_in_model(model, "MNXM1", id_of_main_compartment)[0],
        helpers.find_met_in_model(model, "MNXM9", id_of_main_compartment)[0],
    }

    candidates = [
        rxn
        for rxn in atp_adp_conv_rxns
        if rxn.reversibility is False
        and set(rxn.reactants) == reactants
        and set(rxn.products) == products
    ]

    buzzwords = [
        "maintenance",
        "atpm",
        "requirement",
        "ngam",
        "non-growth",
        "associated",
    ]

    refined_candidates = [
        rxn
        for rxn in candidates
        if any(string in filter_none(rxn.name, "").lower() for string in buzzwords)
    ]

    if refined_candidates:
        return refined_candidates
    else:
        return candidates


def calculate_metabolic_coverage(model):
    u"""
    Return the ratio of reactions and genes included in the model.

    Determine whether the amount of reactions and genes in model not equal to
    zero, then return the ratio.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns
    -------
    float
        The ratio of reactions to genes also called metabolic coverage.

    Raises
    ------
    ValueError
        If the model does not contain either reactions or genes.

    Notes
    -----
    According to [1]_ this is a good quality indicator expressing the degree of
    metabolic coverage i.e. modeling detail of a given reconstruction. The
    authors explain that models with a 'high level of modeling detail have
    ratios >1, and [models] with low level of detail have ratios <1'. They
    explain that 'this difference arises because [models] with basic or
    intermediate levels of detail often include many reactions in which several
    gene products and their enzymatic transformations are ‘lumped’'.

    References
    ----------
    .. [1] Monk, J., Nogales, J., & Palsson, B. O. (2014). Optimizing
          genome-scale network reconstructions. Nature Biotechnology, 32(5),
          447–452. http://doi.org/10.1038/nbt.2870

    """
    if len(model.reactions) == 0 or len(model.genes) == 0:
        raise ValueError("The model contains no reactions or genes.")
    return float(len(model.reactions)) / float(len(model.genes))


def find_protein_complexes(model):
    """
    Find reactions that are catalyzed by at least a heterodimer.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns
    -------
    list
        Reactions whose gene-protein-reaction association contains at least one
        logical AND combining different gene products (heterodimer).

    """
    complexes = []
    for rxn in model.reactions:
        if not rxn.gene_reaction_rule:
            continue
        size = find_top_level_complex(rxn.gene_reaction_rule)
        if size >= 2:
            complexes.append(rxn)
    return complexes


@lrudecorator(size=2)
def find_pure_metabolic_reactions(model):
    """
    Return reactions that are neither transporters, exchanges, nor pseudo.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    return set(model.reactions) - helpers.find_interchange_biomass_reactions(model)


def is_constrained_reaction(model, rxn):
    """Return whether a reaction has fixed constraints."""
    lower_bound, upper_bound = helpers.find_bounds(model)
    if rxn.reversibility:
        return rxn.lower_bound > lower_bound or rxn.upper_bound < upper_bound
    else:
        return rxn.lower_bound > 0 or rxn.upper_bound < upper_bound


def find_oxygen_reactions(model):
    """Return list of oxygen-producing/-consuming reactions."""
    o2_in_model = helpers.find_met_in_model(model, "MNXM4")
    return set(
        [
            rxn
            for met in model.metabolites
            for rxn in met.reactions
            if met.formula == "O2" or met in o2_in_model
        ]
    )


def find_unique_metabolites(model):
    """Return set of metabolite IDs without duplicates from compartments."""
    unique = set()
    for met in model.metabolites:
        is_missing = True
        for comp in model.compartments:
            if met.id.endswith("_{}".format(comp)):
                unique.add(met.id[: -(len(comp) + 1)])
                is_missing = False
                break
        if is_missing:
            unique.add(met.id)
    return unique


@lrudecorator(size=2)
def find_duplicate_metabolites_in_compartments(model):
    """
    Return list of metabolites with duplicates in the same compartment.

    This function identifies duplicate metabolites in each compartment by
    determining if any two metabolites have identical InChI-key annotations.
    For instance, this function would find compounds with IDs ATP1 and ATP2 in
    the cytosolic compartment, with both having the same InChI annotations.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns
    -------
    list
        A list of tuples of duplicate metabolites.

    """
    unique_identifiers = ["inchikey", "inchi"]
    duplicates = []
    for met_1, met_2 in combinations(model.metabolites, 2):
        if met_1.compartment == met_2.compartment:
            for key in unique_identifiers:
                if key in met_1.annotation and key in met_2.annotation:
                    if met_1.annotation[key] == met_2.annotation[key]:
                        duplicates.append((met_1.id, met_2.id))
                        break
    return duplicates


def find_reactions_with_partially_identical_annotations(model):
    """
    Return duplicate reactions based on identical annotation.

    Identify duplicate reactions globally by checking if any two metabolic
    reactions have the same entries in their annotation attributes. This can be
    useful to identify one 'type' of reactions that occurs in several
    compartments, to curate merged models or to clean-up bulk model
    modifications. The heuristic looks at annotations with the keys
    "metanetx.reaction", "kegg.reaction", "brenda", "rhea", "biocyc",
    "bigg.reaction" only.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns
    -------
    dict
        A mapping from sets of annotations to groups of reactions with those
        annotations.
    int
        The total number of unique reactions that are duplicated.

    """
    duplicates = {}
    rxn_db_identifiers = [
        "metanetx.reaction",
        "kegg.reaction",
        "brenda",
        "rhea",
        "biocyc",
        "bigg.reaction",
    ]
    # Build a list that associates a reaction with a set of its annotations.
    ann_rxns = []
    for rxn in model.reactions:
        ann = []
        for key in rxn_db_identifiers:
            if key in rxn.annotation:
                if isinstance(rxn.annotation[key], list):
                    ann.extend([(key, elem) for elem in rxn.annotation[key]])
                else:
                    ann.append((key, rxn.annotation[key]))
        ann_rxns.append((rxn, frozenset(ann)))
    # Compute the intersection between annotations and record the matching
    # reaction identifiers.
    for (rxn_a, ann_a), (rxn_b, ann_b) in combinations(ann_rxns, 2):
        mutual_pair = tuple(ann_a & ann_b)
        if len(mutual_pair) > 0:
            duplicates.setdefault(mutual_pair, set()).update([rxn_a.id, rxn_b.id])
    # Transform the object for JSON compatibility
    num_duplicated = set()
    duplicated = {}
    for key in duplicates:
        # Object keys must be strings in JSON.
        new_key = ",".join(sorted("{}:{}".format(ns, term) for ns, term in key))
        duplicated[new_key] = rxns = list(duplicates[key])
        num_duplicated.update(rxns)
    return duplicated, len(num_duplicated)


def map_metabolites_to_structures(metabolites, compartments):
    """
    Map metabolites from the identifier namespace to structural space.

    Metabolites who lack structural annotation (InChI or InChIKey) are ignored.

    Parameters
    ----------
    metabolites : iterable
        The cobra.Metabolites to map.
    compartments : iterable
        The different compartments to consider. Structures are treated
        separately for each compartment.

    Returns
    -------
    dict
        A mapping from a cobra.Metabolite to its compartment specific
        structure index.

    """
    # TODO (Moritz Beber): Consider SMILES?
    unique_identifiers = ["inchikey", "inchi"]
    met2mol = {}
    molecules = {c: [] for c in compartments}
    for met in metabolites:
        ann = []
        for key in unique_identifiers:
            mol = met.annotation.get(key)
            if mol is not None:
                ann.append(mol)
        # Ignore metabolites without the required information.
        if len(ann) == 0:
            continue
        ann = set(ann)
        # Compare with other structures in the same compartment.
        mols = molecules[met.compartment]
        for i, mol_group in enumerate(mols):
            if len(ann & mol_group) > 0:
                mol_group.update(ann)
                # We map to the index of the group because it is hashable and
                # cheaper to compare later.
                met2mol[met] = "{}-{}".format(met.compartment, i)
                break
        if met not in met2mol:
            # The length of the list corresponds to the 0-index after appending.
            met2mol[met] = "{}-{}".format(met.compartment, len(mols))
            mols.append(ann)
    return met2mol


def find_duplicate_reactions(model):
    """
    Return a list with pairs of reactions that are functionally identical.

    Identify duplicate reactions globally by checking if any
    two reactions have the same metabolites, same directionality and are in
    the same compartment.

    This can be useful to curate merged models or to clean-up bulk model
    modifications. The heuristic compares reactions in a pairwise manner.
    For each reaction, the metabolite annotations are checked for a description
    of the structure (via InChI and InChIKey).If they exist, substrates and
    products as well as the stoichiometries of any reaction pair are compared.
    Only reactions where the substrates, products, stoichiometry and
    reversibility are identical are considered to be duplicates.
    This test will not be able to identify duplicate reactions if there are no
    structure annotations. Further, it will report reactions with
    differing bounds as equal if they otherwise match the above conditions.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns
    -------
    list
        A list of pairs of duplicate reactions based on metabolites.
    int
        The number of unique reactions that have a duplicates

    """
    met2mol = map_metabolites_to_structures(model.metabolites, model.compartments)
    # Build a list associating reactions with their stoichiometry in molecular
    # structure space.
    structural = []
    for rxn in model.reactions:
        # Ignore reactions that have metabolites without structures.
        if not all(met in met2mol for met in rxn.metabolites):
            continue
        # We consider substrates and products separately since, for example,
        # the InChI for H2O and OH is the same.
        substrates = {met2mol[met]: rxn.get_coefficient(met) for met in rxn.reactants}
        products = {met2mol[met]: rxn.get_coefficient(met) for met in rxn.products}
        structural.append((rxn, substrates, products))
    # Compare reactions using their structure-based stoichiometries.
    num_duplicated = set()
    duplicates = []
    for (rxn_a, sub_a, prod_a), (rxn_b, sub_b, prod_b) in combinations(structural, 2):
        # Compare the substrates.
        if sub_a != sub_b:
            continue
        # Compare the products.
        if prod_a != prod_b:
            continue
        # Compare whether they are both (ir-)reversible.
        if rxn_a.reversibility != rxn_b.reversibility:
            continue
        # TODO (Moritz Beber): We could compare bounds here but it might be
        #  worth knowing about the reactions even if their bounds differ?
        duplicates.append((rxn_a.id, rxn_b.id))
        num_duplicated.add(rxn_a.id)
        num_duplicated.add(rxn_b.id)
    return duplicates, len(num_duplicated)


def find_reactions_with_identical_genes(model):
    """
    Return reactions that have identical genes.

    Identify duplicate reactions globally by checking if any
    two reactions have the same genes.
    This can be useful to curate merged models or to clean-up bulk model
    modifications, but also to identify promiscuous enzymes.
    The heuristic compares reactions in a pairwise manner and reports on
    reaction pairs whose genes are identical. Reactions with missing genes are
    skipped.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns
    -------
    dict
        A mapping from sets of genes to all the reactions containing those
        genes.
    int
        The total number of unique reactions that appear duplicates based on
        their gene-protein-reaction associations.

    """
    duplicates = dict()
    for rxn_a, rxn_b in combinations(model.reactions, 2):
        if not (rxn_a.genes and rxn_b.genes):
            continue
        if rxn_a.genes == rxn_b.genes:
            # This works because the `genes` are frozen sets.
            identifiers = rxn_a.genes
            duplicates.setdefault(identifiers, set()).update([rxn_a.id, rxn_b.id])
    # Transform the object for JSON compatibility
    num_duplicated = set()
    duplicated = {}
    for key in duplicates:
        # Object keys must be strings in JSON.
        new_key = ",".join(sorted(g.id for g in key))
        duplicated[new_key] = rxns = list(duplicates[key])
        num_duplicated.update(rxns)
    return duplicated, len(num_duplicated)


def check_transport_reaction_gpr_presence(model):
    """Return the list of transport reactions that have no associated gpr."""
    return [
        rxn
        for rxn in helpers.find_transport_reactions(model)
        if not rxn.gene_reaction_rule
    ]


def find_medium_metabolites(model):
    """Return the list of metabolites ingested/excreted by the model."""
    return [
        met.id
        for rxn in model.medium
        for met in model.reactions.get_by_id(rxn).metabolites
    ]


def find_external_metabolites(model):
    """Return all metabolites in the external compartment."""
    ex_comp = find_external_compartment(model)
    return [met for met in model.metabolites if met.compartment == ex_comp]
