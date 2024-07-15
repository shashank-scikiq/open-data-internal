import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RetailB2cComponent } from './retail-b2c.component';

describe('RetailB2cComponent', () => {
  let component: RetailB2cComponent;
  let fixture: ComponentFixture<RetailB2cComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [RetailB2cComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(RetailB2cComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
