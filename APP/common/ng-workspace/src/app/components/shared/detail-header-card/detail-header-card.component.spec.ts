import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DetailHeaderCardComponent } from './detail-header-card.component';

describe('DetailHeaderCardComponent', () => {
  let component: DetailHeaderCardComponent;
  let fixture: ComponentFixture<DetailHeaderCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DetailHeaderCardComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DetailHeaderCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
