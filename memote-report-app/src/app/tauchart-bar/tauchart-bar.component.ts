import { Component, OnInit, ViewEncapsulation, Input, AfterViewInit } from '@angular/core';
import { ReportDataService } from '../report-data.service';
import { Chart, api } from 'taucharts';
import 'taucharts/dist/plugins/tooltip';
import 'taucharts/dist/plugins/export-to';

@Component({
  selector: 'app-tauchart-bar',
  template: '<div id="tau-horizbar-{{css_tag}}" style="height: 50vh; width: 40vw"> </div>',
  encapsulation: ViewEncapsulation.None
})
export class TauChartBarComponent implements OnInit, AfterViewInit {
  @Input() plotType: string;
  chart: any;
  chart_settings: any;
  css_tag = 'total';

  constructor(private data: ReportDataService) {
  }

  public initialize() {
    this.chart = new Chart(this.chart_settings);
    this.chart.renderTo('#tau-horizbar-' + this.css_tag);
  }

  public composeChartSettings() {
    switch (this.plotType) {
      case 'snapshot-sections': {
        this.chart_settings['y'] = 'section';
        this.chart_settings['x'] = 'score';
        this.chart_settings['color'] = 'score';
        this.chart_settings['data'] = this.data.score.sections;
        this.chart_settings['guide']['x'] = {
          nice: false,
          min: 0, max : 1,
          tickFormat: 'percent'};
        this.chart_settings['guide']['color'] = {
          brewer : ['rgb(161, 18, 18)', 'rgb(18, 161, 46)']
        };
        this.css_tag = 'sections';
        break;
      }
      case 'diff-sections': {
        this.chart_settings['y'] = 'model';
        this.chart_settings['x'] = 'score';
        this.chart_settings['color'] = 'score';
        this.chart_settings['data'] = this.data.score.sections.diff;
        this.chart_settings['guide']['x'] = {
          nice: false,
          min: 0, max : 1, tickFormat: 'percent'};
        this.chart_settings['guide']['color'] = {
            brewer : ['rgb(161, 18, 18)', 'rgb(18, 161, 46)']
          };
        this.css_tag = 'sections';
        break;
      }
      case 'diff-total': {
        this.chart_settings['y'] = 'model';
        this.chart_settings['x'] = 'total_score';
        this.chart_settings['data'] = this.data.score.total_score.diff;
        this.chart_settings['guide']['x'] = {
          nice: false,
          min: 0, max : 1, tickFormat: 'percent'};
        break;
      }
    }
  }

  ngOnInit() {

    this.chart_settings = {
      type: 'horizontal-bar',
      y: NaN,
      x: NaN,
      color: NaN,
      data: NaN,
      plugins: [
        api.plugins.get('tooltip')(),
        api.plugins.get('export-to')()
      ],
      guide: {
        showGridLines: 'xy'
      },
      settings: { fitModel: 'normal'}
    };
    this.composeChartSettings();
  }

  ngAfterViewInit() {
    this.initialize();
  }
}
