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

from __future__ import absolute_import

from warnings import warn
from builtins import dict

from pandas import DataFrame

import memote.support.annotation as annotation
from memote.support.helpers import df2dict


def test_metabolite_annotation_presence(read_only_model, store):
    """Expect all metabolites to have a non-empty annotation attribute."""
    store["metabolites_without_annotation"] = [
        met.id for met in annotation.find_components_without_annotation(
            read_only_model, "metabolites")]
    assert len(store["metabolites_without_annotation"]) == 0, \
        "The following metabolites lack any form of annotation: " \
        "{}".format(", ".join(store["metabolites_without_annotation"]))


def test_reaction_annotation_presence(read_only_model, store):
    """Expect all reactions to have a non-empty annotation attribute."""
    store["reactions_without_annotation"] = [
        rxn.id for rxn in annotation.find_components_without_annotation(
            read_only_model, "reactions")]
    assert len(store["reactions_without_annotation"]) == 0, \
        "The following reactions lack any form of annotation: " \
        "{}".format(", ".join(store["reactions_without_annotation"]))


def test_metabolite_annotation_overview(read_only_model, store):
    """
    Expect all metabolites to have annotations from common databases.

    The required databases are outlined in `annotation.py`.
    """
    overview = annotation.generate_component_annotation_overview(
        read_only_model, "metabolites")
    store['met_annotation_overview'] = df2dict(overview)
    for db in annotation.METABOLITE_ANNOTATIONS:
        sub = overview.loc[~overview[db], db]
        assert len(sub) == 0, \
            "The following metabolites lack annotation for {}: " \
            "{}".format(db, ", ".join(sub.index))


def test_reaction_annotation_overview(read_only_model, store):
    """
    Expect all reactions to have annotations from common databases.

    The required databases are outlined in `annotation.py`.
    """
    overview = annotation.generate_component_annotation_overview(
        read_only_model, "reactions")
    store['rxn_annotation_overview'] = df2dict(overview)
    for db in annotation.REACTION_ANNOTATIONS:
        sub = overview.loc[~overview[db], db]
        assert len(sub) == 0, \
            "The following reactions lack annotation for {}: " \
            "{}".format(db, ", ".join(sub.index))


def test_metabolite_annotation_wrong_ids(read_only_model, store):
    """
    Expect all annotations of metabolites to be in the correct format.

    The required formats, i.e., regex patterns are outlined in `annotation.py`.
    """
    has_annotation = annotation.generate_component_annotation_overview(
        read_only_model, "metabolites")
    matches = annotation.generate_component_annotation_miriam_match(
        read_only_model, "metabolites")
    wrong = DataFrame(has_annotation.values & (~matches.values),
                      index=has_annotation.index,
                      columns=has_annotation.columns)
    store['met_wrong_annotation_ids'] = df2dict(wrong)
    for db in annotation.METABOLITE_ANNOTATIONS:
        sub = wrong.loc[wrong[db], db]
        assert len(sub) == 0, \
            "The following metabolites use wrong IDs for {}: " \
            "{}".format(db, ", ".join(sub.index))


def test_reaction_annotation_wrong_ids(read_only_model, store):
    """
    Expect all annotations of reactions to be in the correct format.

    The required formats, i.e., regex patterns are outlined in `annotation.py`.
    """
    has_annotation = annotation.generate_component_annotation_overview(
        read_only_model, "reactions")
    matches = annotation.generate_component_annotation_miriam_match(
        read_only_model, "reactions")
    wrong = DataFrame(has_annotation.values & (~matches.values),
                      index=has_annotation.index,
                      columns=has_annotation.columns)
    store["rxn_wrong_annotation_ids"] = df2dict(wrong)
    for db in annotation.REACTION_ANNOTATIONS:
        sub = wrong.loc[wrong[db], db]
        assert len(sub) == 0, \
            "The following reactions use wrong IDs for {}: " \
            "{}".format(db, ", ".join(sub.index))


def test_metabolite_id_namespace_consistency(read_only_model, store):
    """Expect metabolite IDs to be from the same namespace."""
    met_id_ns = annotation.generate_component_id_namespace_overview(
        read_only_model, "metabolites")
    distribution = met_id_ns.sum()
    store['met_ids_in_each_namespace'] = dict(
        (key, int(val)) for key, val in distribution.iteritems())
    # The BioCyc regex is extremely general, we ignore it here.
    cols = list(distribution.index)
    cols.remove('biocyc')
    largest = distribution[cols].idxmax()
    if distribution[largest] == 0:
        largest = 'biocyc'
    if largest != 'bigg.metabolite':
        warn(
            'memote currently only supports syntax checks for BiGG identifiers.'
            ' Please consider mapping your IDs from {} to BiGG'
            ''.format(largest)
        )
    assert distribution[largest] == len(read_only_model.metabolites), \
        "Metabolite IDs that don't belong to the largest fraction: {}"\
        "".format(met_id_ns.loc[~met_id_ns[largest], largest].index)


def test_reaction_id_namespace_consistency(read_only_model, store):
    """Expect reaction IDs to be from the same namespace."""
    rxn_id_ns = annotation.generate_component_id_namespace_overview(
        read_only_model, "reactions")
    distribution = rxn_id_ns.sum()
    store['rxn_ids_in_each_namespace'] = dict(
        (key, int(val)) for key, val in distribution.iteritems())
    # The BioCyc regex is extremely general, we ignore it here.
    cols = list(distribution.index)
    cols.remove('biocyc')
    largest = distribution[cols].idxmax()
    if distribution[largest] == 0:
        largest = 'biocyc'
    if largest != 'bigg.reaction':
        warn(
            'memote currently only supports syntax checks for BiGG identifiers.'
            ' Please consider mapping your IDs from {} to BiGG'
            ''.format(largest)
        )
    assert distribution[largest] == len(read_only_model.metabolites), \
        "Reaction IDs that don't belong to the largest fraction: {}" \
        "".format(rxn_id_ns.loc[~rxn_id_ns[largest], largest].index)
