import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TabularizeComponent } from './tabularize.component';

describe('TabularizeComponent', () => {
  let component: TabularizeComponent;
  let fixture: ComponentFixture<TabularizeComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TabularizeComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TabularizeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
