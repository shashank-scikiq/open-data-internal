import { Component, OnInit } from '@angular/core';
import { LogisticSearchService } from '@openData/app/core/api/logistic-search/logistic-search.service';

@Component({
  selector: 'app-logistic-search',
  templateUrl: './logistic-search.component.html',
  styleUrl: './logistic-search.component.scss'
})
export class LogisticSearchComponent implements OnInit {
  domain: string = 'Logistics Search';
  dateRangeDate: string = '';
  isLoading: boolean = true;

  constructor(private logisticSearch: LogisticSearchService) {}

  ngOnInit(): void {
    this.isLoading = true;
    this.logisticSearch.getDateRange().subscribe(
      (response: any) => {
        this.logisticSearch.setDateRange([new Date(response.min_date), new Date(response.max_date)]);
        this.logisticSearch.setChoosableDateRange([new Date(response.min_date), new Date(response.max_date)]);
        this.isLoading = false;
      }, (error: Error) => {
        console.log(error);
        this.isLoading = false;
      }
    )
  }
}
