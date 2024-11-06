import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OpenDataFooterComponent } from './open-data-footer.component';

describe('OpenDataFooterComponent', () => {
  let component: OpenDataFooterComponent;
  let fixture: ComponentFixture<OpenDataFooterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [OpenDataFooterComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(OpenDataFooterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
