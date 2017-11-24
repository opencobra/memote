import { TestBed, inject } from '@angular/core/testing';

import { ReportDataService } from './report-data.service';

describe('ReportDataService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ReportDataService]
    });
  });

  it('should be created', inject([ReportDataService], (service: ReportDataService) => {
    expect(service).toBeTruthy();
  }));
});
