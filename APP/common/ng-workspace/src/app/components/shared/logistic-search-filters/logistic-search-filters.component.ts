import { Component, OnInit } from '@angular/core';
import { LogisticSearchService } from '@openData/app/core/api/logistic-search/logistic-search.service';

@Component({
  selector: 'app-logistic-search-filters',
  templateUrl: './logistic-search-filters.component.html',
  styleUrl: './logistic-search-filters.component.scss'
})
export class LogisticSearchFiltersComponent implements OnInit {

  timeIntervals: string[] = [
    "Overall", "3am-6am", "6am-8am", "8am-10am", "10am-12pm", 
    "12pm-3pm", "3pm-6pm", "6pm-9pm", "9pm-12am", "12am-3am"
  ];
  selectedInterval: string = 'Overall';
  overallSelected: boolean = true;

  cities: string[] = ['New Delhi', 'Bangalore'];
  selectedCity: string = 'New Delhi';
  dateRange: any = [];
  availableDateRange: any = [];

  constructor(private logisticSearchService: LogisticSearchService) {}

  ngOnInit(): void {
    this.updateValue();
    this.logisticSearchService.choosableDateRange$.subscribe((value) => {
      this.availableDateRange = value;
      this.logisticSearchService.dateRange$.subscribe((value) => {
        this.dateRange = value;
      });
    })
    
    this.logisticSearchService.activeTimeInterval$.subscribe(
      (res: any) => {
        if (res) {
          this.selectedInterval = res;
          this.overallSelected = Boolean(res=='Overall')
        }
      })
    
  }

  setDateRange(value: any) {
    this.logisticSearchService.setDateRange(value);
    this.logisticSearchService.filterUpdated.next({updated: true});
  }

  updateTimeInterval(option: string) {
    if (this.selectedInterval==option) {
      this.selectedInterval = this.timeIntervals[0];
    } else {
      this.selectedInterval=option;
    }
    this.updateValue('timeInterval');
  }
  
  updateValue(updatedFor: string = 'city') {
    if (updatedFor == 'city') {
      this.logisticSearchService.setActiveCity(this.selectedCity);
    } else {
      this.overallSelected = this.selectedInterval == 'Overall';
      this.logisticSearchService.setActiveTimeInterval(this.selectedInterval);
    }
    this.logisticSearchService.filterUpdated.next({updated: true, updatedFor});
  }
}
