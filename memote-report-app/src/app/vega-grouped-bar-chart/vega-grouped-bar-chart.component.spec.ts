import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { VegaGroupedBarChartComponent } from './vega-grouped-bar-chart.component';

describe('VegaGroupedBarChartComponent', () => {
  let component: VegaGroupedBarChartComponent;
  let fixture: ComponentFixture<VegaGroupedBarChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ VegaGroupedBarChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VegaGroupedBarChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
