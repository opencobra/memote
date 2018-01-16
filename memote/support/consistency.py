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

"""Supporting functions for stoichiometric consistency checks."""

from __future__ import absolute_import

import logging
from operator import attrgetter

import numpy as np
from cobra import Reaction
from cobra.exceptions import Infeasible
from cobra.flux_analysis import flux_variability_analysis

import memote.support.consistency_helpers as con_helpers
import memote.support.helpers as helpers

LOGGER = logging.getLogger(__name__)

# The following dictionary is based on the list of energy metabolites chosen
# as part of the following publication:
# Fritzemeier, C. J., Hartleb, D., Szappanos, B., Papp, B., & Lercher,
# M. J. (2017). Erroneous energy-generating cycles in published genome scale
# metabolic networks: Identification and removal. PLoS Computational
# Biology, 13(4), 1–14. http://doi.org/10.1371/journal.pcbi.1005494
ENERGY_COUPLES = {
    'atp_c': 'adp_c',
    'ctp_c': 'cdp_c',
    'gtp_c': 'gdp_c',
    'utp_c': 'udp_c',
    'itp_c': 'idp_c',
    'nadph_c': 'nadp_c',
    'nadh_c': 'nad_c',
    'fadh2_c': 'fad_c',
    'fmnh2_c': 'fmn_c',
    'q8h2_c': 'q8_c',
    'mql8_c': 'mqn8_c',
    'mql6_c': 'mqn6_c',
    'mql7_c': 'mqn7_c',
    '2dmmql8_c': '2dmmq8_c',
    'accoa_c': 'coa_c',
    'glu__L_c': 'akg_c',
    'h_p': 'h_c'
}


def check_stoichiometric_consistency(model):
    """
    Verify the consistency of the model stoichiometry.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Notes
    -----
    See [1]_ section 3.1 for a complete description of the algorithm.

    .. [1] Gevorgyan, A., M. G Poolman, and D. A Fell.
           "Detection of Stoichiometric Inconsistencies in Biomolecular Models."
           Bioinformatics 24, no. 19 (2008): 2245.

    """
    Model, Constraint, Variable, Objective = con_helpers.get_interface(model)
    # The transpose of the stoichiometric matrix N.T in the paper.
    stoich_trans = Model()
    internal_rxns = con_helpers.get_internals(model)
    metabolites = set(met for rxn in internal_rxns for met in rxn.metabolites)
    LOGGER.info("model '%s' has %d internal reactions", model.id,
                len(internal_rxns))
    LOGGER.info("model '%s' has %d internal metabolites", model.id,
                len(metabolites))
    for metabolite in metabolites:
        stoich_trans.add(Variable(metabolite.id, lb=1))
    stoich_trans.update()
    con_helpers.add_reaction_constraints(
        stoich_trans, internal_rxns, Constraint)
    # The objective is to minimize the metabolite mass vector.
    stoich_trans.objective = Objective(1)
    stoich_trans.objective.set_linear_coefficients(
        {var: 1. for var in stoich_trans.variables})
    stoich_trans.objective.direction = "min"
    status = stoich_trans.optimize()
    if status == "optimal":
        return True
    elif status == "infeasible":
        return False
    else:
        raise RuntimeError(
            "Could not determine stoichiometric consistencty."
            " Solver status is '{}'"
            " (only optimal or infeasible expected).".format(status))


