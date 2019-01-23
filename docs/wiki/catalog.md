## (Compiled 2018-06-19)

Scored and unscored tests in memote.

### Scored Tests
A meaningful score can only be calculated on tests that are universal to constraint-based models. With the selection below we have tried to identify tests that a) ensure that the model adheres to the basic concepts of constraint-based modeling and b) that the model is easily accessible and convertible ensuring interoperability between tools.
1. **Consistency**
   - Number of Mass-Unbalanced Reactions
   - Number of Disconnected Metabolites
   - Stoichiometric Consistency
   - Number of Charge-Imbalanced Reactions
   - Fraction of Unbounded Reactions in the Default Condition
   - Number of Metabolites Produced Without Substrate Consumption
   - Number of Metabolites Consumed Without Product Removal
2. **Annotation**
   - Metabolites without Annotation
   - Missing Metabolite Annotations Per Database
   - Wrong Metabolite Annotations Per Database
   - Reactions without Annotation
   - Missing Reaction Annotations Per Database
   - Wrong Reaction Annotations Per Database
   - Genes without Annotation
   - Missing Gene Annotations Per Database
   - Wrong Gene Annotations Per Database
   - Uniform Metabolite Identifier Namespace
   - Uniform Reaction Identifier Namespace
3. **SBO**
   - Metabolites without SBO-Term Annotation
   - Reactions without SBO-Term Annotation
   - Genes without SBO-Term Annotation
   - Metabolic Reactions without SBO:0000176
   - Transport Reactions without SBO:0000185
   - Metabolites without SBO:0000247
   - Genes without SBO:0000243
   - Exchange reactions without SBO:0000627
   - Demand reactions without SBO:0000628
   - Sink reactions without SBO:0000632
   - Biomass reactions without SBO:0000629
### Unscored Tests
No score is calculated for this section of tests since the results depend either on the simulation condition, the type of organism or the modeling paradigm. In effect, the results here serve as supporting statistics and information.

1. **Basic**
   - Model Identifier
   - Total Number of Genes
   - Total Number of Reactions
   - Total Number of Metabolites
   - Metabolites without Formula
   - Metabolites without Charge
   - Reactions without GPR
   - Non-Growth Associated Maintenance Reaction
   - Metabolic Coverage
   - Total Number of Compartments
   - Number of Enzyme Complexes
   - Number of Purely Metabolic Reactions
   - Number of Purely Metabolic Reactions with Constraints
   - Number of Transport Reactions
   - Number of Tranport Reactions with Constraints
   - Fraction of Transport Reactions without GPR
   - Number of Reversible Oxygen-Containing Reactions
   - Number of Unique Metabolites
   - Number of Duplicate Metabolites in Identical Compartments
   - Number of Duplicate Reactions
   - Medium Components
2. **Biomass**
   - Amount of Biomass Reactions
   - Biomass Consistency
   - Biomass Production At Default State
   - Biomass Production In Complete Medium
   - Blocked Biomass Precursors At Default State
   - Blocked Biomass Precursors In Complete Medium
   - Growth-associated Maintenance in Biomass Reaction
   - Unrealistic Growth Rate In Default Condition
   - Ratio of Direct Metabolites in Biomass Reaction
   - Number of Missing Essential Biomass Precursors
3. **Matrix Conditioning**
   - Ratio between largest and smallest non-zero coefficients
   - Number of independent conservation relations in model
   - Number of steady-state flux solution vectors
   - Rank of S-Matrix
   - Degrees of freedom of S-Matrix
4. **Stoichiometric Matrix**
   - Erroneous Energy-generating Cycles
   - Stoichiometrically Balanced Cycles
   - Number of Orphan Metabolites
   - Number of Dead-end Metabolites
 
### Experimental Data
