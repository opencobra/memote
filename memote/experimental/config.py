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
from os.path import dirname, join, isabs

import ruamel.yaml as yaml
from jsonschema import Draft4Validator
from importlib_resources import open_text
from six import iteritems

from memote.experimental.medium import Medium
from memote.experimental.essentiality import EssentialityExperiment
from memote.experimental.growth import GrowthExperiment

__all__ = ("ExperimentConfiguration",)

LOGGER = logging.getLogger(__name__)


class ExperimentConfiguration(object):
    """Represent an experimental configuration."""

    with open_text("memote.experimental.schemata", "configuration.json",
                   encoding="utf-8") as file_handle:
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
            self.config = yaml.safe_load(file_h)
        self._base = dirname(filename)
        self.media = dict()
        self.essentiality = dict()
        self.growth = dict()

    def load_data(self, model):
        """
        Load a configuration file and validate it.

        Parameters
        ----------
        model : cobra.Model
            The metabolic model under investigation.

        """
        self.validate()
        self.load_medium(model)
        self.load_essentiality(model)
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
        path = self.get_path(data,
                             join("data", "experimental", "essentiality"))
        for exp_id, exp in iteritems(experiments):
            if exp is None:
                exp = dict()
            filename = exp.get("filename")
            if filename is None:
                filename = join(path, "{}.csv".format(exp_id))
            elif not isabs(filename):
                filename = join(path, filename)
            experiment = EssentialityExperiment(
                identifier=exp_id, obj=exp, filename=filename)
            if experiment.medium is not None:
                assert experiment.medium in self.media, \
                    "Experiment '{}' has an undefined medium '{}'.".format(
                        exp_id, experiment.medium)
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
        path = self.get_path(data,
                             join("data", "experimental", "growth"))
        for exp_id, exp in iteritems(experiments):
            if exp is None:
                exp = dict()
            filename = exp.get("filename")
            if filename is None:
                filename = join(path, "{}.csv".format(exp_id))
            elif not isabs(filename):
                filename = join(path, filename)
            growth = GrowthExperiment(
                identifier=exp_id, obj=exp, filename=filename)
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
