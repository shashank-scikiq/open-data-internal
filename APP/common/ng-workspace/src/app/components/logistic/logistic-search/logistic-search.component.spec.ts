import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LogisticSearchComponent } from './logistic-search.component';

describe('LogisticSearchComponent', () => {
  let component: LogisticSearchComponent;
  let fixture: ComponentFixture<LogisticSearchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LogisticSearchComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LogisticSearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
