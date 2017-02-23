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
Supporting functions for consistency checks performed on the model object.
"""

from __future__ import absolute_import

__all__ = ("check_stoichiometric_consistency", "check_unconserved_metabolites")

import logging

import sympy

LOGGER = logging.getLogger(__name__)


def check_stoichiometric_consistency(model):
    """
    Confirm that the metabolic model is mass-balanced.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    """
    Model = model.solver.interface.Model
    Constraint = model.solver.interface.Constraint
    Variable = model.solver.interface.Variable
    Objective = model.solver.interface.Objective
    mass_balances_model = Model()
    for metabolite in model.metabolites:
        mass_balances_model.add(Variable(metabolite.id, lb=1))
    for reaction in model.reactions:
        if reaction not in model.exchanges:
            expression = sympy.Add(
                *[coefficient * mass_balances_model.variables[metabolite.id]
                for (metabolite, coefficient) in reaction.metabolites.items()])
            constraint = Constraint(expression, lb=0, ub=0, name=reaction.id)
            mass_balances_model.add(constraint)
    mass_balances_model.objective = Objective(1)
    mass_balances_model.objective.set_linear_coefficients(
        {var: 1. for var in mass_balances_model.variables})
    mass_balances_model.objective.direction = 'min'
    status = mass_balances_model.optimize()
    if status == 'optimal':
        return True
    elif status == 'infeasible':
        return False
    else:
        raise Exception("Couldn't determine stoichiometric consistencty."
                        "Solver returned '{}' solution status (only feasible or optimal expected).".format(status))


def check_unconserved_metabolites(model):
    """
    Find unconserved metabolites in the metabolic model.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    """
    Model = model.solver.interface.Model
    Constraint = model.solver.interface.Constraint
    Variable = model.solver.interface.Variable
    Objective = model.solver.interface.Objective
    mass_balances_model = Model()
    y_vars = list()
    for metabolite in model.metabolites:
        met_var = Variable(metabolite.id)
        y_var = Variable('y_{}'.format(metabolite.id), type='binary')
        y_vars.append(y_var)
        mass_balances_model.add([met_var, y_var])
        mass_balances_model.add(Constraint(y_var - met_var, ub=0, name='switch_{}'.format(metabolite.id)))
    mass_balances_model.update()
    for reaction in model.reactions:
        if reaction in model.exchanges:
            continue
        expression = sympy.Add(*[coefficient * mass_balances_model.variables[metabolite.id] for metabolite, coefficient in reaction.metabolites.items()])
        constraint = Constraint(expression, lb=0, ub=0, name=reaction.id)
        mass_balances_model.add(constraint)
    mass_balances_model.objective = Objective(1)
    mass_balances_model.objective.set_linear_coefficients({var: 1. for var in y_vars})
    status = mass_balances_model.optimize()
    if status == 'optimal':
        return [model.metabolites.get_by_id(var.name.replace('y_', '')) for var in y_vars if var.primal < 0.8]
    else:
        raise Exception("Couldn't compute list of unconserved metabolites."
                       "Solver returned '{}' solution status (only feasible or optimal expected).".format(status))
