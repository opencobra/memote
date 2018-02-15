export const spec = {
  "$schema": "https://vega.github.io/schema/vega/v3.0.json",
  "width": 500,
  "height": 150,
  "padding": 5,

  "signals": [
    {
      "name": "clicked",
      "value": null,
      "on": [
        {
          "events": "@legendSymbol:click, @legendLabel:click",
          "update": "{value: datum.value}",
          "force":  true
        }
      ]
    }
  ],

  "data": [
    {
      "name": "scores",
      "values": []
    },
    {
      "name": "selected",
      "on": [
        {"trigger": "clicked", "toggle": "clicked"}
      ]
    }
  ],

  "scales": [
    {
      "name": "x",
      "type": "point",
      "range": "width",
      "domain": {"data": "scores", "field": "sha"}
    },
    {
      "name": "y",
      "type": "linear",
      "range": "height",
      "nice": true,
      "zero": true,
      "domain": {"data": "scores", "field": "score"}
    },
    {
      "name": "color",
      "type": "ordinal",
      "range": "category",
      "domain": {"data": "scores", "field": "branch"}
    }
  ],

  "axes": [
    {"orient": "bottom", "scale": "x", "title": "History"},
    {"orient": "left", "scale": "y", "title": "Score"}
  ],

  "marks": [
    {
      "type": "group",
      "from": {
        "facet": {
          "name": "series",
          "data": "scores",
          "groupby": "branch"
        }
      },
      "legends": [
        {
          "stroke": "color",
          "title": "Branches",
          "padding": 4,
          "encode": {
            "symbols": {
              "name": "legendSymbol",
              "interactive": true,
              "enter": {
                "cursor": {"value": "pointer"}
              },
              "update": {
                "strokeWidth": {"value": 2},
                "size": {"value": 50},
                "opacity": [
                  {"test": "!length(data('selected')) || indata('selected', 'value', datum.value)", "value": 1},
                  {"value": 0.15}
                ]
              }
            },
            "labels": {
              "name": "legendLabel",
              "interactive": true,
              "enter": {
                "cursor": {"value": "pointer"}
              },
              "update": {
                "opacity": [
                  {"test": "!length(data('selected')) || indata('selected', 'value', datum.value)", "value": 1},
                  {"value": 0.15}
                ]
              }
            }
          }
        }
      ],


      "marks": [
        {
          "type": "line",
          "from": {"data": "series"},
          "encode": {
            "enter": {
              "x": {"scale": "x", "field": "sha"},
              "y": {"scale": "y", "field": "score"},
              "stroke": {"scale": "color", "field": "branch"},
              "strokeWidth": {"value": 2}
            },
            "update": {
              "interpolate": {"value": "linear"},
              "opacity": [
                {"test": "!length(data('selected')) || indata('selected', 'value', datum.branch)", "value": 1 },
                {"value": 0}
              ]
            }
          }
        },
        {
          "type": "symbol",
          "from": {"data": "series"},
          "encode": {
            "enter": {
              "x": {"scale": "x", "field": "sha"},
              "y": {"scale": "y", "field": "score"},
              "fill": {"scale": "color", "field": "branch"},
              "size": {"value": 240},
              "tooltip": {"scale": "x", "field": "sha"}
            },
            "update": {
              "stroke": {"value": "#000"},
              "strokeWidth": {"value": 1},
              "opacity": [
                {"test": "!length(data('selected')) || indata('selected', 'value', datum.branch)", "value": 1},
                {"value": 0}
              ]
            },
            "hover": {
              "opacity": [
                {"test": "!length(data('selected')) || indata('selected', 'value', datum.branch)", "value": 0.75},
                {"value": 0}
              ],
              "cursor": {"value": "pointer"}
            }
          }
        }
      ]
    }
  ]
};
