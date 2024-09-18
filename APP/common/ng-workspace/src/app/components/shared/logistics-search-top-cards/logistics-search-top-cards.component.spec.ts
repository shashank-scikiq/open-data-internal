import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LogisticsSearchTopCardsComponent } from './logistics-search-top-cards.component';

describe('LogisticsSearchTopCardsComponent', () => {
  let component: LogisticsSearchTopCardsComponent;
  let fixture: ComponentFixture<LogisticsSearchTopCardsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LogisticsSearchTopCardsComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LogisticsSearchTopCardsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
