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
#   DB             gen,rxn,met              url
#
# 'MetaNetX'    ['rxn','met']       'http://www.metanetx.org'
# 'Kegg'        ['gen','rxn','met'] 'http://www.kegg.jp/'
# 'SEED'        ['met']             'http://modelseed.org/'
#
# 'InChIKey'    ['met']     'http://cactus.nci.nih.gov/chemical/structure'
# 'ChEBI'       ['met']     'http://bioportal.bioontology.org/ontologies/CHEBI'
# 'BRENDA'      ['rxn']     'http://www.brenda-enzymes.org/'
# 'RHEA'        ['rxn']     'http://www.rhea-db.org/'
# 'HMDB'        ['met']     'http://www.hmdb.ca/'
#
# 'BioCyc'      ['rxn','met']   'http://biocyc.org'
# 'Reactome'    ['met']         'http://www.reactome.org/'
# 'BiGG'        ['rxn','met']   'http://bigg.ucsd.edu/universal/'
# 'PubChem'     ['met']         'https://pubchem.ncbi.nlm.nih.gov/'
# 'RefSeq'      ['gen']         'http://www.ncbi.nlm.nih.gov/projects/RefSeq/'
# 'Uniprot'     ['gen']         'http://www.uniprot.org/'
# 'EC-Code'     ['rxn']         'http://www.enzyme-database.org/'
# 'EcoGene'     ['gen']         'http://ecogene.org/'
# 'NCBI GI'     ['gen']         'http://www.ncbi.nlm.nih.gov/protein/'
# 'NCBI Gene'   ['gen']         'http://ncbigene.bio2rdf.org/fct'
# 'NCBI Protein'['gen']         'http://www.ncbi.nlm.nih.gov/protein'
# 'CCDS'        ['gen']         'http://www.ncbi.nlm.nih.gov/CCDS/'
# 'HPRD'        ['gen']         'http://www.hprd.org/'
# 'ASAP'        ['gen']         'http://asap.ahabs.wisc.edu/asap/home.php'

GENE_PRODUCT_ANNOTATIONS = OrderedDict([
    ('refseq', re.compile(
        r"^((AC|AP|NC|NG|NM|NP|NR|NT|"
        r"NW|XM|XP|XR|YP|ZP)_\d+|"
        r"(NZ\_[A-Z]{4}\d+))(\.\d+)?$")),
    ('uniprot', re.compile(
        r"^([A-N,R-Z][0-9]([A-Z][A-Z, 0-9]"
        r"[A-Z, 0-9][0-9]){1,2})|([O,P,Q]"
        r"[0-9][A-Z, 0-9][A-Z, 0-9][A-Z, 0-9]"
        r"[0-9])(\.\d+)?$")),
    ('ecogene', re.compile(r"^EG\d+$")),
    ('kegg.gene', re.compile(r"^\w+:[\w\d\.-]*$")),
    ('ncbigi', re.compile(r"^(GI|gi)\:\d+$")),
    ('ncbigene', re.compile(r"^\d+$")),
    ('ncbiprotein', re.compile(r"^(\w+\d+(\.\d+)?)|(NP_\d+)$")),
    ('ccds', re.compile(r"^CCDS\d+\.\d+$")),
    ('hprd', re.compile(r"^\d+$")),
    ('asap', re.compile(r"^[A-Za-z0-9-]+$"))
])


REACTION_ANNOTATIONS = OrderedDict([
    ('rhea', re.compile(r"^\d{5}$")),
    ('kegg.reaction', re.compile(r"^R\d+$")),
    ('metanetx.reaction', re.compile(r"^MNXR\d+$")),
    ('bigg.reaction', re.compile(r"^[a-z_A-Z0-9]+$")),
    ('ec-code', re.compile(
        r"^\d+\.-\.-\.-|\d+\.\d+\.-\.-|"
        r"\d+\.\d+\.\d+\.-|"
        r"\d+\.\d+\.\d+\.(n)?\d+$")),
    ('brenda', re.compile(
        r"^\d+\.-\.-\.-|\d+\.\d+\.-\.-|"
        r"\d+\.\d+\.\d+\.-|"
        r"\d+\.\d+\.\d+\.(n)?\d+$")),
    ('biocyc', re.compile(
        r"^[A-Z-0-9]+(?<!CHEBI)"
        r"(\:)?[A-Za-z0-9+_.%-]+$"))
])


