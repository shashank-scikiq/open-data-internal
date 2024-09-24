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

  constructor(private logisticSearch: LogisticSearchService) {}

  ngOnInit(): void {
    this.logisticSearch.getDateRange().subscribe(
      (response: any) => {
        this.dateRangeDate = response.data;
      }, (error: Error) => {
        console.log(error);
      }
    )
  }
}
