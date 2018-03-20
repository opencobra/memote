export const specMetric = {
  '$schema': 'https://vega.github.io/schema/vega/v3.0.json',
  'width': 300,
  'height': 150,
  'padding': 0,

  'signals': [
    {
      'name': 'clicked',
      'value': null,
      'on': [
        {
          'events': '@legendSymbol:click, @legendLabel:click',
          'update': '{value: datum.value}',
          'force':  true
        }
      ]
    },
    {
      'name': 'type',
      'value': 'metric',
      'description': 'This keyword describes which data is displayed on the y-axis.',
      // 'update': ' ("value" === "metric") ? \
      // domain("y", {"data": "scores", "field": "metric"})' : \
      // domain("y", {"data": "scores", "field": "data"})'
    },
  ],

  'data': [
    {
      'name': 'scores',
      'values': []
    },
    {
      'name': 'selected',
      'on': [
        {'trigger': 'clicked', 'toggle': 'clicked'}
      ]
    }
  ],

  'scales': [
    {
      'name': 'x',
      'type': 'point',
      'range': 'width',
      'domain': {'data': 'scores', 'field': 'commit'}
    },
    {
      'name': 'y',
      'type': 'linear',
      'range': 'height',
      'nice': true,
      'zero': true,
      'domain': {'data': 'scores', 'field': 'metric'}
    },
    {
      'name': 'color',
      'type': 'ordinal',
      'range': 'category',
      'domain': {'data': 'scores', 'field': 'branch'}
    }
  ],

  'axes': [
    {
      'orient': 'bottom',
      'scale': 'x',
      'title': 'History',
      'encode': {
        'labels': {
          'interactive': true,
          'update': {
            'angle': {'value': 50},
            'limit': {'value': 50},
            'baseline': {'value': 'top'},
            'dx': {'value': 3},
            'align': {'value': 'left'},
          },
        }
      }
    },
    {'orient': 'left', 'scale': 'y', 'title': 'Metric'}
  ],

  'marks': [
    {
      'type': 'group',
      'from': {
        'facet': {
          'name': 'series',
          'data': 'scores',
          'groupby': 'branch'
        }
      },
      'legends': [
        {
          'stroke': 'color',
          'title': 'Branches',
          'padding': 4,
          'orient': 'left',
          'offset': 30,
          'encode': {
            'symbols': {
              'name': 'legendSymbol',
              'interactive': true,
              'enter': {
                'cursor': {'value': 'pointer'}
              },
              'update': {
                'strokeWidth': {'value': 2},
                'size': {'value': 50},
                'opacity': [
                  {'test': '!length(data("selected")) || indata("selected", "value", datum.branch)', 'value': 1 },
                  {'value': 0.15}
                ]
              }
            },
            'labels': {
              'name': 'legendLabel',
              'interactive': true,
              'enter': {
                'cursor': {'value': 'pointer'}
              },
              'update': {
                'opacity': [
                  {'test': '!length(data("selected")) || indata("selected", "value", datum.branch)', 'value': 1 },
                  {'value': 0.15}
                ]
              }
            }
          }
        }
      ],


      'marks': [
        {
          'type': 'line',
          'from': {'data': 'series'},
          'encode': {
            'enter': {
              'x': {'scale': 'x', 'field': 'commit'},
              'y': {'scale': 'y', 'field': 'metric'},
              'stroke': {'scale': 'color', 'field': 'branch'},
              'strokeWidth': {'value': 2}
            },
            'update': {
              'interpolate': {'value': 'linear'},
              'opacity': [
                {'test': '!length(data("selected")) || indata("selected", "value", datum.branch)', 'value': 1 },
                {'value': 0}
              ]
            }
          }
        },
        {
          'type': 'symbol',
          'from': {'data': 'series'},
          'encode': {
            'enter': {
              'x': {'scale': 'x', 'field': 'commit'},
              'y': {'scale': 'y', 'field': 'metric'},
              'fill': {'scale': 'color', 'field': 'branch'},
              'size': {'value': 80},
              'tooltip': {'scale': 'x', 'field': 'commit'}
            },
            'update': {
              'stroke': {'value': '#000'},
              'strokeWidth': {'value': 1},
              'opacity': [
                {'test': '!length(data("selected")) || indata("selected", "value", datum.branch)', 'value': 1},
                {'value': 0}
              ]
            },
            'hover': {
              'opacity': [
                {'test': '!length(data("selected")) || indata("selected", "value", datum.branch)', 'value': 0.5},
                {'value': 0}
              ],
              'cursor': {'value': 'pointer'}
            }
          }
        }
      ]
    }
  ]
};
