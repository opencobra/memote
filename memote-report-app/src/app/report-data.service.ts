import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ResultCard } from './resultcard.model';
import { TestResult } from './test-result.model';
import { TestHistory } from './test-history.model';
import { TestDiff } from './test-diff.model';
// import * as testData from './data/testData.json';

@Injectable()
export class ReportDataService {
  metaData: any;
  allTests: any[] = [];
  scoredCard: Object;
  statisticsCards: ResultCard[] = [];
  scoredTests: string[] = [];
  reportType: string;
  allExpandState = false;
  score: any;
  scorePerSection: Object = {};
  testWeights: Object = {};
  testWeightsExpanded: Object = {};

  constructor(private http: HttpClient) {}

  public loadResults(): void {
    this.reportType = ((<any>window).reportType);
    switch (this.reportType) {
      case 'history': {
        this.convertHistoryResults((<any>window).data);
        break;
      }
      case 'snapshot': {
        // TODO: Might want to parse and decompress a string in future.
        // const data = JSON.parse((<any>window).data);
        this.convertResults((<any>window).data);
        break;
      }
      case 'diff': {
        this.convertDiffResults((<any>window).data);
        break;
      }
      default: {
        // This is for development purposes only. When no matching reportType is specified the
        // app resorts to displaying the test data.
        // this.http.get('/data/testDiff.json')
        // .subscribe(data => {this.convertDiffResults(data); });
        // this.reportType = 'diff';
        // break;
        this.http.get('/data/testData.json')
        .subscribe(data => {this.convertResults(data); });
        this.reportType = 'snapshot';
        break;
        // this.http.get('/data/testHistory.json')
        // .subscribe(data => {this.convertHistoryResults(data); });
        // this.reportType = 'history';
        // break;
      }
  }
}

  public togglePanel() {
    this.allExpandState = !this.allExpandState;
  }

  public byID(string) {
    return this.allTests.find(x => x.id === string);
  }

  public byReg(string) {
    const expr = new RegExp(string);
    const groupedResultIDs = [];
    for (const testResultObject of this.allTests) {
      if (expr.test(testResultObject.id)) {
        groupedResultIDs.push(testResultObject.id);
      }
    }
    return groupedResultIDs;
  }

  public isScored(string) {
    return this.scoredTests.includes(string);
  }

  public getParam(string, integer) {
    return string.split(':')[integer];
  }

  public getString(object) {
    return JSON.stringify(object);
  }

  private convertResults(data: Object): void {
    // Store each test result as a TestResult object in a central list.
    for (const test of Object.keys(data['tests'])){
      if (data['tests'][test]['message'] instanceof Object) {
        for (const param of Object.keys(data['tests'][test]['result'])) {
          const newID = test + ':' + param;
          this.allTests.push(
              new TestResult(
                newID,
                {data: data['tests'][test]['data'][param],
                duration: data['tests'][test]['duration'][param],
                message: data['tests'][test]['message'][param],
                metric: data['tests'][test]['metric'][param],
                result: data['tests'][test]['result'][param],
                summary: data['tests'][test]['summary'],
                title: data['tests'][test]['title'],
                format_type: data['tests'][test]['format_type']}
              )
            );
        }
      } else {
      this.allTests.push(
          new TestResult(
            test,
            data['tests'][test])
      );
      }
    }
    this.extractMetadata(data);
    this.extractScoring(data);
    this.extractTestWeights(data);
    this.distributeCardsToSections(data);
    this.determineScoredTests();
    this.determineScorePerSection();
  }

