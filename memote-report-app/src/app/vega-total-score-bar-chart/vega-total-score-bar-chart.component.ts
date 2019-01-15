import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ElementRef } from '@angular/core';
import { parse, View, Warn } from 'vega-lib';
import { ReportDataService } from '../report-data.service';
import { specTotalScoreBarChart } from './vega-total-score-bar-chart.total-score-bar-chart-spec';

@Component({
  selector: 'app-vega-total-score-bar-chart',
  template: '',
  styleUrls: [],
  encapsulation: ViewEncapsulation.None
})
export class VegaTotalScoreBarChartComponent implements OnInit {
  @Input() testId: string;
  nativeElement: any;

  constructor(private data: ReportDataService, private elementRef: ElementRef) {
    this.nativeElement = elementRef.nativeElement;
  }

  public initialize() {
    // Initialize the vega bar chart
    specTotalScoreBarChart.data[0]['values'] = this.data.score.total_score.diff;
    const view = new View(parse(specTotalScoreBarChart))
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
