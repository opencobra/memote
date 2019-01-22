/* tslint:disable */ 
export const specBarChart: any = {
  "$schema": "https://vega.github.io/schema/vega/v4.json",
  "width": 300,
  "height": 200,
  "autosize": 'fit',
  "padding": 'strict',
  "data": [
    {
      "name": "table",
      "values": [],
      'transform': [
        {"type": "formula", "as": "percent", "expr": "round(datum.score * 100)"}
      ]
    }
  ],

  "signals": [
  ],

  "scales": [
    {
      "name": "xscale",
      "type": "band",
      "domain": {"data": "table", "field": "section"},
      "range": "width",
      "padding": 0.05,
      "round": true
    },
    {
      "name": "yscale",
      "domain": {"data": "table", "field": "percent"},
      "nice": true,
      "range": "height"
    }
  ],

  "axes": [
    { "orient": "bottom", "scale": "xscale" },
    { "orient": "left", "scale": "yscale" }
  ],

  "marks": [
    {
      "type": "rect",
      "from": {"data":"table"},
      "encode": {
        "enter": {
          "x": {"scale": "xscale", "field": "section"},
          "width": {"scale": "xscale", "band": 1},
          "y": {"scale": "yscale", "field": "percent"},
          "y2": {"scale": "yscale", "value": 0}
        }
      }
    },
    {"type": "text",
    "from": {
        "data": "table"
      },
    "encode":{
      "enter":{
        "text": {"field": "percent"},
         "x": {
            "scale": "xscale",
            "field": "section",
            "band": 0.5
          },
          "y": {
            "scale": "yscale",
            "field": "percent",
            "offset" : -2
          },
        "fill": {"value": "black"},
        "align": {"value": "center"},
        "baseline": {"value": "bottom"},
        "fontSize": {"value": 18}
      }
    }
    }
  ]
};
/* tslint:enable */
