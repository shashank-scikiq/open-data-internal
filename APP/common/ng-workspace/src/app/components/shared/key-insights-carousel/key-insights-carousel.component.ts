import { Component, Input, QueryList, ViewChildren, ElementRef, OnChanges, SimpleChanges } from '@angular/core';
import { delay } from 'rxjs';

@Component({
  selector: 'app-key-insights-carousel',
  templateUrl: './key-insights-carousel.component.html',
  styleUrl: './key-insights-carousel.component.scss'
})
export class KeyInsightsCarouselComponent  {
  @Input() items: any[] = [];
  // active: number = 0;
  // metaDataChecked: boolean = false;

  // @ViewChildren('item') itemElements!: QueryList<ElementRef>;

  // constructor() {}

  // async ngOnChanges(changes: SimpleChanges) {
  //   if (changes['items']['currentValue']?.length) {
  //     this.items = changes['items']['currentValue'];
  //     console.log(this.items)
  //     await delay(4000)
  //     this.active = (this.items.length - 2) > 0 ? Math.floor(this.items.length / 2) : 0;  
  //     this.loadShow();
  //   }
  // }

  // next() {
  //   this.active = this.active + 1 < this.items.length ? this.active + 1 : this.active;
  //   this.loadShow();
  // }

  // previous() {
  //   this.active = this.active - 1 >= 0 ? this.active - 1 : this.active;
  //   this.loadShow();
  // }

  // loadShow() {
  //   const itemsArray = this.itemElements.toArray();

  //   if (!itemsArray || itemsArray.length === 0) return;

  //   itemsArray[this.active].nativeElement.style.transform = `none`;
  //   itemsArray[this.active].nativeElement.style.zIndex = '1';
  //   itemsArray[this.active].nativeElement.style.filter = 'none';
  //   itemsArray[this.active].nativeElement.style.opacity = '1';

  //   let stt = 0;
  //   for (let i = this.active + 1; i < itemsArray.length; i++) {
  //     stt++;
  //     itemsArray[i].nativeElement.style.transform = `translateX(${120 * stt}px) scale(${1 - 0.2 * stt}) perspective(16px) rotateY(-1deg)`;
  //     itemsArray[i].nativeElement.style.zIndex = `${-stt}`;
  //     itemsArray[i].nativeElement.style.filter = 'blur(5px)';
  //     itemsArray[i].nativeElement.style.opacity = stt > 2 ? '0' : '0.6';
  //   }

  //   stt = 0;
  //   for (let i = this.active - 1; i >= 0; i--) {
  //     stt++;
  //     itemsArray[i].nativeElement.style.transform = `translateX(${-120 * stt}px) scale(${1 - 0.2 * stt}) perspective(16px) rotateY(1deg)`;
  //     itemsArray[i].nativeElement.style.zIndex = `${-stt}`;
  //     itemsArray[i].nativeElement.style.filter = 'blur(5px)';
  //     itemsArray[i].nativeElement.style.opacity = stt > 2 ? '0' : '0.6';
  //   }
  // }

  currentCardIndex = 0;
  nextCardIndex = 1;
  previousCardIndex: number | null = null;

  ngOnInit(): void {
    if (this.items.length) {
      this.nextCardIndex = this.items.length > 1 ? 1 : 0;
    }
  }

  onCardClick(index: number): void {
    if (this.currentCardIndex !== index) {
      this.previousCardIndex = this.currentCardIndex;
      this.currentCardIndex = index;
      this.nextCardIndex = (this.currentCardIndex + 1) % this.items.length;
    }
  }
}
