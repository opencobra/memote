import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ScoreFormulaComponent } from './score-formula.component';

describe('ScoreFormulaComponent', () => {
  let component: ScoreFormulaComponent;
  let fixture: ComponentFixture<ScoreFormulaComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ScoreFormulaComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ScoreFormulaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
