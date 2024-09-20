import { Component, OnInit } from '@angular/core';
import { LogisticSearchService } from '@openData/app/core/api/logistic-search/logistic-search.service';
import { delay } from 'rxjs';

@Component({
  selector: 'app-logistics-search-top-cards',
  templateUrl: './logistics-search-top-cards.component.html',
  styleUrl: './logistics-search-top-cards.component.scss'
})
export class LogisticsSearchTopCardsComponent implements OnInit {
  topCardData: any = [];
  topCardsGroupData: any = [];
  isLoading: boolean = true;

  constructor(private logisticSearchService: LogisticSearchService) { }

  ngOnInit(): void {
    this.logisticSearchService.filterUpdated$.subscribe(
      (val: any) => {
        this.topCardsGroupData = [];
        if(val?.updatedFor == 'timeInterval') {
          this.prepareData();
        } else {
          this.getData();
        }
      }
    )
  }

  getData() {
    this.isLoading = true;
    this.logisticSearchService.getTopCardsData().subscribe(
      (response: any) => {
        this.topCardData = response.data;
        this.prepareData();
      }, (error: Error) => {
      console.log(error);
    }
    )
  }

  prepareData() {
    let cardsData = [];

    for (let data of this.topCardData) {
      if (data.time_of_day == this.logisticSearchService.activeTimeInterval.value) {
        cardsData.push({
          count: `${data.searched_data}`,
          heading: "Total searches",
          showVarience: false,
          type: "default"
        })
        cardsData.push({
          count: `${data.total_conversion_percentage}%`,
          heading: "% Search-to-confirm",
          showVarience: false,
          type: "default"
        })
        cardsData.push({
          count: `${data.total_assigned_percentage}%`,
          heading: "% Search-to-rider-assign",
          showVarience: false,
          type: "default"
        })
      }
    }

    this.topCardsGroupData = cardsData;
    delay(500);
    this.isLoading = false;
  }
}