def find_unconserved_metabolites(model):
    """
    Detect unconserved metabolites.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Notes
    -----
    See [1]_ section 3.2 for a complete description of the algorithm.


    .. [1] Gevorgyan, A., M. G Poolman, and D. A Fell.
           "Detection of Stoichiometric Inconsistencies in Biomolecular Models."
           Bioinformatics 24, no. 19 (2008): 2245.

    """
    Model, Constraint, Variable, Objective = con_helpers.get_interface(model)
    stoich_trans = Model()
    internal_rxns = con_helpers.get_internals(model)
    metabolites = set(met for rxn in internal_rxns for met in rxn.metabolites)
    # The binary variables k[i] in the paper.
    k_vars = list()
    for met in metabolites:
        # The element m[i] of the mass vector.
        m_var = Variable(met.id)
        k_var = Variable("k_{}".format(met.id), type="binary")
        k_vars.append(k_var)
        stoich_trans.add([m_var, k_var])
        # This constraint is equivalent to 0 <= k[i] <= m[i].
        stoich_trans.add(Constraint(
            k_var - m_var, ub=0, name="switch_{}".format(met.id)))
    stoich_trans.update()
    con_helpers.add_reaction_constraints(
        stoich_trans, internal_rxns, Constraint)
    # The objective is to maximize the binary indicators k[i], subject to the
    # above inequality constraints.
    stoich_trans.objective = Objective(1)
    stoich_trans.objective.set_linear_coefficients(
        {var: 1. for var in k_vars})
    stoich_trans.objective.direction = "max"
    status = stoich_trans.optimize()
    if status == "optimal":
        # TODO: See if that could be a Boolean test `bool(var.primal)`.
        return set([model.metabolites.get_by_id(var.name[2:])
                    for var in k_vars if var.primal < 0.8])
    else:
        raise RuntimeError(
            "Could not compute list of unconserved metabolites."
            " Solver status is '{}'"
            " (only optimal or infeasible expected).".format(status))


def find_inconsistent_min_stoichiometry(model, atol=1e-13):
    """
    Detect inconsistent minimal net stoichiometries.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    atol : float, optional
        Values below the absolute tolerance are treated as zero. Expected to be
        very small but larger than zero.

    Notes
    -----
    See [1]_ section 3.3 for a complete description of the algorithm.


    .. [1] Gevorgyan, A., M. G Poolman, and D. A Fell.
           "Detection of Stoichiometric Inconsistencies in Biomolecular Models."
           Bioinformatics 24, no. 19 (2008): 2245.

    """
    if check_stoichiometric_consistency(model):
        return set()
    Model, Constraint, Variable, Objective = con_helpers.get_interface(model)
    unconserved_mets = find_unconserved_metabolites(model)
    LOGGER.info("model has %d unconserved metabolites", len(unconserved_mets))
    internal_rxns = con_helpers.get_internals(model)
    internal_mets = set(met for rxn in internal_rxns for met in rxn.metabolites)
    get_id = attrgetter("id")
    reactions = sorted(internal_rxns, key=get_id)
    metabolites = sorted(internal_mets, key=get_id)
    stoich, met_index, rxn_index = con_helpers.stoichiometry_matrix(
        metabolites, reactions)
    left_ns = con_helpers.nullspace(stoich.T)
    # deal with numerical instabilities
    left_ns[np.abs(left_ns) < atol] = 0.0
    LOGGER.info("nullspace has dimension %d", left_ns.shape[1])
    inc_minimal = set()
    (problem, indicators) = con_helpers.create_milp_problem(
        left_ns, metabolites, Model, Variable, Constraint, Objective)
    LOGGER.debug(str(problem))
    cuts = list()
    for met in unconserved_mets:
        row = met_index[met]
        if (left_ns[row] == 0.0).all():
            LOGGER.debug("%s: singleton minimal unconservable set", met.id)
            # singleton set!
            inc_minimal.add((met,))
            continue
        # expect a positive mass for the unconserved metabolite
        problem.variables[met.id].lb = 1e-3
        status = problem.optimize()
        while status == "optimal":
            LOGGER.debug("%s: status %s", met.id, status)
            LOGGER.debug("sum of all primal values: %f",
                         sum(problem.primal_values.values()))
            LOGGER.debug("sum of binary indicators: %f",
                         sum(var.primal for var in indicators))
            solution = [model.metabolites.get_by_id(var.name[2:])
                        for var in indicators if var.primal > 0.2]
            LOGGER.debug("%s: set size %d", met.id, len(solution))
            inc_minimal.add(tuple(solution))
            if len(solution) == 1:
                break
            cuts.append(con_helpers.add_cut(
                problem, indicators, len(solution) - 1, Constraint))
            status = problem.optimize()
        LOGGER.debug("%s: last status %s", met.id, status)
        # reset
        problem.variables[met.id].lb = 0.0
        problem.remove(cuts)
        cuts.clear()
    return inc_minimal


