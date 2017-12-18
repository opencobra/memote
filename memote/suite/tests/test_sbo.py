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

"""Tests for SBO terms performed on an instance of ``cobra.Model``."""

from __future__ import absolute_import, division

import memote.support.basic as basic
import memote.support.helpers as helpers

import memote.support.annotation as annotation
from memote.utils import annotate, truncate, get_ids, wrapper


@annotate(title="Metabolites without SBO-Term Annotation", type="length")
def test_metabolite_sbo_presence(read_only_model):
    """Expect all metabolites to have a some form of SBO-Term annotation.

    The Systems Biology Ontology (SBO) allows researchers to annotate a model
    with terms which indicate the intended function of its individual
    components. The available terms are controlled and relational and can be
    viewed here http://www.ebi.ac.uk/sbo/main/tree.
    """
    ann = test_metabolite_sbo_presence.annotation
    ann["data"] = get_ids(annotation.find_components_without_sbo_terms(
        read_only_model, "metabolites"))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} metabolites ({:.2%}) lack annotation with any type of
        SBO term: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        ))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Reactions without SBO-Term Annotation", type="length")
def test_reaction_sbo_presence(read_only_model):
    """Expect all reactions to have a some form of SBO-Term annotation.

    The Systems Biology Ontology (SBO) allows researchers to annotate a model
    with terms which indicate the intended function of its individual
    components. The available terms are controlled and relational and can be
    viewed here http://www.ebi.ac.uk/sbo/main/tree.
    """
    ann = test_reaction_sbo_presence.annotation
    ann["data"] = get_ids(annotation.find_components_without_sbo_terms(
        read_only_model, "reactions"))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} reactions ({:.2%}) lack annotation with any type of
        SBO term: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        ))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Genes without SBO-Term Annotation", type="length")
def test_reaction_sbo_presence(read_only_model):
    """Expect all genes to have a some form of SBO-Term annotation.

    The Systems Biology Ontology (SBO) allows researchers to annotate a model
    with terms which indicate the intended function of its individual
    components. The available terms are controlled and relational and can be
    viewed here http://www.ebi.ac.uk/sbo/main/tree.
    """
    ann = test_reaction_sbo_presence.annotation
    ann["data"] = get_ids(annotation.find_components_without_sbo_terms(
        read_only_model, "genes"))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """A total of {} genes ({:.2%}) lack annotation with any type of
        SBO term: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        ))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Metabolic Reactions without SBO:0000176", type="length")
def test_metabolic_reaction_sbo_presence(read_only_model):
    """Expect all metabolic reactions to be annotated with SBO:0000176.

    SBO:0000176 represents the term 'biochemical reaction'. Every metabolic
    reaction that is not a transport or boundary reaction should be annotated
    with this. The results shown are relative to the total amount of pure
    metabolic reactions.
    """
    ann = test_metabolic_reaction_sbo_presence.annotation
    ann["data"] = get_ids(sbo.check_component_for_specific_sbo_term(
        basic.find_pure_metabolic_reactions(read_only_model)) "SBO:0000176"))
    ann["metric"] = len(ann["data"]) / len(
    basic.find_pure_metabolic_reactions(read_only_model))
    ann["message"] = wrapper.fill(
        """A total of {} metabolic reactions ({:.2%}) lack annotation with the
        SBO term "SBO:0000176" for 'biochemical reaction': {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        ))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Transport Reactions without SBO:0000185", type="length")
def test_transport_reaction_sbo_presence(read_only_model):
    """Expect all transport reactions to be annotated with SBO:0000185.

    SBO:0000185 represents the term 'transport reaction'. Every transport
    reaction that is not a pure metabolic or boundary reaction should be
    annotated with this. The results shown are relative to the total of all
    transport reactions.
    """
    ann = test_transport_reaction_sbo_presence.annotation
    ann["data"] = get_ids(sbo.check_component_for_specific_sbo_term(
        helpers.find_transport_reactions(read_only_model)) "SBO:0000185"))
    ann["metric"] = len(ann["data"]) / len(
    basic.find_transport_reactions(read_only_model))
    ann["message"] = wrapper.fill(
        """A total of {} transport reactions ({:.2%}) lack annotation with the
        SBO term "SBO:0000185" for 'transport reaction': {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        ))
    assert len(ann["data"]) == 0, ann["message"]
