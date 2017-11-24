import { TestResult } from './test-result.model';

export class PyModule {
/* This class corresponds to the highest level of categorization in the
test-results data output by memote: The segregation into python modules i.e.
those in memote.suite.tests. This class serves as a datacarrier, allowing for
simpler transfer of the data across components.
*/
  public moduleName: string;
  public testResults: TestResult[];

  constructor(moduleName: string, testResults: TestResult[]){
    this.moduleName = moduleName;
    this.testResults = testResults;
  }
}
