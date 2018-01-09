import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { TestResult } from '.././test-result.model';

@Component({
  selector: 'app-tabularize',
  templateUrl: './tabularize.component.html',
  styleUrls: ['./tabularize.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class TabularizeComponent implements OnInit {
  @Input() testCase: TestResult;
  @Input() scored = false;
  keyValuePairs = [];
  resultObject = [];

  constructor() { }

  ngOnInit() {
     if (this.scored) {
       this.keyValuePairs = Object.entries(this.testCase.metric);
     } else {
       this.keyValuePairs = Object.entries(this.testCase.data);
     }
     this.resultObject = Object.entries(this.testCase.result);
  }

  getType(val) {
    return typeof val;
  }

}
