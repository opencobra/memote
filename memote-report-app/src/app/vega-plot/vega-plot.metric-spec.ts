export const specMetric = {
  "$schema": "https://vega.github.io/schema/vega/v3.0.json",
  "width": 350,
  "height": 200,
  "padding": 0,
  "signals": [
    {
      "name": "shift", "value": false,
      "on": [
        {
          "events": "@legendSymbol:click, @legendLabel:click",
          "update": "event.shiftKey",
          "force":  true
        }
      ]
    },
    {
      "name": "clicked", "value": null,
      "on": [
        {
          "events": "@legendSymbol:click, @legendLabel:click",
          "update": "{value: datum.value}",
          "force":  true
        }
      ]
    },
    {
      "name": "type",
      "value": "data",
      "description": "This keyword describes which data is displayed on the y-axis."
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
        {
          "trigger": "clicked",
          "toggle": "clicked"
        }
      ]
    }
  ],
  "scales": [
    {
      "name": "x",
      "type": "point",
      "range": "width",
      "domain": {
        "data": "scores",
        "field": "commit"
      }
    },
    {
      "name": "y",
      "type": "linear",
      "range": "height",
      "nice": true,
      "zero": true,
      "domain": {
        "data": "scores",
        "field": {"signal" : "type"}
      }
    },
    {
      "name": "color",
      "type": "ordinal",
      "range": ["#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"],
      "domain": {
        "data": "scores",
        "field": "branch"
      }
    }
  ],
  "axes": [
    {
      "orient": "bottom",
      "scale": "x",
      "title": "History",
      "encode": {
        "labels": {
          "interactive": true,
          "update": {
            "angle": {
              "value": 50
            },
            "limit": {
              "value": 50
            },
            "baseline": {
              "value": "top"
            },
            "dx": {
              "value": 3
            },
            "align": {
              "value": "left"
            }
          }
        }
      }
    },
    {
      "orient": "left",
      "scale": "y",
      "title": {"signal" : "type === 'metric' ? 'Metric': 'Data'"}
    }
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
      "orient": "left",
      "offset": 30,
      "encode": {
        "symbols": {
          "name": "legendSymbol",
          "interactive": true,
          "enter": {
                "cursor": {
                  "value": "pointer"
                }
          },
          "update": {
            "fill": {"value": "transparent"},
            "strokeWidth": {"value": 2},
            "opacity": [
              {"test": "!length(data('selected')) || indata('selected', 'value', datum.value)", "value": 0.7},
              {"value": 0.15}
            ],
            "size": {"value": 64}
          }
        },
        "labels": {
          "name": "legendLabel",
          "interactive": true,
          "enter": {
                "cursor": {
                  "value": "pointer"
                }
          },
          "update": {
            "opacity": [
              {"test": "!length(data('selected')) || indata('selected', 'value', datum.value)", "value": 1},
              {"value": 0.25}
            ]
          }
        }
      }
    }
  ],
      "marks": [
        {
          "type": "line",
          "from": {
            "data": "series"
          },
          "encode": {
            "enter": {
              "x": {
                "scale": "x",
                "field": "commit"
              },
              "y": {
                "scale": "y",
                "field": {"signal" : "type"}
              },
              "stroke": {
                "scale": "color",
                "field": "branch"
              },
              "strokeWidth": {
                "value": 2
              }
            },
            "update": {
              "interpolate": {
                "value": "linear"
              },
              "opacity": [
                {
                  "test": "!length(data('selected')) || indata('selected', 'value', datum.branch)",
                  "value": 1
                },
                {
                  "value": 0
                }
              ]
            }
          }
        },
        {
          "type": "symbol",
          "from": {
            "data": "series"
          },
          "encode": {
            "enter": {
              "x": {
                "scale": "x",
                "field": "commit"
              },
              "y": {
                "scale": "y",
                "field": {"signal" : "type"}
              },
              "fill": {
                "scale": "color",
                "field": "branch"
              },
              "size": {
                "value": 90
              },
              "tooltip": {
                "scale": "x",
                "field": "commit"
              }
            },
            "update": {
              "opacity": [
                {
                  "test": "!length(data('selected')) || indata('selected', 'value', datum.branch)",
                  "value": 1
                },
                {
                  "value": 0
                }
              ]
            },
            "hover": {
              "opacity": [
                {
                  "test": "!length(data('selected')) || indata('selected', 'value', datum.branch)",
                  "value": 0.5
                },
                {
                  "value": 0
                }
              ],
              "cursor": {
                "value": "pointer"
              }
            }
          }
        }
      ]
    }
  ]
};
