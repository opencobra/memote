import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ResultButtonComponent } from './result-button.component';

describe('ResultButtonComponent', () => {
  let component: ResultButtonComponent;
  let fixture: ComponentFixture<ResultButtonComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ResultButtonComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ResultButtonComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
