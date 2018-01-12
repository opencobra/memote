import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ResultCard } from './resultcard.model';
import { TestResult } from './test-result.model';
import * as testData from './data/testData.json';

@Injectable()
export class ReportDataService {
  metaData: any;
  allTests: TestResult[] = [];
  scoredCard: Object;
  statisticsCards: ResultCard[] = [];

  constructor(private http: HttpClient) {}

  public loadResults(): void {
    // this.http.get("data/testData.json").subscribe(data => {this.rawReportData = data});
    this.convertResults((<any>window).data || testData);
  }

  public byID(string){
    return this.allTests.find(x => x.id === string);
  }

  public getString(object){
    return JSON.stringify(object);
  }

  private convertResults(data:Object): void{
    // Store each test result as a TestResult object in a central list.
    for (const test of Object.keys(data["tests"])){
      this.allTests.push(
        new TestResult(
          test,
          data["tests"][test]))
    };
    // Extract metaddata information to be used in the metadata card
    this.metaData = data["meta"];
    for (const card of Object.keys(data["cards"])){
      if (card === "scored"){
        this.scoredCard = data["cards"]["scored"]
      }
      else{
        this.statisticsCards.push(
          new ResultCard(
            card,
            data["cards"][card],
          )
        )
      }
    }
  }
}
