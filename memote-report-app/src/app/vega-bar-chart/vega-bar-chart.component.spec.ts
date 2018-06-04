import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { VegaBarChartComponent } from './vega-bar-chart.component';

describe('VegaBarChartComponent', () => {
  let component: VegaBarChartComponent;
  let fixture: ComponentFixture<VegaBarChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ VegaBarChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VegaBarChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
