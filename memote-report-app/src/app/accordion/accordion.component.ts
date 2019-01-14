import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ReportDataService } from './../report-data.service';
import {MatBadgeModule} from '@angular/material/badge';

@Component({
  selector: 'app-accordion',
  templateUrl: './accordion.component.html',
  styleUrls: ['./accordion.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class AccordionComponent implements OnInit {
  @Input() case: string;
  weight = 1;

  constructor(private data: ReportDataService) { }

  ngOnInit() {}

  isWeighted(testId: string) {
    if (testId in this.data.testWeightsExpanded
      && this.data.testWeightsExpanded[testId] !== 1
      && this.data.testWeightsExpanded[testId] !== null) {
      this.weight = this.data.testWeightsExpanded[testId];
      return true;
    } else {
      return false;
    }
  }

}
