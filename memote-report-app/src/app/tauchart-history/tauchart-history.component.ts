import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ElementRef } from '@angular/core';
import { ReportDataService } from '../report-data.service';
// import { PassThrough } from 'stream';

@Component({
  selector: 'app-tauchart-history',
  template: '<div> </div>',
  styleUrls: ['./tauchart-history.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class TauChartHistoryComponent implements OnInit {
  @Input() testObject: any;
  @Input() testId: string;
  format_type: string;
  nativeElement: any;
  chart: any;
  historyData: Object[];

  constructor(private data: ReportDataService, private elementRef: ElementRef) {
    this.nativeElement = elementRef.nativeElement;
  }

  public initialize() {
    this.chart.renderTo(this.nativeElement);
  }

  public invertScoredData(history: Object[]) {
    for (const result of history){
      console.log(result.metric)
      result.metric = 1 - result.metric;
      console.log(result.metric)
    }
  }

  ngOnInit() {
    this.format_type = this.testObject.format_type;

    // Define settings for fast and responsive loading:
    const tau_settings = {
      asyncRendering: true,
      renderingTimeout: 1000,
    };

    const tau_guide = {
      showAnchors: 'always',
      interpolate: 'linear',
      showGridLines: 'xy',
      x: { nice: false
         },
    };

    // Determine wether to plot data or metric.
    if (this.data.isScored(this.data.getParam(this.testId, 0))) {
      this.format_type = 'metric';
      this.invertScoredData(this.testObject.history);
      tau_guide['y'] = { min: 0,
        max: 1,
        nice: false,
        tickFormat: 'percent'
      };
    } else {
      this.format_type = 'data';
    }

    this.chart = new Taucharts.Chart({
      data: this.testObject.history,
      type: 'line',
      x: 'commit',
      y: this.format_type,
      color: 'branch',
      settings: tau_settings,
      plugins: [
        Taucharts.api.plugins.get('legend')(),
        Taucharts.api.plugins.get('tooltip')()
      ],
      guide: tau_guide
  });

  this.initialize();
  }
}
