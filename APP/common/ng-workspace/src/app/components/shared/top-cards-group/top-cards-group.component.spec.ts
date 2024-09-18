import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TopCardsGroupComponent } from './top-cards-group.component';

describe('TopCardsGroupComponent', () => {
  let component: TopCardsGroupComponent;
  let fixture: ComponentFixture<TopCardsGroupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [TopCardsGroupComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(TopCardsGroupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
