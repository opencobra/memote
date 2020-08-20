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

"""Tests performed on the annotations of an instance of ``cobra.Model``."""

from __future__ import absolute_import, division

from builtins import dict

import pytest

import memote.support.annotation as annotation
from memote.utils import annotate, get_ids, truncate, wrapper


@annotate(title="Presence of Metabolite Annotation", format_type="count")
def test_metabolite_annotation_presence(model):
    """
    Expect all metabolites to have a non-empty annotation attribute.

    This test checks if any annotations at all are present in the SBML
    annotations field for each metabolite, irrespective of the type of
    annotation i.e. specific database  cross-references, ontology terms,
    additional information. For this test to pass the model is expected to
    have metabolites and each of them should have some form of annotation.

    Implementation:
    Check if the annotation attribute of each cobra.Metabolite object of the
    model is unset or empty.

    """
    ann = test_metabolite_annotation_presence.annotation
    ann["data"] = get_ids(
        annotation.find_components_without_annotation(model, "metabolites")
    )
    ann["metric"] = len(ann["data"]) / len(model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} metabolites ({:.2%}) lack any form of annotation:
        {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Presence of Reaction Annotation", format_type="count")
def test_reaction_annotation_presence(model):
    """
    Expect all reactions to have a non-empty annotation attribute.

    This test checks if any annotations at all are present in the SBML
    annotations field for each reaction, irrespective of the type of
    annotation i.e. specific database  cross-references, ontology terms,
    additional information. For this test to pass the model is expected to
    have reactions and each of them should have some form of annotation.

    Implementation:
    Check if the annotation attribute of each cobra.Reaction object of the
    model is unset or empty.

    """
    ann = test_reaction_annotation_presence.annotation
    ann["data"] = get_ids(
        annotation.find_components_without_annotation(model, "reactions")
    )
    ann["metric"] = len(ann["data"]) / len(model.reactions)
    ann["message"] = wrapper.fill(
        """A total of {} reactions ({:.2%}) lack any form of annotation:
        {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Presence of Gene Annotation", format_type="count")
def test_gene_product_annotation_presence(model):
    """
    Expect all genes to have a non-empty annotation attribute.

    This test checks if any annotations at all are present in the SBML
    annotations field (extended by FBC package) for each gene product,
    irrespective of the type of annotation i.e. specific database,
    cross-references, ontology terms, additional information. For this test to
    pass the model is expected to have genes and each of them should have some
    form of annotation.

    Implementation:
    Check if the annotation attribute of each cobra.Gene object of the
    model is unset or empty.

    """
    ann = test_gene_product_annotation_presence.annotation
    ann["data"] = get_ids(annotation.find_components_without_annotation(model, "genes"))
    ann["metric"] = len(ann["data"]) / len(model.genes)
    ann["message"] = wrapper.fill(
        """A total of {} genes ({:.2%}) lack any form of
        annotation: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@pytest.mark.parametrize("db", list(annotation.METABOLITE_ANNOTATIONS))
@annotate(
    title="Metabolite Annotations Per Database",
    format_type="percent",
    message=dict(),
    data=dict(),
    metric=dict(),
)
def test_metabolite_annotation_overview(model, db):
    """
    Expect all metabolites to have annotations from common databases.

    Specific database cross-references are paramount to mapping information.
    To provide references to as many databases as possible helps to make the
    metabolic model more accessible to other researchers. This does not only
    facilitate the use of a model in a broad array of computational pipelines,
    it also promotes the metabolic model itself to become an organism-specific
    knowledge base.

    For this test to pass, each metabolite annotation should contain
    cross-references to a number of databases. The currently selection is
    listed in `annotation.py`, but an ongoing discussion can be found at
    https://github.com/opencobra/memote/issues/332. For each database this
    test checks for the presence of its corresponding namespace ID to comply
    with the MIRIAM guidelines i.e. they have to match those defined on
    https://identifiers.org/.

    Since each database is quite different and some potentially incomplete, it
    may not be feasible to achieve 100% coverage for each of them. Generally
    it should be possible, however, to obtain cross-references to at least
    one of the databases for all metabolites consistently.

    Implementation:
    Check if the keys of the annotation attribute of each cobra.Metabolite of
    the model match with a selection of common biochemical databases. The
    annotation  attribute of cobrapy components is a dictionary of
    key:value pairs.

    """
    ann = test_metabolite_annotation_overview.annotation
    ann["data"][db] = get_ids(
        annotation.generate_component_annotation_overview(model.metabolites, db)
    )
    ann["metric"][db] = len(ann["data"][db]) / len(model.metabolites)
    ann["message"][db] = wrapper.fill(
        """The following {} metabolites ({:.2%}) lack annotation for {}:
        {}""".format(
            len(ann["data"][db]), ann["metric"][db], db, truncate(ann["data"][db])
        )
    )
    assert len(ann["data"][db]) == 0, ann["message"][db]


@pytest.mark.parametrize("db", list(annotation.REACTION_ANNOTATIONS))
@annotate(
    title="Reaction Annotations Per Database",
    format_type="percent",
    message=dict(),
    data=dict(),
    metric=dict(),
)
def test_reaction_annotation_overview(model, db):
    """
    Expect all reactions to have annotations from common databases.

    Specific database cross-references are paramount to mapping information.
    To provide references to as many databases as possible helps to make the
    metabolic model more accessible to other researchers. This does not only
    facilitate the use of a model in a broad array of computational pipelines,
    it also promotes the metabolic model itself to become an organism-specific
    knowledge base.

    For this test to pass, each reaction annotation should contain
    cross-references to a number of databases. The currently selection is
    listed in `annotation.py`, but an ongoing discussion can be found at
    https://github.com/opencobra/memote/issues/332. For each database this
    test checks for the presence of its corresponding namespace ID to comply
    with the MIRIAM guidelines i.e. they have to match those defined on
    https://identifiers.org/.

    Since each database is quite different and some potentially incomplete, it
    may not be feasible to achieve 100% coverage for each of them. Generally
    it should be possible, however, to obtain cross-references to at least
    one of the databases for all reactions consistently.

    Implementation:
    Check if the keys of the annotation attribute of each cobra.Reaction of
    the model match with a selection of common biochemical databases. The
    annotation  attribute of cobrapy components is a dictionary of
    key:value pairs.

    """
    ann = test_reaction_annotation_overview.annotation
    ann["data"][db] = get_ids(
        annotation.generate_component_annotation_overview(model.reactions, db)
    )
    ann["metric"][db] = len(ann["data"][db]) / len(model.reactions)
    ann["message"][db] = wrapper.fill(
        """The following {} reactions ({:.2%}) lack annotation for {}:
        {}""".format(
            len(ann["data"][db]), ann["metric"][db], db, truncate(ann["data"][db])
        )
    )
    assert len(ann["data"][db]) == 0, ann["message"][db]


@pytest.mark.parametrize("db", list(annotation.GENE_PRODUCT_ANNOTATIONS))
@annotate(
    title="Gene Annotations Per Database",
    format_type="percent",
    message=dict(),
    data=dict(),
    metric=dict(),
)
def test_gene_product_annotation_overview(model, db):
    """
    Expect all genes to have annotations from common databases.

    Specific database cross-references are paramount to mapping information.
    To provide references to as many databases as possible helps to make the
    metabolic model more accessible to other researchers. This does not only
    facilitate the use of a model in a broad array of computational pipelines,
    it also promotes the metabolic model itself to become an organism-specific
    knowledge base.

    For this test to pass, each gene annotation should contain
    cross-references to a number of databases. The currently selection is
    listed in `annotation.py`, but an ongoing discussion can be found at
    https://github.com/opencobra/memote/issues/332. For each database this
    test checks for the presence of its corresponding namespace ID to comply
    with the MIRIAM guidelines i.e. they have to match those defined on
    https://identifiers.org/.

    Since each database is quite different and some potentially incomplete, it
    may not be feasible to achieve 100% coverage for each of them. Generally
    it should be possible, however, to obtain cross-references to at least
    one of the databases for all gene products consistently.

    Implementation:
    Check if the keys of the annotation attribute of each cobra.Gene of
    the model match with a selection of common genome databases. The
    annotation  attribute of cobrapy components is a dictionary of
    key:value pairs.

    """
    ann = test_gene_product_annotation_overview.annotation
    ann["data"][db] = get_ids(
        annotation.generate_component_annotation_overview(model.genes, db)
    )
    ann["metric"][db] = len(ann["data"][db]) / len(model.genes)
    ann["message"][db] = wrapper.fill(
        """The following {} genes ({:.2%}) lack annotation for {}:
        {}""".format(
            len(ann["data"][db]), ann["metric"][db], db, truncate(ann["data"][db])
        )
    )
    assert len(ann["data"][db]) == 0, ann["message"][db]


@pytest.mark.parametrize("db", list(annotation.METABOLITE_ANNOTATIONS))
@annotate(
    title="Metabolite Annotation Conformity Per Database",
    format_type="percent",
    message=dict(),
    data=dict(),
    metric=dict(),
)
def test_metabolite_annotation_wrong_ids(model, db):
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

    Implementation:
    For those metabolites whose annotation keys match any of the tested
    databases, check if the corresponding values match the identifier pattern
    of each database.

    """
    ann = test_metabolite_annotation_wrong_ids.annotation
    ann["data"][db] = total = get_ids(
        set(model.metabolites).difference(
            annotation.generate_component_annotation_overview(model.metabolites, db)
        )
    )
    ann["metric"][db] = 1.0
    ann["message"][db] = wrapper.fill(
        """There are no metabolite annotations for the {} database.
        """.format(
            db
        )
    )
    assert len(total) > 0, ann["message"][db]
    ann["data"][db] = get_ids(
        annotation.generate_component_annotation_miriam_match(
            model.metabolites, "metabolites", db
        )
    )
    ann["metric"][db] = len(ann["data"][db]) / len(total)
    ann["message"][db] = wrapper.fill(
        """A total of {} metabolite annotations ({:.2%}) do not match the
        regular expression patterns defined on identifiers.org for the {}
        database: {}""".format(
            len(ann["data"][db]), ann["metric"][db], db, truncate(ann["data"][db])
        )
    )
    assert len(ann["data"][db]) == 0, ann["message"][db]


@pytest.mark.parametrize("db", annotation.REACTION_ANNOTATIONS)
@annotate(
    title="Reaction Annotation Conformity Per Database",
    format_type="percent",
    message=dict(),
    data=dict(),
    metric=dict(),
)
def test_reaction_annotation_wrong_ids(model, db):
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

    Implementation:
    For those reaction whose annotation keys match any of the tested
    databases, check if the corresponding values match the identifier pattern
    of each database.

    """
    ann = test_reaction_annotation_wrong_ids.annotation
    ann["data"][db] = total = get_ids(
        set(model.reactions).difference(
            annotation.generate_component_annotation_overview(model.reactions, db)
        )
    )
    ann["metric"][db] = 1.0
    ann["message"][db] = wrapper.fill(
        """There are no reaction annotations for the {} database.
        """.format(
            db
        )
    )
    assert len(total) > 0, ann["message"][db]
    ann["data"][db] = get_ids(
        annotation.generate_component_annotation_miriam_match(
            model.reactions, "reactions", db
        )
    )
    ann["metric"][db] = len(ann["data"][db]) / len(model.reactions)
    ann["message"][db] = wrapper.fill(
        """A total of {} reaction annotations ({:.2%}) do not match the
        regular expression patterns defined on identifiers.org for the {}
        database: {}""".format(
            len(ann["data"][db]), ann["metric"][db], db, truncate(ann["data"][db])
        )
    )
    assert len(ann["data"][db]) == 0, ann["message"][db]


@pytest.mark.parametrize("db", annotation.GENE_PRODUCT_ANNOTATIONS)
@annotate(
    title="Gene Annotation Conformity Per Database",
    format_type="percent",
    message=dict(),
    data=dict(),
    metric=dict(),
)
def test_gene_product_annotation_wrong_ids(model, db):
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

    Implementation:
    For those genes whose annotation keys match any of the tested
    databases, check if the corresponding values match the identifier pattern
    of each database.

    """
    ann = test_gene_product_annotation_wrong_ids.annotation
    ann["data"][db] = total = get_ids(
        set(model.genes).difference(
            annotation.generate_component_annotation_overview(model.genes, db)
        )
    )
    ann["metric"][db] = 1.0
    ann["message"][db] = wrapper.fill(
        """There are no gene annotations for the {} database.
        """.format(
            db
        )
    )
    assert len(total) > 0, ann["message"][db]
    ann["data"][db] = get_ids(
        annotation.generate_component_annotation_miriam_match(model.genes, "genes", db)
    )
    ann["metric"][db] = len(ann["data"][db]) / len(model.genes)
    ann["message"][db] = wrapper.fill(
        """A total of {} gene annotations ({:.2%}) do not match the
        regular expression patterns defined on identifiers.org for the {}
        database: {}""".format(
            len(ann["data"][db]), ann["metric"][db], db, truncate(ann["data"][db])
        )
    )
    assert len(ann["data"][db]) == 0, ann["message"][db]


@annotate(title="Uniform Metabolite Identifier Namespace", format_type="count")
def test_metabolite_id_namespace_consistency(model):
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

    Implementation:
    Generate a table with each column corresponding to one
    database from the selection and each row to a metabolite identifier. A
    Boolean entry indicates whether the identifier matches the regular
    expression of the corresponding database. Since the Biocyc pattern matches
    broadly, we assume that any instance of an identifier matching to Biocyc
    AND any other database pattern is a false positive match for Biocyc and
    thus set it to ``false``. Sum the positive matches for each database and
    assume that the largest set is the 'main' identifier namespace.

    """
    ann = test_metabolite_id_namespace_consistency.annotation
    overview = annotation.generate_component_id_namespace_overview(model, "metabolites")
    distribution = overview.sum()
    cols = list(distribution.index)
    largest = distribution[cols].idxmax()
    # Assume that all identifiers match the largest namespace.
    ann["data"] = list(
        set(get_ids(model.metabolites)).difference(
            overview[overview[largest]].index.tolist()
        )
    )
    ann["metric"] = len(ann["data"]) / len(model.metabolites)
    ann["message"] = wrapper.fill(
        """{} metabolite identifiers ({:.2%}) deviate from the largest found
        namespace ({}): {}""".format(
            len(ann["data"]), ann["metric"], largest, truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Uniform Reaction Identifier Namespace", format_type="count")
def test_reaction_id_namespace_consistency(model):
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

    Implementation:
    Generate a pandas.DataFrame with each column corresponding to one
    database from the selection and each row to the reaction ID. A boolean
    entry indicates whether the metabolite ID matches the regex pattern
    of the corresponding database. Since the Biocyc pattern matches quite,
    assume that any instance of an identifier matching to Biocyc
    AND any other DB pattern is a false positive match for Biocyc and then set
    the boolean to ``false``. Sum the positive matches for each database and
    assume that the largest set is the 'main' identifier namespace.

    """
    ann = test_reaction_id_namespace_consistency.annotation
    overview = annotation.generate_component_id_namespace_overview(model, "reactions")
    distribution = overview.sum()
    cols = list(distribution.index)
    largest = distribution[cols].idxmax()
    # Assume that all identifiers match the largest namespace.
    ann["data"] = list(
        set(get_ids(model.reactions)).difference(
            overview[overview[largest]].index.tolist()
        )
    )
    ann["metric"] = len(ann["data"]) / len(model.reactions)
    ann["message"] = wrapper.fill(
        """{} reaction identifiers ({:.2%}) deviate from the largest found
        namespace ({}): {}""".format(
            len(ann["data"]), ann["metric"], largest, truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]
