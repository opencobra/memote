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
import sympy
from numpy.linalg import svd
from six import iteritems

__all__ = (
    "check_stoichiometric_consistency", "find_unconserved_metabolites",
    "find_inconsistent_min_stoichiometry")

LOGGER = logging.getLogger(__name__)


def add_reaction_constraints(model, reactions, Constraint):
    """
    Add the stoichiometric coefficients as constraints.

    Parameters
    ----------
    model : optlang.Model
        The transposed stoichiometric matrix representation.
    reactions : iterable
        Container of `cobra.Reaction` instances.
    Constraint : optlang.Constraint
        The constraint class for the specific interface.
    """
    for rxn in reactions:
        expression = sympy.Add(
            *[coefficient * model.variables[metabolite.id]
              for (metabolite, coefficient) in rxn.metabolites.items()])
        constraint = Constraint(expression, lb=0, ub=0, name=rxn.id)
        model.add(constraint)


def stoichiometry_matrix(metabolites, reactions):
    matrix = np.zeros((len(metabolites), len(reactions)))
    met_index = {met: i for i, met in enumerate(metabolites)}
    rxn_index = dict()

    for i, rxn in enumerate(reactions):
        rxn_index[rxn] = i
        for met, coef in iteritems(rxn.metabolites):
            j = met_index[met]
            matrix[j, i] = coef

    return matrix, met_index, rxn_index


def nullspace(matrix, atol=1e-13, rtol=0.0):
    """
    Compute the nullspace of a 2D `numpy.array`.

    Notes
    -----
    Adapted from:
    https://scipy.github.io/old-wiki/pages/Cookbook/RankNullspace.html
    """
    matrix = np.atleast_2d(matrix)
    u, s, vh = svd(matrix)
    tol = max(atol, rtol * s[0])
    return np.compress(s < tol, vh, axis=0).T


