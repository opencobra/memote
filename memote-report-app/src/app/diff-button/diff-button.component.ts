import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ReportDataService } from './../report-data.service';
import { AsyncPipe } from '@angular/common';

@Component({
  selector: 'app-diff-button',
  templateUrl: './diff-button.component.html',
  styleUrls: ['./diff-button.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class DiffButtonComponent implements OnInit {
  @Input() testId: string;
  metricList: any[] = [];
  highlightColor: string;

  constructor(private data: ReportDataService) {
  }

  ngOnInit() {
    this.getDiffColor();
  }

  getDiffColor() {
    if ( this.data.isScored(this.data.getParam(this.testId, 0)) ) {
      for (const results of this.data.byID(this.testId).diff){
        this.metricList.push(results.metric);
      }
      this.spectrum(this.ratioOrVariance(this.metricList));
    } else {
    if (this.data.byID(this.testId).format_type !== 'raw') {
      switch (this.data.byID(this.testId).format_type) {
        case 'count':
          for (const results of this.data.byID(this.testId).diff){
            this.metricList.push(results.data.length);
          }
          break;
        case 'number':
          for (const results of this.data.byID(this.testId).diff){
          this.metricList.push(results.data);
          }
          break;
        case 'percent':
          for (const results of this.data.byID(this.testId).diff){
          this.metricList.push(results.metric);
          }
          break;
       }
       this.spectrum(this.ratioOrVariance(this.metricList));
      } else {
        for (const results of this.data.byID(this.testId).diff){
        this.metricList.push(results.data);
        }
        this.spectrum(this.determineStringEquality(this.metricList));
      }
    }
  }

  ratioOrVariance(array: any[]) {
    const minimum = Math.min(...array);
    const maximum = Math.max(...array);
    if (array.length === 2 && array[0] === array[1]) {
      return 0;
    }
    if (minimum === 0) {
      return (1 - (minimum + 1 / maximum + 1)) * 100;
    } else {
      return (1 - (minimum / maximum)) * 100;
    }
  }

  determineStringEquality(array: any[]) {
    let allEqual: boolean;
    if (array.length) {
      allEqual = !!array.reduce(function(a, b){ return (a === b) ? a : NaN; });
    } else {
      allEqual = false;
    }
    if (allEqual) {
      return 0;
    } else {
      return 100;
    }
  }

  spectrum(i: number) {
    const red = ((i * 1.19) + 42).toString(10);
    const green = (123 - (i * 1.05)).toString(10);
    const blue = (184 - (i * 1.66)).toString(10);
    this.highlightColor = ['rgb(', red, ',', green, ',', blue, ')'].join('');
  }

}
