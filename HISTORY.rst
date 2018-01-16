History
=======

Next Release
------------

0.5.0 (2018-01-16)
------------------

* Enable test result and meta-data collection.
* Allow command line option and configuration of exclusive test cases and
  modules skipping all others (``--exclusive test_biomass``).
* Allow command line option and configuration to skip test cases and
  modules (``--skip test_model_id_presence``).
* Introduce a dummy configuration file for the report organization and test
  scoring weights.
* Sort unconfigured tests into the card 'Misc. Tests' in the snapshot report.
* Handle skipped tests better in the snapshot report.
* Bundle the Angular report javascript libraries in the snapshot template
* Pass results into the report as JSON
* Fixed/ changed a lot of visuals on the angular report:
    - Indent the rows of the parametrized test results
    - Color the header text of the parametrized test results in pure black
    - Remove the horizontal lines in the parametrized test results
    - Display all results regardless of scored/ unscored inside of buttons to
      force a uniform line height and a more consistent look
    - Add logic to correctly display errored tests
    - Give skipped and errored test results a distinct look
    - Explicitly handle boolean results, and add boolean as an option for the
      'type' attribute.
    - Fix the raw data output in the textboxes so that they are formatted
      python code.
* Allow command line option to enable the definition of a custom test directory
  in combination with a corresponding config file.
* Extend test descriptions to make it more clear how a user can satisfy the
  test conditions.
* Remove duplicate test for the presence of transport reactions.
* Implement a test for unbounded flux through reactions in the default
  condition.
* Implement a test for detecting metabolites that can either be produced or
  removed from the model when all system boundaries are closed.
* Implement a test for 'direct' metabolites, i.e. the detection of biomass
  precursors that are not involved in any metabolic reactions; only in
  exchange reactions, transporters and the biomass reaction itself.
* Implement a test that checks for a low ratio of transport reactions without
  GPR relative to the total amount of transport reactions.

0.4.6 (2017-10-31)
------------------

* Improve the automated release pipeline. It now creates pumpkins.
* Provide a new decorator ``@register_with`` that can be used in all
  ``test_for*`` modules and replaces the ``model_builder`` function.
* Temporarily change the links to readthedocs to point to latest instead of stable.
* Provide angular2 app for the snapshot report instead of the jinja template

0.4.5 (2017-10-09)
------------------

* Correctly account for reversibility when testing for dead-end and orphan
  metabolites.

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
