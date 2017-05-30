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

"""YAML parser for the experiment configuration files."""

from __future__ import absolute_import

import json
from io import open
from glob import glob
from os.path import dirname, join, basename

import ruamel.yaml as yaml
import jsonschema
from six import iteritems
from goodtables import validate

from memote.io.checks import gene_id_check, check_partial

__all__ = ("ExperimentConfig",)


def name_part(path):
    """
    Return the basename of a file path excluding extensions.

    Parameters
    ----------
    path : str or pathlib.Path
        Can be a full relative or absolute path.

    Returns
    -------
    str or pathlib.Path
        The `basename` component of the path without its extensions.

    """
    return basename(path).split(".", 1)[0]


def extensions_part(path):
    """
    Return the normalized extensions of a file path.

    Parameters
    ----------
    path : str or pathlib.Path
        Can be a full relative or absolute path.

    Returns
    -------
    list
        The extension(s) in lower case as a list.

    Raises
    ------
    IndexError
        If the file path has no extensions.

    """
    return basename(path).lower().split(".")[1:]


class ExperimentConfig(object):
    """

    """
    experiment_types = frozenset(["essentiality", "growth", "production"])
    data_formats = frozenset(["csv", "tsv", "xls", "xlsx", "ods"])

    def __init__(self, filename, model):
        """
        Load and validate an experiment configuration file.

        Parameters
        ----------
        filename : str or pathlib.Path
            The location of the configuration file. The name component must
            be one of {"essentiality", "growth", "production"}.
        model : cobra.Model
            The metabolic model under investigation.

        """
        self.type = name_part(filename)
        assert self.type in self.experiment_types
        with open(filename) as file_h:
            self.content = yaml.safe_load(file_h)
        self.media = list()
        self.media_files = glob(join(dirname(filename), "media", "*"))
        self.media_files = frozenset(filter(
            lambda f: self.data_formats.issuperset(extensions_part(f)),
            self.media_files))
        self.data = list()
        self.data_files = glob(join(dirname(filename), self.type, "*"))
        self.data_files = frozenset(filter(
            lambda f: self.data_formats.issuperset(extensions_part(f)),
            self.data_files))
        self.model = model
        self.validate()

    @classmethod
    def load(cls, filename):
        return cls(filename)
        # TODO: We want to iterate all ValidationErrors and integrate
        # output in pytest.

    def validate(self):
        """Validate the format and content of the configuration file."""
        self.validate_config()
        self.validate_media()
        self.validate_data()

    def validate_config(self):
        """Validate the presence and format of the configuration file."""
        with open(join(
                dirname(__file__), "schemata", "configuration.json")) as file_h:
            schema = json.load(file_h)
        jsonschema.validate(self.content, schema)
        self.media = [
            exp["medium"] for exp in self.content["experiments"]
            if "medium" in exp]
        self.data = list(self.content["experiments"])

    def validate_media(self):
        """Validate the presence of media files."""
        # TODO: Add goodtables validations here. With custom checks.
        # * existence of file
        # * content validation
        # * check compound IDs and presence of exchange reactions in model
        with open(join(
                dirname(__file__), "schemata", "medium.json")) as file_h:
            schema = json.load(file_h)
        for filename in self.media:
            assert filename in self.media_files
            validate(filename, preset='table', schema=schema, order_fields=True)

    def validate_data(self):
        """Validate the presence of data files."""
        with open(join(dirname(__file__), "schemata",
                       "{}.json".format(self.type))) as file_h:
            schema = json.load(file_h)
        checks = {
            "essentiality": [
                check_partial(gene_id_check, frozenset(self.model.genes))
            ],
            "growth": [],
            "production": [],
        }[self.type]
        names = {name_part(f): f for f in self.data_files}
        for exp, obj in iteritems(self.content["experiments"]):
            assert exp in names
            validate(names[exp], preset='table', schema=schema,
                     order_fields=True, custom_checks=checks)
            # * check gene IDs or whatever IDs

