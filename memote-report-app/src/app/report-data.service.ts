import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ResultCard } from './resultcard.model';
import { TestResult } from './test-result.model';

@Injectable()
export class ReportDataService {
  metaData: any;
  allTests: TestResult[] = [];
  scoredCard: Object;
  statisticsCards: ResultCard[] = [];

  constructor(private http:HttpClient){
  }

  public loadResults(): void{
    // this.http.get("data/testData.json").subscribe(data => {this.rawReportData = data});
    this.http.get("data/testData.json").subscribe(data => {this.convertResults(data)});
  }

  public byID(string){
    return this.allTests.find(x => x.id === string);
  }

  public getString(object){
    return JSON.stringify(object);
  }

  private convertResults(data:Object): void{
    // Store each test result as a TestResult object in a central list.
    for (let test of Object.keys(data["tests"])){
      this.allTests.push(
        new TestResult(
          test,
          data["tests"][test]['data'],
          data["tests"][test]['duration'],
          data["tests"][test]['message'],
          data["tests"][test]['metric'],
          data["tests"][test]['result'],
          data["tests"][test]['summary'],
          data["tests"][test]['title'],
         data["tests"][test]['type']));
    };
    // Extract metaddata information to be used in the metadata card
    this.metaData = data["meta"];
    for (let card of Object.keys(data["cards"])){
      if (card === "scored"){
        this.scoredCard = data["cards"]["scored"]
      }
      else{
        this.statisticsCards.push(
          new ResultCard(
            card,
            data["cards"][card]["title"],
            data["cards"][card]["cases"]
          )
        )
      }
    }
    console.log(this.statisticsCards)
  }
}
