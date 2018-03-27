import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ElementRef } from '@angular/core';
import { parse, View } from 'vega-lib';
import { ReportDataService } from '../report-data.service';
import { specMetric } from './vega-plot.metric-spec';
import { TestHistory } from './../test-history.model';

@Component({
  selector: 'app-vega-plot',
  template: '',
  styleUrls: [],
  encapsulation: ViewEncapsulation.None
})
export class VegaPlotComponent implements OnInit {
  @Input() testId: string;
  testObject: TestHistory;
  type: string;
  nativeElement: any;

  constructor(private data: ReportDataService, private elementRef: ElementRef) {
    this.nativeElement = elementRef.nativeElement;
  }

  public initialize() {
    this.testObject = this.data.byID(this.testId);
    this.type = this.testObject.type;

    // Initialize the vega plot
    if (['count', 'raw', 'number'].includes(this.type)) {
      this.type = 'data';
    } else {
      this.type = 'metric';
    }
    specMetric.data[0]['values'] = this.testObject.history;
    const view = new View(parse(specMetric))
      .renderer('svg')
      .signal('type', this.type)
      .initialize(this.nativeElement)
      .hover()
      .run();

    view.addEventListener('click', function(event, item) {
      if (item && item.datum && item.datum.commit) {
        // TODO(Ali Kaafarani): What the alert says
        alert('Navigating to snapshort report for commit' + item.datum.commit);
      }
    });
  }

  ngOnInit() {
    this.initialize();
  }
}
