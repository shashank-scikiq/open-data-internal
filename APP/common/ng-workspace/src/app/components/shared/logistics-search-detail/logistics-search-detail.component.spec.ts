import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LogisticsSearchDetailComponent } from './logistics-search-detail.component';

describe('LogisticsSearchDetailComponent', () => {
  let component: LogisticsSearchDetailComponent;
  let fixture: ComponentFixture<LogisticsSearchDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LogisticsSearchDetailComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LogisticsSearchDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
