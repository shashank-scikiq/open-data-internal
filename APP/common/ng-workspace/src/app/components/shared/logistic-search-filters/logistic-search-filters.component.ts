import { Component, OnInit } from '@angular/core';
import { LogisticSearchService } from '@openData/app/core/api/logistic-search/logistic-search.service';

@Component({
  selector: 'app-logistic-search-filters',
  templateUrl: './logistic-search-filters.component.html',
  styleUrl: './logistic-search-filters.component.scss'
})
export class LogisticSearchFiltersComponent implements OnInit {

  timeIntervals: string[] = [
    "3am-6am",
    "6am-8am",
    "8am-10am",
    "10am-12pm",
    "12pm-3pm",
    "3pm-6pm",
    "6pm-9pm",
    "9pm-12am",
  ];
  selectedInterval: string = '3pm-6pm';

  cities: string[] = ['New Delhi', 'Bangalore'];
  selectedCity: string = 'New Delhi';

  constructor(private logisticSearchService: LogisticSearchService) {}

  ngOnInit(): void {
    this.updateValue();
  }
  
  updateValue(updatedFor: string = 'city') {
    this.logisticSearchService.setActiveCity(this.selectedCity);
    this.logisticSearchService.setActiveTimeInterval(this.selectedInterval);
    this.logisticSearchService.filterUpdated.next({updated: true, updatedFor});
  }
}
