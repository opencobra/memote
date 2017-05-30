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

"""Supporting functions for data-driven tests on genome level."""

from __future__ import absolute_import

import logging
import re
from glob import glob
from os.path import join
from os import listdir
from warnings import warn

import ruamel.yaml as yaml
import pandas as pd
import numpy as np
from cobra.exceptions import Infeasible

__all__ = ()

LOGGER = logging.getLogger(__name__)


def essentiality_file_paths(directory="./"):
    """Identify all relevant essentiality data files."""
    return sorted(glob(join(directory, "*.csv")))


def load_experiment_data_config(config_filepath="config.yml"):
    """Import config.yml file."""
    try:
        with open(config_filepath, 'r') as config:
            return yaml.load(config)
    except IOError:
        warn(
            "There is no config.yml in the memote root directory. Calculations"
            "will proceed using the default configuration of the model."
        )
        return None


def prepare_model_medium(
    model, experiment, experiment_id, config
):
    """
    Return a model which is set up according a specific condition.

    Model conditions should relate to experimental conditions and
    are specified in the config.yml. The type of media, the assumed
    objective function, and measured secretion products should be
    listed in the config.
    """
    working_model = model
    if config:
        try:
            condition = config[experiment][experiment_id]
        except KeyError:
            return None
        else:
            if 'objective' in condition.keys():
                working_model.objective = working_model.reactions.get_by_id(
                    condition['objective'])
                # Not implemented yet.
                # if 'medium' in condition.keys():
                #   working_model.define_medium(condition['medium'])
            return working_model
    else:
        return None


def in_silico_essentiality(
    series, model, experiment_id=None, config_filepath="config.yml"
):
    """
    Perform an in silico gene knockout study on a given model.

    Based on experimental data provided by the user. Returns a series with
    identical shape.
    """
    # TODO: Once cobrapy has a generic and well-tested gene_deletion
    # function, we should replace this.
    in_silico_series = series.copy()
    config = load_experiment_data_config(config_filepath)
    prepared_model = prepare_model_medium(
        model, 'essentiality', experiment_id, config
    )
    if prepared_model:
        pass
    else:
        warn('Calculations will proceed using the default configuration of '
             'the model.')
        prepared_model = model
    for gene in series.index:
        with prepared_model:
            try:
                prepared_model.genes.get_by_id(gene).knock_out()
            except KeyError:
                warn('{} does not exist in {}'.format(gene, model.id))
                in_silico_series.set_value(
                    gene,
                    0
                )
            else:
                try:
                    solution = model.optimize()
                    in_silico_series.set_value(
                        gene,
                        round(solution.f, 3)
                    )
                except Infeasible as e:
                    print(e)
                    in_silico_series.set_value(
                        gene,
                        0
                    )
    return in_silico_series


def prepare_essentiality_data(filename, model, config_filepath="config.yml"):
    """Convert CSV to dataframe combining experimental and predicted data."""
    essentiality_dataframe = {}
    experiment_id = filename[2:].split('.')[0]
    experiment_data_tag = '{}_experiment'.format(experiment_id)
    model_data_tag = '{}_model'.format(experiment_id)
    essentiality_dataframe[experiment_data_tag] = pd.read_csv(
        filename, sep='\t', index_col=0, squeeze=True
    )
    essentiality_dataframe[model_data_tag] = in_silico_essentiality(
        essentiality_dataframe[experiment_data_tag],
        model,
        experiment_id,
        config_filepath
    )
    return pd.DataFrame(essentiality_dataframe)


def prepare_qualitative_comparison(dataframe):
    """Convert quantitative dataframe into qualitative dataframe."""
    exp, mod = dataframe.columns
    dataframe[dataframe > 1e-6] = True
    dataframe[dataframe < 1e-6] = False
    dataframe.dropna(inplace=True)
    dataframe['true_positives'] = np.where(
        dataframe[exp] == dataframe[mod],
        True,
        False
    )
    return dataframe, exp
