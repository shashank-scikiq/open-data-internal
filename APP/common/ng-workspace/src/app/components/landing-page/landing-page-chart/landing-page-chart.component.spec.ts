import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LandingPageChartComponent } from './landing-page-chart.component';

describe('LandingPageChartComponent', () => {
  let component: LandingPageChartComponent;
  let fixture: ComponentFixture<LandingPageChartComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LandingPageChartComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LandingPageChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
