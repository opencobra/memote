# memote - A continuously integrated metabolic model testing suite

**DISCLAIMER: This page is subject to changes as the tool development progresses.**

## Test Catalogue (Compiled 2018-06-19)
Please refer to the (API documentation COMING SOON)[COMING SOON] for a full overview of tests that have already been implemented.

## Community Suggestions for Additional Tests in the Future

### General
1. **Basic**
   - [ ] Calculate Species Knowledge Index (SKI) (requires gbk and species name as input)[#188](https://github.com/opencobra/memote/issues/188)
   - [ ] Calculate degree of completeness (requires gbk as input)[#188](https://github.com/opencobra/memote/issues/188)
   - [ ] (Test for version increment (requires git history))?
2. **Biomass**
   - [ ] Provide advanced statistics on how to improve growth rate [#76](https://github.com/biosustain/memote/issues/76)
   - [ ] Test against unrealistic growth [#38](https://github.com/biosustain/memote/issues/38)
   - [ ] Test presence of biomass reaction annotation
     - [ ] > 1 Pubmed ID
     - [ ] human readable 'decision/ evidence' description field [ECO](http://www.evidenceontology.org/userguide/))?
3. **Consistency**
   - [ ] Test logic of GPR - [#61](https://github.com/biosustain/memote/pull/61)
   - [ ] Test NADH production in closed state of the model [#189](https://github.com/opencobra/memote/issues/189)
   - [ ] Test NADPH production in closed state of the model [#189](https://github.com/opencobra/memote/issues/189)
   - [ ] Test thermodynamic consistency
   - [ ] Test for reasonable bounds [#3](https://github.com/biosustain/memote/issues/3)
   - [ ] (Test reaction direction/ reversibility based on estimated standard deltaG)? [#60](https://github.com/biosustain/memote/issues/60)
   - [ ] Calculate metabolic space that is completely computable (based on blocked reactions)
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
   - [ ] Test presence of specific type of metabolite annotations in MIRIAM style [#103](https://github.com/biosustain/memote/pull/103)
     - [ ] SMILES
     - [ ] InChI Full Length
   - [] Test presence of specific type of reaction annotations in MIRIAM style [#103](https://github.com/biosustain/memote/pull/103)
     - [ ] Pubchem
     - [ ] Chebi
   - [ ] Test consistency of gene IDs (belonging to refseq/ genbank namespace of target organism) [#185](https://github.com/opencobra/memote/issues/185)
   - [X] Test presence of specific type of gene annotations in MIRIAM style [#185](https://github.com/opencobra/memote/issues/185)
     - [ ] Genbank gene ID
     - [ ] Swissprot
     - [ ] EC-Code
     - [ ] BRENDA
     - [ ] E.Coli Gene Names

### Experimental Data
1. basic
   - [ ] Test if input data is present [#39](https://github.com/biosustain/memote/issues/39)
   - [ ] Test that input data is in the specified format [#39](https://github.com/biosustain/memote/issues/39)
2. media
   - [ ] Test model for known carbon splits [#75](https://github.com/biosustain/memote/issues/75)
   - [ ] Test model for P/O-ratios [#75](https://github.com/biosustain/memote/issues/75)
3. secprod
   - [ ] Test if compounds known to accumulate overlap with demand reactions [#65](https://github.com/biosustain/memote/pull/65)
   - [ ] Test for known secretion products [#72](https://github.com/biosustain/memote/issues/72)
