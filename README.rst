====================================================
memote - the genome-scale metabolic model test suite
====================================================

.. image:: https://img.shields.io/pypi/v/memote.svg
        :target: https://pypi.python.org/pypi/memote

.. image:: https://img.shields.io/travis/opencobra/memote.svg
        :target: https://travis-ci.org/opencobra/memote

.. image:: https://readthedocs.org/projects/memote/badge/?version=latest
        :target: https://memote.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://codecov.io/gh/opencobra/memote/branch/master/graph/badge.svg
        :target: https://codecov.io/gh/opencobra/memote
        :alt: Coverage

.. image:: https://badges.gitter.im/opencobra/memote.svg
        :target: https://gitter.im/opencobra/memote
        :alt: Gitter

.. summary-start

Our goal in promoting this tool is to achieve two major shifts in the metabolic
model building community:

1. Models should be version-controlled such that changes can be tracked and if
   necessary reverted. Ideally, they should be available through a public
   repository such as GitHub that will allow other researchers to inspect,
   share, and contribute to the model.
2. Models should, for the benefit of the community and for research gain, live
   up to certain standards and minimal functionality.

The `memote` tool therefore performs four subfunctions:

1. Create a skeleton git repository for the model.
2. Run the current model through a `test suite that represents the community
   standard`_.
3. Generate an informative report which details the results of the test suite in
   a visually appealing manner.
4. (Re-)compute test statistics for an existing version controlled history of
   a metabolic model.

And in order to make this process as easy as possible the generated repository
can easily be integrated with continuous integration testing providers such as
Travis CI, which means that anytime you push a model change to GitHub, the test
suite will be run automatically and a report will be available for you to look
at via GitHub pages for your repository.

.. _test suite that represents the community    standard: 
  https://github.com/opencobra/memote/wiki/Test-Catalog

.. summary-end

* Documentation: https://memote.readthedocs.io/.

Installation
============

We highly recommend creating a Python virtualenv for your model testing purposes.

To install memote, run this command in your terminal:

.. code-block:: console

    $ pip install memote

This is the preferred method to install memote, as it will always install the
most recent stable release.

.. who-start

Contact
=======

For comments and questions get in touch via

* our `gitter chatroom <https://gitter.im/opencobra/memote>`_
* or our `mailing list <https://groups.google.com/forum/#!forum/memote>`_.

Are you excited about this project? Consider `contributing
<https://memote.readthedocs.io/en/latest/contributing.html>`_ by adding novel
tests, reporting or fixing bugs, and generally help us make this a better
software for everyone.

Copyright
=========

* Copyright (c) 2017, Novo Nordisk Foundation Center for Biosustainability,
  Technical University of Denmark.
* Free software: `Apache Software License 2.0 <LICENSE>`_

.. who-end

Credits
=======

This package was created with Cookiecutter_ and the
`audreyr/cookiecutter-pypackage`_ project template.

Memote relies on click_ for the command line interface, pytest_ for unit 
and model tests, gitpython_ for interacting with git repositories, 
pandas_ for tabular datastructures and data input, jinja2_ for interacting 
with HTML templates, cobrapy_ for analysing genome-scale metabolic 
models, python_libsbml_ for reading and writing Systems Biology Markup 
Language (SBML_), ruamel_ for handling YAML generation, travispy_ and 
travis-encrypt_ for interacting with Travis CI, pygithub_ for access to the 
Github API, sympy_ for matrix calculations, sqlalchemy_ for managing 
``history`` results, numpydoc_ for beautifully formatted doc strings using 
sphinx_, pylru_ for caching, goodtables_ for validation of tabular data, 
depinfo_ for pretty printing our dependencies, six_ and future_ for backward 
and forward compatibility.

The Memote Report App user interface is built with `Angular 5`_, 
`Angular Flex-Layout`_, and `Angular Material`_. We rely on Vega_ for plotting 
results.

The initial development of memote has received funding from:

.. image:: https://upload.wikimedia.org/wikipedia/commons/d/d5/Novo_nordisk_foundation_Logo.png
        :target: http://novonordiskfonden.dk/en

.. image:: https://innovationsfonden.dk/sites/all/themes/novigo/logo.png
        :target: https://innovationsfonden.dk/da

.. image:: http://dd-decaf.eu/images/decaf-logo-md.svg
        :target: http://dd-decaf.eu/

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: 
  https://github.com/audreyr/cookiecutter-pypackage
.. _click: http://click.pocoo.org/5/
.. _pytest: https://docs.pytest.org/en/latest/
.. _gitpython: https://github.com/gitpython-developers/GitPython
.. _pandas: https://pypi.org/project/pandas/
.. _jinja2: http://jinja.pocoo.org/
.. _cobrapy: https://github.com/opencobra/cobrapy
.. _python_libsbml: https://pypi.org/project/python-libsbml/
.. _SBML: http://sbml.org/Main_Page
.. _ruamel: https://pypi.org/project/ruamel.yaml/
.. _travispy: https://pypi.org/project/TravisPy/
.. _travis-encrypt: https://pypi.org/project/travis-encrypt/
.. _pygithub: https://github.com/PyGithub/PyGithub
.. _sympy: http://www.sympy.org/en/index.html
.. _sqlalchemy: http://www.sqlalchemy.org/
.. _numpydoc: https://github.com/numpy/numpydoc
.. _sphinx: http://www.sphinx-doc.org/en/stable/
.. _pylru: https://pypi.org/project/pylru/
.. _goodtables: https://github.com/frictionlessdata/goodtables-py
.. _depinfo: https://pypi.org/project/depinfo/
.. _six: https://pypi.org/project/six/
.. _future: https://pypi.org/project/future/
.. _Angular 5: https://angular.io/
.. _Angular Flex-Layout: https://github.com/angular/flex-layout
.. _Angular Material: https://material.angular.io/
.. _Vega: https://vega.github.io/vega/
