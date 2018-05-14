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

import pytest

import memote.support.basic as basic
import memote.support.helpers as helpers
import memote.support.sbo as sbo

from memote.utils import annotate, truncate, get_ids, wrapper


@annotate(title="Metabolites without SBO-Term Annotation", format_type="count")
def test_metabolite_sbo_presence(read_only_model):
    """Expect all metabolites to have a some form of SBO-Term annotation.

    The Systems Biology Ontology (SBO) allows researchers to annotate a model
    with terms which indicate the intended function of its individual
    components. The available terms are controlled and relational and can be
    viewed here http://www.ebi.ac.uk/sbo/main/tree.
    """
    ann = test_metabolite_sbo_presence.annotation
    ann["data"] = get_ids(sbo.find_components_without_sbo_terms(
        read_only_model, "metabolites"))
    try:
        ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
        ann["message"] = wrapper.fill(
            """A total of {} metabolites ({:.2%}) lack annotation with any type
            of SBO term: {}""".format(
                len(ann["data"]), ann["metric"], truncate(ann["data"])))
    except ZeroDivisionError:
        ann["metric"] = 1.0
        ann["message"] = "The model has no metabolites."
        pytest.skip(ann["message"])
    assert len(ann["data"]) == len(read_only_model.metabolites), ann["message"]


@annotate(title="Reactions without SBO-Term Annotation", format_type="count")
def test_reaction_sbo_presence(read_only_model):
    """Expect all reactions to have a some form of SBO-Term annotation.

    The Systems Biology Ontology (SBO) allows researchers to annotate a model
    with terms which indicate the intended function of its individual
    components. The available terms are controlled and relational and can be
    viewed here http://www.ebi.ac.uk/sbo/main/tree.
    """
    ann = test_reaction_sbo_presence.annotation
    ann["data"] = get_ids(sbo.find_components_without_sbo_terms(
        read_only_model, "reactions"))
    try:
        ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
        ann["message"] = wrapper.fill(
            """A total of {} reactions ({:.2%}) lack annotation with any type
            of SBO term: {}""".format(
                len(ann["data"]), ann["metric"], truncate(ann["data"])))
    except ZeroDivisionError:
        ann["metric"] = 1.0
        ann["message"] = "The model has no reactions."
        pytest.skip(ann["message"])
    assert len(ann["data"]) == len(read_only_model.reactions), ann["message"]


@annotate(title="Genes without SBO-Term Annotation", format_type="count")
def test_gene_sbo_presence(read_only_model):
    """Expect all genes to have a some form of SBO-Term annotation.

    The Systems Biology Ontology (SBO) allows researchers to annotate a model
    with terms which indicate the intended function of its individual
    components. The available terms are controlled and relational and can be
    viewed here http://www.ebi.ac.uk/sbo/main/tree.
    """
    ann = test_gene_sbo_presence.annotation
    ann["data"] = get_ids(sbo.find_components_without_sbo_terms(
        read_only_model, "genes"))
    try:
        ann["metric"] = len(ann["data"]) / len(read_only_model.genes)
        ann["message"] = wrapper.fill(
            """A total of {} genes ({:.2%}) lack annotation with any type of
            SBO term: {}""".format(
                len(ann["data"]), ann["metric"], truncate(ann["data"])))
    except ZeroDivisionError:
        ann["metric"] = 1.0
        ann["message"] = "The model has no genes."
        pytest.skip(ann["message"])
    assert len(ann["data"]) == len(read_only_model.genes), ann["message"]


