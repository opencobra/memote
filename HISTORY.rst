History
=======

Next Release
------------

0.9.4 (2019-02-20)
------------------
* Add metrics, i.e., model-size independent test outcomes to almost all test
  cases.
* Repair auto generation of API docs and update section on test suite.

0.9.3 (2019-01-30)
------------------
* Enhance the function for finding unique metabolites and make it more robust.
* Improve logging output when there is a problem with serializing a result to
  JSON.
* Fix some test cases that got broken by cobrapy's new boundary identification.

0.9.2 (2019-01-28)
------------------
* Fix bug that would lead to biomass SBO annotations not being reported.

0.9.1 (2019-01-28)
------------------
* Add ``seed.reaction`` namespace to the reaction annotation databases.

0.9.0 (2019-01-28)
------------------
* Change SBO annotation tests to check for multiple terms until we can properly
  handle the ontology.
* Remove 'Steady-state flux solution vectors' test case.
* Improve the descriptions of stoichiometric matrix test cases.
* Fix the discovery or orphan and dead-end metabolites.
* Improve detection of metabolites that are not consumed or not produced by
  only opening exchange reactions not other boundary reactions.
* Thematically reorganize the test cases in the config.
* Instead of min/max bounds consider the median bounds for testing (un-)bounded
  fluxes.
* Use a model context for every test case.
* Fix bug which involved find_transport_reactions to ignore compartments.
* Internal change to use model context rather than copy.
* Internal changes to JSON structure.
* Remove tests for metabolite inconsistency with closed bounds. The results
  are a subset only of the unconserved metabolites.
* Make the consistency tests account better for numeric instability.
* Add the GLPK exact solver as a possible option.
* Update memote-report-app from Angular 5.1.0 to 7.2.0.
* Reduce the prominence of the total score in the reports.
* Provide partial calculations for each section.
* Show overall formula of how the total score is calculated.
* Clearly indicate weights/ multipliers by introducing margenta badges next to each test in the report.
* In the reports, improve the descriptions of the 'Help' section and rename this section to 'Readme'.
* Rename the principal sections and include a brief explanation for each.
* Fix bug that would show a test as 'Errored' although it only failed. Fixed by making condition in errorFailsafe
  in test-result.model.ts more specific for cases where data is undefined or null.
* Fix bug that would make parametrized tests disappear from the report if they had errored or if for some reason their 'data' attribute
  was undefined.
* Unpin pytest (require >= 4.0) and adjust some internal mechanics accordingly.
* Display an alternative message if some biomass components do not contain a
  formula.
* Extend the annotations tests by a check for full length InChI strings.
* Fix a bug in ``Unrealistic Growth Rate In Default Medium`` which reported the
  opposite of what was the case.
* Extend the description of each test by a description of how it is
  implemented.
* Refactor test that identifies duplicate reactions to take into metabolites,
  reaction directionality and compartments into account.
* Add additional tests that identify reactions having identical annotations and
  identical genes.
* Refactor test that identifies duplicate metabolites to use for inchi
  strings in addition to inchikeys.
* Round score to and display a single decimal value.
* Fix bug that would show a test as errored whenever it was marked as skipped.
* Read SBML files with modified parser that can collect the level, version and
  whether the FBC package is used.
* Validate the SBML structure with the libSBML python API if the parser errors
  and produce a simple SBML validation report.
* Add test cases that report on the level and version, and FBC availability
  through the memote reports.

0.8.11 (2019-01-07)
-------------------
* Temporarily pin pytest to <4.1 in order to avoid a breaking API change on their part.

0.8.10 (2018-12-21)
-------------------
* Refactor the test for enzyme complexes to only return an estimated size.

0.8.9 (2018-12-11)
------------------
* Compress JSON and SQLite storage of results using gzip by default. JSON 
  continues to work either compressed or uncompressed. At the moment we 
  offer no database migration, please contact us if you need help in 
  migrating a large existing SQLite database rather than just re-computing it.

