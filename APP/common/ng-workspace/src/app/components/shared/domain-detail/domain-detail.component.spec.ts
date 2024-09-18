import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DomainDetailComponent } from './domain-detail.component';

describe('DomainDetailComponent', () => {
  let component: DomainDetailComponent;
  let fixture: ComponentFixture<DomainDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DomainDetailComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DomainDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
