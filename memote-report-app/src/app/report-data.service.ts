import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ResultCard } from './resultcard.model';
import { TestResult } from './test-result.model';
// import * as testData from './data/testData.json';

@Injectable()
export class ReportDataService {
  metaData: any;
  allTests: TestResult[] = [];
  scoredCard: Object;
  statisticsCards: ResultCard[] = [];
  scoredTests: string[] = [];

  constructor(private http: HttpClient) {}

  public loadResults(): void {
    // TODO: Might want to parse and decompress a string in future.
    // const data = JSON.parse((<any>window).data);
    // this.convertResults((<any>window).data);
    this.http.get('/data/testData.json').subscribe(data => {this.convertResults(data); });
  }

  public byID(string) {
    return this.allTests.find(x => x.id === string);
  }

  public isScored(string) {
    return this.scoredTests.includes(string);
  }

  public getString(object) {
    return JSON.stringify(object);
  }

  private convertResults(data: Object): void {
    // Store each test result as a TestResult object in a central list.
    for (const test of Object.keys(data['tests'])){
      this.allTests.push(
        new TestResult(
          test,
          data['tests'][test]));
    }
    // Extract metaddata information to be used in the metadata card
    this.metaData = data['meta'];
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
    // Build a list of IDs of tests that are scored. This is only used in the
    //  logic of `coloured-score.component`.
    for (const section of Object.keys(this.scoredCard['sections'])) {
      if (this.scoredCard['sections'][section]['cases'] instanceof Array) {
      for (const testId of this.scoredCard['sections'][section]['cases']) {
        console.log(testId);
        this.scoredTests.push(testId);
      }
    }
  }
}
