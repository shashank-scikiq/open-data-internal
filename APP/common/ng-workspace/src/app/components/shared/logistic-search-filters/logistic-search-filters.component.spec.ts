import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LogisticSearchFiltersComponent } from './logistic-search-filters.component';

describe('LogisticSearchFiltersComponent', () => {
  let component: LogisticSearchFiltersComponent;
  let fixture: ComponentFixture<LogisticSearchFiltersComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LogisticSearchFiltersComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LogisticSearchFiltersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
