export const specMetric = {
  "$schema": "https://vega.github.io/schema/vega/v3.0.json",
  "width": 300,
  "height": 150,
  "padding": 0,
  "signals": [
    {
      "name": "clicked",
      "value": null,
      "on": [
        {
          "events": "@legendSymbol:click, @legendLabel:click",
          "update": "{value: datum.value}",
          "force": true
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
      "values": [
        {
          "commit": "095aeaa8d998fdec3ce34e99bf1bd56bd443087e",
          "metric": 0.02280501710376283,
          "data": 20,
          "result": "failed",
          "branch": "origin/master"
        },
        {
          "commit": "2bdf753982b7e4e0fd61421828aa0c4a26722988",
          "metric": 0.022598870056497175,
          "data": 20,
          "result": "failed",
          "branch": "origin/master"
        },
        {
          "commit": "54032275776f2810b78af11b960cc65bb6c2b002",
          "metric": 0.022650056625141562,
          "data": 20,
          "result": "failed",
          "branch": "origin/master"
        },
        {
          "commit": "e7e2f680853599a2e8ed8d540da5801e06865482",
          "metric": 0.024968789013732832,
          "data": 20,
          "result": "failed",
          "branch": "origin/master"
        },
        {
          "commit": "4da7d0de7823f1b179dd70e2e295eff6f7960fa0",
          "metric": 0.04962779156327544,
          "data": 40,
          "result": "failed",
          "branch": "origin/master"
        },
        {
          "commit": "0089055223ebabc54385a9d5fbe5eb03837e902d",
          "metric": 0.048327137546468404,
          "data": 39,
          "result": "failed",
          "branch": "origin/master"
        },
        {
          "commit": "c453461bccc9de73f0a94f1e53ae3b24eabe59c3",
          "metric": 0.048327137546468404,
          "data": 39,
          "result": "failed",
          "branch": "origin/master"
        },
        {
          "commit": "095aeaa8d998fdec3ce34e99bf1bd56bd443087e",
          "metric": 0.02280501710376283,
          "data": 20,
          "result": "failed",
          "branch": "master"
        },
        {
          "commit": "2bdf753982b7e4e0fd61421828aa0c4a26722988",
          "metric": 0.022598870056497175,
          "data": 20,
          "result": "failed",
          "branch": "master"
        },
        {
          "commit": "54032275776f2810b78af11b960cc65bb6c2b002",
          "metric": 0.022650056625141562,
          "data": 20,
          "result": "failed",
          "branch": "master"
        },
        {
          "commit": "e7e2f680853599a2e8ed8d540da5801e06865482",
          "metric": 0.024968789013732832,
          "data": 20,
          "result": "failed",
          "branch": "master"
        },
        {
          "commit": "4da7d0de7823f1b179dd70e2e295eff6f7960fa0",
          "metric": 0.04962779156327544,
          "data": 40,
          "result": "failed",
          "branch": "master"
        },
        {
          "commit": "0089055223ebabc54385a9d5fbe5eb03837e902d",
          "metric": 0.048327137546468404,
          "data": 39,
          "result": "failed",
          "branch": "master"
        },
        {
          "commit": "c453461bccc9de73f0a94f1e53ae3b24eabe59c3",
          "metric": 0.048327137546468404,
          "data": 39,
          "result": "failed",
          "branch": "master"
        }
      ]
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
      "range": {"scheme": "redyellowblue-10"},
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
                "strokeWidth": {
                  "value": 2
                },
                "size": {
                  "value": 50
                },
                "opacity": [
                  {
                    "test": "!length(data('selected')) || indata('selected', 'value', datum.branch)",
                    "value": 1
                  },
                  {
                    "value": 0.15
                  }
                ]
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
                  {
                    "test": "!length(data('selected')) || indata('selected', 'value', datum.branch)",
                    "value": 1
                  },
                  {
                    "value": 0.15
                  }
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
                "value": 80
              },
              "tooltip": {
                "scale": "x",
                "field": "commit"
              }
            },
            "update": {
              "stroke": {
                "value": "#000"
              },
              "strokeWidth": {
                "value": 1
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