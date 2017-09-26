History
=======

Next Release
------------

0.4.4 (2017-09-26)
------------------

* Fix a bunch of bugs:
    - Remove false positive detection of Biocyc annotation
    - Allow memote to identify CTP or GTP driven transport reactions
    - Refactor how memote detects GAM in the biomass reaction
* Add tests to find deadend, orphan and disconnected metabolites.
* Extend and improve algorithm to find energy-generating cycles
* Remove the ``print`` statement from ``memote.support.annotation
  .generate_component_annotation_miriam_match``.
* Fix the bug in the assertion output of ``memote.memote.suite.tests.test_basic
  .test_gene_protein_reaction_rule_presence``.
* Split mass-charge-balance test into two separate tests for more clarity
* Fix a bug in ``memote.support.consistency_helpers.get_internals`` that did
  not exclude the (by definition) imbalanced biomass reactions.

0.4.3 (2017-09-25)
------------------

* Fix documentation building and add auto-generation of docs.
* Make the command line output of pytest more verbose until the report is up to
  speed.
* Temporarily skip ``test_find_stoichiometrically_balanced_cycles``
* Catch errors when testing for compartments and loops.

0.4.2 (2017-08-22)
------------------

* Push all branches with ``memote online``.

0.4.1 (2017-08-22)
------------------

* Fix JSON serialization of test results.

0.4.0 (2017-08-21)
------------------

* Add a programmatic API in module ``memote.suite.api`` (#162).
* Reorganize the structure and build process for auto-documenting ``memote`` (#172).
* Add a new command ``memote online`` (#95, #153).
* Add more basic tests.

0.3.6 (2017-08-15)
------------------

* Improve GitHub support.
* Update the readthedocs and gitter badge.
* Add a function ``memote.show_versions()`` for easy dependency checking.

0.3.4 (2017-08-12)
------------------

* Properly configure Travis deployment.

0.3.3 (2017-08-12)
------------------

* Build tags.

0.3.2 (2017-08-12)
------------------

* Enable automatic deployment to PyPi.

0.3.0 (2017-08-12)
------------------

* Greatly extend the core test modules:
  * basic
  * consistency
  * biomass
  * annotation
  * syntax
* Add an Angular-material based report with plotly.
* Add documentation on readthedocs.io.
* Make the first release on PyPi.

0.2.0 (2017-02-09)
------------------

* Yet another package structure for supporting functions, their tests, and the
  model test suite.

0.1.0 (2017-01-30)
------------------

* New package structure and start of joint development
