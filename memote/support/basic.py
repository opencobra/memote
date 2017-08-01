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

from __future__ import absolute_import

import logging

from memote.support.helpers import find_atp_adp_converting_reactions

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
    return [rxn for rxn in model.reactions if
            0 > rxn.lower_bound > -1000 or
            0 < rxn.upper_bound < 1000]


def find_zero_constrained_reactions(model):
    """Return list of reactions that are constrained to zero flux."""
    return [rxn for rxn in model.reactions if
            rxn.lower_bound == 0 and
            rxn.upper_bound == 0]


def find_irreversible_reactions(model):
    """Return list of reactions that are irreversible."""
    return [rxn for rxn in model.reactions if rxn.reversibility is False]


def find_unconstrained_reactions(model):
    """Return list of reactions that are not constrained at all."""
    return [rxn for rxn in model.reactions if
            rxn.lower_bound <= -1000 and
            rxn.upper_bound >= 1000]


def find_ngam(model):
    """
    Return a the non growth-associated maintenance reaction.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    atp_adp_conv_rxns = find_atp_adp_converting_reactions(model)
    return [rxn for rxn in atp_adp_conv_rxns
            if rxn.build_reaction_string() == 'atp_c + h2o_c --> '
                                              'adp_c + h_c + pi_c' and not
            rxn.lower_bound <= 0]


def calculate_metabolic_coverage(model):
    """
    Return the ratio of reactions and genes included in the model.

    According to [1] this is a good quality indicator expressing the degree of
    metabolic coverage i.e. modeling detail of a given reconstruction. The
    authors explain that models with a 'high level of modeling detail have
    ratios >1, and [models] with low level of detail have ratios <1'. They
    explain that 'this difference arises because [models] with basic or
    intermediate levels of detail often include many reactions in which several
    gene products and their enzymatic transformations are ‘lumped’'.

    References
    ----------
    [1] Monk, J., Nogales, J., & Palsson, B. O. (2014). Optimizing genome-scale
    network reconstructions. Nature Biotechnology, 32(5), 447–452.
    http://doi.org/10.1038/nbt.2870

    """
    if len(model.reactions) == 0 or len(model.genes) == 0:
        raise ValueError("The model contains no reactions or genes.")
    return float(len(model.reactions)) / float(len(model.genes))
