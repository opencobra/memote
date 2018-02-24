import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ElementRef } from '@angular/core';
import { parse, View } from 'vega-lib';
import { ReportDataService } from '../report-data.service';
import { spec } from './vega-plot.vega-spec';

@Component({
  selector: 'app-vega-plot',
  template: '',
  styleUrls: [],
  encapsulation: ViewEncapsulation.None
})
export class VegaPlotComponent {
  @Input() testId: string;
  plotData: object[];

  constructor(private data: ReportDataService, private elementRef: ElementRef) {
    // TODO(Ali Kaafarani): Replace test data with actual data from the report
    // this.plotData = data.byID(this.testId)...;
    this.plotData = [
      {"branch": "master", "score": 3, "sha": "sha-shared-1"},
      {"branch": "fail", "score": 3, "sha": "sha-shared-1"},
      {"branch": "fail", "score": 2, "sha": "sha-fail-1"},
      {"branch": "improve", "score": 3, "sha": "sha-shared-1"},
      {"branch": "improve", "score": 2, "sha": "sha-opt-1"},
      {"branch": "fail", "score": 0, "sha": "sha-fail-2"},
      {"branch": "improve", "score": 3, "sha": "sha-opt-2"},
      {"branch": "improve", "score": 4, "sha": "sha-opt-3"},
      {"branch": "master", "score": 3, "sha": "sha-4"},
      {"branch": "improve", "score": 5, "sha": "sha-opt-4"},
      {"branch": "improve", "score": 4, "sha": "sha-shared-2"},
      {"branch": "master", "score": 4, "sha": "sha-shared-3"},
      {"branch": "improve", "score": 4, "sha": "sha-shared-3"},
      {"branch": "master", "score": 4, "sha": "sha-6"}
    ];

    // Initialize the vega plot
    spec.data[0]['values'] = this.plotData;
    const view = new View(parse(spec))
      .renderer('canvas')
      .initialize(elementRef.nativeElement)
      .hover()
      .run();

    view.addEventListener('click', function(event, item) {
      if(item && item.datum && item.datum.sha) {
        // TODO(Ali Kaafarani): What the alert says
        alert("Navigating to snapshort report for commit '" + item.datum.sha + "'");
      }
    });
  }
}
