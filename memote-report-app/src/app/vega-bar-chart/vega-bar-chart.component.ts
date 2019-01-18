import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ElementRef } from '@angular/core';
import { parse, View, Warn } from 'vega-lib';
import { ReportDataService } from '../report-data.service';
import { specBarChart } from './vega-bar-chart.bar-chart-spec';

@Component({
  selector: 'app-vega-bar-chart',
  template: '',
  styleUrls: [],
  encapsulation: ViewEncapsulation.None
})
export class VegaBarChartComponent implements OnInit {
  @Input() testId: string;
  nativeElement: any;

  constructor(private data: ReportDataService, private elementRef: ElementRef) {
    this.nativeElement = elementRef.nativeElement;
  }

  public initialize() {
    // Initialize the vega bar chart
    specBarChart.data[0]['values'] = this.data.score.sections;
    const view = new View(parse(specBarChart))
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
