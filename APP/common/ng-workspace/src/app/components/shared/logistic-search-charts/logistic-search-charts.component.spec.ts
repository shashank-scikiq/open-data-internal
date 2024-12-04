import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LogisticSearchChartsComponent } from './logistic-search-charts.component';

describe('LogisticSearchChartsComponent', () => {
  let component: LogisticSearchChartsComponent;
  let fixture: ComponentFixture<LogisticSearchChartsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LogisticSearchChartsComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LogisticSearchChartsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
