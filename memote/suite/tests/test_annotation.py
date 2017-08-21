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
from pandas import DataFrame

import memote.support.annotation as annotation
from memote.support.helpers import df2dict
from memote.utils import annotate, truncate, get_ids, wrapper


@annotate(title="Metabolites without Annotation", type="length")
def test_metabolite_annotation_presence(read_only_model):
    """Expect all metabolites to have a non-empty annotation attribute."""
    ann = test_metabolite_annotation_presence.annotation
    ann["data"] = get_ids(annotation.find_components_without_annotation(
        read_only_model, "metabolites"))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} metabolites ({:.2%}) lack any form of annotation: 
        {}""".format(len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Reactions without Annotation", type="integer")
def test_reaction_annotation_presence(read_only_model):
    """Expect all reactions to have a non-empty annotation attribute."""
    ann = test_reaction_annotation_presence.annotation
    ann["data"] = get_ids(annotation.find_components_without_annotation(
            read_only_model, "reactions"))
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """A total of {} reactions ({:.2%}) lack any form of annotation: 
        {}""".format(len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@pytest.mark.parametrize("db", list(annotation.METABOLITE_ANNOTATIONS))
@annotate(title="Missing Metabolite Annotations Per Database",
          type="object", message=dict(), data=dict(), metric=dict())
def test_metabolite_annotation_overview(read_only_model, db):
    """
    Expect all metabolites to have annotations from common databases.

    The required databases are outlined in `annotation.py`.
    """
    ann = test_metabolite_annotation_overview.annotation
    ann["data"][db] = get_ids(annotation.generate_component_annotation_overview(
        read_only_model.metabolites, db))
    # TODO: metric must also be a dict in this case.
    ann["metric"][db] = len(ann["data"][db]) / len(read_only_model.metabolites)
    ann["message"][db] = wrapper.fill(
        """The following {} metabolites ({:.2%}) lack annotation for {}: 
        {}""".format(len(ann["data"][db]), ann["metric"][db], db,
                     truncate(ann["data"][db])))
    assert len(ann["data"][db]) == 0, ann["message"][db]


@pytest.mark.parametrize("db", list(annotation.REACTION_ANNOTATIONS))
@annotate(title="Missing Reaction Annotations Per Database",
          type="object", message=dict(), data=dict(), metric=dict())
def test_reaction_annotation_overview(read_only_model, db):
    """
    Expect all reactions to have annotations from common databases.

    The required databases are outlined in `annotation.py`.
    """
    ann = test_reaction_annotation_overview.annotation
    ann["data"][db] = get_ids(annotation.generate_component_annotation_overview(
        read_only_model.reactions, db))
    ann["metric"][db] = len(ann["data"][db]) / len(read_only_model.reactions)
    ann["message"][db] = wrapper.fill(
        """The following {} reactions ({:.2%}) lack annotation for {}: 
        {}""".format(len(ann["data"][db]), ann["metric"][db], db,
                     truncate(ann["data"][db])))
    assert len(ann["data"][db]) == 0, ann["message"][db]


@pytest.mark.parametrize("db", list(annotation.METABOLITE_ANNOTATIONS))
@annotate(title="Wrong Metabolite Annotations Per Database",
          type="object", message=dict(), data=dict(), metric=dict())
def test_metabolite_annotation_wrong_ids(read_only_model, db):
    """
    Expect all annotations of metabolites to be in the correct format.

    The required formats, i.e., regex patterns are outlined in `annotation.py`.
    """
    ann = test_metabolite_annotation_wrong_ids.annotation
    ann["data"][db] = get_ids(
        annotation.generate_component_annotation_miriam_match(
            read_only_model.metabolites, "metabolites", db))
    ann["metric"][db] = len(ann["data"][db]) / len(read_only_model.metabolites)
    ann["message"][db] = wrapper.fill(
        """The provided metabolite annotations for the {} database do not match 
        the regular expression patterns defined on identifiers.org. A total of 
        {} metabolite annotations ({:.2%}) needs to be fixed: {}""".format(
            db, len(ann["data"][db]), ann["metric"][db],
            truncate(ann["data"][db])))
    assert len(ann["data"][db]) == 0, ann["message"][db]


@pytest.mark.parametrize("db", annotation.REACTION_ANNOTATIONS)
@annotate(title="Wrong Reaction Annotations Per Database",
          type="object", message=dict(), data=dict(), metric=dict())
def test_reaction_annotation_wrong_ids(read_only_model, db):
    """
    Expect all annotations of reactions to be in the correct format.

    The required formats, i.e., regex patterns are outlined in `annotation.py`.
    """
    ann = test_reaction_annotation_wrong_ids.annotation
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


@annotate(title="Uniform Metabolite Identifier Namespace", type="length")
def test_metabolite_id_namespace_consistency(read_only_model):
    """Expect metabolite identifiers to be from the same namespace."""
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
    ann["data"] = overview[overview[largest]].index.tolist()
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """{} metabolite identifiers ({:.2%}) do not match the largest found 
        namespace ({}): {}""".format(
            len(ann["data"]), ann["metric"], largest, truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Uniform Metabolite Identifier Namespace", type="length")
def test_reaction_id_namespace_consistency(read_only_model):
    """Expect reaction identifiers to be from the same namespace."""
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
    ann["data"] = overview[overview[largest]].index.tolist()
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """{} reaction identifiers ({:.2%}) do not match the largest found 
        namespace ({}): {}""".format(
            len(ann["data"]), ann["metric"], largest, truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]
