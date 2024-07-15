import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RetailB2bComponent } from './retail-b2b.component';

describe('RetailB2bComponent', () => {
  let component: RetailB2bComponent;
  let fixture: ComponentFixture<RetailB2bComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [RetailB2bComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(RetailB2bComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
