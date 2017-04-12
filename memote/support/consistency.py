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
from cobra import Reaction
import memote.support.consistency_helpers as cons_helpers
import memote.support.helpers as helpers

__all__ = (
    "check_stoichiometric_consistency", "find_unconserved_metabolites",
    "find_inconsistent_min_stoichiometry", "produce_atp_closed_xchngs")

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
    Model, Constraint, Variable, Objective = cons_helpers.get_interface(model)
    # The transpose of the stoichiometric matrix N.T in the paper.
    stoich_trans = Model()
    internal_rxns, metabolites = cons_helpers.get_internals(model)
    for metabolite in metabolites:
        stoich_trans.add(Variable(metabolite.id, lb=1))
    stoich_trans.update()
    cons_helpers.add_reaction_constraints(
        stoich_trans, internal_rxns, Constraint
    )
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
    Model, Constraint, Variable, Objective = cons_helpers.get_interface(model)
    stoich_trans = Model()
    internal_rxns, metabolites = cons_helpers.get_internals(model)
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
    cons_helpers.add_reaction_constraints(
        stoich_trans, internal_rxns, Constraint
    )
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
    Model, Constraint, Variable, Objective = cons_helpers.get_interface(model)
    unconserved_mets = find_unconserved_metabolites(model)
    LOGGER.info("model has %d unconserved metabolites", len(unconserved_mets))
    internal_rxns, internal_mets = cons_helpers.get_internals(model)
    get_id = attrgetter("id")
    reactions = sorted(internal_rxns, key=get_id)
    metabolites = sorted(internal_mets, key=get_id)
    stoich, met_index, rxn_index = cons_helpers.stoichiometry_matrix(
        metabolites, reactions
    )
    left_ns = cons_helpers.nullspace(stoich.T)
    # deal with numerical instabilities
    left_ns[np.abs(left_ns) < atol] = 0.0
    LOGGER.info("nullspace has dimension %d", left_ns.shape[1])
    inc_minimal = set()
    (problem, indicators) = cons_helpers.create_milp_problem(
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
            cuts.append(cons_helpers.add_cut(problem, indicators,
                                             len(solution) - 1, Constraint))
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


    .. [1] Gevorgyan, A., M. G Poolman, and D. A Fell.
        "Detection of Stoichiometric Inconsistencies in Biomolecular Models."
           Bioinformatics 24, no. 19 (2008): 2245.
    """
    raise NotImplementedError(
        "Coming soon™ if considered useful.")


def produce_atp_closed_xchngs(model):
    """
    Closes the model's exchanges and tries to optimize the production of atp_c.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    """
    status = False
    if 'atp_c' in model.metabolites:
        with model:
            xchngs = helpers.find_demand_and_exchange_reactions(model)
            for exchange in xchngs:
                exchange.bounds = [0, 0]
            met = model.metabolites.get_by_id('atp_c')
            dm_rxn = Reaction(id='TestDM_{}'.format(met.id))
            dm_rxn.add_metabolites({met: -1})
            model.add_reactions([dm_rxn])
            model.objective = dm_rxn
            try:
                solution = model.optimize()
                if solution.objective_value != 0:
                    status = True
            except Infeasible:
                status = False
        return status
    else:
        return status
