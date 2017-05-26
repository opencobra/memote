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

"""Annotation tests performed on an instance of `cobra.Model`."""

from __future__ import absolute_import

from warnings import warn
import memote.support.annotation as annotation
from memote.support.helpers import get_difference


def test_mets_without_annotation(read_only_model, store):
    """Expect all metabolites to have a non-zero annotation attribute."""
    store["metabolites_without_annotations"] = [
        met.id for met in annotation.find_met_without_annotations(
            read_only_model)]
    assert len(store["metabolites_without_annotations"]) == 0, \
        "The following metabolites lack any form of annotation: " \
        "{}".format(", ".join(store["metabolites_without_annotations"]))


def test_rxns_without_annotation(read_only_model, store):
    """Expect all reactions to have a non-zero annotation attribute."""
    store["reactions_without_annotations"] = [
        rxn.id for rxn in annotation.find_rxn_without_annotations(
            read_only_model)]
    assert len(store["reactions_without_annotations"]) == 0, \
        "The following reactions lack any form of annotation: " \
        "{}".format(", ".join(store["reactions_without_annotations"]))


def test_mets_annotation_overview(read_only_model, store):
    """
    Expect all mets to have annotations from common databases.

    The required databases are outlined in annotation.py.
    """
    store['met_annotation_overview'] = \
        annotation.generate_met_annotation_overview(read_only_model)
    for db_id in annotation.METABOLITE_ANNOTATIONS:
        assert \
            len(store['met_annotation_overview'][db_id]) == 0, \
            "The following metabolites lack annotation for {}: " \
            "{}".format(
                db_id, ", ".join(store['met_annotation_overview'][db_id])
            )


def test_rxns_annotation_overview(read_only_model, store):
    """
    Expect all rxns to have annotations from common databases.

    The required databases are outlined in annotation.py.
    """
    store['rxn_annotation_overview'] = \
        annotation.generate_rxn_annotation_overview(read_only_model)
    for db_id in annotation.REACTION_ANNOTATIONS:
        assert \
            len(store['rxn_annotation_overview'][db_id]) == 0, \
            "The following reactions lack annotation for {}: " \
            "{}".format(
                db_id, ", ".join(store['rxn_annotation_overview'][db_id])
            )


def test_met_wrong_annotation_ids(read_only_model, store):
    """
    Expect all annotations of metabolites to be in the correct format.

    The required formats i.e. regex patterns are outlined in annotation.py.
    """
    met_annotation_overview = \
        annotation.generate_met_annotation_overview(read_only_model)
    store['met_wrong_annotation_ids'] = annotation.find_wrong_annotation_ids(
        read_only_model,
        met_annotation_overview,
        "met"
    )
    for db_id in annotation.METABOLITE_ANNOTATIONS:
        assert \
            len(store['met_wrong_annotation_ids'][db_id]) == \
            len(
                get_difference(
                    met_annotation_overview[db_id],
                    read_only_model,
                    "met"
                )
            ), "The following metabolites use wrong IDs for {}: " \
            "{}".format(
                db_id, ", ".join(store['met_wrong_annotation_ids'][db_id])
            )


def test_rxn_wrong_annotation_ids(read_only_model, store):
    """
    Expect all annotations of reactions to be in the correct format.

    The required formats i.e. regex patterns are outlined in annotation.py.
    """
    rxn_annotation_overview = \
        annotation.generate_rxn_annotation_overview(read_only_model)
    store['rxn_wrong_annotation_ids'] = annotation.find_wrong_annotation_ids(
        read_only_model,
        rxn_annotation_overview,
        "rxn"
    )
    for db_id in annotation.REACTION_ANNOTATIONS:
        assert \
            len(store['rxn_wrong_annotation_ids'][db_id]) == \
            len(
                get_difference(
                    rxn_annotation_overview[db_id],
                    read_only_model,
                    "rxn"
                )
            ), "The following reactions use wrong IDs for {}: " \
            "{}".format(
                db_id, ", ".join(store['rxn_wrong_annotation_ids'][db_id])
            )


def test_met_id_namespace_consistency(read_only_model, store):
    """
    Expect metabolite IDs to be from the same namespace.
    """
    met_id_namespace = annotation.collect_met_id_namespace(read_only_model)
    distribution = met_id_namespace[met_id_namespace == 1].count()
    store['met_ids_in_each_namespace'] = \
        {item: list(met_id_namespace[met_id_namespace[item] == 1].index)
         for item in distribution.index}
    store['met_id_namespace_largest_fraction'] = distribution.idxmax()
    if store['met_id_namespace_largest_fraction'] != 'bigg.metabolite':
        warn(
            'Memote currently only supports syntax checks for BiGG database '
            'IDs. Please consider mapping your IDs from {} to BiGG'.format(
                store['met_id_namespace_largest_fraction']
            )
        )
    assert \
        len(
            store['met_ids_in_each_namespace']
            [store['met_id_namespace_largest_fraction']]
        ) == len(read_only_model.metabolites), \
        "Metabolite IDs that don't belong to the largest fraction: {}".format(
            [db_id + ":" + ", ".join(store['ids_in_each_namespace'][db_id])
                for db_id in store['met_ids_in_each_namespace'].keys()
                if store['met_ids_in_each_namespace'][db_id] != [] and
                db_id != [store['met_id_namespace_largest_fraction']]]
        )


def test_rxn_id_namespace_consistency(read_only_model, store):
    """
    Expect reaction IDs to be from the same namespace.
    """
    rxn_id_namespace = annotation.collect_rxn_id_namespace(read_only_model)
    distribution = rxn_id_namespace[rxn_id_namespace == 1].count()
    store['rxn_ids_in_each_namespace'] = \
        {item: list(met_id_namespace[rxn_id_namespace[item] == 1].index)
         for item in distribution.index}
    store['rxn_id_namespace_largest_fraction'] = distribution.idxmax()
    if store['met_id_namespace_largest_fraction'] != 'bigg.reaction':
        warn(
            'Memote currently only supports syntax checks for BiGG database '
            'IDs. Please consider mapping your IDs from {} to BiGG'.format(
                store['met_id_namespace_largest_fraction']
            )
        )
    assert \
        len(
            store['rxn_ids_in_each_namespace']
            [store['rxn_id_namespace_largest_fraction']]
        ) == len(read_only_model.metabolites), \
        "Reaction IDs that don't belong to the largest fraction: {}".format(
            [db_id + ":" + ", ".join(store['rxn_ids_in_each_namespace'][db_id])
                for db_id in store['rxn_ids_in_each_namespace'].keys()
                if store['rxn_ids_in_each_namespace'][db_id] != [] and
                db_id != [store['rxn_id_namespace_largest_fraction']]]
        )
