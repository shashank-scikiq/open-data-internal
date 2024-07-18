import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DetailCategoryFilterComponent } from './detail-category-filter.component';

describe('DetailCategoryFilterComponent', () => {
  let component: DetailCategoryFilterComponent;
  let fixture: ComponentFixture<DetailCategoryFilterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DetailCategoryFilterComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DetailCategoryFilterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
