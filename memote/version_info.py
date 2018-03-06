# -*- coding: utf-8 -*-

# Adapated from:
# https://github.com/pandas-dev/pandas/blob/master/pandas/util/_print_versions.py
# which is published under a BSD license.

"""Provide a single function for a user to capture important dependencies."""

from __future__ import absolute_import, print_function

from builtins import dict

import platform

import pip

__all__ = ("show_versions", "PKG_ORDER")

SYS_ORDER = [
    "OS",
    "OS-release",
    "Python"
]
PKG_ORDER = [
    "pip",
    "setuptools",
    "memote",
    "cobra",
    "future",
    "swiglpk",
    "optlang",
    "ruamel.yaml",
    "pandas",
    "numpy",
    "python-libsbml",
    "lxml",
    "click",
    "click_configfile",
    "click_log",
    "pytest",
    "Jinja2",
    "jinja2-ospath",
    "cookiecutter",
    "git",
    "github",
    "travispy",
    "travis",
    "numpydoc"
    "goodtables"
]


def get_sys_info():
    """Return system information as a dict."""
    blob = dict()
    blob["OS"] = platform.system()
    blob["OS-release"] = platform.release()
    blob["Python"] = platform.python_version()
    return blob


def get_pkg_info():
    """Return Python package information as a dict."""
    dependencies = frozenset(PKG_ORDER)
    blob = dict()
    for dist in pip.get_installed_distributions():
        if dist.project_name in dependencies:
            blob[dist.project_name] = dist.version
    return blob


def show_versions():
    """Print the formatted information to standard out."""
    info = get_sys_info()
    info.update(get_pkg_info())
    format_str = "{:<%d} {:>%d}" % (max(map(len, info)),
                                    max(map(len, info.values())))
    print("\nSystem Information")
    print("==================")
    for name in SYS_ORDER:
        print(format_str.format(name, info[name]))

    print("\nPackage Versions")
    print("================")
    for name in PKG_ORDER:
        if name in info:
            print(format_str.format(name, info[name]))
