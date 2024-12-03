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
        if (val?.updatedFor && ['timeInterval', 'activeState'].includes(val.updatedFor)) {
          if (Object.keys(this.topCardData)?.length) {
            this.prepareData();
          }
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
        if (response) {
          this.topCardData = response.data;
          if (Object.keys(this.topCardData)?.length) {
            this.prepareData();
          }
        }
      }, (error: Error) => {
        console.log(error);
      }
    )
  }

  prepareData() {
    let cardsData = [];
    const key = this.logisticSearchService.pincodeLevelView.value ?
      this.logisticSearchService.activeCity.value :
      this.logisticSearchService.activeState.value.toUpperCase()
    const data = this.topCardData[key][this.logisticSearchService.activeTimeInterval.value]

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

    this.topCardsGroupData = cardsData;
    delay(500);
    this.isLoading = false;
  }
}
