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

"""Annotation tests performed on an instance of ``cobra.Model``."""

from __future__ import absolute_import, division

from warnings import warn
from builtins import dict

import pytest

import memote.support.annotation as annotation
from memote.utils import annotate, truncate, get_ids, wrapper


@annotate(title="Metabolites without Annotation", format_type="count")
def test_metabolite_annotation_presence(read_only_model):
    """
    Expect all metabolites to have a non-empty annotation attribute.

    This test checks if any annotations at all are present in the SBML
    annotations field for each metabolite, irrespective of the type of
    annotation i.e. specific database  cross-references, ontology terms,
    additional information. For this test to pass the model is expected to
    have metabolites and each of them should have some form of annotation.
    """
    ann = test_metabolite_annotation_presence.annotation
    ann["data"] = get_ids(annotation.find_components_without_annotation(
        read_only_model, "metabolites"))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} metabolites ({:.2%}) lack any form of annotation:
        {}""".format(len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Reactions without Annotation", format_type="count")
def test_reaction_annotation_presence(read_only_model):
    """
    Expect all reactions to have a non-empty annotation attribute.

    This test checks if any annotations at all are present in the SBML
    annotations field for each reaction, irrespective of the type of
    annotation i.e. specific database  cross-references, ontology terms,
    additional information. For this test to pass the model is expected to
    have reactions and each of them should have some form of annotation.
    """
    ann = test_reaction_annotation_presence.annotation
    ann["data"] = get_ids(annotation.find_components_without_annotation(
        read_only_model, "reactions"))
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """A total of {} reactions ({:.2%}) lack any form of annotation:
        {}""".format(len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Genes without Annotation", format_type="count")
def test_gene_product_annotation_presence(read_only_model):
    """
    Expect all genes to have a non-empty annotation attribute.

    This test checks if any annotations at all are present in the SBML
    annotations field (extended by FBC package) for each gene product,
    irrespective of the type of annotation i.e. specific database,
    cross-references, ontology terms, additional information. For this test to
    pass the model is expected to have genes and each of them should have some
    form of annotation.
    """
    ann = test_gene_product_annotation_presence.annotation
    ann["data"] = get_ids(annotation.find_components_without_annotation(
        read_only_model, "genes"))
    ann["metric"] = len(ann["data"]) / len(read_only_model.genes)
    ann["message"] = wrapper.fill(
        """A total of {} genes ({:.2%}) lack any form of
        annotation: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@pytest.mark.parametrize("db", list(annotation.METABOLITE_ANNOTATIONS))
@annotate(title="Missing Metabolite Annotations Per Database",
          format_type="percent", message=dict(), data=dict(), metric=dict())
def test_metabolite_annotation_overview(read_only_model, db):
    """
    Expect all metabolites to have annotations from common databases.

    Specific database cross-references are paramount to mapping information.
    To provide references to as many databases as possible helps to make the
    metabolic model more accessible to other researchers. This does not only
    facilitate the use of a model in a broad array of computational pipelines,
    it also promotes the metabolic model itself to become an organism-specific
    knowledge base.

    For this test to pass, each metabolite annotation should contain
    cross-references to a number of databases (listed in `annotation.py`).
    For each database this test checks for the presence of its corresponding
    namespace ID to comply with the MIRIAM guidelines i.e. they have to match
    those defined on https://identifiers.org/.

    Since each database is quite different and some potentially incomplete, it
    may not be feasible to achieve 100% coverage for each of them. Generally
    it should be possible, however, to obtain cross-references to at least
    one of the databases for all metabolites consistently.
    """
    ann = test_metabolite_annotation_overview.annotation
    ann["data"][db] = get_ids(
        annotation.generate_component_annotation_overview(
            read_only_model.metabolites, db))
    ann["metric"][db] = len(ann["data"][db]) / len(read_only_model.metabolites)
    ann["message"][db] = wrapper.fill(
        """The following {} metabolites ({:.2%}) lack annotation for {}:
        {}""".format(len(ann["data"][db]), ann["metric"][db], db,
                     truncate(ann["data"][db])))
    assert len(ann["data"][db]) == 0, ann["message"][db]


