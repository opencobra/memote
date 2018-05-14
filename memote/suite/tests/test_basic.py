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

"""Perform basic tests on an instance of ``cobra.Model``."""

from __future__ import absolute_import, division

import memote.support.basic as basic
import memote.support.helpers as helpers
from memote.utils import (
    annotate, get_ids, get_ids_and_bounds, truncate, wrapper)


@annotate(title="Model Identifier", format_type="raw")
def test_model_id_presence(read_only_model):
    """
    Expect that the model has an identifier.

    The MIRIAM guidelines require a model to be identified via an ID.
    While it is not required, the ID will be displayed on the memote
    reports, which helps to distinguish the output clearly.
    """
    ann = test_model_id_presence.annotation
    assert hasattr(read_only_model, "id")
    ann["data"] = read_only_model.id
    assert bool(read_only_model.id)


@annotate(title="Total Number of Genes", format_type="count")
def test_genes_presence(read_only_model):
    """
    Expect that at least one gene is defined in the model.

    A metabolic model can still be a useful tool without any
    genes, however there are certain methods which rely on the presence of
    genes and, more importantly, the corresponding gene-protein-reaction
    rules. This test requires that there is at least one gene defined.
    """
    ann = test_genes_presence.annotation
    assert hasattr(read_only_model, "genes")
    ann["data"] = get_ids(read_only_model.genes)
    ann["message"] = "{:d} genes are defined in the model.".format(
        len(ann["data"]))
    assert len(ann["data"]) >= 1, ann["message"]


@annotate(title="Total Number of Reactions", format_type="count")
def test_reactions_presence(read_only_model):
    """
    Expect that at least one reaction is defined in the model.

    To be useful a metabolic model should consist at least of a few reactions.
    This test simply checks if there are more than zero reactions.
    """
    ann = test_reactions_presence.annotation
    assert hasattr(read_only_model, "reactions")
    ann["data"] = get_ids(read_only_model.reactions)
    ann["message"] = "{:d} reactions are defined in the model.".format(
        len(ann["data"]))
    assert len(ann["data"]) >= 1, ann["message"]


@annotate(title="Total Number of Metabolites", format_type="count")
def test_metabolites_presence(read_only_model):
    """
    Expect that at least one metabolite is defined in the model.

    To be useful a metabolic model should consist at least of a few
    metabolites that are converted by reactions.
    This test simply checks if there are more than zero metabolites.
    """
    ann = test_metabolites_presence.annotation
    assert hasattr(read_only_model, "metabolites")
    ann["data"] = get_ids(read_only_model.metabolites)
    ann["message"] = "{:d} metabolites are defined in the model.".format(
        len(ann["data"]))
    assert len(ann["data"]) >= 1, ann["message"]


