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

"""Supporting functions for annotation checks performed on the model object."""

from __future__ import absolute_import

import logging
import re

from memote.support.helpers import (get_difference)

LOGGER = logging.getLogger(__name__)

# MIRIAM (http://www.ebi.ac.uk/miriam/) styled identifiers for
# common databases that are currently included are:
# DB    rxn,met,gen url
# 'MetaNetX'  ['rxn','met'] 'http://www.metanetx.org'
# 'Kegg'  ['rxn','met'] 'http://www.kegg.jp/'
# 'SEED'  ['met']  'http://modelseed.org/'
# 'InChIKey'  ['met'] 'http://cactus.nci.nih.gov/chemical/structure'
# 'ChEBI' ['met'] 'http://bioportal.bioontology.org/ontologies/CHEBI'
# 'EnzymeNomenclature'    ['rxn'] 'http://www.enzyme-database.org/'
# 'BRENDA'    ['rxn']    'http://www.brenda-enzymes.org/'
# 'RHEA'  ['rxn']  'http://www.rhea-db.org/'
# 'HMDB'  ['met'] 'http://www.hmdb.ca/'
# 'BioCyc'  ['rxn','met'] 'http://biocyc.org'
# 'Reactome'    ['met'] 'http://www.reactome.org/'
# 'BiGG'    ['rxn','met']   'http://bigg.ucsd.edu/universal/'

REACTION_ANNOTATIONS = {'metanetx.reaction': re.compile(r"^MNXR\d+$"),
                        'kegg.reaction': re.compile(r"^R\d+$"),
                        'ec-code': re.compile(r"^\d+\.-\.-\.-|\d+\.\d+\.-\.-|"
                                              r"\d+\.\d+\.\d+\.-|"
                                              r"\d+\.\d+\.\d+\.(n)?\d+$"),
                        'brenda': re.compile(r"^\d+\.-\.-\.-|\d+\.\d+\.-\.-|"
                                             r"\d+\.\d+\.\d+\.-|"
                                             r"\d+\.\d+\.\d+\.(n)?\d+$"),
                        'rhea': re.compile(r"^\d{5}$"),
                        'biocyc': re.compile(r"^[A-Z-0-9]+(?<!CHEBI)"
                                             r"(\:)?[A-Za-z0-9+_.%-]+$"),
                        'bigg.reaction': re.compile(r"^[a-z_A-Z0-9]+$")}


METABOLITE_ANNOTATIONS = {'metanetx.chemical': re.compile(r"^MNXM\d+$"),
                          'kegg.compound': re.compile(r"^C\d+$"),
                          'seed.compound': re.compile(r"^cpd\d+$"),
                          'inchikey': re.compile(r"^[A-Z]{14}\-"
                                                 r"[A-Z]{10}(\-[A-Z])?"),
                          'chebi': re.compile(r"^CHEBI:\d+$"),
                          'hmdb': re.compile(r"^HMDB\d{5}$"),
                          'biocyc': re.compile(r"^[A-Z-0-9]+(?<!CHEBI)"
                                               r"(\:)?[A-Za-z0-9+_.%-]+$"),
                          'reactome': re.compile(r"(^R-[A-Z]{3}-[0-9]+"
                                                 r"(-[0-9]+)?$)|"
                                                 r"(^REACT_\d+(\.\d+)?$)"),
                          'bigg.metabolite': re.compile(r"^[a-z_A-Z0-9]+$")}


def find_met_without_annotations(model):
    """
    Find metabolites with empty annotation attributes.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model.

    Returns
    -------
    list
        Metabolites that have empty annotation attributes.

    """
    return [met for met in model.metabolites if met.annotation == {}]


def generate_met_annotation_overview(model):
    """
    List metabolites which lack annotation for a given database.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model.

    Returns
    -------
    dict
        Dictionary that contains the database namespaces as keys and a list of
        metabolites without annotation in each namespace as the values.

    """
    met_annotation_overview = {key: [] for key in METABOLITE_ANNOTATIONS}
    for met in model.metabolites:
        for key in METABOLITE_ANNOTATIONS:
            if key not in met.annotation:
                met_annotation_overview[key].append(met)
    return met_annotation_overview


def find_rxn_without_annotations(model):
    """
    Find reactions with empty annotation attributes.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model.

    Returns
    -------
    list
        Reactions that have empty annotation attributes.

    """
    return [rxn for rxn in model.reactions if rxn.annotation == {}]


def generate_rxn_annotation_overview(model):
    """
    List reactions which lack annotation for a given database.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model.

    Returns
    -------
    dict
        Dictionary that contains the database namespaces as keys and a list of
        reactions without annotation in each namespace as the values.

    """
    rxn_annotation_overview = {key: [] for key in REACTION_ANNOTATIONS}
    for rxn in model.reactions:
        for key in REACTION_ANNOTATIONS:
            if key not in rxn.annotation:
                rxn_annotation_overview[key].append(rxn)
    return rxn_annotation_overview


def find_wrong_annotation_ids(model, overview_dict, type):
    """
    Check the correctness of the annotations of annotated model components.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model.

    overview_dict
        Dictionary that contains the database namespaces as keys and a list of
        mets/rxns without annotation in each namespace as the values.

    type : str
        Either 'rxn' or 'met'.

    Returns
    -------
    dict
        Dictionary that contains the database namespaces as keys and a list of
        mets/rxns that have wrong ids of each namespace as the values.

    """
    if type == 'rxn':
        items_anno_wrong_ids = {db_id: [] for db_id in REACTION_ANNOTATIONS}
        pattern_storage = REACTION_ANNOTATIONS
    if type == 'met':
        items_anno_wrong_ids = {db_id: [] for db_id in METABOLITE_ANNOTATIONS}
        pattern_storage = METABOLITE_ANNOTATIONS
    for db_id in overview_dict:
        items_with_annotation = get_difference(
            overview_dict[db_id],
            model,
            type
        )
        for item in items_with_annotation:
            if type(item.annotation[db_id]) == str:
                if not re.match(
                    pattern_storage[db_id], item.annotation[db_id]
                ):
                    items_anno_wrong_ids[db_id].append(item)
            if type(item.annotation[db_id]) == list:
                for anno_id in item.annotation[db_id]:
                    if not re.match(
                        pattern_storage[db_id], anno_id
                    ):
                        items_anno_wrong_ids[db_id].append(item)
                        break
                    else:
                        pass
    return items_anno_wrong_ids
