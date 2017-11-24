import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { PyModule } from './../../pymodule.model';
import { TestResult } from './../../test-result.model';
import { ReportDataService } from './../../report-data.service';

@Component({
  selector: 'app-statistics',
  templateUrl: './statistics.component.html',
  styleUrls: ['./statistics.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class StatisticsComponent implements OnInit {
  @Input() module: PyModule;

  constructor(private data: ReportDataService) { }

  ngOnInit() {
  }

}
