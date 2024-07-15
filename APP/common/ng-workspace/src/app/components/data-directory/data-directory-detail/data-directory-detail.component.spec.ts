import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DataDirectoryDetailComponent } from './data-directory-detail.component';

describe('DataDirectoryDetailComponent', () => {
  let component: DataDirectoryDetailComponent;
  let fixture: ComponentFixture<DataDirectoryDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DataDirectoryDetailComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DataDirectoryDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