@pytest.mark.parametrize("db", list(annotation.REACTION_ANNOTATIONS))
@annotate(title="Missing Reaction Annotations Per Database",
          format_type="percent", message=dict(), data=dict(), metric=dict())
def test_reaction_annotation_overview(read_only_model, db):
    """
    Expect all reactions to have annotations from common databases.

    Specific database cross-references are paramount to mapping information.
    To provide references to as many databases as possible helps to make the
    metabolic model more accessible to other researchers. This does not only
    facilitate the use of a model in a broad array of computational pipelines,
    it also promotes the metabolic model itself to become an organism-specific
    knowledge base.

    For this test to pass, each reaction annotation should contain
    cross-references to a number of databases (listed in `annotation.py`).
    For each database this test checks for the presence of its corresponding
    namespace ID to comply with the MIRIAM guidelines i.e. they have to match
    those defined on https://identifiers.org/.

    Since each database is quite different and some potentially incomplete, it
    may not be feasible to achieve 100% coverage for each of them. Generally
    it should be possible, however, to obtain cross-references to at least
    one of the databases for all reactions consistently.
    """
    ann = test_reaction_annotation_overview.annotation
    ann["data"][db] = get_ids(
        annotation.generate_component_annotation_overview(
            read_only_model.reactions, db))
    ann["metric"][db] = len(ann["data"][db]) / len(read_only_model.reactions)
    ann["message"][db] = wrapper.fill(
        """The following {} reactions ({:.2%}) lack annotation for {}:
        {}""".format(len(ann["data"][db]), ann["metric"][db], db,
                     truncate(ann["data"][db])))
    assert len(ann["data"][db]) == 0, ann["message"][db]


@pytest.mark.parametrize("db", list(annotation.GENE_PRODUCT_ANNOTATIONS))
@annotate(title="Missing Gene Annotations Per Database",
          format_type="percent", message=dict(), data=dict(), metric=dict())
def test_gene_product_annotation_overview(read_only_model, db):
    """
    Expect all genes to have annotations from common databases.

    Specific database cross-references are paramount to mapping information.
    To provide references to as many databases as possible helps to make the
    metabolic model more accessible to other researchers. This does not only
    facilitate the use of a model in a broad array of computational pipelines,
    it also promotes the metabolic model itself to become an organism-specific
    knowledge base.

    For this test to pass, each gene product annotation should contain
    cross-references to a number of databases (listed in `annotation.py`).
    For each database this test checks for the presence of its corresponding
    namespace ID to comply with the MIRIAM guidelines i.e. they have to match
    those defined on https://identifiers.org/.

    Since each database is quite different and some potentially incomplete, it
    may not be feasible to achieve 100% coverage for each of them. Generally
    it should be possible, however, to obtain cross-references to at least
    one of the databases for all gene products consistently.
    """
    ann = test_gene_product_annotation_overview.annotation
    ann["data"][db] = get_ids(
        annotation.generate_component_annotation_overview(
            read_only_model.genes, db))
    ann["metric"][db] = len(ann["data"][db]) / len(read_only_model.genes)
    ann["message"][db] = wrapper.fill(
        """The following {} genes ({:.2%}) lack annotation for {}:
        {}""".format(len(ann["data"][db]), ann["metric"][db], db,
                     truncate(ann["data"][db])))
    assert len(ann["data"][db]) == 0, ann["message"][db]


@pytest.mark.parametrize("db", list(annotation.METABOLITE_ANNOTATIONS))
@annotate(title="Wrong Metabolite Annotations Per Database",
          format_type="percent", message=dict(), data=dict(), metric=dict())
