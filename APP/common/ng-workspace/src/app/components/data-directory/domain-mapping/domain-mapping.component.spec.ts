import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DomainMappingComponent } from './domain-mapping.component';

describe('DomainMappingComponent', () => {
  let component: DomainMappingComponent;
  let fixture: ComponentFixture<DomainMappingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DomainMappingComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DomainMappingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