0.8.8 (2018-12-10)
------------------
* Adjust the reversibility index test to not use name matching and increase 
  the threshold slightly. Also adjust the description of the test.
* Adjust tests to the change in the ``add_boundary`` interface.
* Identify blocked reactions using the cobrapy built-in function.

0.8.7 (2018-11-21)
------------------
* Add a feature to allow suppling a commit range to ``memote history``.
* Add a test that checks if reactions are annotated with reactome identifiers.
* Add a feature that allows identifying specific metabolites by matching
  annotation information against the metabolite shortlist for a given MNX ID.
* Change every usage of SBO key to lower case to conform to the identifiers.org 
  namespace for the Systems Biology Ontology.
* Remove that metabolite SBO terms are used when identifying transport 
  reactions as this may lead to false positives.
* Return metabolite IDs when finding duplicate metabolites to avoid 
  serialization errors.
* Identify transport reactions first by formula then by annotation.
* For the diff report, run pytest in different processes to avoid accidentally
  overwriting the results of the former with the results of the later runs.
* In the diff report, fix a typo that allowed the diff button to depart the 
  defined colour scheme (blue -> red) to cyan.
* Fix the snapshot report not showing environment information.
* Allow ``memote run`` to skip commits where the model was not
  changed, if the flag ``--skip-unchanged`` is provided.
* Fix the default value of the overall score to be zero instead of one and
  make sure that the calculation is ensured with unit tests.
* Fix medium and experiment loading
* Add a test to check reaction directionality with thermodynamic estimation
  from eQuilibrator API.

0.8.6 (2018-09-13)
------------------
* Fix test titles and descriptions.

0.8.5 (2018-08-20)
------------------
* Unpin cobra dependency and set it to >0.13.3.
* Set ruamel.yaml to >=0.15 to keep up with cobra.

0.8.4 (2018-07-18)
------------------
* Handle various pytest verbosity options better.
* Improve ``memote new`` behavior.

0.8.3 (2018-07-16)
------------------
* ``memote run`` in a repository now immediately commits the result to the
  deployment branch.

0.8.2 (2018-07-16)
------------------
* Allow running of ``memote history`` from any branch.
* Let the history report only use commits where the model actually changed.
* Proofread and update all docstrings and comments inside the ``memote``
  subfolder.
* Reworded all test titles to be a) shorter and b) as neutral as was
  sensibly possible.
* Reordered tests in the `test-config.yaml` such that results belonging to a
  category are grouped logically.
* Updated the documentation to include a newer flowchart, up-to-date getting
  started and custom test sections.
* Update code to account for breaking changes in the most recent version of 
  cobrapy (0.13.0) and subsequently unpin cobrapy dependency (set to >=0.13.0).

0.8.1 (2018-06-27)
------------------
* Allow users to selective recompute the history of results.
* Skip commits in the history that did not change the model file.
* Change format_type on experimental tests from `count` to `percent`
* Fix typo in `test_basic.py` that lead to tests returning `null` which breaks
  the diff report frontend.
* Update the diff report to properly show errored and skipped tests
* Fix issues with asynchronicity on the diff report.
* Change format_type on experimental tests from ``count`` to ``percent``
* Fix typo in ``test_basic.py`` that lead to tests returning `null` which
  breaks the diff report frontend.
* Update the diff report to properly show errored and skipped tests


0.8.0 (2018-06-22)
------------------
* Finalize testing comparing with experimental data (growth and esentiality).
* Temporarily disable ``test_find_inconsistent_min_stoichiometry``.
* Update the nullspace function.
* Improve optlang compatibility.
* Add test ``find_medium_metabolites`` to detect and display all substrates
  capable of being taken up by model
* Display the score on History and Snapshot reports.
* Invert the colour coding.
* Display results as percentages.
* Add ability to generate a diff report which compares two or more models.
* Annotation of metabolite shortlist simplified.

0.7.6 (2018-05-28)
------------------
* Refactor internal API and JSON object creation.