@annotate(title="Metabolic Reactions without SBO:0000176", format_type="count")
def test_metabolic_reaction_specific_sbo_presence(read_only_model):
    """Expect all metabolic reactions to be annotated with SBO:0000176.

    SBO:0000176 represents the term 'biochemical reaction'. Every metabolic
    reaction that is not a transport or boundary reaction should be annotated
    with this. The results shown are relative to the total amount of pure
    metabolic reactions.
    """
    ann = test_metabolic_reaction_specific_sbo_presence.annotation
    pure = basic.find_pure_metabolic_reactions(read_only_model)
    ann["data"] = get_ids(sbo.check_component_for_specific_sbo_term(
        pure, "SBO:0000176"))
    try:
        ann["metric"] = len(ann["data"]) / len(pure)
        ann["message"] = wrapper.fill(
            """A total of {} metabolic reactions ({:.2%} of all purely
            metabolic reactions) lack annotation with the SBO term
            "SBO:0000176" for 'biochemical reaction': {}""".format(
                len(ann["data"]), ann["metric"], truncate(ann["data"])))
    except ZeroDivisionError:
        ann["metric"] = 1.0
        ann["message"] = "The model has no metabolic reactions."
        pytest.skip(ann["message"])
    assert len(ann["data"]) == len(pure), ann["message"]


@annotate(title="Transport Reactions without SBO:0000185", format_type="count")
def test_transport_reaction_specific_sbo_presence(read_only_model):
    """Expect all transport reactions to be annotated properly.

    'SBO:0000185', 'SBO:0000588', 'SBO:0000587', 'SBO:0000655', 'SBO:0000654',
    'SBO:0000660', 'SBO:0000659', 'SBO:0000657', and 'SBO:0000658' represent
    the terms 'transport reaction' and 'translocation reaction', in addition
    to their children (more specific transport reaction labels). Every
    transport reaction that is not a pure metabolic or boundary reaction should
    be annotated with one of these terms. The results shown are relative to the
    total of all transport reactions.
    """
    sbo_transport_terms = helpers.TRANSPORT_RXN_SBO_TERMS
    ann = test_transport_reaction_specific_sbo_presence.annotation
    transports = helpers.find_transport_reactions(read_only_model)
    ann["data"] = get_ids(sbo.check_component_for_specific_sbo_term(
        transports, sbo_transport_terms))
    try:
        ann["metric"] = len(ann["data"]) / len(transports)
        ann["message"] = wrapper.fill(
            """A total of {} metabolic reactions ({:.2%} of all transport
            reactions) lack annotation with one of the SBO terms: {} for
            'biochemical reaction': {}""".format(
                len(ann["data"]), ann["metric"], sbo_transport_terms,
                truncate(ann["data"])))
    except ZeroDivisionError:
        ann["metric"] = 1.0
        ann["message"] = "The model has no transport reactions."
        pytest.skip(ann["message"])
    assert len(ann["data"]) == len(transports), ann["message"]


@annotate(title="Metabolites without SBO:0000247", format_type="count")
def test_metabolite_specific_sbo_presence(read_only_model):
    """Expect all metabolites to be annotated with SBO:0000247.

    SBO:0000247 represents the term 'simple chemical'. Every metabolite should
    be annotated with this.
    """
    ann = test_metabolite_specific_sbo_presence.annotation
    ann["data"] = get_ids(sbo.check_component_for_specific_sbo_term(
        read_only_model.metabolites, "SBO:0000247"))
    try:
        ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
        ann["message"] = wrapper.fill(
            """A total of {} transport reactions ({:.2%} of all metabolites)
            lack annotation with the SBO term "SBO:0000247" for
            'simple chemical': {}""".format(
                len(ann["data"]), ann["metric"], truncate(ann["data"])))
    except ZeroDivisionError:
        ann["metric"] = 1.0
        ann["message"] = "The model has no metabolites."
        pytest.skip(ann["message"])
    assert len(ann["data"]) == len(read_only_model.metabolites), ann["message"]


