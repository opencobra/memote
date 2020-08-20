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
from memote.utils import annotate, get_ids, get_ids_and_bounds, truncate, wrapper


@annotate(title="Model Identifier", format_type="raw")
def test_model_id_presence(model):
    """
    Expect that the model has an identifier.

    The MIRIAM guidelines require a model to be identified via an ID.
    Further, the ID will be displayed on the memote snapshot
    report, which helps to distinguish the output clearly.

    Implementation:
    Check if the cobra.Model object has a non-empty "id"
    attribute, this value is parsed from the "id" attribute of the <model> tag
    in the SBML file e.g. <model fbc:strict="true" id="iJO1366">.

    """
    ann = test_model_id_presence.annotation
    assert hasattr(model, "id")
    ann["data"] = model.id
    ann["metric"] = 1.0 - float(bool(ann["data"]))
    ann["message"] = "The model ID is {}".format(ann["data"])
    assert bool(model.id)


@annotate(title="Total Genes", format_type="count")
def test_genes_presence(model):
    """
    Expect that at least one gene is defined in the model.

    A metabolic model can still be a useful tool without any
    genes, however there are certain methods which rely on the presence of
    genes and, more importantly, the corresponding gene-protein-reaction
    rules. This test requires that there is at least one gene defined.

    Implementation:
    Check if the cobra.Model object has non-empty "genes"
    attribute, this list is populated from the list of fbc:listOfGeneProducts
    which should contain at least one fbc:geneProduct.

    """
    ann = test_genes_presence.annotation
    assert hasattr(model, "genes")
    ann["data"] = get_ids(model.genes)
    ann["message"] = "{:d} genes are defined in the model.".format(len(ann["data"]))
    assert len(ann["data"]) >= 1, ann["message"]


@annotate(title="Total Reactions", format_type="count")
def test_reactions_presence(model):
    """
    Expect that at least one reaction is defined in the model.

    To be useful a metabolic model should consist at least of a few reactions.
    This test simply checks if there are more than zero reactions.

    Implementation:
    Check if the cobra.Model object has non-empty "reactions"
    attribute, this list is populated from the list of sbml:listOfReactions
    which should contain at least one sbml:reaction.

    """
    ann = test_reactions_presence.annotation
    assert hasattr(model, "reactions")
    ann["data"] = get_ids(model.reactions)
    ann["message"] = "{:d} reactions are defined in the model.".format(len(ann["data"]))
    assert len(ann["data"]) >= 1, ann["message"]


@annotate(title="Total Metabolites", format_type="count")
def test_metabolites_presence(model):
    """
    Expect that at least one metabolite is defined in the model.

    To be useful a metabolic model should consist at least of a few
    metabolites that are converted by reactions.
    This test simply checks if there are more than zero metabolites.

    Implementation:
    Check if the cobra.Model object has non-empty
    "metabolites" attribute, this list is populated from the list of
    sbml:listOfSpecies which should contain at least one sbml:species.

    """
    ann = test_metabolites_presence.annotation
    assert hasattr(model, "metabolites")
    ann["data"] = get_ids(model.metabolites)
    ann["message"] = "{:d} metabolites are defined in the model.".format(
        len(ann["data"])
    )
    assert len(ann["data"]) >= 1, ann["message"]