0.7.5 (2018-05-25)
------------------
* Expose more of the internal API to the top level.
* Also, remember to carry a towel!

0.7.4 (2018-05-23)
------------------
* Add test ``find_duplicate_reactions`` to detect duplicate reactions in model
* Add dynamic upper and lower bounds. They are based on the most extreme bound
  values given in a model (if none exist -1000 and 1000 are chosen as defaults)
* Fix logic in ``find_bounds`` function in ``helpers.py``

0.7.3 (2018-05-23)
------------------
* Make the report type variable a string in the ``index.html``.

0.7.2 (2018-05-22)
------------------
* Distribute the missing tests.

0.7.1 (2018-05-16)
------------------
* Fix a problem with the report caused by previous refactoring.

0.7.0 (2018-05-15)
------------------

* Remove the pip dependency in ``show_versions``.
* Update the CI to use stages and ``tox-travis``.
* Modify some editor and other configuration.
* Expose testing of experimental essentiality and growth data in memote.
* Create a configuration system for media that is extensible to further
  experimental data types.
* Add test for identifying purely metabolic reactions with fixed constraints in
  models
* Add test for identifying transport reactions with fixed constraints in models
* Add test for identifying reversible oxygen-containing reactions in models
* Add division import from __future__ to ``test_biomass`` and
  ``test_consistency`` where it was missing.
* Add O2 to MetaNetX shortlist, allowing for easier identification
* Allow tests and test module to be skipped or run exclusively when creating
  a snapshot report.
* Fix some typos
* Add history report view and connect it to `memote report history` call.
* ``find_direct_metabolites`` detects and removes false positives.
* ``find_transport_reactions`` detects reactions using forumlae and annotations
* Add tests for detecting gene annotations (and verifying they are in
  MIRIAM style)
* Add unit tests for ``matrix.py`` in file ``test_for_matrix.py``.
* Add tests ``find_metabolites_not_produced_with_open_bounds`` and
  ``find_metabolites_not_consumed_with_open_bounds``
* Add test ``find_duplicate_metabolites_in_compartments`` to detect duplicate
  metabolites in identical compartments
* Cache heavily used support functions in ``helpers.py`` and
  ``consistency_helpers.py``

0.6.2 (2018-03-12)
------------------

* Test summary only displays extended narrative summary describing test,
  and not one-line summary describing expected function behavior/output
* Fix the following bugs:
    - Fix type annotation on the test for Biomass Production in Complete Medium
    - Fix TypeError when running memote new which was associated with unicode
      and string formatting in py2.7
    - Sort existing test results from misc into the respective categories
      (by editing test_config.yml)
    - Move Matrix statistics category to unscored side into their own card
    - Add a tuple of (number of reactions, number of genes) to the data
      annotation of the metabolic coverage test.
* Add filter in ``report_data_service`` that changed the test result status to
  "error" when the data attribute is ``null``, thus avoiding that the report
  interface breaks when trying to access data.
* Add test for identifying stoichiometrically balanced cycles in models
* Correct the arguments used for repositories such that ``memote run`` and
  ``memote history`` work as expected inside of a repository.

0.6.1 (2018-03-01)
------------------

* Emergency fix for distributing required JSON file.

0.6.0 (2018-02-27)
------------------

* Let Travis re-package the snapshot report with every release.
* Add new module to test for the presence of SBO term annotations.
* Add a test for Biomass production in complete medium.
* Clarify extend of mass- and charge-imbalance testing.
* Remove much of the boilerplate code of the report template as a preparation
  for the history and diff report.
* Fix bug with test_blocked_reactions
* Update the testData.json with data from the previous release
* Fix a small bug with the metrics of mass/charge unbalanced reactions.
* Correctly invert the found identifiers in wrong annotations and namespace
  consistency in order to report the correct results.
* Add a cross-reference shortlist using MetaNetX flatfiles
* Add a script that can be used to add more metabolites and then to
  re-generate the shortlist