def find_elementary_leakage_modes(model, atol=1e-13):
    """
    Detect elementary leakage modes.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    atol : float, optional
        Values below the absolute tolerance are treated as zero. Expected to be
        very small but larger than zero.

    Notes
    -----
    See [1]_ section 3.4 for a complete description of the algorithm.

    References
    ----------
    .. [1] Gevorgyan, A., M. G Poolman, and D. A Fell.
           "Detection of Stoichiometric Inconsistencies in Biomolecular
           Models."
           Bioinformatics 24, no. 19 (2008): 2245.

    """
    raise NotImplementedError(
        "Coming soon™ if considered useful.")


def detect_energy_generating_cycles(model, metabolite_id):
    u"""
    Detect erroneous energy-generating cycles for a a single metabolite.

    The function will first build a dissipation reaction corresponding to the
    input metabolite. This reaction is then set as the objective for
    optimization, after closing all exchanges. If the reaction was able to
    carry flux, an erroneous energy-generating cycle must be present. In this
    case a list of reactions with a flux greater than zero is returned.
    Otherwise, the function returns False.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    metabolite_id : str
        The identifier of an energy metabolite.

    Notes
    -----
    "[...] energy generating cycles (EGC) [...] charge energy metabolites
    without a source of energy. [...] To efficiently identify the existence of
    diverse EGCs, we first add a dissipation reaction to the metabolic network
    for each metabolite used to transmit cellular energy; e.g., for ATP, the
    irreversible reaction ATP + H2O → ADP + P + H+ is added. These dissipation
    reactions close any existing energy-generating cycles, thereby converting
    them to type-III pathways. Fluxes through any of the dissipation reactions
    at steady state indicate the generation of energy through the metabolic
    network. Second, all uptake reactions are constrained to zero. The sum of
    the fluxes through the energy dissipation reactions is now maximized using
    FBA. For a model without EGCs, these reactions cannot carry any flux
    without the uptake of nutrients. [1]_."

    References
    ----------
    .. [1] Fritzemeier, C. J., Hartleb, D., Szappanos, B., Papp, B., & Lercher,
     M. J. (2017). Erroneous energy-generating cycles in published genome scale
     metabolic networks: Identification and removal. PLoS Computational
     Biology, 13(4), 1–14. http://doi.org/10.1371/journal.pcbi.1005494

    """
    met = model.metabolites.get_by_id(metabolite_id)
    dissipation_product = model.metabolites.get_by_id(ENERGY_COUPLES[met.id])
    dissipation_rxn = Reaction('Dissipation')
    model = helpers.close_boundaries_sensibly(model)
    model.add_reactions([dissipation_rxn])
    if met.id in ['atp_c', 'ctp_c', 'gtp_c', 'utp_c', 'itp_c']:
        # build nucleotide-type dissipation reaction
        dissipation_rxn.reaction = "h2o_c --> h_c + pi_c"
    elif met.id in ['nadph_c', 'nadh_c']:
        # build nicotinamide-type dissipation reaction
        dissipation_rxn.reaction = "--> h_c"
    elif met.id in ['fadh2_c', 'fmnh2_c', 'q8h2_c', 'mql8_c',
                    'mql6_c', 'mql7_c', 'dmmql8_c']:
        # build redox-partner-type dissipation reaction
        dissipation_rxn.reaction = "--> 2 h_c"
    elif met.id == 'accoa_c':
        dissipation_rxn.reaction = "h2o_c --> h_c + ac_c"
    elif met.id == 'glu__L_c':
        dissipation_rxn.reaction = "h2o_c --> 2 h_c + nh3_c"
    elif met.id == 'h_p':
        pass

    dissipation_rxn.add_metabolites(
        {met.id: -1, dissipation_product: 1})
    model.objective = dissipation_rxn
    solution = model.optimize()
    if solution.status == 'infeasible':
        raise RuntimeError(
            "The model cannot be solved as the solver status is"
            "infeasible. This may be a bug."
        )
    elif solution.objective_value > 0.0:
        return solution.fluxes[solution.fluxes.abs() > 0.0].index. \
            drop(["Dissipation"]).tolist()
    else:
        return []


