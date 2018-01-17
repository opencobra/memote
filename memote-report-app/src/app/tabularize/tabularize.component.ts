import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ReportDataService } from './../report-data.service';

@Component({
  selector: 'app-tabularize',
  templateUrl: './tabularize.component.html',
  styleUrls: ['./tabularize.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class TabularizeComponent implements OnInit {
  @Input() case: string;

  constructor(private data: ReportDataService) { }

  ngOnInit() { }

}
