import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ResultCard } from './../../resultcard.model';
import { TestResult } from './../../test-result.model';
import { ReportDataService } from './../../report-data.service';

@Component({
  selector: 'app-statistics',
  templateUrl: './statistics.component.html',
  styleUrls: ['./statistics.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class StatisticsComponent implements OnInit {
  @Input() currentCard: ResultCard;

  constructor(private data: ReportDataService) { }

  ngOnInit() {
  }

}
