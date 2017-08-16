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
from cobra.exceptions import Infeasible
from cobra.flux_analysis import flux_variability_analysis

import memote.support.helpers as helpers
import memote.support.consistency_helpers as con_helpers

__all__ = (
    "check_stoichiometric_consistency", "find_unconserved_metabolites",
    "find_inconsistent_min_stoichiometry")

LOGGER = logging.getLogger(__name__)


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
    internal_rxns, metabolites = con_helpers.get_internals(model)
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
    internal_rxns, metabolites = con_helpers.get_internals(model)
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
    internal_rxns, internal_mets = con_helpers.get_internals(model)
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


def produce_atp_closed_exchanges(model):
    """
    Close the model's exchanges and tries to optimize the production of atp_c.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    try:
        met = model.metabolites.get_by_id('atp_c')
    except KeyError:
        return False
    with model:
        for exchange in model.exchanges:
            exchange.bounds = (0, 0)
        dm_rxn = model.add_boundary(met, type="demand")
        model.objective = dm_rxn
        try:
            solution = model.optimize()
            state = solution.objective_value > 0.0
        except Infeasible:
            state = False
    return state


def find_imbalanced_reactions(model):
    """
    Find metabolic reactions that not mass and/or charge balanced.

    This will exclude biomass, exchange and demand reactions as they are
    unbalanced by definition.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    exchanges = set(model.exchanges)
    biomass = set(helpers.find_biomass_reaction(model))
    total_rxns = set(model.reactions)
    metab_rxns = total_rxns - (exchanges | biomass)
    return [rxn for rxn in metab_rxns if len(rxn.check_mass_balance()) > 0]


def find_blocked_reactions(model):
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
    """
    Find metabolic rxns in stoichiometrically balanced cycles (SBCs).

    The flux distribution of nominal FVA is compared with loopless FVA
    (loopless=True) to determine reactions that participate in loops, as
    participation in loops would increase the flux through a given reactions to
    the maximal bounds. This function then returns reactions where the flux
    differs between the two FVA calculations.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Notes
    -----
    "SBCs are artifacts of metabolic reconstructions due to insufficient
    constraints (e.g., thermodynamic constraints and regulatory
    constraints) [1]_." They are defined by internal reactions that carry flux
    in spite of closed exchange reactions.

    References
    ----------
    .. [1] Thiele, I., & Palsson, B. Ø. (2010, January). A protocol for
           generating a high-quality genome-scale metabolic reconstruction.
           Nature protocols. Nature Publishing Group.
           http://doi.org/10.1038/nprot.2009.203

    """
    fva_result = flux_variability_analysis(model, loopless=False)
    fva_result_loopless = flux_variability_analysis(model, loopless=True)
    row_ids_max = fva_result[
        fva_result.maximum != fva_result_loopless.maximum].index
    row_ids_min = fva_result[
        fva_result.minimum != fva_result_loopless.minimum].index
    differential_fluxes = set(row_ids_min).union(set(row_ids_max))

    return [model.reactions.get_by_id(id) for id in differential_fluxes]
