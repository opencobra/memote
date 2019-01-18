import { TestResult } from './test-result.model';

export class ResultCard {
  public cardName: string;
  public cardID: string;
  public associatedTests: TestResult[];

  constructor(
    cardID: string,
    {title, cases}: {title: string, cases: TestResult[]}
  ) {
    this.cardID = cardID;
    this.cardName = title;
    this.associatedTests = cases;
  }
}
