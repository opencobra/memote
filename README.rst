===============================
memote
===============================


.. image:: https://img.shields.io/pypi/v/memote.svg
        :target: https://pypi.python.org/pypi/memote

.. image:: https://img.shields.io/travis/biosustain/memote.svg
        :target: https://travis-ci.org/biosustain/memote

.. image:: https://readthedocs.org/projects/memote/badge/?version=latest
        :target: https://memote.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/biosustain/memote/shield.svg
     :target: https://pyup.io/repos/github/biosustain/memote/
     :alt: Updates

.. image:: https://codecov.io/gh/biosustain/memote/branch/master/graph/badge.svg
        :target: https://codecov.io/gh/biosustain/memote
        :alt: Coverage

Genome-scale metabolic model test suite.

Our goal in promoting this tool is to achieve to major shifts in the metabolic
model building community:

1. Models should be version-controlled such that changes can be tracked and if
   necessary reverted. Ideally, they should be available through a public
   repository such as on GitHub. That will allow other researchers to inspect,
   share, and contribute to the model.
2. Models should, for the benefit of the community and for research gain, live
   up to certain standards and minimal functionality.

The `memote` tool therefore performs four subfunctions:

1. Create a skeleton git repository for the model.
2. Run the current model through a test suite which we hope will be the
   representation of the community standard.
3. Generate an informative report which details the results of the test suite in
   a visually appealing manner.
4. (Re-)compute test statistics for an existing version controlled history of
   the model at hand.

And in order to make this process as easy as possible the generated repository
can easily be integrated with Travis CI which means that anytime you push a
model change to GitHub, the test suite will be run automatically and a report
will be available for you to look at via GitHub pages for your repository.

* Free software: `Apache Software License 2.0 <LICENSE>`_
* Documentation: https://memote.readthedocs.io.


Features
--------

* TODO

Copyright
---------

Copyright (c) 2017 Novo Nordisk Foundation Center for Biosustainability,
Technical University of Denmark.

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`biosustain/cookiecutter-decaf-python`: https://github.com/biosustain/cookiecutter-decaf-python
