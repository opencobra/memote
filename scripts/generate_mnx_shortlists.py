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

# MetaNetX has been published as:
# MetaNetX/MNXref - reconciliation of metabolites and biochemical reactions to
# bring together genome-scale metabolic networks
# Sébastien Moretti, Olivier Martin, T. Van Du Tran, Alan Bridge,
# Anne Morgat and Marco Pagni
# Nucleic Acids Research (2016), 44(D1):D523-D526
# https://doi.org/10.1093/bioinformatics/btt036
# https://www.metanetx.org/
#

"""Scripts to generate a reduced shortlist from MetaNetX database dumps."""

from __future__ import absolute_import

import logging
import sqlite3
from builtins import open
from os.path import exists, dirname, join, pardir

import click
import click_log
import pandas as pd
from requests import get

LOGGER = logging.getLogger()
click_log.basic_config(LOGGER)


def generate_shortlist(mnx_db, shortlist):
    """
    Create a condensed cross-references format from a long table.

    Parameters
    ----------
    mnx_db : pandas.DataFrame
    shortlist : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
        A condensed format with MetaNetX identifiers as columns and database
        identifiers as rows. Elements are lists and often have multiple entries.

    """
    # Reduce the whole database to targets of interest.
    xref = mnx_db.loc[mnx_db["MNX_ID"].isin(shortlist["MNX_ID"]), :]
    # Drop deprecated MetaNetX identifiers.
    # xref = xref.loc[~xref["XREF"].str.startswith("deprecated", na=False), :]
    # Drop self-references.
    xref = xref.loc[xref["XREF"] != xref["MNX_ID"], :]
    # Split namespaces from identifiers.
    xref[["XREF_ID", "XREF"]] = xref["XREF"].str.split(":", n=1, expand=True)
    # Group the data in the xref dataframe so that one MNX ID maps to all
    # corresponding cross-references from other databases. Then list all
    # identifiers that belong to these databases:
    # MNX_ID    XREF_ID
    # MNXM0     chebi       [23367, 59999]
    #           metacyc     [UNKNOWN]
    # Make a separate column for every XREF_ID:
    # MNX_ID    chebi           metacyc
    # MNXM0     [23367, 59999]  [UNKNOWN]
    xref = xref.groupby(["MNX_ID", "XREF_ID"], as_index=False, sort=False)[
        "XREF"].apply(list).unstack('XREF_ID')
    # Re-insert MetaNetX identifiers as lists.
    xref["mnx"] = [[x] for x in xref.index]
    # Transpose the dataframe such that the index are now xref databases and the
    # column names are metanetx IDs.
    return xref.T


@click.command()
@click.help_option("--help", "-h")
@click_log.simple_verbosity_option(
    LOGGER, default="INFO", show_default=True,
    type=click.Choice(["CRITICAL", "ERROR", "WARN", "INFO", "DEBUG"]))
@click.argument("mnx_dump", type=click.Path(dir_okay=False))
def generate(mnx_dump):
    """
    Generate a shortlist of metabolites with cross-references using MetaNetX.

    MNX_DUMP : The compounds dump from MetaNetX usually called 'chem_xref.tsv'.
        Will be downloaded if it doesn't exist.

    """
    LOGGER.info("Read shortlist.")
    targets = pd.read_table(join(dirname(__file__), "shortlist.tsv"))
    if not exists(mnx_dump):
        # Download the MetaNetX compounds dump if it doesn't exists.
        # Download done as per https://stackoverflow.com/a/16696317.
        LOGGER.info("MetaNetX dump '%s' does not exist. Downloading...",
                    mnx_dump)
        with open(mnx_dump, "wb") as file_handle, \
            get("https://www.metanetx.org/cgi-bin/mnxget/mnxref/chem_xref.tsv",
                stream=True) as stream:
            for chunk in stream.iter_content(chunk_size=1024):
                file_handle.write(chunk)
        LOGGER.info("Done.")
    LOGGER.info("Read the MetaNetX dump with cross-references.")
    db = pd.read_table(mnx_dump, comment='#',
                       names=['XREF', 'MNX_ID', 'Evidence', 'Description'])
    LOGGER.info("Generate the shortlist cross-references.")
    res = generate_shortlist(db, targets)
    LOGGER.info("Save result.")
    res.to_json(join(dirname(__file__), pardir, "memote", "support", "data",
                     "met_id_shortlist.json"), force_ascii=False)


if __name__ == "__main__":
    generate()
