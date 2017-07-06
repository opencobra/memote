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
from future.utils import native_str

import pandas as pd

from collections import OrderedDict

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

REACTION_ANNOTATIONS = [('rhea', re.compile(r"^\d{5}$")),
                        ('kegg.reaction', re.compile(r"^R\d+$")),
                        ('metanetx.reaction', re.compile(r"^MNXR\d+$")),
                        ('bigg.reaction', re.compile(r"^[a-z_A-Z0-9]+$")),
                        ('ec-code', re.compile(
                            r"^\d+\.-\.-\.-|\d+\.\d+\.-\.-|"
                            r"\d+\.\d+\.\d+\.-|"
                            r"\d+\.\d+\.\d+\.(n)?\d+$")
                         ),
                        ('brenda', re.compile(
                            r"^\d+\.-\.-\.-|\d+\.\d+\.-\.-|"
                            r"\d+\.\d+\.\d+\.-|"
                            r"\d+\.\d+\.\d+\.(n)?\d+$")
                         ),
                        ('biocyc', re.compile(
                            r"^[A-Z-0-9]+(?<!CHEBI)"
                            r"(\:)?[A-Za-z0-9+_.%-]+$")
                         )
                        ]
REACTION_ANNOTATIONS = OrderedDict(REACTION_ANNOTATIONS)


METABOLITE_ANNOTATIONS = [('kegg.compound', re.compile(r"^C\d+$")),
                          ('seed.compound', re.compile(r"^cpd\d+$")),
                          ('inchikey', re.compile(r"^[A-Z]{14}\-"
                                                  r"[A-Z]{10}(\-[A-Z])?")),
                          ('chebi', re.compile(r"^CHEBI:\d+$")),
                          ('hmdb', re.compile(r"^HMDB\d{5}$")),
                          ('reactome', re.compile(r"(^R-[A-Z]{3}-[0-9]+"
                                                  r"(-[0-9]+)?$)|"
                                                  r"(^REACT_\d+(\.\d+)?$)")),
                          ('metanetx.chemical', re.compile(r"^MNXM\d+$")),
                          ('bigg.metabolite', re.compile(r"^[a-z_A-Z0-9]+$")),
                          ('biocyc', re.compile(r"^[A-Z-0-9]+(?<!CHEBI)"
                                                r"(\:)?[A-Za-z0-9+_.%-]+$"))
                          ]
METABOLITE_ANNOTATIONS = OrderedDict(METABOLITE_ANNOTATIONS)


def find_components_without_annotation(model, components):
    """
    Find model components with empty annotation attributes.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model.
    components : {"metabolites", "reactions", "genes"}
        A string denoting `cobra.Model` components.

    Returns
    -------
    list
        The components without any annotation.

    """
    return [elem for elem in getattr(model, components) if
            elem.annotation is None or len(elem.annotation) == 0]


def generate_component_annotation_overview(model, components):
    """
    Tabulate which MIRIAM databases the component's annotation match.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model.
    components : {"metabolites", "reactions", "genes"}
        A string denoting `cobra.Model` components.

    Returns
    -------
    pandas.DataFrame
        The index of the table is given by the component identifiers. Each
        column corresponds to one MIRIAM database and a Boolean entry
        determines whether the annotation matches.

    """
    databases = list({
        "metabolites": METABOLITE_ANNOTATIONS,
        "reactions": REACTION_ANNOTATIONS
    }[components])
    data = list()
    index = list()
    for elem in getattr(model, components):
        index.append(elem.id)
        data.append(tuple(db in elem.annotation for db in databases))
    return pd.DataFrame(data, index=index, columns=databases)


def generate_component_annotation_miriam_match(model, components):
    """
    Tabulate which MIRIAM databases the component's annotation match.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model.
    components : {"metabolites", "reactions", "genes"}
        A string denoting `cobra.Model` components.

    Returns
    -------
    pandas.DataFrame
        The index of the table is given by the component identifiers. Each
        column corresponds to one MIRIAM database and a Boolean entry
        determines whether the annotation matches.

    """
    def check_annotation(key, annotation):
        if key not in annotation:
            return False
        test = annotation[key]
        pattern = patterns[key]
        if isinstance(test, native_str):
            print("string match!")
            return pattern.match(test) is not None
        return all(pattern.match(elem) is not None for elem in test)

    patterns = {
        "metabolites": METABOLITE_ANNOTATIONS,
        "reactions": REACTION_ANNOTATIONS
    }[components]
    databases = list(patterns)
    data = list()
    index = list()
    for elem in getattr(model, components):
        index.append(elem.id)
        data.append(tuple(check_annotation(db, elem.annotation)
                          for db in databases))
    return pd.DataFrame(data, index=index, columns=databases)


def generate_component_id_namespace_overview(model, components):
    """
    Tabulate which MIRIAM databases the component's annotation match.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model.
    components : {"metabolites", "reactions", "genes"}
        A string denoting `cobra.Model` components.

    Returns
    -------
    pandas.DataFrame
        The index of the table is given by the component identifiers. Each
        column corresponds to one MIRIAM database and a Boolean entry
        determines whether the annotation matches.

    """
    patterns = {
        "metabolites": METABOLITE_ANNOTATIONS,
        "reactions": REACTION_ANNOTATIONS
    }[components]
    databases = list(patterns)
    data = list()
    index = list()
    for elem in getattr(model, components):
        index.append(elem.id)
        data.append(tuple(patterns[db].match(elem.id) is not None
                          for db in databases))
    return pd.DataFrame(data, index=index, columns=databases)
