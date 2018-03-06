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

"""Supporting functions for stoichiometric consistency checks."""

from __future__ import absolute_import, division

import logging

from numpy import sqrt

LOGGER = logging.getLogger(__name__)


def confusion_matrix(predicted_essential, expected_essential,
                     predicted_nonessential, expected_nonessential):
    """
    Compute a representation of the confusion matrix.

    Parameters
    ----------
    predicted_essential : set
    expected_essential : set
    predicted_nonessential : set
    expected_nonessential : set

    Returns
    -------
    dict
        Confusion matrix as different keys of a dictionary. The abbreviated
        keys correspond to the ones used in [1]_.

    References
    ----------
    .. [1] `Wikipedia entry for the Confusion matrix
           <https://en.wikipedia.org/wiki/Confusion_matrix>`_

    """
    true_positive = predicted_essential & expected_essential
    tp = len(true_positive)
    true_negative = predicted_nonessential & expected_nonessential
    tn = len(true_negative)
    false_positive = predicted_essential - expected_essential
    fp = len(false_positive)
    false_negative = predicted_nonessential - expected_nonessential
    fn = len(false_negative)
    # sensitivity or true positive rate
    try:
        tpr = tp / (tp + fn)
    except ZeroDivisionError:
        tpr = float("nan")
    # specificity or true negative rate
    try:
        tnr = tn / (tn + fp)
    except ZeroDivisionError:
        tnr = float("nan")
    # precision or positive predictive value
    try:
        ppv = tp / (tp + fp)
    except ZeroDivisionError:
        ppv = float("nan")
    # false discovery rate
    fdr = 1 - ppv
    # accuracy
    try:
        acc = (tp + tn) / (tp + tn + fp + fn)
    except ZeroDivisionError:
        acc = float("nan")
    # Compute Matthews correlation coefficient.
    try:
        mcc = (tp * tn - fp * fn) / sqrt((tp + fp) * (tp + fn) * (tn + fn))
    except ZeroDivisionError:
        mcc = float("nan")
    return {
        "TP": list(true_positive),
        "TN": list(true_negative),
        "FP": list(false_positive),
        "FN": list(false_negative),
        "TPR": tpr,
        "TNR": tnr,
        "PPV": ppv,
        "FDR": fdr,
        "ACC": acc,
        "MCC": mcc
    }
