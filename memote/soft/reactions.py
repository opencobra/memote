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

"""
The module provides soft expectations on model reactions that will mostly
generate log output and warnings but will likely not fail a test suite.
"""

from __future__ import absolute_import
import re
from ..util import find_demand_and_exchange_reactions, find_transport_reactions, find_atp_adp_converting_reactions

__all__ = ("check_rxn_id_extracellular_tag",)

import logging

LOGGER = logging.getLogger(__name__)


def check_rxn_id_extracellular_tag(model):
    """Return a list of extracellular reactions in model that have not been tagged as such.

     The function excludes exchange and demand reactions from the list

    :param model: A cobrapy metabolic model
    :type model: cobra.core.Model.Model
    """

    reactions_with_all_metabolites_in_e = [rxn for rxn in model.reactions if rxn.get_compartments() == list('e')]
    extracellular_reactions = (set(reactions_with_all_metabolites_in_e) -
                               set(find_demand_and_exchange_reactions(model)))
    return [rxn for rxn in extracellular_reactions if not re.match('[A-Z0-9]+.*?e.*?', rxn.id)]


def check_reaction_id_periplasm(model):
    """Return a list of periplasmic reactions that have not been tagged as such.

    :param model: A cobrapy metabolic model
    :type model: cobra.core.Model.Model
    """
    reactions_with_all_metabolites_in_pp = [rxn for rxn in model.reactions if rxn.get_compartments() == list('p')]
    return [rxn for rxn in reactions_with_all_metabolites_in_pp if not re.match('[A-Z0-9]+.*?pp.*?', rxn.id)]


def check_reaction_tag_chloroplast(model):
    """Return a list of chloroplast reactions that have not been tagged as such.

    :param model: A cobrapy metabolic model
    :type model: cobra.core.Model.Model
    """
    reactions_with_all_mets_in_h = [rxn for rxn in model.reactions if rxn.get_compartments() == list('h')]
    return [rxn for rxn in reactions_with_all_mets_in_h if not re.match('[A-Z0-9]+.*?h.*?', rxn.id)]


def check_reaction_tag_endoplasmatic_reticulum(model):
    """Return a list of ER reactions that have not been tagged as such.

    :param model: A cobrapy metabolic model
    :type model: cobra.core.Model.Model
    """
    reactions_with_all_mets_in_er = [rxn for rxn in model.reactions if rxn.get_compartments() == list('er')]
    return [rxn for rxn in reactions_with_all_mets_in_er if not re.match('[A-Z0-9]+.*?er.*?', rxn.id)]


def check_reaction_tag_golgi(model):
    """Return a list of golgi reactions that have not been tagged as such.

    :param model: A cobrapy metabolic model
    :type model: cobra.core.Model.Model
    """
    reactions_with_all_mets_in_g = [rxn for rxn in model.reactions if rxn.get_compartments() == list('g')]
    return [rxn for rxn in reactions_with_all_mets_in_g if not re.match('[A-Z0-9]+.*?g.*?', rxn.id)]


def check_reaction_tag_lysosome(model):
    """Return a list of lysosomic reactions that have not been tagged as such.

    :param model: A cobrapy metabolic model
    :type model: cobra.core.Model.Model
    """
    reactions_with_all_mets_in_l = [rxn for rxn in model.reactions if rxn.get_compartments() == list('l')]
    return [rxn for rxn in reactions_with_all_mets_in_l if not re.match('[A-Z0-9]+.*?l.*?', rxn.id)]


def check_reaction_tag_mitochondrion(model):
    """Return a list of mitochondrial reactions that have not been tagged as such.

    :param model: A cobrapy metabolic model
    :type model: cobra.core.Model.Model
    """
    reactions_with_all_mets_in_m = [rxn for rxn in model.reactions if rxn.get_compartments() == list('m')]
    return [rxn for rxn in reactions_with_all_mets_in_m if not re.match('[A-Z0-9]+.*?m.*?', rxn.id)]


def check_reaction_tag_nucleus(model):
    """Return a list of nucleic reactions that have not been tagged as such.

    :param model: A cobrapy metabolic model
    :type model: cobra.core.Model.Model
    """
    reactions_with_all_mets_in_n = [rxn for rxn in model.reactions if rxn.get_compartments() == list('n')]
    return [rxn for rxn in reactions_with_all_mets_in_n if not re.match('[A-Z0-9]+.*?n.*?', rxn.id)]


def check_reaction_tag_peroxisome(model):
    """Return a list of peroxisomic reactions that have not been tagged as such.

    :param model: A cobrapy metabolic model
    :type model: cobra.core.Model.Model
    """
    reactions_with_all_mets_in_x = [rxn for rxn in model.reactions if rxn.get_compartments() == list('x')]
    return [rxn for rxn in reactions_with_all_mets_in_x if not re.match('[A-Z0-9]+.*?x.*?', rxn.id)]


def check_reaction_tag_vacuole(model):
    """Return a list of vacuolic reactions that have not been tagged as such.

    :param model: A cobrapy metabolic model
    :type model: cobra.core.Model.Model
    """
    reactions_with_all_mets_in_v = [rxn for rxn in model.reactions if rxn.get_compartments() == list('v')]
    return [rxn for rxn in reactions_with_all_mets_in_v if not re.match('[A-Z0-9]+.*?v.*?', rxn.id)]


def check_reaction_tag_transporter(model):
    """Return a list of transport reactions that have not been tagged as such.


    A transport reaction is defined as follows:
       -- It contains metabolites from at least 2 compartments
       -- At least 1 metabolite undergoes no chemical reaction
          i.e. the formula stays the same on both sides of the equation

    Reactions that only transport protons ('H') across the membrane are excluded, as well as
    Reactions with redox cofactors whose formula is either 'X' or 'XH2'

    :param model: A cobrapy metabolic model
    :type model: cobra.core.Model.Model
    """
    transport_rxns = find_transport_reactions(model)
    atp_adp_rxns = find_atp_adp_converting_reactions(model)

    non_abc_transporters = set(transport_rxns).difference(set(atp_adp_rxns))

    return [rxn for rxn in non_abc_transporters if not re.match('[A-Z0-9]+.*?t.*?', rxn.id)]
