export const specGroupedBarChart: any = {
  '$schema': 'https://vega.github.io/schema/vega/v4.json',
  'width': 300,
  'height': 240,
  'padding': 5,

  'data': [
    {
      'name': 'diff',
      'values': [],
      'transform': [
        {"type": "formula", "as": "percent", "expr": "round(datum.score * 100)"}
      ]
    }
  ],
  "legends": [
    {
      'columns' : 0,
      "orient": "bottom",
      "fill": "color",
      "encode": {
        "title": {
          "update": {
            "fontSize": {"value": 14}
          }
        },
        "labels": {
          "interactive": false
        }
      }
    }
  ],
  'scales': [
    {
      'name': 'yscale',
      'type': 'band',
      'domain': {'data': 'diff', 'field': 'model'},
      'range': 'height',
      'padding': 0.2
    },
    {
      'name': 'xscale',
      'type': 'linear',
      'domain': {'data': 'diff', 'field': 'percent'},
      'range': 'width',
      'round': true,
      'zero': true,
      'nice': true
    },
    {
      'name': 'color',
      'type': 'ordinal',
      'domain': {'data': 'diff', 'field': 'section'},
      'range': {'scheme': 'category20'}
    }
  ],

  'axes': [
    {'orient': 'left', 'scale': 'yscale', 'tickSize': 0, 'labelPadding': 4, 'zindex': 1},
    {'orient': 'bottom', 'scale': 'xscale'}
  ],

  'marks': [
    {
      'type': 'group',

      'from': {
        'facet': {
          'data': 'diff',
          'name': 'facet',
          'groupby': 'model'
        }
      },

      'encode': {
        'enter': {
          'y': {'scale': 'yscale', 'field': 'model'}
        }
      },

      'signals': [
        {'name': 'height', 'update': 'bandwidth("yscale")'}
      ],

      'scales': [
        {
          'name': 'pos',
          'type': 'band',
          'range': 'height',
          'domain': {'data': 'facet', 'field': 'section'}
        }
      ],

      'marks': [
        {
          'name': 'bars',
          'from': {'data': 'facet'},
          'type': 'rect',
          'encode': {
            'enter': {
              'y': {'scale': 'pos', 'field': 'section'},
              'height': {'scale': 'pos', 'band': 1},
              'x': {'scale': 'xscale', 'field': 'percent'},
              'x2': {'scale': 'xscale', 'percent': 0},
              'fill': {'scale': 'color', 'field': 'section'}
            }
          }
        },
        {
          'type': 'text',
          'from': {'data': 'bars'},
          'encode': {
            'enter': {
              'x': {'field': 'x2', 'band': 1, 'offset': 4},
              'y': {'field': 'y', 'offset': {'field': 'height', 'mult': 0.5}},
              'fill': {'value': 'black'},
              'align': {'value': 'left'},
              'baseline': {'value': 'middle'},
              'text': { 'field': 'datum.percent'},
              "fontSize": {"value": 18}
            }
          }
        }
      ]
    }
  ]
}
