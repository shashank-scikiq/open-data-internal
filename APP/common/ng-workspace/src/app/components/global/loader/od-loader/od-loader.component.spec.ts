import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OdLoaderComponent } from './od-loader.component';

describe('OdLoaderComponent', () => {
  let component: OdLoaderComponent;
  let fixture: ComponentFixture<OdLoaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [OdLoaderComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(OdLoaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
