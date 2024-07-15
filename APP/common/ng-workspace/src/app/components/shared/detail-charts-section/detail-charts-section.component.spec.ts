import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DetailChartsSectionComponent } from './detail-charts-section.component';

describe('DetailChartsSectionComponent', () => {
  let component: DetailChartsSectionComponent;
  let fixture: ComponentFixture<DetailChartsSectionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DetailChartsSectionComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DetailChartsSectionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
