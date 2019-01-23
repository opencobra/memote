Currently, memote only supports data from gene essentiality studies. However, we intend to expand on the types of supported experiments. This article gives a brief introduction to the file and naming requirements.

# Types of Experiments:
For now, we plan to support four principal types of experiments and their corresponding datasets. Each type is stored in their own folder in `data/experiments/`. Memote supports reading `.csv`, `.tsv`, `.xls`, and `.xlsx` files.

| Type of Experiment  | Examples  | Required Subfolder  |
|---|---|---|
| Gene Manipulation  | Essentiality, Knockdown, (Overexpression)| `essentiality/` |
| Growth Studies  | Growth on various C-Sources, N-Sources, P-Sources, S-Sources, Respiration, Trace Metals  | `growth/` |
| Secretion | Metabolite Secretion, Accumulation  | `secretion/` |
| Production  | Optimized product formation  | `production/` |
| Yields  | P/O-ratio, Yxs, Yps, Ypo | `yields/` |

# Data File Format:
The filename should simply consist of letters or digits separated by underscores because the filename will be used as the experiment ID and internally to handle the data. Users may specify a label using any unicode characters which is what will be visible on the plots in the report.

Example file name: `"e_M9_glucose.csv"`

## Example file structure:
|Gene ID|Growth Rate|
|---|---|
|b0025|0|
|b0418|0.183|

Note: It is important to use the same gene IDs that are used by the model!

# Configuration File Format:
As an optional input, memote supports the use of YAML formatted configuration files. Here a user can specify the details of the conditions used for a given experiment. In all types of experiments it is possible to change the objective and constraints by supplying either reaction IDs or Optlang constraint definitions in the form of JSON files. With yield, secretion and essentiality experiments the medium has to be specified in the respective YAML configuration file since changing the medium there constitutes a novel experiment. For growth studies and production experiments the medium is defined within the tabular data files.

## Configuration Template:

```yaml
version: "0.1"
medium:
  context: # by default data/experimental/media everything will be searched relative to this directory
  definitions:
    known_medium:
      filename:  # by default <context>/<known_medium>.csv so outer context + identifier + CSV
essentiality:
  context: # by default data/experimental/essentiality everything will be searched relative to this directory  
  experiments:
    Experiment_Id: #alphanumeric name only, the same as the filename for the experiment.
      filename:  # by default <context>/<Experiment_Id>.csv so outer context + identifier + CSV
      medium: "known_medium" # medium key
      objective: "single_reaction_id"  # or "Optlang_Obj_Function.json"
      constraints:
      - "ratio_constraint_definion.json"
      label: "Plot-Ready Label"
growth:
  context:  # by default data/experimental/growth, everything will be searched relative to this directory
  experiments:
    Experiment_Id: #alphanumeric name only, the same as the filename for the experiment.
      filename:  # by default <context>/<Experiment_Id>.csv so outer context + identifier + CSV
      medium: "known_medium" # medium key
      objective: "single_reaction_id"  # or "Optlang_Obj_Function.json"
      constraints:
      - "ratio_constraint_definion.json"
      label: "Plot-Ready Label"
```

For instance, if the gene essentiality study was carried out in a special medium the model's constrains on uptake reactions have to be adapted. So, instead of using M9 minimal medium and glucose, a user has used a different carbon source: `"M9_mannose.csv"`. Carbon sources are defined in a simple `.csv` file in the folder `data/experiments/media/`.

Note: It is important that the experiment ID is identical to the data file (`.csv`) of the corresponding experiment!

## Example file structure:

```yaml
version: "1.1"
experiments:
  strain_V28_essentiality_m9_mannose:
    medium: "m9_mannose"
    objectives:
      - "BIOMASS"
    regulation:
      - "ratio_constraint_definion.json"
    label: "Strain V28, Gene Essentiality, Mannose"
```

Note: Omitting the principal parameters [Medium, Objective, Regulation] of a config file or the config file itself will lead to memote using the default model settings!

The configuration file is validated against the following [JSON schema](http://spacetelescope.github.io/understanding-json-schema/):

```json
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "memote experiments configuration schema",
    "description": "The following JSON schema is used to validate a configuration file (typically YAML) that describes one or more experiments to be tested by memote.",

    "definitions": {
        "stringSet": {
            "type": "array",
            "items": { "type": "string" },
            "uniqueItems": true
        },
        "experiment": {
            "type": "object",
            "properties": {
                "medium": { "type": "string" },
                "objectives": { "$ref": "#/definitions/stringSet" },
                "constraints": { "$ref": "#/definitions/stringSet" },
                "label": { "type": "string" }
            },
            "additionalProperties": false
        }
    },

    "type": "object",
    "properties": {
        "version": {
            "type": "string",
            "enum": ["0.1"]
        },
        "experiments": {
            "type": "object",
            "additionalProperties": { "$ref": "#/definitions/experiment" }
        }
    },
    "required": ["version", "experiments"],
    "additionalProperties": false
}
```
