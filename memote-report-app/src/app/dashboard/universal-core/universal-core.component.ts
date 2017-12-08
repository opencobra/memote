import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { TestResult } from './../../test-result.model';
import { ReportDataService } from './../../report-data.service';
import { KeysPipe } from './../../keys.pipe';

@Component({
  selector: 'app-universal-core',
  templateUrl: './universal-core.component.html',
  styleUrls: ['./universal-core.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class UniversalCoreComponent implements OnInit {
  @Input() scoreData: Object;
  panelOpenState: boolean = false;

  constructor(private data: ReportDataService) { }

  ngOnInit() {
  }

}
