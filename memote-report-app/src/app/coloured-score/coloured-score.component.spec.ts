import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ColouredScoreComponent } from './coloured-score.component';

describe('ColouredScoreComponent', () => {
  let component: ColouredScoreComponent;
  let fixture: ComponentFixture<ColouredScoreComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ColouredScoreComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ColouredScoreComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
