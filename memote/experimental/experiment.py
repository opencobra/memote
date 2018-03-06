# -*- coding: utf-8 -*-

# Copyright 2018 Novo Nordisk Foundation Center for Biosustainability,
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

"""Provide a base class for experiment definitions."""

from __future__ import absolute_import

import logging

from memote.experimental.experimental_base import ExperimentalBase

__all__ = ("Experiment",)

LOGGER = logging.getLogger(__name__)


class Experiment(ExperimentalBase):
    """Base class for experimental data."""

    def __init__(self, obj, **kwargs):
        """
        Initialize an experiment.

        Parameters
        ----------
        obj : dict
        kwargs

        """
        super(Experiment, self).__init__(obj=obj, **kwargs)
        self.objective = obj.get("objective")
        # TODO: This is a placeholder. Constraints need to be loaded with
        # optlang.
        self.constraints = obj.get("constraints", [])
        if len(self.constraints) > 0:
            raise NotImplementedError(
                "This feature is not implemented yet. Please let us know that "
                "you want it at https://github.com/opencobra/memote/issues.")

    def evaluate(self, model):
        """Abstract base method for evaluating experimental data."""
        raise NotImplementedError("Base class does not implement this method.")
