import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { VegaTotalScoreBarChartComponent } from './vega-total-score-bar-chart.component';

describe('VegaBarChartComponent', () => {
  let component: VegaTotalScoreBarChartComponent;
  let fixture: ComponentFixture<VegaTotalScoreBarChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ VegaTotalScoreBarChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VegaTotalScoreBarChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
