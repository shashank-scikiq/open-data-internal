import { Component, ElementRef, HostListener, Input, OnChanges, OnInit, SimpleChanges, ViewChild } from '@angular/core';

@Component({
  selector: 'app-top-cards-group',
  templateUrl: './top-cards-group.component.html',
  styleUrl: './top-cards-group.component.scss'
})
export class TopCardsGroupComponent implements OnChanges, OnInit {
  @Input() data: any = [];
  @Input() isLoading: boolean = false;
  tooltipText: any = null;
  prevDateRange: any = null;

  scrollEnabled: boolean = false;

  @ViewChild('slider', { read: ElementRef }) public slider: ElementRef<any> | undefined;

  ngOnInit(): void {
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.checkForScrolling();
    console.log(this.data, this.isLoading)
  }

  formatNumber(num: number) {
    var num_parts = num.toString().split(".");
    num_parts[0] = num_parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return num_parts.join(".");
  }

  @HostListener('window:resize', ['$event'])
  checkForScrolling() {
    const upperCardsSection: any = document.getElementsByClassName('upper-cards-section')[0];
    const sectionWidth = upperCardsSection?.offsetWidth;

    const cardsCount = this.data?.length ?? 0;

    this.scrollEnabled = Boolean(sectionWidth < ((cardsCount*350) + ((cardsCount - 1)*4) + 20));
  }

  public scrollRight(): void {
    this.slider?.nativeElement.scrollTo({ left: (this.slider?.nativeElement.scrollLeft + 354), behavior: 'smooth' });
  }

  public scrollLeft(): void {
    this.slider?.nativeElement.scrollTo({ left: (this.slider?.nativeElement.scrollLeft - 354), behavior: 'smooth' });
  }
}
