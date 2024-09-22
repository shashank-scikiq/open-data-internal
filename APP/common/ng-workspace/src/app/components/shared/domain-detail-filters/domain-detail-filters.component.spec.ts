import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DomainDetailFiltersComponent } from './domain-detail-filters.component';

describe('DomainDetailFiltersComponent', () => {
  let component: DomainDetailFiltersComponent;
  let fixture: ComponentFixture<DomainDetailFiltersComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DomainDetailFiltersComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DomainDetailFiltersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
