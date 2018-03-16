import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ResultCard } from './resultcard.model';
import { TestResult } from './test-result.model';
import { TestHistory } from './test-history.model';
// import * as testData from './data/testData.json';

@Injectable()
export class ReportDataService {
  metaData: any;
  allTests: any[] = [];
  scoredCard: Object;
  statisticsCards: ResultCard[] = [];
  scoredTests: string[] = [];
  reportType: string;

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
        // Diff report stuff happens here
        break;
      }
      default: {
        // This is for development purposes only. When no matching reportType is specified the
        // app resorts to displaying the test data.
        this.http.get('/data/testHistory.json')
        .subscribe(data => {this.convertHistoryResults(data); });
        break;
      }
  }
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
        for (const param of Object.keys(data['tests'][test]['data'])) {
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
                type: data['tests'][test]['type']}
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
    this.distributeCardsToSections(data);
    this.determineScoredTests();
  }

  private convertHistoryResults(data: Object): void {
    // Store each test history result as a TestHistory object in a central list.
    for (const test of Object.keys(data['tests'])){
      if (data['tests'][test]['history'] instanceof Object) {
        for (const param of Object.keys(data['tests'][test]['history'])) {
          const newID = test + ':' + param;
          this.allTests.push(
              new TestHistory(
                newID,
                {history: data['tests'][test]['history'][param],
                summary: data['tests'][test]['summary'],
                title: data['tests'][test]['title'],
                type: data['tests'][test]['type']}
              )
            );
        }
      } else {
      this.allTests.push(
          new TestHistory(
            test,
            data['tests'][test])
      );
    }
  }
  this.distributeCardsToSections(data);
  this.determineScoredTests();
}

  private extractMetadata(data: Object): void {
    // Extract metaddata information to be used in the metadata card
    this.metaData = data['meta'];
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
}
