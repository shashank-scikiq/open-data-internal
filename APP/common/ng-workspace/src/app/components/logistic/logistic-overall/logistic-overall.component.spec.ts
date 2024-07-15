import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LogisticOverallComponent } from './logistic-overall.component';

describe('LogisticOverallComponent', () => {
  let component: LogisticOverallComponent;
  let fixture: ComponentFixture<LogisticOverallComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LogisticOverallComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LogisticOverallComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
