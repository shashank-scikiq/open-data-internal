import { ComponentFixture, TestBed } from '@angular/core/testing';

import { KeyInsightsCarouselComponent } from './key-insights-carousel.component';

describe('KeyInsightsCarouselComponent', () => {
  let component: KeyInsightsCarouselComponent;
  let fixture: ComponentFixture<KeyInsightsCarouselComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [KeyInsightsCarouselComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(KeyInsightsCarouselComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
