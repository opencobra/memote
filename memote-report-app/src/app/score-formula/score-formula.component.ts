import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ReportDataService } from './../report-data.service';
import { PassThrough } from 'stream';

@Component({
  selector: 'app-score-formula',
  templateUrl: './score-formula.component.html',
  styleUrls: ['./score-formula.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class ScoreFormulaComponent implements OnInit {
  @Input() position: string;
  scoreType = 'Total Score';
  modelScore: string[] = [];
  formulae: string[] = [];
  sections: Object[] = [];

  constructor(private data: ReportDataService) {
  }

  ngOnInit() {
    this.getScore();
    this.constructFormulae();
  }

  getScore() {
    this.modelScore = this.data.scorePerSection[this.position]['scores'];
    if (this.position !== 'Total Score') {
      this.scoreType = 'Sub Total';
      }
    }

  constructFormulae() {
    let i;
    for (i = 0; i < this.data.scorePerSection['Total Score']['scores'].length; i++) {
      if (this.scoreType === 'Total Score') {
        const formula = this.constructTotalFormula(i);
        this.formulae.push(formula);
      } else {
        continue;
      }
    }
    console.log(this.formulae);
  }

  constructTotalFormula(i: any) {
  let numerator = '';
  let denominator = '';
  let first = true;
  let addition = '';
  for (const section of Object.keys(this.data.scorePerSection)) {
    if (section !== 'Total Score') {
      const weight = this.data.scorePerSection[section]['weights'][i];
      const score = this.data.scorePerSection[section]['scores'][i];
      numerator += addition + '(' + weight + ' * ' + (score.toFixed(4) * 100) + ')';
      denominator += addition + '(' + weight + ' * ' + 100 + ')';
    }
    if (first) {
      addition = ' + ';
      first = false;
    }
  }
  const total_score = this.data.scorePerSection['Total Score']['scores'][i];
  return '`(' + numerator + ')/(' + denominator + ') = ' + (total_score.toFixed(3) * 100) + '`';
  }

  constructTotalDenominator() {

  }
}
