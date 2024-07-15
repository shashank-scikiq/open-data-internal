import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DqReportComponent } from './dq-report.component';

describe('DqReportComponent', () => {
  let component: DqReportComponent;
  let fixture: ComponentFixture<DqReportComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DqReportComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DqReportComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
