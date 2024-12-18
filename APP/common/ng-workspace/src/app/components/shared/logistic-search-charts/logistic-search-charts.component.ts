import { Component, OnInit } from '@angular/core';
import { LogisticSearchService } from '@openData/app/core/api/logistic-search/logistic-search.service';

@Component({
  selector: 'app-logistic-search-charts',
  templateUrl: './logistic-search-charts.component.html',
  styleUrl: './logistic-search-charts.component.scss'
})
export class LogisticSearchChartsComponent implements OnInit {

  isLoadingOverall: boolean = false;
  isLoadingDistrictsData: boolean = false;
  isLoadingStatesData: boolean = false;
  panIndiaSearchData: any = null;
  visiblePanIndiaSearchData: any = null;
  isPincodeView: any = false;

  topStatesSearchData: any = null;
  topDistrictsSearchData: any = null;
  visibleTopStatesSearchData: any = null;
  visibleTopDistrictsSearchData: any = null;

  activeTimeInterval: any;
  activeState: string = 'TT';


  constructor(private logisticsSearchService: LogisticSearchService) {}

  ngOnInit(): void {
    this.logisticsSearchService.pincodeLevelView$.subscribe((response: any) => {
      this.isPincodeView = response;
    })
    this.logisticsSearchService.filterUpdated$.subscribe(
      (val: any) => {
        if (val.updatedFor && ['dayType', 'activeState', 'dateRange'].includes(val.updatedFor)) {
          this.fetchTrendChartsData();
        }
      }
    )

    this.logisticsSearchService.activeTimeInterval$.subscribe(
      (val: any) => {
        this.activeTimeInterval = val;
        this.updateData();
      }
    )

    this.logisticsSearchService.activeState$.subscribe(
      (val: any) => {
        this.activeState = val;
      }
    )

    this.fetchTrendChartsData();
  }

  updateData() {
    if (this.panIndiaSearchData)
      this.visiblePanIndiaSearchData = this.panIndiaSearchData[this.activeTimeInterval] ?? null;
    if (this.topStatesSearchData)
      this.visibleTopStatesSearchData = this.topStatesSearchData[this.activeTimeInterval] ?? null;
    if (this.topDistrictsSearchData)
      this.visibleTopDistrictsSearchData = this.topDistrictsSearchData[this.activeTimeInterval] ?? null;
  }

  fetchTrendChartsData() {
    if (this.logisticsSearchService.activeState.value == 'TT') {
      this.isLoadingOverall = true;
      this.logisticsSearchService.getTopCummulativeSearches().subscribe(
        (response: any) => {
          this.panIndiaSearchData = response;
          this.visiblePanIndiaSearchData = this.panIndiaSearchData[this.activeTimeInterval];
          this.isLoadingOverall = false;
        }, (error: Error) => {
          console.log(error);
          this.isLoadingOverall = false;
        }
      )
    }

    this.isLoadingStatesData = true;
    this.logisticsSearchService.getTopStateSearches().subscribe(
      (response: any) => {
        this.topStatesSearchData = response;
        this.visibleTopStatesSearchData = this.topStatesSearchData[this.activeTimeInterval];
        console.log(this.visibleTopStatesSearchData)
        this.isLoadingStatesData = false;
      }, (error: Error) => {
        console.log(error);
        this.topStatesSearchData = null
        this.visibleTopStatesSearchData = null;
        this.isLoadingStatesData = false;
      }
    )

    this.isLoadingDistrictsData = true;
    this.logisticsSearchService.getTopDistrictSearches().subscribe(
      (response: any) => {
        this.topDistrictsSearchData = response;
        this.visibleTopDistrictsSearchData = this.topDistrictsSearchData[this.activeTimeInterval];
        this.isLoadingDistrictsData = false;
      }, (error: Error) => {
        console.log(error);
        this.topDistrictsSearchData = null;
        this.visibleTopDistrictsSearchData = null;
        this.isLoadingDistrictsData = false;
      }
    )

    // this.logisticsSearchService.getTopStateSearches().subscribe(
    //   (response: any) => {
    //     console.log(response);
    //   }
    // )

    // this.logisticsSearchService.getTopDistrictSearches().subscribe(
    //   (response: any) => {
    //     console.log(response);
    //   }
    // )
  }

}
