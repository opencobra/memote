import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';

@Component({
  selector: 'app-tabularize',
  templateUrl: './tabularize.component.html',
  styleUrls: ['./tabularize.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class TabularizeComponent implements OnInit {
  @Input() objectData: any;
  @Input() scored: boolean = false;
  keyValuePairs = [];

  constructor() { }

  ngOnInit() {
     this.keyValuePairs = Object.entries(this.objectData);
  }

  getType(val) {
    return typeof val;
  }

}
