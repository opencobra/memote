import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ReportDataService } from './../report-data.service';

@Component({
  selector: 'app-score-formula',
  templateUrl: './score-formula.component.html',
  styleUrls: ['./score-formula.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class ScoreFormulaComponent implements OnInit {
  @Input() testId: string;

  constructor(private data: ReportDataService) {
  }

  ngOnInit() {
  }
}
