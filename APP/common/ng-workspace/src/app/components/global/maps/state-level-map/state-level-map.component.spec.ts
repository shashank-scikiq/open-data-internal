import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StateLevelMapComponent } from './state-level-map.component';

describe('StateLevelMapComponent', () => {
  let component: StateLevelMapComponent;
  let fixture: ComponentFixture<StateLevelMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [StateLevelMapComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(StateLevelMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
