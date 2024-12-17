import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PincodeLevelMapComponent } from './pincode-level-map.component';

describe('PincodeLvelMapComponent', () => {
  let component: PincodeLevelMapComponent;
  let fixture: ComponentFixture<PincodeLevelMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [PincodeLevelMapComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(PincodeLevelMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
