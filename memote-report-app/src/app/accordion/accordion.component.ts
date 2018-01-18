import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ReportDataService } from './../report-data.service';

@Component({
  selector: 'app-accordion',
  templateUrl: './accordion.component.html',
  styleUrls: ['./accordion.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class AccordionComponent implements OnInit {
  @Input() case: string;

  constructor(private data: ReportDataService) { }

  ngOnInit() { }

}
