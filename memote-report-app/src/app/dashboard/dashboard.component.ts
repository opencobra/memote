import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { ReportDataService } from './../report-data.service';
import { AttributeFilterPipe } from './../olfilter.pipe';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class DashboardComponent implements OnInit {

  constructor(private data: ReportDataService) {}

  ngOnInit() {
  }

}
