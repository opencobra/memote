import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ReportDataService } from './../report-data.service';
// import { PassThrough } from 'stream';

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
  sectionWeight = 1;

  constructor(private data: ReportDataService) {
  }

  ngOnInit() {
    this.getScore();
    this.constructFormulae();
  }

  getSectionWeight() {
    if (this.position !== 'Total Score') {
      const weight = this.data.scorePerSection[this.position]['weights'][0];
      if ( weight !== 1 && typeof weight !== 'undefined') {
        this.sectionWeight = weight;
        return true;
      }
      return false;
      }
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
        const formula = this.constructSubTotalFormula(i);
        this.formulae.push(formula);
      }
    }
  }

  constructTotalFormula(i: any) {
  let numerator = '';
  let denominator = '';
  let first = true;
  let addition = '';
  for (const section of Object.keys(this.data.scorePerSection)) {
    if (section !== 'Total Score') {
      const weight = this.data.scorePerSection[section]['weights'][i];
      const score = this.data.scorePerSection[section]['scores'][i] * 100;
      numerator += addition + '(' + weight + ' * ' + (score.toFixed(2)) + ')';
      denominator += addition + '(' + weight + ' * ' + 100 + ')';
    }
    if (first) {
      addition = ' + ';
      first = false;
    }
  }
  const total_score = this.data.scorePerSection['Total Score']['scores'][i] * 100;
  return '`(' + numerator + ')/(' + denominator + ') = ' + (total_score.toFixed(2)) + '`';
  }

  constructSubTotalFormula(i: any) {
    let numerator = '';
    let denominator = '';
    let addition = ' + ';
    let weight = 1;
    let unweighted_denominator = 0;
    let unweighted_numerator_100 = 0;
    let unweighted_numerator_0 = 0;
    let score = 0;
    for (const test of this.data.scoredCard['sections'][this.position]['cases']) {
      if (test in Object.keys(this.data.testWeights)) {
        const weight = this.data.testWeights[test];
      }
      for (const paramtest of this.data.byReg(test)) {
        if (this.data.reportType === 'snapshot') {
          score = (1 - this.data.byID(paramtest).metric) * 100;
        } else {
          score = (1 - this.data.byID(paramtest).diff[i].metric) * 100;
        }
        if (weight === 1) {
          if (score === 0) {
            unweighted_denominator += 1;
            unweighted_numerator_0 += 1;
            continue;
          } else if (score === 100) {
            unweighted_numerator_100 += 1;
            unweighted_denominator += 1;
            continue;
          } else {
            numerator += (score.toFixed(2)) +  addition;
            unweighted_denominator += 1;
          }
        }
        if (weight !== 1) {
          numerator += '(' + weight + ' * ' + (score.toFixed(2)) + ')' + addition;
          denominator += '(' + weight + ' * ' + 100 + ')' + addition;
        }
      }
    }
    if (unweighted_numerator_100 > 0) {
      numerator += '(' + unweighted_numerator_100 + ' * ' + 100 + ')' + addition;
    }
    if (unweighted_numerator_0 > 0) {
      numerator += '(' + unweighted_numerator_0 + ' * ' + 0 + ')';
    }
    denominator += '(' + unweighted_denominator + ' * ' + 100 + ')';
    const section_score = this.data.scorePerSection[this.position]['scores'][i] * 100;
    return '`(' + numerator + ')/(' + denominator + ') = ' + (section_score.toFixed(2)) + '`';
  }
}
