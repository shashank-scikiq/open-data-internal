import { Component, OnInit } from '@angular/core';
import { LogisticSearchService } from '@openData/app/core/api/logistic-search/logistic-search.service';

@Component({
  selector: 'app-logistics-search-detail',
  templateUrl: './logistics-search-detail.component.html',
  styleUrl: './logistics-search-detail.component.scss'
})
export class LogisticsSearchDetailComponent implements OnInit {
  isLoading: boolean = true;

  constructor(private logisticSearchService: LogisticSearchService) {}

  ngOnInit(): void {
    this.isLoading = true;
    this.logisticSearchService.getDateRange().subscribe(
      (response: any) => {
        this.logisticSearchService.setDateRange([new Date(response.min_date), new Date(response.max_date)]);
        this.logisticSearchService.setChoosableDateRange([new Date(response.min_date), new Date(response.max_date)]);
        this.isLoading = false;
      }, (error: Error) => { console.log(error); this.isLoading = true }
    )
  }
}
