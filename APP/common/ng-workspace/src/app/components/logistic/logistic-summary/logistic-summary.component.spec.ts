import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LogisticSummaryComponent } from './logistic-summary.component';

describe('LogisticSummaryComponent', () => {
  let component: LogisticSummaryComponent;
  let fixture: ComponentFixture<LogisticSummaryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LogisticSummaryComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LogisticSummaryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