@annotate(title="Metabolites without Formula", format_type="count")
def test_metabolites_formula_presence(read_only_model):
    """
    Expect all metabolites to have a formula.

    To be able to ensure that reactions are mass-balanced, all model
    metabolites ought to be provided with a chemical formula.
    """
    ann = test_metabolites_formula_presence.annotation
    ann["data"] = get_ids(
        basic.check_metabolites_formula_presence(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """There are a total of {}
        metabolites ({:.2%}) without a formula: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Metabolites without Charge", format_type="count")
def test_metabolites_charge_presence(read_only_model):
    """
    Expect all metabolites to have charge information.

    To be able to ensure that reactions are charge-balanced, all model
    metabolites ought to be provided with a charge.
    """
    ann = test_metabolites_charge_presence.annotation
    ann["data"] = get_ids(
        basic.check_metabolites_charge_presence(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """There are a total of {}
        metabolites ({:.2%}) without a charge: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Reactions without GPR", format_type="count")
def test_gene_protein_reaction_rule_presence(read_only_model):
    """
    Expect all non-exchange reactions to have a GPR rule.

    Gene-Protein-Reaction rules express which gene has what function.
    The presence of this annotation is important to justify the existence
    of reactions in the model, and is required to conduct in silico gene
    deletion studies. However, reactions without GPR may also be valid:
    Spontaneous reactions, or known reactions with yet undiscovered genes
    likely lack GPR.
    """
    ann = test_gene_protein_reaction_rule_presence.annotation
    missing_gpr_metabolic_rxns = set(
        basic.check_gene_protein_reaction_rule_presence(read_only_model)
    ).difference(set(read_only_model.exchanges))
    ann["data"] = get_ids(missing_gpr_metabolic_rxns)
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """There are a total of {} reactions ({:.2%}) without GPR:
        {}""".format(len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Non-Growth Associated Maintenance Reaction",
          format_type="count")
def test_ngam_presence(read_only_model):
    """
    Expect a single non growth-associated maintenance reaction.

    The Non-Growth Associated Maintenance reaction (NGAM) is an
    ATP-hydrolysis reaction added to metabolic models to represent energy
    expenses that the cell invests in continuous processes independent of
    the growth rate.
    """
    ann = test_ngam_presence.annotation
    ann["data"] = get_ids(basic.find_ngam(read_only_model))
    ann["message"] = wrapper.fill(
        """A total of {} NGAM reactions could be identified:
        {}""".format(len(ann["data"]), truncate(ann["data"])))
    assert len(ann["data"]) == 1, ann["message"]


@annotate(title="Metabolic Coverage", format_type="percent")
def test_metabolic_coverage(read_only_model):
    u"""
    Expect a model to have a metabolic coverage >= 1.

    The degree of metabolic coverage indicates the modeling detail of a
    given reconstruction calculated by dividing the total amount of
    reactions by the amount of genes. Models with a 'high level of modeling
    detail have ratios >1, and models with a low level of detail have
    ratios <1. This difference arises as models with basic or intermediate
    levels of detail are assumed to include many reactions in which several
    gene products and their enzymatic transformations are ‘lumped’.
    """
    ann = test_metabolic_coverage.annotation
    ann["data"] = (len(read_only_model.reactions), len(read_only_model.genes))
    ann["metric"] = basic.calculate_metabolic_coverage(read_only_model)
    ann["message"] = wrapper.fill(
        """The degree of metabolic coverage is {:.2}.""".format(ann["metric"]))
    assert ann["metric"] >= 1, ann["message"]


@annotate(title="Total Number of Compartments", format_type="count")
def test_compartments_presence(read_only_model):
    """
    Expect that more than two compartments are defined in the model.

    While simplified metabolic models may be perfectly viable, generally
    across the tree of life organisms contain at least one distinct
    compartment: the cytosol or cytoplasm. In the case of prokaryotes there is
    usually a periplasm, and eurkaryotes are more complex. In addition to the
    internal compartment, a metabolic model also reflects the extracellular
    environment i.e. the medium/ metabolic context in which the modelled cells
    grow. Hence, in total, at least two compartments can be expected from a
    metabolic model.
    """
    # TODO: Fix the test in a later PR! Should expect 2 compartments instead!
    ann = test_compartments_presence.annotation
    assert hasattr(read_only_model, "compartments")
    ann["data"] = list(read_only_model.get_metabolite_compartments())
    ann["message"] = wrapper.fill(
        """A total of {:d} compartments are defined in the model: {}""".format(
            len(ann["data"]), truncate(ann["data"])))
    assert len(ann["data"]) >= 3, ann["message"]


@annotate(title="Number of Enzyme Complexes", format_type="count")
def test_protein_complex_presence(read_only_model):
    """
    Expect that more than one enzyme complex is present in the model.

    Based on the gene-protein-reaction (GPR) rules, it is possible to infer
    whether a reaction is catalyzed by a single gene product, isozymes or by a
    heteromeric protein complex. This test checks that at least one
    such protein complex is defined in the GPR of the model. For S. cerevisiae
    it could be shown that "essential proteins tend to [cluster] together in
    essential complexes" (https://doi.org/10.1074%2Fmcp.M800490-MCP200).

    This might also be a relevant metric for other organisms.
    """
    ann = test_protein_complex_presence.annotation
    ann["data"] = list(basic.find_protein_complexes(read_only_model))
    ann["message"] = wrapper.fill(
        """A total of {:d} protein complexes are defined through GPR rules in
        the model.""".format(len(ann["data"])))
    assert len(ann["data"]) >= 1, ann["message"]


@annotate(title="Number of Purely Metabolic Reactions", format_type="count")
def test_find_pure_metabolic_reactions(read_only_model):
    """
    Expect at least one pure metabolic reaction to be defined in the model.

    If a reaction is neither a transport reaction, a biomass reaction nor a
    boundary reaction, it is counted as a purely metabolic reaction. This test
    requires the presence of metabolite formula to be able to identify
    transport reactions. This test is passed when the model contains at least
    one purely metabolic reaction i.e. a conversion of one metabolite into
    another.
    """
    ann = test_find_pure_metabolic_reactions.annotation
    ann["data"] = get_ids(
        basic.find_pure_metabolic_reactions(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """A total of {:d} ({:.2%}) purely metabolic reactions are defined in
        the model, this excludes transporters, exchanges, or pseudo-reactions:
        {}""".format(len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) >= 1, ann["message"]


@annotate(title="Number of Purely Metabolic Reactions with Constraints",
          format_type="count")
def test_find_constrained_pure_metabolic_reactions(read_only_model):
    """
    Expect zero or more purely metabolic reactions to have fixed constraints.

    If a reaction is neither a transport reaction, a biomass reaction nor a
    boundary reaction, it is counted as a purely metabolic reaction. This test
    requires the presence of metabolite formula to be able to identify
    transport reactions. This test simply reports the number of purely
    metabolic reactions that have fixed constraints and does not have any
    mandatory 'pass' criteria.
    """
    ann = test_find_constrained_pure_metabolic_reactions.annotation
    pmr = basic.find_pure_metabolic_reactions(read_only_model)
    ann["data"] = get_ids_and_bounds(
        [rxn for rxn in pmr if basic.is_constrained_reaction(
            read_only_model, rxn)])
    ann["metric"] = len(ann["data"]) / len(pmr)
    ann["message"] = wrapper.fill(
        """A total of {:d} ({:.2%}) purely metabolic reactions have fixed
        constraints in the model, this excludes transporters, exchanges, or
        pseudo-reactions: {}""".format(len(ann["data"]), ann["metric"],
                                       truncate(ann["data"])))


@annotate(title="Number of Transport Reactions", format_type="count")
def test_find_transport_reactions(read_only_model):
    """
    Expect >= 1 transport reactions are present in the read_only_model.

    Cellular metabolism in any organism usually involves the transport of
    metabolites across a lipid bi-layer. This test reports how many
    of these reactions, which transports metabolites from one compartment
    to another, are present in the model, as at least one transport reaction
    must be present for cells to take up nutrients and/or excrete waste.

    A transport reaction is defined as follows:
    1. It contains metabolites from at least 2 compartments and
    2. at least 1 metabolite undergoes no chemical reaction, i.e.,
    the formula and/or annotation stays the same on both sides of the equation.

    A notable exception is transport via PTS, which also contains the following
    restriction:
    3. The transported metabolite(s) are transported into a compartment through
    the exchange of a phosphate.

    An example of tranport via PTS would be
    pep(c) + glucose(e) -> glucose-6-phosphate(c) + pyr(c)

    Reactions similar to transport via PTS (referred to as "modified transport
    reactions") follow a similar pattern:
    A(x) + B-R(y) -> A-R(y) + B(y)

    Such modified transport reactions can be detected, but only when a formula
    field exists for all metabolites in a particular reaction. If this is not
    the case, transport reactions are identified through annotations, which
    cannot detect modified tranport reactions.

    """
    ann = test_find_transport_reactions.annotation
    ann["data"] = get_ids(helpers.find_transport_reactions(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """A total of {:d} ({:.2%}) transport reactions are defined in the
        model, this excludes purely metabolic reactions, exchanges, or
        pseudo-reactions: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) >= 1, ann["message"]


@annotate(title="Number of Tranport Reactions with Constraints",
          format_type="count")
def test_find_constrained_transport_reactions(read_only_model):
    """
    Expect zero or more transport reactions to have fixed constraints.

    Cellular metabolism in any organism usually involves the transport of
    metabolites across a lipid bi-layer. Hence, this test reports how many
    of these reactions, which transports metabolites from one compartment
    to another, have fixed constraints. This test does not have any mandatory
    'pass' criteria.

    A transport reaction is defined as follows:
    1. It contains metabolites from at least 2 compartments and
    2. at least 1 metabolite undergoes no chemical reaction, i.e.,
    the formula and/or annotation stays the same on both sides of the equation.

    A notable exception is transport via PTS, which also contains the following
    restriction:
    3. The transported metabolite(s) are transported into a compartment through
    the exchange of a phosphate.

    An example of tranport via PTS would be
    pep(c) + glucose(e) -> glucose-6-phosphate(c) + pyr(c)

    Reactions similar to transport via PTS (referred to as "modified transport
    reactions") follow a similar pattern:
    A(x) + B-R(y) -> A-R(y) + B(y)

    Such modified transport reactions can be detected, but only when a formula
    field exists for all metabolites in a particular reaction. If this is not
    the case, transport reactions are identified through annotations, which
    cannot detect modified tranport reactions.
    """
    ann = test_find_constrained_transport_reactions.annotation
    transporters = helpers.find_transport_reactions(read_only_model)
    ann["data"] = get_ids_and_bounds(
        [rxn for rxn in transporters if basic.is_constrained_reaction(
            read_only_model, rxn)])
    ann["metric"] = len(ann["data"]) / len(transporters)
    ann["message"] = wrapper.fill(
        """A total of {:d} ({:.2%}) transport reactions have fixed
        constraints in the model: {}""".format(len(ann["data"]), ann["metric"],
                                               truncate(ann["data"])))


@annotate(title="Fraction of Transport Reactions without GPR",
          format_type="percent")
def test_transport_reaction_gpr_presence(read_only_model):
    """
    Expect a small fraction of transport reactions not to have a GPR rule.

    As it is hard to identify the exact transport processes within a cell,
    transport reactions are often added purely for modeling purposes.
    Highlighting where assumptions have been made vs where
    there is proof may help direct the efforts to improve transport and
    transport energetics of the tested metabolic model.
    However, transport reactions without GPR may also be valid:
    Diffusion, or known reactions with yet undiscovered genes likely lack GPR.
    """
    # TODO: Update threshold with improved insight from meta study.
    ann = test_transport_reaction_gpr_presence.annotation
    ann["data"] = get_ids(
        basic.check_transport_reaction_gpr_presence(read_only_model)
    )
    ann["metric"] = len(ann["data"]) / len(
        helpers.find_transport_reactions(read_only_model)
    )
    ann["message"] = wrapper.fill(
        """There are a total of {} transport reactions ({:.2%} of all
        transport reactions) without GPR:
        {}""".format(len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert ann["metric"] < 0.2, ann["message"]


@annotate(title="Number of Reversible Oxygen-Containing Reactions",
          format_type="count")
def test_find_reversible_oxygen_reactions(read_only_model):
    """
    Expect zero or more oxygen-containing reactions to be reversible.

    The directionality of oxygen-producing/-consuming reactions affects the
    model's ability to grow anaerobically i.e. create faux-anaerobic organisms.
    This test reports how many of these oxygen-containing reactions are
    reversible. This test does not have any mandatory 'pass' criteria.

    """
    ann = test_find_reversible_oxygen_reactions.annotation
    o2_rxns = basic.find_oxygen_reactions(read_only_model)
    ann["data"] = get_ids([rxn for rxn in o2_rxns if rxn.reversibility])
    ann["metric"] = len(ann["data"]) / len(o2_rxns)
    ann["message"] = wrapper.fill(
        """There are a total of {} reversible oxygen-containing reactions
        ({:.2%} of all oxygen-containing reactions): {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))


@annotate(title="Number of Unique Metabolites", format_type="count")
def test_find_unique_metabolites(read_only_model):
    """
    Expect there to be less metabolites when removing compartment tag.

    Metabolites may be transported into different compartments, which means
    that in a compartimentalized model the number of metabolites may be
    much higher than in a model with no compartments. This test counts only
    one occurrence of each metabolite and returns this as the number of unique
    metabolites. The test expects that the model is compartimentalized, and
    thus, that the number of unique metabolites is generally lower than the
    total number of metabolites.
    """
    ann = test_find_unique_metabolites.annotation
    ann["data"] = list(basic.find_unique_metabolites(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.metabolites)
    ann["message"] = wrapper.fill(
        """Not counting the same entities in other compartments, there is a
        total of {} ({:.2%}) unique metabolites in the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])))
    assert len(ann["data"]) < len(read_only_model.metabolites), ann["message"]


@annotate(title="Number of Duplicate Metabolites in Identical Compartments",
          format_type="count")
def test_find_duplicate_metabolites_in_compartments(read_only_model):
    """
    Expect there to be zero duplicate metabolites in the same compartments.

    The main reason for having this test is to clean up merged models or models
    from automated reconstruction pipelines as these are prone to having
    identical metabolites from different namespaces (hence different IDs). This
    test therefore expects that every metabolite in any particular compartment
    has unique inchikey values.
    """
    ann = test_find_duplicate_metabolites_in_compartments.annotation
    ann["data"] = basic.find_duplicate_metabolites_in_compartments(
        read_only_model)
    ann["message"] = wrapper.fill(
        """There are a total of {} metabolites in the model which
        have duplicates in the same compartment: {}""".format(
            len(ann["data"]), truncate(ann["data"])))
    assert len(ann["data"]) == 0, ann["message"]
