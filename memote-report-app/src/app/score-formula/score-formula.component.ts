import { Component, OnInit, ViewEncapsulation, Input } from '@angular/core';
import { ReportDataService } from './../report-data.service';

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

  constructor(private data: ReportDataService) {
  }

  ngOnInit() {
    this.obtainScore();
  }

  obtainScore() {
    switch (this.data.reportType) {
      case 'snapshot': {
        if (this.position !== 'Total Score') {
          for (const sectionScoreObject of this.data.score.sections) {
            if (sectionScoreObject.section === this.position) {
              this.modelScore.push(sectionScoreObject.score);
            }
            }
            this.scoreType = 'Sub Total';
            return this.modelScore;
          }
        return this.modelScore === this.data.score.total_score;
      }
      case 'diff': {
        if (this.position !== 'Total Score') {
          for (const sectionScoreObject of this.data.score.sections.diff) {
            if (sectionScoreObject.section === this.position) {
              this.modelScore.push(sectionScoreObject.score);
            }
            }
            this.scoreType = 'Sub Total';
            return this.modelScore;
          }
        for (const sectionScoreObject of this.data.score.total_score.diff) {
            this.modelScore.push(sectionScoreObject.total_score);
          }
      }
  }
  }

}