def test_metabolite_annotation_wrong_ids(read_only_model, db):
    """
    Expect all annotations of metabolites to be in the correct format.

    To identify databases and the identifiers belonging to them, computational
    tools rely on the presence of specific patterns. Only when these patterns
    can be identified consistently is an ID truly machine-readable. This test
    checks if the database cross-references in metabolite annotations conform
    to patterns defined according to the MIRIAM guidelines, i.e. matching
    those that are defined at https://identifiers.org/.

    The required formats, i.e., regex patterns are further outlined in
    `annotation.py`. This test does not carry out a web query for the composed
    URI, it merely controls that the regex patterns match the identifiers.
    """
    ann = test_metabolite_annotation_wrong_ids.annotation
    ann["data"][db] = total = get_ids(
        set(read_only_model.metabolites).difference(
            annotation.generate_component_annotation_overview(
                read_only_model.metabolites, db)))
    ann["metric"][db] = 1.0
    ann["message"][db] = wrapper.fill(
        """There are no metabolite annotations for the {} database.
        """.format(db))
    assert len(total) > 0, ann["message"][db]
    ann["data"][db] = get_ids(
        annotation.generate_component_annotation_miriam_match(
            read_only_model.metabolites, "metabolites", db))
    ann["metric"][db] = len(ann["data"][db]) / len(total)
    ann["message"][db] = wrapper.fill(
        """The provided metabolite annotations for the {} database do not match
        the regular expression patterns defined on identifiers.org. A total of
        {} metabolite annotations ({:.2%}) needs to be fixed: {}""".format(
            db, len(ann["data"][db]), ann["metric"][db],
            truncate(ann["data"][db])))
    assert len(ann["data"][db]) == 0, ann["message"][db]


@pytest.mark.parametrize("db", annotation.REACTION_ANNOTATIONS)
@annotate(title="Wrong Reaction Annotations Per Database",
          format_type="percent", message=dict(), data=dict(), metric=dict())
def test_reaction_annotation_wrong_ids(read_only_model, db):
    """
    Expect all annotations of reactions to be in the correct format.

    To identify databases and the identifiers belonging to them, computational
    tools rely on the presence of specific patterns. Only when these patterns
    can be identified consistently is an ID truly machine-readable. This test
    checks if the database cross-references in reaction annotations conform
    to patterns defined according to the MIRIAM guidelines, i.e. matching
    those that are defined at https://identifiers.org/.

    The required formats, i.e., regex patterns are further outlined in
    `annotation.py`. This test does not carry out a web query for the composed
    URI, it merely controls that the regex patterns match the identifiers.
    """
    ann = test_reaction_annotation_wrong_ids.annotation
    ann["data"][db] = total = get_ids(
        set(read_only_model.reactions).difference(
            annotation.generate_component_annotation_overview(
                read_only_model.reactions, db)))
    ann["metric"][db] = 1.0
    ann["message"][db] = wrapper.fill(
        """There are no reaction annotations for the {} database.
        """.format(db))
    assert len(total) > 0, ann["message"][db]
    ann["data"][db] = get_ids(
        annotation.generate_component_annotation_miriam_match(
            read_only_model.reactions, "reactions", db))
    ann["metric"][db] = len(ann["data"][db]) / len(read_only_model.reactions)
    ann["message"][db] = wrapper.fill(
        """The provided reaction annotations for the {} database do not match
        the regular expression patterns defined on identifiers.org. A total of
        {} reaction annotations ({:.2%}) needs to be fixed: {}""".format(
            db, len(ann["data"][db]), ann["metric"][db],
            truncate(ann["data"][db])))
    assert len(ann["data"][db]) == 0, ann["message"][db]


@pytest.mark.parametrize("db", annotation.GENE_PRODUCT_ANNOTATIONS)
@annotate(title="Wrong Gene Annotations Per Database",
          format_type="percent", message=dict(), data=dict(), metric=dict())
