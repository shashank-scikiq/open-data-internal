import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PanIndiaMapComponent } from './pan-india-map.component';

describe('PanIndiaMapComponent', () => {
  let component: PanIndiaMapComponent;
  let fixture: ComponentFixture<PanIndiaMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [PanIndiaMapComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(PanIndiaMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
