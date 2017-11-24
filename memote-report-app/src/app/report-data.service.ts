import { Injectable, Observable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { PyModule } from './pymodule.model';
import { TestResult } from './test-result.model';

@Injectable()
export class ReportDataService {
  metaData: Object = [];
  reportData: Object[] = [];
  scoreData: PyModule;

  constructor(private http:HttpClient){
  }

  public loadResults(): void{
    // this.http.get("data/testData.json").subscribe(data => {this.rawReportData = data});
    this.http.get("data/testData.json").subscribe(data => {this.convertResults(data)});
  }

  public getString(object){
    return JSON.stringify(object);
  }

  private convertResults(data:any[]): void{
    this.metaData = data["meta"];
    console.log(this.metaData);
      for (let key of Object.keys(data["report"])){
        // console.log(data["report"][key]);
        let inner_list = [];
        for (let test of Object.keys(data["report"][key])){
          let content = data["report"][key][test];
          inner_list.push(
            new TestResult(test, content['data'], content['duration'], content['message'],
             content['metric'], content['result'], content['summary'], content['title'],
           content['type'])
         );
        }
        // console.log(inner_list);
        if (key === "test_consistency" ) {
          this.scoreData = new PyModule(key, inner_list)
        } else {
        this.reportData.push(new PyModule(key, inner_list));
        }
      }
    // console.log(this.reportData);
  }
}
