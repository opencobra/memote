import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ElementRef } from '@angular/core';
import { ReportDataService } from '../report-data.service';
import { Chart, api } from 'taucharts';
import 'taucharts/dist/plugins/tooltip';
import 'taucharts/dist/plugins/legend';
import 'taucharts/dist/plugins/export-to';
import { isNgTemplate } from '@angular/compiler';

@Component({
  selector: 'app-tauchart-bar',
  template: '<div style="width:100%; height:100%"> </div>',
  encapsulation: ViewEncapsulation.None
})
export class TauChartBarComponent implements OnInit {
  @Input() testObject: any;
  nativeElement: any;
  chart: any;

  constructor(private data: ReportDataService, private elementRef: ElementRef) {
    this.nativeElement = elementRef.nativeElement;
  }

  public initialize() {
    this.chart.renderTo(this.nativeElement);
  }

  ngOnInit() {

    const tau_guide = {
      showGridLines: 'xy',
      x: { nice: false,
        min: 0, max : 1,
        tickFormat: 'percent'
         },
      color: { brewer : ['rgb(161, 18, 18)', 'rgb(18, 161, 46)']}
    };

    this.chart = new Chart({
      type: 'horizontal-bar',
      y: 'section',
      x: 'score',
      color: 'score',
      data: this.data.score.sections,
      plugins: [
        api.plugins.get('tooltip')(),
        api.plugins.get('export-to')()
      ],
      guide: tau_guide,
      settings: { fitModel: 'normal'}
  });

  this.initialize();
  }
}
