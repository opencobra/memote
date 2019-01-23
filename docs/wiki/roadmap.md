# Memote Dev Roadmap

## Prioritized issues/ specific feature requests
Please refer to: https://waffle.io/opencobra/memote.

Issues we plan to cover sooner are at the top of the 'sorted' section, the further down they are the lesser the priority we've assigned to them.

## Sprint Plan for November/ December:
* Collect and display all results and meta-information from the tests
* Define a universal set of scored core tests
* Run a meta-study of model quality and reconstruction pipeline endpoints
* Extend data tests


## Future Plans
Extensions and ideas in no specific order, but quite likely to be tackled soon.
* Display all results and meta-information on the reports
* Display a simple score on the reports
* Simplify bulk testing and reporting of models (i.e. the diff report)
* Separate report generation and testing
* Define a robust scoring system for the test results
* Support GenBank files as a data input
* Implement a memote service to support drag&drop snapshot testing through a web interface
* Export results from the reports report in several data types (python, matlab, json, [julia?, excel?])

## Wish List
Anything goes here; for the distant future.
* Generate a badge for a model repository based on the test results
* Offer the option to fix all errors that are found.
* In the history report, show incremental improvement from the previous commit.
* Simplify dockerization of model repositories (and the corresponding memote version etc)

## Assorted Tests that have not yet been implemented

