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

"""Provide a YAML parser for experiment configuration files."""

from __future__ import absolute_import

import json
import logging
from io import open
from math import isnan
from os.path import dirname, isabs, join

from importlib_resources import open_text
from jsonschema import Draft4Validator
from ruamel.yaml import YAML
from six import iteritems

from memote.experimental.essentiality import EssentialityExperiment
from memote.experimental.growth import GrowthExperiment
from memote.experimental.medium import Medium


__all__ = ("ExperimentConfiguration",)

LOGGER = logging.getLogger(__name__)
yaml = YAML(typ="safe")


class ExperimentConfiguration(object):
    """Represent an experimental configuration."""

    with open_text(
        "memote.experimental.schemata", "configuration.json", encoding="utf-8"
    ) as file_handle:
        SCHEMA = json.load(file_handle)

    def __init__(self, filename, **kwargs):
        """
        Load and validate an experiment configuration file.

        Parameters
        ----------
        filename : str or pathlib.Path
            The location of the configuration file.

        """
        super(ExperimentConfiguration, self).__init__(**kwargs)
        with open(filename) as file_h:
            self.config = yaml.load(file_h)
        self._base = dirname(filename)
        self.media = dict()
        self.essentiality = dict()
        self.growth = dict()

    def load(self, model):
        """
        Load all information from an experimental configuration file.

        Parameters
        ----------
        model : cobra.Model
            The metabolic model under investigation.

        """
        self.load_medium(model)
        self.load_essentiality(model)
        self.load_growth(model)
        # self.load_experiment(config.config.get("growth"), model)
        return self

    def validate(self):
        """Validate the configuration file."""
        validator = Draft4Validator(self.SCHEMA)
        if not validator.is_valid(self.config):
            for err in validator.iter_errors(self.config):
                LOGGER.error(str(err.message))
            validator.validate(self.config)

    def load_medium(self, model):
        """Load and validate all media."""
        media = self.config.get("medium")
        if media is None:
            return
        definitions = media.get("definitions")
        if definitions is None or len(definitions) == 0:
            return
        path = self.get_path(media, join("data", "experimental", "media"))
        for medium_id, medium in iteritems(definitions):
            if medium is None:
                medium = dict()
            filename = medium.get("filename")
            if filename is None:
                filename = join(path, "{}.csv".format(medium_id))
            elif not isabs(filename):
                filename = join(path, filename)
            tmp = Medium(identifier=medium_id, obj=medium, filename=filename)
            tmp.load()
            tmp.validate(model)
            self.media[medium_id] = tmp

    def load_essentiality(self, model):
        """Load and validate all data files."""
        data = self.config.get("essentiality")
        if data is None:
            return
        experiments = data.get("experiments")
        if experiments is None or len(experiments) == 0:
            return
        path = self.get_path(data, join("data", "experimental", "essentiality"))
        minimal_growth_rate = self.get_minimal_growth_rate(model)
        for exp_id, exp in iteritems(experiments):
            if exp is None:
                exp = dict()
            filename = exp.get("filename")
            if filename is None:
                filename = join(path, "{}.csv".format(exp_id))
            elif not isabs(filename):
                filename = join(path, filename)
            experiment = EssentialityExperiment(
                identifier=exp_id,
                obj=exp,
                filename=filename,
                minimal_growth_rate=minimal_growth_rate,
            )
            if experiment.medium is not None:
                assert (
                    experiment.medium in self.media
                ), "Experiment '{}' has an undefined medium '{}'.".format(
                    exp_id, experiment.medium
                )
                experiment.medium = self.media[experiment.medium]
            experiment.load()
            experiment.validate(model)
            self.essentiality[exp_id] = experiment

    def load_growth(self, model):
        """Load and validate all data files."""
        data = self.config.get("growth")
        if data is None:
            return
        experiments = data.get("experiments")
        if experiments is None or len(experiments) == 0:
            return
        path = self.get_path(data, join("data", "experimental", "growth"))
        minimal_growth_rate = self.get_minimal_growth_rate(model)
        for exp_id, exp in iteritems(experiments):
            if exp is None:
                exp = dict()
            filename = exp.get("filename")
            if filename is None:
                filename = join(path, "{}.csv".format(exp_id))
            elif not isabs(filename):
                filename = join(path, filename)
            growth = GrowthExperiment(
                identifier=exp_id,
                obj=exp,
                filename=filename,
                minimal_growth_rate=minimal_growth_rate,
            )
            if growth.medium is not None:
                assert (
                    growth.medium in self.media
                ), "Growth-experiment '{}' has an undefined medium '{}'.".format(
                    exp_id, growth.medium
                )
                growth.medium = self.media[growth.medium]
            growth.load()
            growth.validate(model)
            self.growth[exp_id] = growth

    def get_path(self, obj, default):
        """Return a relative or absolute path to experimental data."""
        path = obj.get("path")
        if path is None:
            path = join(self._base, default)
        if not isabs(path):
            path = join(self._base, path)
        return path

    def get_minimal_growth_rate(self, model, threshold=0.1):
        """Calculate min growth default value or return input value.

        This value is used to determine if a model is capable of growth under
        certain experimental conditions.

        Parameters
        ----------
        model : cobra.Model
        threshold : float, optional
            If no input is provided by the user the default value is set to a
            coefficient `threshold` times the growth under default constraints
            (default: 0.1).

        """
        minimal_growth_rate = self.config.get("minimal_growth_rate")
        if minimal_growth_rate is None:
            minimal_growth_rate = model.slim_optimize() * threshold
            if isnan(minimal_growth_rate):
                LOGGER.error(
                    "Threshold set to {} due to infeasible "
                    "solution (NaN produced) with default "
                    "constraints.".format(model.tolerance)
                )
                minimal_growth_rate = model.tolerance
        return minimal_growth_rate