* Add helper function ``find_met_in_model`` which looks up a query metabolite
  ID using the MNX namespace in the shortlist and:

    - If no compartment is provided, returns a list of all possible candidates
      metabolites.
    - If a compartment is provided, tries to return a list containing only
      ONE corresponding metabolite.

* Add helper function ``find_compartment_id_in_model`` to identify
  compartments using an internal shortlist of possible compartment names.
* Provide tests for each function
* Refactor code to use these functions specifically:
    - ``find_ngam``
    - ``find_biomass_reaction``
    - ``detect_energy_generating_cycles``
    - ``find_exchange_rxns``
    - ``find_demand_rxns``
    - ``find_sink_rxns``
    - ``gam_in_biomass``
    - ``find_biomass_precursors``
* Improve ``find_ngam`` in addition to agnostically looking for ATP hydrolysis
  reactions, the test now also looks for a range of possible "buzzwords" in
  the reaction NAME: ['maintenance', 'atpm', 'requirement', 'ngam',
  'non-growth', 'associated']. One match suffices as a classification.
* Improve ``find_biomass_reaction`` to look for three attributes in a biomass
  reaction, one of which is sufficient to classify it as a biomass reaction:

    1. "Buzzwords" in the reaction ID: ['biomass', 'growth', 'bof']
    2. An annotation matching the SBO-Term SBO:0000630 specifically!
    3. Containing a metabolite matching the regex:
       ``^biomass(_[a-zA-Z]+?)*?$`` (case-insensitive)
* Add function ``bundle_biomass_components`` to identify whether a given
  biomass reaction is 'split' or 'lumped'. This function looks simply at the
  size of the biomass reaction. Based on a guess-timated cut-off the reaction
  is then classified. If it is 'lumped' it is returned without changes, if it
  is 'split' the reactions of any non-energy precursor metabolite are returned
  as well. This is based on the assumption that a 'split' biomass reaction has
  the following structure:
  a (1 gDW ash) + b (1 gDW phospholipids) + c (free fatty acids) +
  d (1 gDW carbs) + e (1 gDW protein) + f (1 gDW RNA) + g (1 gDW DNA) +
  h (vitamins/cofactors)-> 1 gDCW biomass.
  We're supposing that for each macromolecule precursor metabolite there is a
  single reaction defining its composition i.e. ``e`` = protein would have the
  reaction: ``alanine + asparagine + ... + valine --> e``
* Add function, test and model test to identify missing essential precursors
  to the biomass reaction.
  The function is ``essential_precursors_not_in_biomass``
* Record the score of individual test cases and sections in the result output.
* Correct the import of module 'annotation' with 'sbo' in ``test_sbo.py``
* Refactor sink_react_list to sink_reactions for improved readability
* Allow ``test_sink_specific_sbo_presence`` to be skipped when no sink reactions
  are present with a metric of 1.0
* Fix a bug that compared the length of a float to generate a metric in
  ``test_basic.py`` and generated a TypeError.
* Fix a bug that prevented ``find_biomass_precursors``
  in ``memote/support/biomass.py`` from functioning due to a malformed set
* In CONTRIBUTING.rst replace link to semantic commit guide by seesparkbox
  with link to guide by karma, due to error with sphinx linkcheck.
* Fix a bug that prevented ``find_biomass_precursors`` from correctly
  identifying ``atp`` and ``h2o`` metabolites in cobra model reactions
* Fix improperly labeled sbo terms for biomass production in ``biomass.py``
  and ``test_for_helpers.py``.
* Add matrix conditioning functions in ``matrix.py`` which are used for
  model stoichiometric matrix testing in ``test_matrix.py``
* Add missing rank and nullspace_basis functions in ``consistency_helpers.py``
* Fix issue with improper string/dict formatting in ``test_biomass.py`` tests
* Re-organize the architecture to read in external configurations and add
  custom tests.
* Add an argument ``--location`` which replaces ``--directory`` which can be
  used to set the directory or database where results should be stored.


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
* Fix UnicodeDecodeError when memote tries to open the html template for the
  snapshot report.

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
