import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { PyModule } from './../../pymodule.model';
import { TestResult } from './../../test-result.model';

@Component({
  selector: 'app-universal-core',
  templateUrl: './universal-core.component.html',
  styleUrls: ['./universal-core.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class UniversalCoreComponent implements OnInit {
  @Input() scoreData: PyModule;
  panelOpenState: boolean = false;

  constructor() { }

  ngOnInit() {
  }

  getColor(value){
    let hue=((1-value)*131).toString(10);
    return ["hsl(",hue,",75%,40%)"].join("");
}

}
