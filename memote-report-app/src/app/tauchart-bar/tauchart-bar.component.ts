import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ElementRef } from '@angular/core';
import { ReportDataService } from '../report-data.service';
import { Chart, api } from 'taucharts';
import 'taucharts/dist/plugins/tooltip';
import 'taucharts/dist/plugins/export-to';

@Component({
  selector: 'app-tauchart-bar',
  template: '<div style="width: 100%; height: 70%, padding: 2%"> </div>',
  encapsulation: ViewEncapsulation.None
})
export class TauChartBarComponent implements OnInit {
  @Input() plotType: string;
  nativeElement: any;
  chart: any;
  chart_settings: Object;

  constructor(private data: ReportDataService, private elementRef: ElementRef) {
    this.nativeElement = elementRef.nativeElement;
  }

  public initialize() {
    this.chart = new Chart(this.chart_settings);
    this.chart.renderTo(this.nativeElement);
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
        break;
      }
      case 'diff-sections': {
        console.log(this.data.score.sections.diff);
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
        break;
      }
      case 'diff-total': {
        console.log(this.data.score.total_score.diff);
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

    console.log(this.plotType);

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
    this.initialize();
  }
}
