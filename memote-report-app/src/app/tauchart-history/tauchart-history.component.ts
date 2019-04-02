import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ReportDataService } from '../report-data.service';
// import { PassThrough } from 'stream';

@Component({
  selector: 'app-tauchart-history',
  templateUrl: './tauchart-history.component.html',
  styleUrls: ['./tauchart-history.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class TauChartHistoryComponent implements OnInit {
  @Input() position: string;
  scoreType = 'Total Score';
  modelScore: string[] = [];
  formulae: string[] = [];
  sections: Object[] = [];
  sectionWeight = 1;

  constructor(private data: ReportDataService) {
  }

  ngOnInit() {

    const datasource = [{
      type:'us', count:20, date:'12-2013'
    },{
      type:'us', count:10, date:'01-2014'
    },{
      type:'bug', count:15, date:'02-2014'
    },{
      type:'bug', count:23, date:'05-2014'
    }];

    const chart = new Taucharts.Chart({
      data: datasource,
      type: 'line',
      x: 'date',
      y: 'count',
      color: 'type' // there will be two lines with different colors on the chart
  });

  chart.renderTo('#tauchart');
  }
}
