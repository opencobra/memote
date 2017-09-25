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
from warnings import warn

import pandas as pd
import numpy as np
from cobra.flux_analysis import single_gene_deletion

__all__ = ()

LOGGER = logging.getLogger(__name__)


def configure_model(model, config):
    """
    Return a model which is set up according a specific condition.

    Model conditions should relate to experimental conditions and
    are specified in the config.yml. The type of media, the assumed
    objective function, and measured secretion products should be
    listed in the config.
    """
    objective = config['objectives'][0]
    if isinstance(objective, dict):
        model.objective = objective
    else:
        model.objective = {model.reactions.get_by_id(objective): 1}


def in_silico_essentiality(model, data):
    """
    Perform an in silico gene knockout study on a given model.

    Based on experimental data provided by the user. Returns a series with
    identical shape.
    """
    genes = [g for g in data['Gene ID'] if g in model.genes]
    results = single_gene_deletion(model, gene_list=genes, method='fba')
    warn("The following genes are not in the model and were ignored: {}."
         "".format(", ".join(set(data['Gene ID']) - set(genes))))
    return pd.concat([data[data['Gene ID'].isin(genes)], results], axis=1,
                     copy=False)


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
