import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MonthRangePickerComponent } from './month-range-picker.component';

describe('MonthRangePickerComponent', () => {
  let component: MonthRangePickerComponent;
  let fixture: ComponentFixture<MonthRangePickerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MonthRangePickerComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(MonthRangePickerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
