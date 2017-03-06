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

"""
Supporting functions for stoichiometric consistency checks.
"""

from __future__ import absolute_import

import logging
from operator import attrgetter

import numpy as np
import sympy
from nump.linalg import svd
from six import iteritems

__all__ = ("check_stoichiometric_consistency", "find_unconserved_metabolites")

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
    for metabolite in metabolites:
        # The element m[i] of the mass vector.
        m_var = Variable(metabolite.id)
        k_var = Variable("k_{}".format(metabolite.id), type="binary")
        k_vars.append(k_var)
        stoich_trans.add([m_var, k_var])
        # This constraint is equivalent to 0 <= k[i] <= m[i].
        stoich_trans.add(Constraint(
            k_var - m_var, ub=0, name="switch_{}".format(metabolite.id)))
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


def unconserved_minimal_set(metabolite_index, reaction_index, nullspace):
    """
    Find minimal unconserved sets.
    """
    # create continuous y vars
    # create binary k vars
    # constrain y - k to lower bound 0
    # add nullspace constraints
    # constrain y > 0 (y >= epsilon)
    # minimize

def find_inconsistent_min_stoichiometry(model, tol=1e-15):
    """
    Find minimal unbalanced reaction sets.

    Notes
    -----
    See [1]_ section 3.3 for a complete description of the algorithm.


    .. [1] Gevorgyan, A., M. G Poolman, and D. A Fell.
           "Detection of Stoichiometric Inconsistencies in Biomolecular Models."
           Bioinformatics 24, no. 19 (2008): 2245.
    """
    if check_stoichiometric_consistency(model):
        return set()
    unconserved_mets = find_unconserved_metabolites(model)
    internal_rxns = set(model.reactions) - set(model.exchanges)
    internal_mets = set(met for rxn in internal_rxns for met in rxn.metabolites)
    LOGGER.debug("model has %d internal metabolites", len(internal_mets))
    LOGGER.debug("model has %d internal reactions", len(internal_rxns))
    get_id = attrgetter("id")
    reactions = sorted(internal_rxns, key=get_id)
    metabolites = sorted(internal_mets, key=get_id)
    stoich, met_index, rxn_index = stoichiometry_matrix(metabolites, reactions)
    left_ns = nullspace(stoich.T)
    inc_minimal = set()
    for met in unconserved_mets:
        row = met_index[met]
        if (left_ns[row] < tol).all():
            # singleton set
            inc_minimal.add((met,))
            continue

    return set()
