import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DataDirectoryComponent } from './data-directory.component';

describe('DataDirectoryComponent', () => {
  let component: DataDirectoryComponent;
  let fixture: ComponentFixture<DataDirectoryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DataDirectoryComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(DataDirectoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