  private convertHistoryResults(data: Object): void {
    // Store each test history result as a TestHistory object in a central list.
    for (const test of Object.keys(data['tests'])){
      if (data['tests'][test]['history'] instanceof Array) {
        this.allTests.push(
          new TestHistory(
            test,
            data['tests'][test])
      );
      } else {
        for (const param of Object.keys(data['tests'][test]['history'])) {
          const newID = test + ':' + param;
          this.allTests.push(
              new TestHistory(
                newID,
                {history: data['tests'][test]['history'][param],
                summary: data['tests'][test]['summary'],
                title: data['tests'][test]['title'],
                format_type: data['tests'][test]['format_type']}
              )
            );
        }
    }
  }
  this.distributeCardsToSections(data);
  this.determineScoredTests();
  this.extractScoring(data);
}

private convertDiffResults(data: Object): void {
  // Store each test diff result as a TestDiff object in a central list.
  for (const test of Object.keys(data['tests'])){
    if (data['tests'][test]['diff'] instanceof Array) {
      this.allTests.push(
        new TestDiff(
          test,
          data['tests'][test])
    );
    } else {
      for (const param of Object.keys(data['tests'][test]['diff'])) {
        const newID = test + ':' + param;
        this.allTests.push(
            new TestDiff(
              newID,
              {diff: data['tests'][test]['diff'][param],
              summary: data['tests'][test]['summary'],
              title: data['tests'][test]['title'],
              format_type: data['tests'][test]['format_type']}
            )
          );
      }
  }
}
this.distributeCardsToSections(data);
this.determineScoredTests();
this.extractScoring(data);
this.extractTestWeights(data);
this.determineScorePerSection();
}

  private extractMetadata(data: Object): void {
    // Extract metaddata information to be used in the metadata card.
    this.metaData = data['meta'];
  }

  private extractScoring(data: Object): void {
    // Extract score information to be used in the score display and bar chart plot.
    this.score = data['score'];
  }

  private extractTestWeights(data: Object): void {
    // Extract information for each test weight used in the score-formula component.
    this.testWeights = data['weights'];

    for (const testId of Object.keys(this.testWeights)) {
      const parameterizedTestIds = this.byReg(testId);
      for (const paramId of parameterizedTestIds) {
        this.testWeightsExpanded[paramId] = this.testWeights[testId];
      }
    }
  }

  private distributeCardsToSections(data: Object): void {
    for (const card of Object.keys(data['cards'])){
      if (card === 'scored') {
        this.scoredCard = data['cards']['scored'];
      } else {
        this.statisticsCards.push(
          new ResultCard(
            card,
            data['cards'][card],
          )
        );
      }
    }
  }

  private determineScoredTests() {
    // Build a list of IDs of tests that are scored. This is only used in the
    //  logic of `result-button.component`.
    // Has to be executed after distributeCardsToSections()
    for (const section of Object.keys(this.scoredCard['sections'])) {
      if (this.scoredCard['sections'][section]['cases'] instanceof Array) {
      for (const testId of this.scoredCard['sections'][section]['cases']) {
        this.scoredTests.push(testId);
      }
    }
  }
}

  private extractData(string) {
    const reformatted_data = {};
    for (const diff_results of (this.byID(string).diff)) {
      reformatted_data[diff_results.model] = diff_results.data;
  }
  return this.getString(reformatted_data);

  }

  public determineScorePerSection() {
    let total_score: string[] = [];
    let sections: Object[] = [];
    if (this.reportType === 'snapshot') {
      sections = this.score.sections;
      total_score = [this.score.total_score];
    } else {
      sections = this.score.sections.diff;
      for (const totalScoreObj of this.score.total_score.diff) {
        total_score.push(totalScoreObj.total_score);
      }
    }
    let weights: string[] = [];
    let scores: string[] = [];
    for (const section of sections) {
      const sectionName = section['section'];
      if (!(this.scorePerSection.hasOwnProperty(sectionName))) {
        weights.push(this.scoredCard['sections'][sectionName].weight);
        scores.push(section['score']);
        this.scorePerSection[sectionName] = {
          'weights': weights,
          'scores': scores};
      } else {
        this.scorePerSection[sectionName]['weights'].push(this.scoredCard['sections'][sectionName].weight);
        this.scorePerSection[sectionName]['scores'].push(section['score']);
      }
      weights = [];
      scores = [];
    }
    this.scorePerSection['Total Score'] = {'scores': total_score};
  }
}