def test_gene_product_annotation_wrong_ids(read_only_model, db):
    """
    Expect all annotations of genes/gene-products to be in the correct format.

    To identify databases and the identifiers belonging to them, computational
    tools rely on the presence of specific patterns. Only when these patterns
    can be identified consistently is an ID truly machine-readable. This test
    checks if the database cross-references in reaction annotations conform
    to patterns defined according to the MIRIAM guidelines, i.e. matching
    those that are defined at https://identifiers.org/.

    The required formats, i.e., regex patterns are further outlined in
    `annotation.py`. This test does not carry out a web query for the composed
    URI, it merely controls that the regex patterns match the identifiers.
    """
    ann = test_gene_product_annotation_wrong_ids.annotation
    ann["data"][db] = total = get_ids(
        set(read_only_model.genes).difference(
            annotation.generate_component_annotation_overview(
                read_only_model.genes, db)))
    ann["metric"][db] = 1.0
    ann["message"][db] = wrapper.fill(
        """There are no gene annotations for the {} database.
        """.format(db))
    assert len(total) > 0, ann["message"][db]
    ann["data"][db] = get_ids(
        annotation.generate_component_annotation_miriam_match(
            read_only_model.genes, "genes", db))
    ann["metric"][db] = len(ann["data"][db]) / len(read_only_model.genes)
    ann["message"][db] = wrapper.fill(
        """The provided gene/gene-product annotations for the {} database do
        not match the regular expression patterns defined on identifiers.org.
        A total of {} gene product annotations ({:.2%}) needs to be
        fixed: {}""".format(
            db, len(ann["data"][db]), ann["metric"][db],
            truncate(ann["data"][db])))
    assert len(ann["data"][db]) == 0, ann["message"][db]


@annotate(title="Uniform Metabolite Identifier Namespace", format_type="count")
def test_metabolite_id_namespace_consistency(read_only_model):
    """
    Expect metabolite identifiers to be from the same namespace.

    In well-annotated models it is no problem if the pool of main identifiers
    for metabolites consists of identifiers from several databases. However,
    in models that lack appropriate annotations, it may hamper the ability of
    other researchers to use it. Running the model through a computational
    pipeline may be difficult without first consolidating the namespace.

    Hence, this test checks if the main metabolite identifiers can be
    attributed to one single namespace based on the regex patterns defined at
    https://identifiers.org/
    """
    ann = test_metabolite_id_namespace_consistency.annotation
    overview = annotation.generate_component_id_namespace_overview(
        read_only_model, "metabolites")
    distribution = overview.sum()
    cols = list(distribution.index)
    largest = distribution[cols].idxmax()
    if largest != 'bigg.metabolite':
        warn(wrapper.fill(
            """memote currently only supports syntax checks for BiGG
            identifiers. Please consider mapping your IDs from {} to BiGG
            """.format(largest)))
    # Assume that all identifiers match the largest namespace.
    ann["data"] = list(set(get_ids(read_only_model.metabolites)).difference(
        overview[overview[largest]].index.tolist()))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """{} metabolite identifiers ({:.2%}) do not match the largest found
        namespace ({}): {}""".format(
            len(ann["data"]), ann["metric"], largest, truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Uniform Metabolite Identifier Namespace", format_type="count")
def test_reaction_id_namespace_consistency(read_only_model):
    """
    Expect reaction identifiers to be from the same namespace.

    In well-annotated models it is no problem if the pool of main identifiers
    for reactions consists of identifiers from several databases. However,
    in models that lack appropriate annotations, it may hamper the ability of
    other researchers to use it. Running the model through a computational
    pipeline may be difficult without first consolidating the namespace.

    Hence, this test checks if the main reaction identifiers can be
    attributed to one single namespace based on the regex patterns defined at
    https://identifiers.org/
    """
    ann = test_reaction_id_namespace_consistency.annotation
    overview = annotation.generate_component_id_namespace_overview(
        read_only_model, "reactions")
    distribution = overview.sum()
    cols = list(distribution.index)
    largest = distribution[cols].idxmax()
    if largest != 'bigg.reaction':
        warn(wrapper.fill(
            """memote currently only supports syntax checks for BiGG
            identifiers. Please consider mapping your IDs from {} to BiGG
            """.format(largest)))
    # Assume that all identifiers match the largest namespace.
    ann["data"] = list(set(get_ids(read_only_model.reactions)).difference(
        overview[overview[largest]].index.tolist()))
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """{} reaction identifiers ({:.2%}) do not match the largest found
        namespace ({}): {}""".format(
            len(ann["data"]), ann["metric"], largest, truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]
