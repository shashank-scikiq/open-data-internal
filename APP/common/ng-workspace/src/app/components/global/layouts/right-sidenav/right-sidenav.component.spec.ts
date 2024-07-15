import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RightSidenavComponent } from './right-sidenav.component';

describe('RightSidenavComponent', () => {
  let component: RightSidenavComponent;
  let fixture: ComponentFixture<RightSidenavComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [RightSidenavComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(RightSidenavComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
