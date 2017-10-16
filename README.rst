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
2. Run the current model through a test suite that represents the community
   standard.
3. Generate an informative report which details the results of the test suite in
   a visually appealing manner.
4. (Re-)compute test statistics for an existing version controlled history of
   a metabolic model.

And in order to make this process as easy as possible the generated repository
can easily be integrated with continuous integration testing providers such as
Travis CI, which means that anytime you push a model change to GitHub, the test
suite will be run automatically and a report will be available for you to look
at via GitHub pages for your repository.

.. summary-end

* Documentation: https://memote.readthedocs.io/.

Installation
============

We highly recommend creating a Python virtualenv for your model tesing purposes.

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

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