@annotate(title="Genes without SBO:0000243", format_type="count")
def test_gene_specific_sbo_presence(read_only_model):
    """Expect all genes to be annotated with SBO:0000243.

    SBO:0000243 represents the term 'gene'. Every gene should
    be annotated with this.
    """
    ann = test_gene_specific_sbo_presence.annotation
    ann["data"] = get_ids(sbo.check_component_for_specific_sbo_term(
        read_only_model.genes, "SBO:0000243"))
    try:
        ann["metric"] = len(ann["data"]) / len(read_only_model.genes)
        ann["message"] = wrapper.fill(
            """A total of {} genes ({:.2%} of all genes) lack
            annotation with the SBO term "SBO:0000243" for
            'gene': {}""".format(
                len(ann["data"]), ann["metric"], truncate(ann["data"])))
    except ZeroDivisionError:
        ann["metric"] = 1.0
        ann["message"] = "The model has no genes."
        pytest.skip(ann["message"])
    assert len(ann["data"]) == len(read_only_model.genes), ann["message"]


@annotate(title="Exchange reactions without SBO:0000627", format_type="count")
def test_exchange_specific_sbo_presence(read_only_model):
    """Expect all exchange reactions to be annotated with SBO:0000627.

    SBO:0000627 represents the term 'exchange reaction'. The Systems Biology
    Ontology defines an exchange reaction as follows: 'A modeling process to
    provide matter influx or efflux to a model, for example to replenish a
    metabolic network with raw materials (eg carbon / energy sources). Such
    reactions are conceptual, created solely for modeling purposes, and do not
    have a  physical correspondence. Exchange reactions, often represented as
    'R_EX_', can operate in the negative (uptake) direction or positive
    (secretion) direction. By convention, a negative flux through an exchange
    reaction represents uptake of the corresponding metabolite, and a positive
    flux represent discharge.' Every exchange reaction should be annotated with
    this. Exchange reactions differ from demand reactions in that the
    metabolites are removed from or added to the extracellular
    environment only.
    """
    ann = test_exchange_specific_sbo_presence.annotation
    exchanges = helpers.find_exchange_rxns(read_only_model)
    ann["data"] = get_ids(sbo.check_component_for_specific_sbo_term(
        exchanges, "SBO:0000627"))
    try:
        ann["metric"] = len(ann["data"]) / len(exchanges)
        ann["message"] = wrapper.fill(
            """A total of {} exchange reactions ({:.2%} of all exchange
            reactions) lack annotation with the SBO term "SBO:0000627" for
            'exchange reaction': {}""".format(
                len(ann["data"]), ann["metric"], truncate(ann["data"])))
    except ZeroDivisionError:
        ann["metric"] = 1.0
        ann["message"] = "The model has no exchange reactions."
        pytest.skip(ann["message"])
    assert len(ann["data"]) == len(exchanges), ann["message"]


@annotate(title="Demand reactions without SBO:0000628", format_type="count")
def test_demand_specific_sbo_presence(read_only_model):
    """Expect all demand reactions to be annotated with SBO:0000627.

    SBO:0000628 represents the term 'demand reaction'. The Systems Biology
    Ontology defines an exchange reaction as follows: 'A modeling process
    analogous to exchange reaction, but which operates upon "internal"
    metabolites. Metabolites that are consumed by these reactions are assumed
    to be used in intra-cellular processes that are not part of the model.
    Demand reactions, often represented 'R_DM_', can also deliver metabolites
    (from intra-cellular processes that are not considered in the model).'
    Every demand reaction should be annotated with
    this. Demand reactions differ from exchange reactions in that the
    metabolites are not removed from the extracellular environment, but from
    any of the organism's compartments. Demand reactions differ from sink
    reactions in that they are designated as irreversible.
    """
    ann = test_demand_specific_sbo_presence.annotation
    demands = helpers.find_demand_reactions(read_only_model)
    ann["data"] = get_ids(sbo.check_component_for_specific_sbo_term(
        demands, "SBO:0000628"))
    try:
        ann["metric"] = len(ann["data"]) / len(demands)
        ann["message"] = wrapper.fill(
            """A total of {} genes ({:.2%} of all demand reactions) lack
            annotation with the SBO term "SBO:0000628" for
            'demand reaction': {}""".format(
                len(ann["data"]), ann["metric"], truncate(ann["data"])))
    except ZeroDivisionError:
        ann["metric"] = 1.0
        ann["message"] = "The model has no demand reactions."
        pytest.skip(ann["message"])
    assert len(ann["data"]) == len(demands), ann["message"]