def check_stoichiometric_consistency(model):
    """
    Confirm that the metabolic model is mass-balanced.

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
    Model = model.solver.interface.Model
    Constraint = model.solver.interface.Constraint
    Variable = model.solver.interface.Variable
    Objective = model.solver.interface.Objective
    # The transpose of the stoichiometric matrix N.T in the paper.
    stoich_trans = Model()
    # Exchange reactions are unbalanced by their nature.
    # We exclude them here and only consider metabolites of the others.
    internal_rxns = set(model.reactions) - set(model.exchanges)
    metabolites = set(met for rxn in internal_rxns for met in rxn.metabolites)
    LOGGER.debug("model has %d internal metabolites", len(metabolites))
    LOGGER.debug("model has %d internal reactions", len(internal_rxns))
    for metabolite in metabolites:
        stoich_trans.add(Variable(metabolite.id, lb=1))
    stoich_trans.update()
    add_reaction_constraints(stoich_trans, internal_rxns, Constraint)
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
    Find unconserved metabolites in the metabolic model.

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
    Model = model.solver.interface.Model
    Constraint = model.solver.interface.Constraint
    Variable = model.solver.interface.Variable
    Objective = model.solver.interface.Objective
    stoich_trans = Model()
    # Exchange reactions are unbalanced by their nature.
    # We exclude them here and only consider metabolites of the others.
    internal_rxns = set(model.reactions) - set(model.exchanges)
    metabolites = set(met for rxn in internal_rxns for met in rxn.metabolites)
    LOGGER.debug("model has %d internal metabolites", len(metabolites))
    LOGGER.debug("model has %d internal reactions", len(internal_rxns))
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
    add_reaction_constraints(stoich_trans, internal_rxns, Constraint)
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


def find_inconsistent_min_stoichiometry(model, tol=1e-13):
    """
    Find minimal unbalanced reaction sets.

    Notes
    -----
    See [1]_ section 3.3 for a complete description of the algorithm.


    .. [1] Gevorgyan, A., M. G Poolman, and D. A Fell.
           "Detection of Stoichiometric Inconsistencies in Biomolecular Models."
           Bioinformatics 24, no. 19 (2008): 2245.
    """
    def create_milp_problem():
        ns_problem = Model()
        k_vars = list()
        for met in metabolites:
            # The element y[i] of the mass vector.
            y_var = Variable(met.id)
            k_var = Variable("k_{}".format(met.id), type="binary")
            k_vars.append(k_var)
            ns_problem.add([y_var, k_var])
            # This constraint is equivalent to 0 <= y[i] <= k[i].
            ns_problem.add(Constraint(
                y_var - k_var, lb=0, name="switch_{}".format(met.id)))
        ns_problem.update()
        # add nullspace constraints
        for (i, row) in enumerate(left_ns):
            if (row == 0.0).all():
                # singleton set!
                continue
            met = met_inv_map[i]
            y_var = ns_problem.variables[met_inv_map[i].id]
            expression = sympy.Add(
                *[coef * y_var for coef in row if coef != 0.0])
            constraint = Constraint(expression, lb=0, ub=0,
                                    name="ns_{}".format(met.id))
            ns_problem.add(constraint)
        # The objective is to minimize the binary indicators k[i], subject to
        # the above inequality constraints.
        ns_problem.objective = Objective(1)
        ns_problem.objective.set_linear_coefficients(
            {k_var: 1. for k_var in k_vars})
        ns_problem.objective.direction = "min"
        return ns_problem, k_vars

    def add_cut(non_zero):
        # non_zero corresponds to 'P' in the paper
        expr = sympy.Add(*k_vars)
        constr = Constraint(expr, ub=non_zero - 1)
        problem.add(constr)
        return constr

    if check_stoichiometric_consistency(model):
        return set()
    Model = model.solver.interface.Model
    Constraint = model.solver.interface.Constraint
    Variable = model.solver.interface.Variable
    Objective = model.solver.interface.Objective
    unconserved_mets = find_unconserved_metabolites(model)
    internal_rxns = set(model.reactions) - set(model.exchanges)
    internal_mets = set(met for rxn in internal_rxns for met in rxn.metabolites)
    LOGGER.debug("model has %d internal metabolites", len(internal_mets))
    LOGGER.debug("model has %d internal reactions", len(internal_rxns))
    get_id = attrgetter("id")
    reactions = sorted(internal_rxns, key=get_id)
    metabolites = sorted(internal_mets, key=get_id)
    stoich, met_index, rxn_index = stoichiometry_matrix(metabolites, reactions)
    met_inv_map = {i: met for (met, i) in iteritems(met_index)}
    left_ns = nullspace(stoich.T)
    # deal with numerical instabilities
    left_ns[np.abs(left_ns) < tol] = 0.0
    inc_minimal = set()
    LOGGER.debug("model has %d unconserved metabolites", len(unconserved_mets))
    problem, k_vars = create_milp_problem()
    for met in unconserved_mets:
        row = met_index[met]
        switch = "switch_{}".format(met.id)
        if (left_ns[row] == 0.0).all():
            LOGGER.debug("%s: singleton minimal unconservable set", met.id)
            # singleton set!
            inc_minimal.add((met,))
            continue
        # expect a positive mass for the unconserved metabolite
        problem.constraints[switch].lb = 1e-6
        status = problem.optimize()
        cuts = list()
        while status == "optimal":
            LOGGER.debug("%s: status %s", met.id, status)
            solution = [model.metabolites.get_by_id(var.name[2:])
                        for var in k_vars if var.primal > 0.2]
            LOGGER.debug("%s: set size %d", met.id, len(solution))
            inc_minimal.add(tuple(solution))
            cuts.append(add_cut(len(solution)))
            status = problem.optimize()
        LOGGER.debug("%s: last status %s", met.id, status)
        # reset
        problem.constraints[switch].lb = 0.0
        problem.remove(cuts)
    return inc_minimal