@annotate(title="Metabolites without Formula", format_type="count")
def test_metabolites_formula_presence(model):
    """
    Expect all metabolites to have a formula.

    To be able to ensure that reactions are mass-balanced, all model
    metabolites ought to be provided with a chemical formula. Since it may be
    difficult to obtain formulas for certain metabolites this test serves as a
    mere report. Models can still be stoichiometrically consistent even
    when chemical formulas are not defined for each metabolite.

    Implementation:
    Check if each cobra.Metabolite has a non-empty "formula"
    attribute. This attribute is set by the parser if there is an
    fbc:chemicalFormula attribute for the corresponding species in the
    SBML.

    """
    ann = test_metabolites_formula_presence.annotation
    ann["data"] = get_ids(basic.check_metabolites_formula_presence(model))
    ann["metric"] = len(ann["data"]) / len(model.metabolites)
    ann["message"] = wrapper.fill(
        """There are a total of {}
        metabolites ({:.2%}) without a formula: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Metabolites without Charge", format_type="count")
def test_metabolites_charge_presence(model):
    """
    Expect all metabolites to have charge information.

    To be able to ensure that reactions are charge-balanced, all model
    metabolites ought to be provided with a charge. Since it may be
    difficult to obtain charges for certain metabolites this test serves as a
    mere report. Models can still be stoichiometrically consistent even
    when charge information is not defined for each metabolite.

    Implementation:
    Check if each cobra.Metabolite has a non-empty "charge"
    attribute. This attribute is set by the parser if there is an
    fbc:charge attribute for the corresponding species in the
    SBML.

    """
    ann = test_metabolites_charge_presence.annotation
    ann["data"] = get_ids(basic.check_metabolites_charge_presence(model))
    ann["metric"] = len(ann["data"]) / len(model.metabolites)
    ann["message"] = wrapper.fill(
        """There are a total of {}
        metabolites ({:.2%}) without a charge: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Reactions without GPR", format_type="count")
def test_gene_protein_reaction_rule_presence(model):
    """
    Expect all non-exchange reactions to have a GPR rule.

    Gene-Protein-Reaction rules express which gene has what function.
    The presence of this annotation is important to justify the existence
    of reactions in the model, and is required to conduct in silico gene
    deletion studies. However, reactions without GPR may also be valid:
    Spontaneous reactions, or known reactions with yet undiscovered genes
    likely lack GPR.

    Implementation:
    Check if each cobra.Reaction has a non-empty
    "gene_reaction_rule" attribute, which is set by the parser if there is an
    fbc:geneProductAssociation defined for the corresponding reaction in the
    SBML.

    """
    ann = test_gene_protein_reaction_rule_presence.annotation
    missing_gpr_metabolic_rxns = set(
        basic.check_gene_protein_reaction_rule_presence(model)
    ).difference(set(model.boundary))
    ann["data"] = get_ids(missing_gpr_metabolic_rxns)
    ann["metric"] = len(ann["data"]) / len(model.reactions)
    ann["message"] = wrapper.fill(
        """There are a total of {} reactions ({:.2%}) without GPR:
        {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Non-Growth Associated Maintenance Reaction", format_type="count")
def test_ngam_presence(model):
    """
    Expect a single non growth-associated maintenance reaction.

    The Non-Growth Associated Maintenance reaction (NGAM) is an
    ATP-hydrolysis reaction added to metabolic models to represent energy
    expenses that the cell invests in continuous processes independent of
    the growth rate. Memote tries to infer this reaction from a list of
    buzzwords, and the stoichiometry and components of a simple ATP-hydrolysis
    reaction.

    Implementation:
    From the list of all reactions that convert ATP to ADP select the reactions
    that match the irreversible reaction "ATP + H2O -> ADP + HO4P + H+",
    whose metabolites are situated within the main model compartment.
    The main model compartment is assumed to be the cytosol, yet, if that
    cannot be identified, it is assumed to be the compartment with the most
    metabolites. The resulting list of reactions is then filtered further by
    attempting to match the reaction name with any of the following buzzwords
    ('maintenance', 'atpm', 'requirement', 'ngam', 'non-growth', 'associated').
    If this is possible only the filtered reactions are returned, if not the
    list is returned as is.

    """
    ann = test_ngam_presence.annotation
    ann["data"] = get_ids(basic.find_ngam(model))
    ann["metric"] = 1.0 - float(len(ann["data"]) == 1)
    ann["message"] = wrapper.fill(
        """A total of {} NGAM reactions could be identified:
        {}""".format(
            len(ann["data"]), truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 1, ann["message"]


@annotate(title="Metabolic Coverage", format_type="percent")
def test_metabolic_coverage(model):
    u"""
    Expect a model to have a metabolic coverage >= 1.

    The degree of metabolic coverage indicates the modeling detail of a
    given reconstruction calculated by dividing the total amount of
    reactions by the amount of genes. Models with a 'high level of modeling
    detail have ratios >1, and models with a low level of detail have
    ratios <1. This difference arises as models with basic or intermediate
    levels of detail are assumed to include many reactions in which several
    gene products and their enzymatic transformations are ‘lumped’.

    Implementation:
    Divides the amount reactions by the amount of genes. Raises an error
    if the model does not contain either reactions or genes.

    """
    ann = test_metabolic_coverage.annotation
    ann["data"] = (len(model.reactions), len(model.genes))
    ann["metric"] = basic.calculate_metabolic_coverage(model)
    ann["message"] = wrapper.fill(
        """The degree of metabolic coverage is {:.2}.""".format(ann["metric"])
    )
    assert ann["metric"] >= 1, ann["message"]


@annotate(title="Total Compartments", format_type="count")
def test_compartments_presence(model):
    """
    Expect that two or more compartments are defined in the model.

    While simplified metabolic models may be perfectly viable, generally
    across the tree of life organisms contain at least one distinct
    compartment: the cytosol or cytoplasm. In the case of prokaryotes there is
    usually a periplasm, and eurkaryotes are more complex. In addition to the
    internal compartment, a metabolic model also reflects the extracellular
    environment i.e. the medium/ metabolic context in which the modelled cells
    grow. Hence, in total, at least two compartments can be expected from a
    metabolic model.

    Implementation:
    Check if the cobra.Model object has a non-empty "compartments"
    attribute, this list is populated from the list of sbml:listOfCompartments
    which should contain at least two sbml:compartment elements.

    """
    ann = test_compartments_presence.annotation
    assert hasattr(model, "compartments")
    ann["data"] = list(model.compartments)
    ann["metric"] = 1.0 - float(len(ann["data"]) >= 2)
    ann["message"] = wrapper.fill(
        """A total of {:d} compartments are defined in the model: {}""".format(
            len(ann["data"]), truncate(ann["data"])
        )
    )
    assert len(ann["data"]) >= 2, ann["message"]


@annotate(title="Enzyme Complexes", format_type="count")
def test_protein_complex_presence(model):
    """
    Expect that more than one enzyme complex is present in the model.

    Based on the gene-protein-reaction (GPR) rules, it is possible to infer
    whether a reaction is catalyzed by a single gene product, isozymes or by a
    heteromeric protein complex. This test checks that at least one
    such heteromeric protein complex is defined in any GPR of the model. For
    S. cerevisiae it could be shown that "essential proteins tend to [cluster]
    together in essential complexes"
    (https://doi.org/10.1074%2Fmcp.M800490-MCP200).

    This might also be a relevant metric for other organisms.

    Implementation:
    Identify GPRs which contain at least one logical AND that combines two
    different gene products.

    """
    ann = test_protein_complex_presence.annotation
    ann["data"] = get_ids(basic.find_protein_complexes(model))
    ann["metric"] = len(ann["data"]) / len(model.reactions)
    ann["message"] = wrapper.fill(
        """A total of {:d} reactions are catalyzed by complexes defined
        through GPR rules in the model.""".format(
            len(ann["data"])
        )
    )
    assert len(ann["data"]) >= 1, ann["message"]


@annotate(title="Purely Metabolic Reactions", format_type="count")
def test_find_pure_metabolic_reactions(model):
    """
    Expect at least one pure metabolic reaction to be defined in the model.

    If a reaction is neither a transport reaction, a biomass reaction nor a
    boundary reaction, it is counted as a purely metabolic reaction. This test
    requires the presence of metabolite formula to be able to identify
    transport reactions. This test is passed when the model contains at least
    one purely metabolic reaction i.e. a conversion of one metabolite into
    another.

    Implementation:
    From the list of all reactions, those that are boundary, transport and
    biomass reactions are removed and the remainder assumed to be pure
    metabolic reactions. Boundary reactions are identified using the attribute
    cobra.Model.boundary. Please read the description of "Transport Reactions"
    and "Biomass Reaction Identified" to learn how they are identified.

    """
    ann = test_find_pure_metabolic_reactions.annotation
    ann["data"] = get_ids(basic.find_pure_metabolic_reactions(model))
    ann["metric"] = len(ann["data"]) / len(model.reactions)
    ann["message"] = wrapper.fill(
        """A total of {:d} ({:.2%}) purely metabolic reactions are defined in
        the model, this excludes transporters, exchanges, or pseudo-reactions:
        {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) >= 1, ann["message"]


@annotate(title="Purely Metabolic Reactions with Constraints", format_type="count")
def test_find_constrained_pure_metabolic_reactions(model):
    """
    Expect zero or more purely metabolic reactions to have fixed constraints.

    If a reaction is neither a transport reaction, a biomass reaction nor a
    boundary reaction, it is counted as a purely metabolic reaction. This test
    requires the presence of metabolite formula to be able to identify
    transport reactions. This test simply reports the number of purely
    metabolic reactions that have fixed constraints and does not have any
    mandatory 'pass' criteria.

    Implementation: From the pool of pure metabolic reactions identify
    reactions which are constrained to values other than the model's minimal or
    maximal possible bounds.

    """
    ann = test_find_constrained_pure_metabolic_reactions.annotation
    pmr = basic.find_pure_metabolic_reactions(model)
    ann["data"] = get_ids_and_bounds(
        [rxn for rxn in pmr if basic.is_constrained_reaction(model, rxn)]
    )
    ann["metric"] = len(ann["data"]) / len(pmr)
    ann["message"] = wrapper.fill(
        """A total of {:d} ({:.2%}) purely metabolic reactions have fixed
        constraints in the model, this excludes transporters, exchanges, or
        pseudo-reactions: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )


@annotate(title="Transport Reactions", format_type="count")
def test_find_transport_reactions(model):
    """
    Expect >= 1 transport reactions are present in the model.

    Cellular metabolism in any organism usually involves the transport of
    metabolites across a lipid bi-layer. This test reports how many
    of these reactions, which transports metabolites from one compartment
    to another, are present in the model, as at least one transport reaction
    must be present for cells to take up nutrients and/or excrete waste.

    Implementation:
    A transport reaction is defined as follows:
    1. It contains metabolites from at least 2 compartments and
    2. at least 1 metabolite undergoes no chemical reaction, i.e.,
    the formula and/or annotation stays the same on both sides of the equation.

    A notable exception is transport via PTS, which also contains the following
    restriction:
    3. The transported metabolite(s) are transported into a compartment through
    the exchange of a phosphate.

    An example of transport via PTS would be
    pep(c) + glucose(e) -> glucose-6-phosphate(c) + pyr(c)

    Reactions similar to transport via PTS (referred to as "modified transport
    reactions") follow a similar pattern:
    A(x) + B-R(y) -> A-R(y) + B(y)

    Such modified transport reactions can be detected, but only when the
    formula is defined for all metabolites in a particular reaction. If this
    is not the case, transport reactions are identified through annotations,
    which cannot detect modified transport reactions.

    """
    ann = test_find_transport_reactions.annotation
    ann["data"] = get_ids(helpers.find_transport_reactions(model))
    ann["metric"] = len(ann["data"]) / len(model.reactions)
    ann["message"] = wrapper.fill(
        """A total of {:d} ({:.2%}) transport reactions are defined in the
        model, this excludes purely metabolic reactions, exchanges, or
        pseudo-reactions: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) >= 1, ann["message"]


@annotate(title="Transport Reactions with Constraints", format_type="count")
def test_find_constrained_transport_reactions(model):
    """
    Expect zero or more transport reactions to have fixed constraints.

    Cellular metabolism in any organism usually involves the transport of
    metabolites across a lipid bi-layer. Hence, this test reports how many
    of these reactions, which transports metabolites from one compartment
    to another, have fixed constraints. This test does not have any mandatory
    'pass' criteria.

    Implementation:
    Please refer to "Transport Reactions" for details on how memote identifies
    transport reactions.
    From the pool of transport reactions identify reactions which are
    constrained to values other than the model's median lower and upper bounds.

    """
    ann = test_find_constrained_transport_reactions.annotation
    transporters = helpers.find_transport_reactions(model)
    ann["data"] = get_ids_and_bounds(
        [rxn for rxn in transporters if basic.is_constrained_reaction(model, rxn)]
    )
    ann["metric"] = len(ann["data"]) / len(transporters)
    ann["message"] = wrapper.fill(
        """A total of {:d} ({:.2%}) transport reactions have fixed
        constraints in the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )


@annotate(title="Fraction of Transport Reactions without GPR", format_type="percent")
def test_transport_reaction_gpr_presence(model):
    """
    Expect a small fraction of transport reactions not to have a GPR rule.

    As it is hard to identify the exact transport processes within a cell,
    transport reactions are often added purely for modeling purposes.
    Highlighting where assumptions have been made versus where
    there is proof may help direct the efforts to improve transport and
    transport energetics of the tested metabolic model.
    However, transport reactions without GPR may also be valid:
    Diffusion, or known reactions with yet undiscovered genes likely lack GPR.

    Implementation:
    Check which cobra.Reactions classified as transport reactions have a
    non-empty "gene_reaction_rule" attribute.

    """
    # TODO: Update threshold with improved insight from meta study.
    ann = test_transport_reaction_gpr_presence.annotation
    ann["data"] = get_ids(basic.check_transport_reaction_gpr_presence(model))
    ann["metric"] = len(ann["data"]) / len(helpers.find_transport_reactions(model))
    ann["message"] = wrapper.fill(
        """There are a total of {} transport reactions ({:.2%} of all
        transport reactions) without GPR:
        {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert ann["metric"] < 0.2, ann["message"]


@annotate(title="Number of Reversible Oxygen-Containing Reactions", format_type="count")
def test_find_reversible_oxygen_reactions(model):
    """
    Expect zero or more oxygen-containing reactions to be reversible.

    The directionality of oxygen-producing/-consuming reactions affects the
    model's ability to grow anaerobically i.e. create faux-anaerobic organisms.
    This test reports how many of these oxygen-containing reactions are
    reversible. This test does not have any mandatory 'pass' criteria.

    Implementation:
    First, find the metabolite representing atmospheric oxygen in the model on
    the basis of an internal mapping table or by specifically looking for the
    formula "O2". Then, find all reactions that produce or consume oxygen and
    report those that are reversible.

    """
    ann = test_find_reversible_oxygen_reactions.annotation
    o2_rxns = basic.find_oxygen_reactions(model)
    ann["data"] = get_ids([rxn for rxn in o2_rxns if rxn.reversibility])
    ann["metric"] = len(ann["data"]) / len(o2_rxns)
    ann["message"] = wrapper.fill(
        """There are a total of {} reversible oxygen-containing reactions
        ({:.2%} of all oxygen-containing reactions): {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )


@annotate(title="Unique Metabolites", format_type="count")
def test_find_unique_metabolites(model):
    """
    Expect there to be less metabolites when removing compartment tag.

    Metabolites may be transported into different compartments, which means
    that in a compartimentalized model the number of metabolites may be
    much higher than in a model with no compartments. This test counts only
    one occurrence of each metabolite and returns this as the number of unique
    metabolites. The test expects that the model is compartimentalized, and
    thus, that the number of unique metabolites is generally lower than the
    total number of metabolites.

    Implementation:
    Reduce the list of metabolites to a unique set by removing the compartment
    tag. The cobrapy SBML parser adds compartment tags to each metabolite ID.

    """
    ann = test_find_unique_metabolites.annotation
    ann["data"] = list(basic.find_unique_metabolites(model))
    ann["metric"] = len(ann["data"]) / len(model.metabolites)
    ann["message"] = wrapper.fill(
        """Not counting the same entities in other compartments, there is a
        total of {} ({:.2%}) unique metabolites in the model: {}""".format(
            len(ann["data"]), ann["metric"], truncate(ann["data"])
        )
    )
    assert len(ann["data"]) < len(model.metabolites), ann["message"]


@annotate(title="Duplicate Metabolites in Identical Compartments", format_type="count")
def test_find_duplicate_metabolites_in_compartments(model):
    """
    Expect there to be zero duplicate metabolites in the same compartments.

    The main reason for having this test is to help cleaning up merged models
    or models from automated reconstruction pipelines as these are prone to
    having identical metabolites from different namespaces
    (hence different IDs). This test therefore expects that every metabolite
    in any particular compartment has unique inchikey values.

    Implementation:
    Identifies duplicate metabolites in each compartment by
    determining if any two metabolites have identical InChI-key annotations.
    For instance, this function would find compounds with IDs ATP1 and ATP2 in
    the cytosolic compartment, with both having the same InChI annotations.

    """
    ann = test_find_duplicate_metabolites_in_compartments.annotation
    ann["data"] = basic.find_duplicate_metabolites_in_compartments(model)
    ann["metric"] = len(ann["data"]) / len(model.metabolites)
    ann["message"] = wrapper.fill(
        """There are a total of {} metabolites in the model which
        have duplicates in the same compartment: {}""".format(
            len(ann["data"]), truncate(ann["data"])
        )
    )
    assert len(ann["data"]) == 0, ann["message"]


@annotate(title="Reactions With Partially Identical Annotations", format_type="percent")
def test_find_reactions_with_partially_identical_annotations(model):
    """
    Expect there to be zero duplicate reactions.

    Identify reactions in a pairwise manner that are annotated
    with identical database references. This does not take into account a
    reaction's directionality or compartment.

    The main reason for having this test is to help cleaning up merged models
    or models from automated reconstruction pipelines as these are prone to
    having identical reactions with identifiers from different namespaces.
    It could also be useful to identify a 'type' of reaction that
    occurs in several compartments.

    Implementation:

    Identify duplicate reactions globally by checking if any
    two metabolic reactions have the same entries in their annotation
    attributes. The heuristic looks at annotations with the keys
    "metanetx.reaction", "kegg.reaction", "brenda", "rhea", "biocyc",
    "bigg.reaction" only.

    """
    ann = test_find_reactions_with_partially_identical_annotations.annotation
    duplicates, total = basic.find_reactions_with_partially_identical_annotations(model)
    ann["data"] = duplicates
    ann["metric"] = total / len(model.reactions)
    ann["message"] = wrapper.fill(
        """Based on annotations there are {} different groups of overlapping
        annotation which corresponds to a total of {} duplicated reactions in
        the model.""".format(
            len(duplicates), total
        )
    )
    assert total == 0, ann["message"]


@annotate(title="Duplicate Reactions", format_type="percent")
def test_find_duplicate_reactions(model):
    """
    Expect there to be zero duplicate reactions.

    Identify reactions in a pairwise manner that use the same set
    of metabolites including potentially duplicate metabolites. Moreover, it
    will take a reaction's directionality and compartment into account.

    The main reason for having this test is to help cleaning up merged models
    or models from automated reconstruction pipelines as these are prone to
    having identical reactions with identifiers from different namespaces.

    Implementation:

    Compare reactions in a pairwise manner.
    For each reaction, the metabolite annotations are checked for a description
    of the structure (via InChI and InChIKey).If they exist, substrates and
    products as well as the stoichiometries of any reaction pair are compared.
    Only reactions where the substrates, products, stoichiometry and
    reversibility are identical are considered to be duplicates.
    This test will not be able to identify duplicate reactions if there are no
    structure annotations. Further, it will report reactions with
    differing bounds as equal if they otherwise match the above conditions.

    """
    ann = test_find_duplicate_reactions.annotation
    duplicates, num = basic.find_duplicate_reactions(model)
    ann["data"] = duplicates
    ann["metric"] = num / len(model.reactions)
    ann["message"] = wrapper.fill(
        """Based on metabolites, directionality and compartment there are a
        total of {} reactions in the model which have duplicates:
        {}""".format(
            num, truncate(duplicates)
        )
    )
    assert num == 0, ann["message"]


@annotate(title="Reactions With Identical Genes", format_type="percent")
def test_find_reactions_with_identical_genes(model):
    """
    Expect there to be zero duplicate reactions.

    Identify reactions in a pairwise manner that use identical
    sets of genes. It does *not* take into account a reaction's directionality,
    compartment, metabolites or annotations.

    The main reason for having this test is to help cleaning up merged models
    or models from automated reconstruction pipelines as these are prone to
    having identical reactions with identifiers from different namespaces.

    Implementation:

    Compare reactions in a pairwise manner and group reactions whose genes
    are identical. Skip reactions with missing genes.

    """
    ann = test_find_reactions_with_identical_genes.annotation
    rxn_groups, num_dup = basic.find_reactions_with_identical_genes(model)
    ann["data"] = rxn_groups
    ann["metric"] = num_dup / len(model.reactions)
    ann["message"] = wrapper.fill(
        """Based only on equal genes there are {} different groups of
        identical reactions which corresponds to a total of {}
        duplicated reactions in the model.""".format(
            len(rxn_groups), num_dup
        )
    )
    assert num_dup == 0, ann["message"]


@annotate(title="Medium Components", format_type="count")
def test_find_medium_metabolites(model):
    """
    Expect zero or more metabolites to be set as medium.

    This test checks all boundary reactions in the model that permit flux
    towards creating a metabolite, and reports those metabolites. This test
    does not have any mandatory 'pass' criteria.

    Implementation:
    Identify the metabolite IDs of each reaction in the method
    cobra.Model.medium. Model.medium returns exchange reactions whose bounds
    permit the uptake of metabolites.

    """
    ann = test_find_medium_metabolites.annotation
    ann["data"] = basic.find_medium_metabolites(model)
    num_ex = basic.find_external_metabolites(model)
    ann["metric"] = len(ann["data"]) / num_ex
    ann["message"] = wrapper.fill(
        """There are a total of {} metabolites in the currently set medium
        (out of {} defined extra-cellular metabolites)
        in the model: {}""".format(
            len(ann["data"]), num_ex, truncate(ann["data"])
        )
    )
