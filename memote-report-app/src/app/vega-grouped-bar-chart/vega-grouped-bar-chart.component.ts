import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ElementRef } from '@angular/core';
import { parse, View, Warn } from 'vega-lib';
import { ReportDataService } from '../report-data.service';
import { specGroupedBarChart } from './vega-grouped-bar-chart.bar-chart-spec';

@Component({
  selector: 'app-vega-grouped-bar-chart',
  template: '',
  styleUrls: [],
  encapsulation: ViewEncapsulation.None
})
export class VegaGroupedBarChartComponent implements OnInit {
  @Input()
  nativeElement: any;

  constructor(private data: ReportDataService, private elementRef: ElementRef) {
    this.nativeElement = elementRef.nativeElement;
  }

  public initialize() {
    // Initialize the vega bar chart
    specGroupedBarChart.data[0]['values'] = this.data.score.sections.diff;
    const view = new View(parse(specGroupedBarChart))
      .renderer('svg')
      .initialize(this.nativeElement)
      .hover()
      .logLevel(Warn)
      .run();
  }

  ngOnInit() {
    this.initialize();
  }
}
