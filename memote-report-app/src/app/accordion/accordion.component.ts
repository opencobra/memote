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

  constructor(private data: ReportDataService) { }

  ngOnInit() {}

  getWeight(testId: string) {
    const weight = this.data.testWeights[testId.split(':')[0]];
  if ( weight !== 1 && typeof weight !== 'undefined') {
    return weight;
  }
  return ' ';
  }

}
