import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';

@Component({
  selector: 'app-coloured-score',
  templateUrl: './coloured-score.component.html',
  styleUrls: ['./coloured-score.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class ColouredScoreComponent implements OnInit {
  @Input() metric: any;

  constructor() { }

  ngOnInit() {
  }

// I tested this scheme against Deuteranopia, Protanopia and Tritanopia
  getColor(value){
    let hue=((1-value)*132).toString(10);
    return ["hsl(",hue,",80%,35%)"].join("");
}

// I tested this scheme against Deuteranopia, Protanopia and Tritanopia
//   getColor(value){
//     let hue=((value*154)+205).toString(10);
//     return ["hsl(",hue,",70%,45%)"].join("");
// }

}
