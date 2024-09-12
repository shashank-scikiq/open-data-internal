import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PincodeLevelMapViewComponent } from './pincode-level-map-view.component';

describe('PincodeLevelMapViewComponent', () => {
  let component: PincodeLevelMapViewComponent;
  let fixture: ComponentFixture<PincodeLevelMapViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [PincodeLevelMapViewComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(PincodeLevelMapViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