def find_mass_imbalanced_reactions(model):
    """
    Find metabolic reactions that are not mass balanced.

    This will exclude biomass, exchange and demand reactions as they are
    unbalanced by definition. It will also fail all reactions where at
    least one metabolite does not have a formula defined.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    internal_rxns = con_helpers.get_internals(model)
    return [
        rxn for rxn in internal_rxns if not con_helpers.is_mass_balanced(rxn)]


def find_charge_imbalanced_reactions(model):
    """
    Find metabolic reactions that are not charge balanced.

    This will exclude biomass, exchange and demand reactions as they are
    unbalanced by definition. It will also fail all reactions where at
    least one metabolite does not have a charge defined.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    internal_rxns = con_helpers.get_internals(model)
    return [
        rxn for rxn in internal_rxns if not con_helpers.is_charge_balanced(rxn)]


def find_universally_blocked_reactions(model):
    """
    Find metabolic reactions that are blocked.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Notes
    -----
    Blocked reactions are those reactions that when optimized for cannot carry
    any flux while all exchanges are open.

    """
    with model:
        for rxn in model.exchanges:
            rxn.bounds = (-1000, 1000)
        fva_result = flux_variability_analysis(model)

    blocked = fva_result.loc[(fva_result["maximum"] == 0.0) &
                             (fva_result["minimum"] == 0.0)]
    return [model.reactions.get_by_id(name) for name in blocked.index]


def find_stoichiometrically_balanced_cycles(model):
    u"""
    Find metabolic rxns in stoichiometrically balanced cycles (SBCs).

    The flux distribution of nominal FVA is compared with loopless FVA
    (loopless=True) to determine reactions that participate in loops, as
    participation in loops would increase the flux through a given reactions
    to the maximal bounds. This function then returns reactions where the
    flux differs between the two FVA calculations.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Notes
    -----
    "SBCs are artifacts of metabolic reconstructions due to insufficient
    constraints (e.g., thermodynamic constraints and regulatory
    constraints) [1]_." They are defined by internal reactions that carry
    flux in spite of closed exchange reactions.

    References
    ----------
    .. [1] Thiele, I., & Palsson, B. Ø. (2010, January). A protocol for
           generating a high-quality genome-scale metabolic reconstruction.
           Nature protocols. Nature Publishing Group.
           http://doi.org/10.1038/nprot.2009.203

    """
    try:
        fva_result = flux_variability_analysis(model, loopless=False)
        fva_result_loopless = flux_variability_analysis(model, loopless=True)
    except Infeasible as err:
        LOGGER.error("Failed to find stoichiometrically balanced cycles "
                     "because '{}'. This may be a bug.".format(err))
        return []
    row_ids_max = fva_result[
        fva_result.maximum != fva_result_loopless.maximum].index
    row_ids_min = fva_result[
        fva_result.minimum != fva_result_loopless.minimum].index
    differential_fluxes = set(row_ids_min).union(set(row_ids_max))
    return [model.reactions.get_by_id(id) for id in differential_fluxes]


