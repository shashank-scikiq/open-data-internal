import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RetailOverallComponent } from './retail-overall.component';

describe('RetailOverallComponent', () => {
  let component: RetailOverallComponent;
  let fixture: ComponentFixture<RetailOverallComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [RetailOverallComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(RetailOverallComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
