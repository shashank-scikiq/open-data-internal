import { Component, Input, QueryList, ViewChildren, ElementRef, OnChanges, SimpleChanges } from '@angular/core';
import { delay } from 'rxjs';

@Component({
  selector: 'app-key-insights-carousel',
  templateUrl: './key-insights-carousel.component.html',
  styleUrl: './key-insights-carousel.component.scss'
})
export class KeyInsightsCarouselComponent  {
  @Input() items: any[] = [];

  currentCardIndex = 0;
  nextCardIndex = 1;
  previousCardIndex: number | null = null;

  ngOnInit(): void {
    if (this.items.length) {
      this.nextCardIndex = this.items.length > 1 ? 1 : 0;
      this.previousCardIndex = this.items.length - 1;
    }
  }

  moveCard(dir: any) {
    if (dir == 'previous') {
      this.currentCardIndex = this.currentCardIndex - 1 < 0 ? this.items.length - 1 : this.currentCardIndex - 1;
    } else {
      this.currentCardIndex = this.currentCardIndex + 1 == this.items.length ? 0 : this.currentCardIndex + 1;
    }
  }


  onCardClick(index: any): void {
    if (this.currentCardIndex !== index) {
      this.previousCardIndex = this.currentCardIndex;
      this.currentCardIndex = index;
      this.nextCardIndex = (this.currentCardIndex + 1) % this.items.length;
    }
  }
}
