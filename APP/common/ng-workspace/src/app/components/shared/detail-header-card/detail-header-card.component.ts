import { Component, ElementRef, HostListener, OnInit, ViewChild } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';
import { MapService } from '@openData/app/core/api/map/map.service';
import { StateCode } from '@openData/core/utils/map';
import { delay } from 'rxjs';

@Component({
  selector: 'app-detail-header-card',
  templateUrl: './detail-header-card.component.html',
  styleUrl: './detail-header-card.component.scss'
})
export class DetailHeaderCardComponent implements OnInit {
  upperCardData: any = [];
  isLoading: boolean = false;
  selectedStateCode: string = 'TT';
  topCardsDelta: any = {};
  tooltipText: any = {};
  prevDateRange: string = '';

  scrollEnabled: boolean = false;

  @ViewChild('slider', { read: ElementRef }) public slider: ElementRef<any> | undefined;

  constructor(
    private appService: AppService,
    private mapService: MapService,
  ) { }

  ngOnInit(): void {
    this.appService.dateRange$.subscribe(() => {
      this.getCardData();
    });
    this.appService.filterUpdated$.subscribe((val: any) => {
      if (val.updated) {
        this.getCardData();
      }
    });
    
    this.mapService.selectedState$.subscribe((val: string) => {
      this.selectedStateCode = val == 'TT' ? val : StateCode[val];
      if (this.topCardsDelta)
        this.updateTopCardsDelta();
    })
  }

  formatNumber(num: number) {
    var num_parts = num.toString().split(".");
    num_parts[0] = num_parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return num_parts.join(".");
  }


  getCardData() {
    this.isLoading = true;
    this.appService.getSummaryCardData().subscribe(
      (response: any) => {
        if (Object.keys(response.top_card_data).length) {
          this.topCardsDelta = response.top_card_data;
          this.tooltipText = response.tooltip_text,
          this.prevDateRange = response.prev_date_range;
          this.updateTopCardsDelta();
        }

      }, (error: Error) => {
        console.log(error);
        this.isLoading = false;
      }
    )
  }

  updateTopCardsDelta() {
    if (Object.keys(this.topCardsDelta).length) {
      this.upperCardData = this.topCardsDelta[this.selectedStateCode];
      this.isLoading = false;

      delay(1000);
      this.checkForScrolling();
    }
  }

  @HostListener('window:resize', ['$event'])
  checkForScrolling() {
    const upperCardsSection: any = document.getElementsByClassName('upper-cards-section')[0];
    const sectionWidth = upperCardsSection.offsetWidth;

    const cardsCount = this.topCardsDelta['TT']?.length ?? 0;

    this.scrollEnabled = Boolean(sectionWidth < ((cardsCount*350) + ((cardsCount - 1)*4) + 20));
  }

  public scrollRight(): void {
    this.slider?.nativeElement.scrollTo({ left: (this.slider?.nativeElement.scrollLeft + 354), behavior: 'smooth' });
  }

  public scrollLeft(): void {
    this.slider?.nativeElement.scrollTo({ left: (this.slider?.nativeElement.scrollLeft - 354), behavior: 'smooth' });
  }
}