def find_orphans(model):
    """
    Return metabolites that are only consumed in reactions.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    return [met for met in model.metabolites
            if (len(met.reactions) > 0) and all(
                (not rxn.reversibility) and (rxn.metabolites[met] < 0)
                for rxn in met.reactions)]


def find_deadends(model):
    """
    Return metabolites that are only produced in reactions.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    return [met for met in model.metabolites
            if (len(met.reactions) > 0) and all(
                (not rxn.reversibility) and
                (rxn.metabolites[met] > 0) for rxn in met.reactions)]


def find_disconnected(model):
    """
    Return metabolites that are not in any of the reactions.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    return [met for met in model.metabolites if len(met.reactions) == 0]


def find_metabolites_produced_with_closed_bounds(model):
    """
    Return metabolites that can be produced when boundary reactions are closed.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    mets_produced = list()
    model = helpers.close_boundaries_sensibly(model)
    for met in model.metabolites:
        with model:
            exch = model.add_boundary(
                met, type='irrex', reaction_id='IRREX', lb=0, ub=1
            )
            if helpers.run_fba(model, exch.id) > 0:
                mets_produced.append(met.id)
    return mets_produced


def find_metabolites_consumed_with_closed_bounds(model):
    """
    Return metabolites that can be consumed when boundary reactions are closed.

    Reverse case from 'find_metabolites_produced_with_closed_bounds', just
    like metabolites should not be produced from nothing, mass should not
    simply be removed from the model.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    mets_consumed = list()
    model = helpers.close_boundaries_sensibly(model)
    for met in model.metabolites:
        with model:
            exch = model.add_boundary(
                met, type='irrex', reaction_id='IRREX', lb=-1, ub=0
            )
            if helpers.run_fba(model, exch.id, direction='min') < 0:
                mets_consumed.append(met.id)
    return mets_consumed


def find_reactions_with_unbounded_flux_default_condition(model):
    """
    Return list of reactions whose flux is unbounded in the default condition.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns:
    --------
    unlimited_reactions: list
        A list of reactions that in default modeling conditions are able to
        carry flux as high/low as the systems maximal and minimal bounds.
    fraction: float
        The fraction of the amount of unbounded reactions to the amount of
        non-blocked reactions.
    conditionally_blocked_reactions: list
        A list of reactions that in default modeling conditions are not able
        to carry flux at all.

    """
    with model:
        try:
            fva_result = flux_variability_analysis(model)
        except Infeasible as err:
            LOGGER.error("Failed to find reactions with unbounded flux "
                         "because '{}'. This may be a bug.".format(err))
            raise Infeasible("It was not possible to run flux variability "
                             "analysis on the model. Make sure that the model "
                             "can be solved! Check if the constraints are not "
                             "too strict.")
        conditionally_blocked = fva_result.loc[(fva_result["maximum"] == 0.0) &
                                               (fva_result["minimum"] == 0.0)]
        max_bound = max([rxn.upper_bound for rxn in model.reactions])
        min_bound = min([rxn.lower_bound for rxn in model.reactions])
        unlimited_flux = fva_result.loc[(fva_result["maximum"] == max_bound) |
                                        (fva_result["minimum"] == min_bound)]
        conditionally_blocked_reactions = [model.reactions.get_by_id(met_id)
                                           for met_id in
                                           conditionally_blocked.index]
        unlimited_reactions = [model.reactions.get_by_id(met_id) for met_id in
                               unlimited_flux.index]
        try:
            fraction = len(unlimited_reactions) / float(
                (len(model.reactions) - len(conditionally_blocked_reactions)))
        except ZeroDivisionError:
            LOGGER.error("Division by Zero! Failed to calculate the "
                         "fraction of unbounded reactions. Does this model "
                         "have any reactions at all?")
            raise ZeroDivisionError("It was not possible to calculate the "
                                    "fraction of unbounded reactions to "
                                    "un-blocked reactions. This may be because"
                                    "the model doesn't have any reactions at "
                                    "all or that none of the reactions can "
                                    "carry a flux larger than zero!")

        return unlimited_reactions, fraction, conditionally_blocked_reactions
