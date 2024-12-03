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

  topStatesSearchData: any = null;
  topDistrictsSearchData: any = null;
  visibleTopStatesSearchData: any = null;
  visibleTopDistrictsSearchData: any = null;

  activeTimeInterval: any;


  constructor(private logisticsSearchService: LogisticSearchService) {}

  ngOnInit(): void {
    this.logisticsSearchService.filterUpdated$.subscribe(
      (val: any) => {
        console.log(val, "here");
      }
    )

    this.logisticsSearchService.activeTimeInterval$.subscribe(
      (val: any) => {
        this.activeTimeInterval = val;
        this.updateData();
      }
    )

    this.fetchTrendChartsData();
  }

  updateData() {
    this.visiblePanIndiaSearchData = this.panIndiaSearchData[this.activeTimeInterval] ?? null;
  }

  fetchTrendChartsData() {
    this.isLoadingOverall = true;
    this.logisticsSearchService.getTopCummulativeSearches().subscribe(
      (response: any) => {
        console.log(response);
        this.panIndiaSearchData = response;
        this.visiblePanIndiaSearchData = this.panIndiaSearchData[this.activeTimeInterval];
        this.isLoadingOverall = false;
      }, (error: Error) => {
        console.log(error);
        this.isLoadingOverall = false;
      }
    )

    this.isLoadingStatesData = true;
    this.logisticsSearchService.getTopStateSearches().subscribe(
      (response: any) => {
        this.topStatesSearchData = response;
        this.visibleTopStatesSearchData = this.topStatesSearchData[this.activeTimeInterval];


        this.isLoadingStatesData = false;
      }, (error: Error) => {
        console.log(error);
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
