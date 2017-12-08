import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { ReportDataService } from './../../report-data.service';

@Component({
  selector: 'app-system-information',
  templateUrl: './system-information.component.html',
  styleUrls: ['./system-information.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class SystemInformationComponent implements OnInit {

  constructor(private data: ReportDataService) {}

  ngOnInit() {
  }

}
