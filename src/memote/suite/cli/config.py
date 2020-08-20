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

"""Define and make parseable the memote configuration file."""

from __future__ import absolute_import

import click
from click_configfile import ConfigFileReader, Param, SectionSchema, matches_section


class ConfigSectionSchema(object):
    """Describes all sections of the memote configuration file."""

    @matches_section("memote")
    class Memote(SectionSchema):
        """
        Describes the memote configuration keys and values.

        Memote configuration should be carried out either in 'setup.cfg' or
        a dedicated 'memote.ini' file.

        """

        collect = Param(type=bool, default=True)
        git = Param(type=bool, default=True)
        addargs = Param(type=str, default="")
        model = Param(type=click.Path(exists=False, dir_okay=False))
        deployment = Param(type=str, default="gh-pages")
        location = Param(type=str)
        github_repository = Param(type=str)
        github_username = Param(type=str)
        exclusive = Param(type=str, multiple=True)
        skip = Param(type=str, multiple=True)
        solver = Param(
            type=click.Choice(["cplex", "glpk", "gurobi", "glpk_exact"]), default="glpk"
        )
        solver_timeout = Param(type=int, default=None)
        experimental = Param(
            type=click.Path(exists=False, dir_okay=False), default=None
        )


class ConfigFileProcessor(ConfigFileReader):
    """Determine which files to look for and what sections."""

    config_files = ["memote.ini", "setup.cfg"]
    config_section_schemas = [ConfigSectionSchema.Memote]
