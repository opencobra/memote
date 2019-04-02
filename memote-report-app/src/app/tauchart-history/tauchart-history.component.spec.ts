import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TauChartHistoryComponent } from './tauchart-history.component';

describe('TauChartHistoryComponent', () => {
  let component: TauChartHistoryComponent;
  let fixture: ComponentFixture<TauChartHistoryComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TauChartHistoryComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TauChartHistoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
