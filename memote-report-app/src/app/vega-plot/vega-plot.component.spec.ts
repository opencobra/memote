import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { VegaPlotComponent } from './vega-plot.component';

describe('VegaPlotComponent', () => {
  let component: VegaPlotComponent;
  let fixture: ComponentFixture<VegaPlotComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ VegaPlotComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VegaPlotComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
