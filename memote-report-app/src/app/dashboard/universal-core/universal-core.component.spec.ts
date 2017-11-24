import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { UniversalCoreComponent } from './universal-core.component';

describe('UniversalCoreComponent', () => {
  let component: UniversalCoreComponent;
  let fixture: ComponentFixture<UniversalCoreComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ UniversalCoreComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UniversalCoreComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
