import { TestResult } from './test-result.model';

export class ResultCard {
  public cardName: string;
  public cardID: string;
  public associatedTests: TestResult[];

  constructor(cardID:string, cardName: string, associatedTests: TestResult[]){
    this.cardID = cardID
    this.cardName = cardName;
    this.associatedTests = associatedTests;
  }
}