METABOLITE_ANNOTATIONS = OrderedDict([
    ('pubchem.compound', re.compile(r"^\d+$")),
    ('kegg.compound', re.compile(r"^C\d+$")),
    ('seed.compound', re.compile(r"^cpd\d+$")),
    ('inchikey', re.compile(
        r"^[A-Z]{14}\-[A-Z]{10}(\-[A-Z])?")),
    ('chebi', re.compile(r"^CHEBI:\d+$")),
    ('hmdb', re.compile(r"^HMDB\d{5}$")),
    ('reactome', re.compile(
        r"(^R-[A-Z]{3}-[0-9]+(-[0-9]+)?$)|(^REACT_\d+(\.\d+)?$)")),
    ('metanetx.chemical', re.compile(r"^MNXM\d+$")),
    ('bigg.metabolite', re.compile(r"^[a-z_A-Z0-9]+$")),
    ('biocyc', re.compile(
        r"^[A-Z-0-9]+(?<!CHEBI)(\:)?[A-Za-z0-9+_.%-]+$"))
])


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


def generate_component_annotation_overview(elements, db):
    """
    Tabulate which MIRIAM databases the component's annotation match.

    Parameters
    ----------
    elements : list
        Elements of a model, either metabolites, reactions, or genes.
    db : str
        One of the MIRIAM database identifiers.

    Returns
    -------
    list
        The components that are not annotated with the specified MIRIAM
        database.

    """
    return [elem for elem in elements if db not in elem.annotation]


def generate_component_annotation_miriam_match(elements, component, db):
    """
    Tabulate which MIRIAM databases the element's annotation match.

    If the relevant MIRIAM identifier is not in an element's annotation it is
    ignored.

    Parameters
    ----------
    elements : list
        Elements of a model, either metabolites or reactions.
    component : {"metabolites", "reactions"}
        A string denoting a type of ``cobra.Model`` component.
    db : str
        One of the MIRIAM database identifiers.

    Returns
    -------
    list
        The components whose annotation does not match the pattern for the
        MIRIAM database.

    """
    def is_faulty(annotation, key, pattern):
        # Ignore missing annotation for this database.
        if key not in annotation:
            return False
        test = annotation[key]
        if isinstance(test, native_str):
            return pattern.match(test) is None
        else:
            return any(pattern.match(elem) is None for elem in test)

    pattern = {
        "metabolites": METABOLITE_ANNOTATIONS,
        "reactions": REACTION_ANNOTATIONS
    }[component][db]
    return [elem for elem in elements
            if is_faulty(elem.annotation, db, pattern)]


def generate_component_id_namespace_overview(model, components):
    """
    Tabulate which MIRIAM databases the component's identifier matches.

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
    df = pd.DataFrame(data, index=index, columns=databases)
    if components != "genes":
        # Clean up of the dataframe. Unfortunately the Biocyc patterns match
        # broadly. Hence, whenever a Metabolite or Reaction ID matches to any
        # DB pattern AND the Biocyc pattern we have to assume that this is a
        # false positive.
        # First determine all rows in which 'biocyc' and other entries are
        # True simultaneously and use this Boolean series to create another
        # column temporarily.
        df['duplicate'] = df[df['biocyc']].sum(axis=1) >= 2
        # Replace all nan values with False
        df['duplicate'].fillna(False, inplace=True)
        # Use the additional column to index the original dataframe to identify
        # false positive biocyc hits and set them to False.
        df.loc[df['duplicate'], 'biocyc'] = False
        # Delete the additional column
        del df['duplicate']
    return df
