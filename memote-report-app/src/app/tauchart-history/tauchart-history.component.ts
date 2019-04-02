import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ElementRef } from '@angular/core';
import { ReportDataService } from '../report-data.service';
// import { PassThrough } from 'stream';

@Component({
  selector: 'app-tauchart-history',
  templateUrl: './tauchart-history.component.html',
  styleUrls: ['./tauchart-history.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class TauChartHistoryComponent implements OnInit {
  @Input() testObject: any;
  @Input() testId: string;
  format_type: string;
  nativeElement: any;
  chart: any;

  constructor(private data: ReportDataService, private elementRef: ElementRef) {
    this.nativeElement = elementRef.nativeElement;
  }

  public initialize() {
    this.chart.renderTo(this.nativeElement);
  }

  ngOnInit() {
    this.format_type = this.testObject.format_type;

    // Define settings for fast and responsive loading:
    const tau_settings = {
      asyncRendering: true,
    }

    // Determine wether to plot data or metric.
    if (this.data.isScored(this.data.getParam(this.testId, 0))) {
      this.format_type = 'metric';
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
      guide: {
        showAnchors: 'always',
        interpolate: 'linear',
        x: { tickFormat: 's' }
      }
  });

  this.initialize();
  }
}
