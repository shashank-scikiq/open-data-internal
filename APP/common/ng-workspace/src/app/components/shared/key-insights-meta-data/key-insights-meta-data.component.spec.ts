import { ComponentFixture, TestBed } from '@angular/core/testing';

import { KeyInsightsMetaDataComponent } from './key-insights-meta-data.component';

describe('KeyInsightsMetaDataComponent', () => {
  let component: KeyInsightsMetaDataComponent;
  let fixture: ComponentFixture<KeyInsightsMetaDataComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [KeyInsightsMetaDataComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(KeyInsightsMetaDataComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