@annotate(title="Sink reactions without SBO:0000632", format_type="count")
def test_sink_specific_sbo_presence(read_only_model):
    """Expect all sink reactions to be annotated with SBO:0000632.

    SBO:0000632 represents the term 'sink reaction'. The Systems Biology
    Ontology defines an exchange reaction as follows: 'A modeling process to
    provide matter influx or efflux to a model, for example to replenish a
    metabolic network with raw materials (eg carbon / energy sources). Such
    reactions are conceptual, created solely for modeling purposes, and do not
    have a physical correspondence. Unlike the analogous demand (SBO:....)
    reactions, which are usually designated as irreversible, sink reactions
    always represent a reversible uptake/secretion processes, and act as a
    metabolite source with no cost to the cell. Sink reactions, also referred
    to as R_SINK_, are generally used for compounds that are metabolized by
    the cell but are produced by non-metabolic, un-modeled cellular processes.'
    Every sink reaction should be annotated with
    this. Sink reactions differ from exchange reactions in that the metabolites
    are not removed from the extracellular environment, but from any of the
    organism's compartments.
    """
    ann = test_sink_specific_sbo_presence.annotation
    sinks = helpers.find_sink_reactions(read_only_model)
    ann["data"] = get_ids(sbo.check_component_for_specific_sbo_term(
        sinks, "SBO:0000632"))
    try:
        ann["metric"] = len(ann["data"]) / len(sinks)
    except ZeroDivisionError:
        ann["metric"] = 1.0
        ann["message"] = "No sink reactions found."
        pytest.skip(ann["message"])
    ann["message"] = wrapper.fill(
        """A total of {} genes ({:.2%} of all sink reactions) lack
        annotation with the SBO term "SBO:0000632" for
        'sink reaction': {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        ))
    assert len(ann["data"]) == len(sinks), ann["message"]


@annotate(title="Biomass reactions without SBO:0000629", format_type="count")
def test_biomass_specific_sbo_presence(read_only_model):
    """Expect all biomass reactions to be annotated with SBO:0000629.

    SBO:0000629 represents the term 'biomass production'. The Systems Biology
    Ontology defines an exchange reaction as follows: 'Biomass production,
    often represented 'R_BIOMASS_', is usually the optimization target reaction
    of constraint-based models, and can consume multiple reactants to produce
    multiple products. It is also assumed that parts of the reactants are also
    consumed in unrepresented processes and hence products do not have to
    reflect all the atom composition of the reactants. Formulation of a
    biomass production process entails definition of the macromolecular
    content (eg. cellular protein fraction), metabolic constitution of
    each fraction (eg. amino acids), and subsequently the atomic composition
    (eg. nitrogen atoms). More complex biomass functions can additionally
    incorporate details of essential vitamins and cofactors required for
    growth.'
    Every reaction representing the biomass production should be annotated with
    this.
    """
    ann = test_biomass_specific_sbo_presence.annotation
    biomass = helpers.find_biomass_reaction(read_only_model)
    ann["data"] = get_ids(sbo.check_component_for_specific_sbo_term(
        biomass, "SBO:0000629"))
    try:
        ann["metric"] = len(ann["data"]) / len(biomass)
    except ZeroDivisionError:
        ann["metric"] = 1.0
        ann["message"] = "No biomass reactions found."
        pytest.skip(ann["message"])
    ann["message"] = wrapper.fill(
        """A total of {} biomass reactions ({:.2%} of all biomass reactions)
        lack annotation with the SBO term "SBO:0000629" for
        'biomass production': {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        ))
    assert len(ann["data"]) == len(biomass), ann["message"]
