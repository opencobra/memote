import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ReportDataService } from './../report-data.service';

@Component({
  selector: 'app-result-button',
  templateUrl: './result-button.component.html',
  styleUrls: ['./result-button.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class ResultButtonComponent implements OnInit {
  @Input() testId: string;

  constructor(private data: ReportDataService) {
  }

  ngOnInit() {
  }

// I tested this scheme against Deuteranopia, Protanopia and Tritanopia
  getColor(value) {
    const hue = (value * 132).toString(10);
    return ['hsl(', hue, ',80%,35%)'].join('');
}

// I tested this scheme against Deuteranopia, Protanopia and Tritanopia
//   getColor(value){
//     let hue=((value*154)+205).toString(10);
//     return ["hsl(",hue,",70%,45%)"].join("");
// }

}