### Core Tests
1. **Basic**
   - [X] Test presence model ID
   - [x] Test presence genes
   - [x] Test presence reactions
   - [X] Test presence GPR [#61](https://github.com/biosustain/memote/issues/61), [#108](https://github.com/biosustain/memote/pull/108)
   - [x] Test presence metabolites
   - [X] Test presence metabolite formula 
   - [X] Test presence metabolite charge [#106](https://github.com/biosustain/memote/issues/106), [#108](https://github.com/biosustain/memote/pull/108)
   - [X] Statistics on constraint distribution (How many reactions are unconstrained, irreversible, have an upper bound, etc.)[#67](https://github.com/biosustain/memote/issues/67), [#108](https://github.com/biosustain/memote/pull/108)
   - [X] Calculate the ratio between reactions and genes included in the reconstruction as a measure of metabolic coverage >1 [#107](https://github.com/biosustain/memote/issues/107), [#108](https://github.com/biosustain/memote/pull/108)
   - [X] Test compartments presence (compartments > 3) [#144](https://github.com/opencobra/memote/issues/144), [#166](https://github.com/opencobra/memote/pull/166)
   - [X] Test Enzyme Complex Presence (enzyme complexes >= 1) [#144](https://github.com/opencobra/memote/issues/144), [#166](https://github.com/opencobra/memote/pull/166)
   - [X] Test Transport Reaction Presence (transport reaction >= 1) [#144](https://github.com/opencobra/memote/issues/144), [#166](https://github.com/opencobra/memote/pull/166)
   - [X] Calculate the amount of purely metabolic reactions [#144](https://github.com/opencobra/memote/issues/144), [#166](https://github.com/opencobra/memote/pull/166)
   - [X] Calculate the amount of unique metabolites [#144](https://github.com/opencobra/memote/issues/144), [#166](https://github.com/opencobra/memote/pull/166)
   - [ ] Calculate Species Knowledge Index (SKI) (requires gbk and species name as input)[#188](https://github.com/opencobra/memote/issues/188)
   - [ ] Calculate degree of completeness (requires gbk as input)[#188](https://github.com/opencobra/memote/issues/188)
   - [ ] (Test for version increment (requires git history))?
2. **Biomass**
   - [X] Test presence biomass reaction(s) [#23](https://github.com/biosustain/memote/pull/23)
   - [X] Test biomass consistency (sum = 1 g/ gDW) [#23](https://github.com/biosustain/memote/pull/23)
   - [X] Test biomass production (growth rate) in default state of the model [#56](https://github.com/biosustain/memote/pull/56)
   - [ ] Provide advanced statistics on how to improve growth rate [#76](https://github.com/biosustain/memote/issues/76)
   - [ ] Test against unrealistic growth [#38](https://github.com/biosustain/memote/issues/38)
   - [X] Test biomass precursor production in default state of the model [#56](https://github.com/biosustain/memote/pull/56)
   - [X] Test biomass precursor production in open state of the model [#56](https://github.com/biosustain/memote/pull/56)
   - [X] Test presence of GAM in biomass reaction [#101](https://github.com/biosustain/memote/pull/101), [#63](https://github.com/biosustain/memote/pull/63)
   - [X] Test presence of NGAM in model [#100](https://github.com/biosustain/memote/pull/100), [#64](https://github.com/biosustain/memote/pull/64)
   - [ ] Test presence of biomass reaction annotation
     - [ ] > 1 Pubmed ID
     - [ ] human readable 'decision/ evidence' description field [ECO](http://www.evidenceontology.org/userguide/))?
3. **Consistency**
   - [ ] Test logic of GPR - [#61](https://github.com/biosustain/memote/pull/61)
   - [X] Test stoichiometric consistency [#14](https://github.com/biosustain/memote/pull/14), [#55](https://github.com/biosustain/memote/pull/55)
   - [X] Test ATP production in closed state of the model [#57](https://github.com/biosustain/memote/pull/57)
   - [ ] Test NADH production in closed state of the model [#189](https://github.com/opencobra/memote/issues/189)
   - [ ] Test NADPH production in closed state of the model [#189](https://github.com/opencobra/memote/issues/189)
   - [X] Test unbalanced reactions [#57](https://github.com/biosustain/memote/pull/57), [#35](https://github.com/biosustain/memote/issues/35)
   - [X] Test blocked reactions [#58](https://github.com/biosustain/memote/pull/58), [#83](https://github.com/biosustain/memote/pull/83), [#69](https://github.com/biosustain/memote/issues/69)
   - [X] Test for the presence of orphaned metabolites [#143](https://github.com/biosustain/memote/issues/143), [#182](https://github.com/biosustain/memote/pull/182)
   - [X] Test for the presence of deadend metabolites [#143](https://github.com/biosustain/memote/issues/143), [#182](https://github.com/biosustain/memote/pull/182)
   - [X] Test for the presence of disconnected metabolites [#143](https://github.com/biosustain/memote/issues/143), [#182](https://github.com/biosustain/memote/pull/182)
   - [ ] Test thermodynamic consistency
   - [ ] Test for reasonable bounds [#3](https://github.com/biosustain/memote/issues/3)
   - [ ] (Test reaction direction/ reversibility based on estimated standard deltaG)? [#60](https://github.com/biosustain/memote/issues/60)
   - [ ] Calculate metabolic space that is completely computable (based on blocked reactions)
   - [X] Test cycle reactions [#104](https://github.com/biosustain/memote/issues/104) (Currently disabled)
   - [ ] Test constant size of experimental bounds => warning if unconstrained
   - [ ] (Test consistent unit definition)?
   - [ ] (Test correct directionality of transport reactions)? [#70](https://github.com/biosustain/memote/issues/70)
4. **Annotation**
   - [ ] (Test presence of a human readable 'decision/ evidence' description field in annotation in the form of [ECO](http://www.evidenceontology.org/userguide/))?
   - [ ] (Test presence reaction subsystem (SEED or KEGG))? [#187](https://github.com/biosustain/memote/issues/187)
   - [ ] (Test subsystem more than central carbon metabolism)? [#187](https://github.com/biosustain/memote/issues/187)
   - [ ] Test presence of reaction confidence score [#59](https://github.com/biosustain/memote/issues/59)
   - [ ] Test style of reaction confidence score to be in accordance with specified SOP [#59](https://github.com/biosustain/memote/issues/59)
   - [ ] (Test confidence score 3 and 4 reactions for presence of DOI (or better Pubmed ID) in annotation dict)?[#186](https://github.com/biosustain/memote/issues/186)
   - [ ] (Test number of included DOI (or better Pubmed ID) == number of reactions as a score for manual curation)?[#186](https://github.com/biosustain/memote/issues/186)
   - [X] Test consistency of metabolite IDs (belonging to a known database namespace) [#103](https://github.com/biosustain/memote/pull/103) [#62](https://github.com/biosustain/memote/pull/62)
   - [X] Test presence metabolite annotations [#103](https://github.com/biosustain/memote/pull/103)
   - [X] Test presence of specific type of metabolite annotations in MIRIAM style [#103](https://github.com/biosustain/memote/pull/103)
     - [X] Kegg
     - [X] Seed
     - [X] InChI Key
     - [X] Chebi
     - [X] HMDB
     - [X] Reactome
     - [X] MetaNetX [#33](https://github.com/biosustain/memote/issues/33)
     - [X] BiGG
     - [X] Biocyc
     - [X] Pubchem Compound ID [#154](https://github.com/biosustain/memote/issues/154), [#181](https://github.com/biosustain/memote/pull/181)
     - [ ] SMILES
     - [ ] InChI Full Length
   - [X] Test validity of metabolite annotation identifiers [#103](https://github.com/biosustain/memote/pull/103)
   - [X] Test consistency of reaction IDs (belonging to a known database namespace) [#103](https://github.com/biosustain/memote/pull/103), [#62](https://github.com/biosustain/memote/pull/62)
   - [X] Test presence reaction annotations [#103](https://github.com/biosustain/memote/pull/103)
   - [X] Test presence of specific type of reaction annotations in MIRIAM style [#103](https://github.com/biosustain/memote/pull/103)
     - [X] Rhea
     - [X] Kegg
     - [X] MetaNetX
     - [X] BiGG
     - [X] EC-Code
     - [X] BRENDA
     - [X] Biocyc
     - [ ] Pubchem
     - [ ] Chebi
   - [X] Test validity of reaction annotation identifiers [#103](https://github.com/biosustain/memote/pull/103)
   - [ ] Test consistency of gene IDs (belonging to refseq/ genbank namespace of target organism) [#185](https://github.com/opencobra/memote/issues/185)
   - [ ] Test presence gene annotations [#185](https://github.com/opencobra/memote/issues/185)
   - [ ] Test presence of specific type of gene annotations in MIRIAM style [#185](https://github.com/opencobra/memote/issues/185)
     - [ ] RefSeq gene ID
     - [ ] Genbank gene ID
     - [ ] Uniprot
     - [ ] Swissprot
     - [ ] EC-Code
     - [ ] BRENDA
     - [ ] E.Coli Gene Names
     - [ ] KEGG
   - [ ] Test validity of gene annotation identifiers
5. **Syntax**
   1. BiGG specific:
      - [X] Test if non-transport reactions tagged to be in a compartment act on metabolites from that compartment [#10](https://github.com/biosustain/memote/pull/10)
      - [X] Test if non-transport reactions outside the cytosol are tagged accordingly [#10](https://github.com/biosustain/memote/pull/10)
      - [X] Test that non-abc transport reactions are tagged with 't' [#20](https://github.com/biosustain/memote/pull/20)
      - [X] Test that abc transport reactions are tagged with 'abc' [#20](https://github.com/biosustain/memote/pull/20)
      - [X] Test that metabolite IDs are all lower-case within exceptions
      - [ ] Test that reaction IDs are all upper-case within exceptions [#184](https://github.com/biosustain/memote/pull/184)
      - [X] Test that demand reaction IDs are all prefixed with 'DM_' [#20](https://github.com/biosustain/memote/pull/20),  [#66](https://github.com/biosustain/memote/pull/66)
      - [X] Test that exchange reaction IDs are all prefixed with 'EX_' [#20](https://github.com/biosustain/memote/pull/20), [#66](https://github.com/biosustain/memote/pull/66)
      - [X] Test that sink reaction IDs are all prefixed with 'SK_' [#102](https://github.com/biosustain/memote/pull/102), [#66](https://github.com/biosustain/memote/pull/66)

### Experimental Data
1. basic
   - [ ] Test if input data is present [#39](https://github.com/biosustain/memote/issues/39)
   - [ ] Test that input data is in the specified format [#39](https://github.com/biosustain/memote/issues/39)
2. genome
   - [ ] Test if gene essentiality data is available [#39](https://github.com/biosustain/memote/issues/39), [#77](https://github.com/biosustain/memote/issues/77)
   - [ ] Test if predictions equal gene essentiality results [#39](https://github.com/biosustain/memote/issues/39), [#77](https://github.com/biosustain/memote/issues/77)
3. media
   - [ ] Test model for known carbon splits [#75](https://github.com/biosustain/memote/issues/75)
   - [ ] Test model for P/O-ratios [#75](https://github.com/biosustain/memote/issues/75)
   - [ ] Test predicted in silico behaviour against experimental measurements on different growth media [#68](https://github.com/biosustain/memote/issues/68), [#71](https://github.com/biosustain/memote/issues/71)
4. secprod
   - [ ] Test if compounds known to accumulate overlap with demand reactions [#65](https://github.com/biosustain/memote/pull/65)
   - [ ] Test for known secretion products [#72](https://github.com/biosustain/memote/issues/72)
5. auxotrophies
   - [ ] Test that the model does not grow/ produce a certain compound in a certain condition [#74](https://github.com/biosustain/memote/issues/74)
