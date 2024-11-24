import { Component, OnInit } from '@angular/core';
import { LogisticSearchService } from '@openData/app/core/api/logistic-search/logistic-search.service';

@Component({
  selector: 'app-logistics-search-detail',
  templateUrl: './logistics-search-detail.component.html',
  styleUrl: './logistics-search-detail.component.scss'
})
export class LogisticsSearchDetailComponent implements OnInit {
  isLoading: boolean = true;
  isPincodeLevelView: boolean = false;
  activeState: string = 'TT';
  activeView: any = 'chloro';
  rawData: any=null;

  activeStateInitialized: boolean = false;
  isPincodeLevelViewInitialized: boolean = false;
  dateRangeInitialized: boolean = false;

  overallData: any = null;
  stateData: any = null;

  configData: any = {
    chloroColorRange: ["#F8F3C5", "#FFCD71", "#FF6F48"],
    bubbleColorRange: [],
    bubbleDataKey: 'Confirm percentage',
    chloroDataKey: 'Search count',
    maxChloroData: 0,
    maxBubbleData: 0
  }


  viewsOptions: any = [
    {
      type: 'chloro',
      title: 'Search Only'
    }, {
      type: 'bubble',
      title: 'Conversion Only'
    }, {
      type: 'both',
      title: 'Search and Conversion'
    },
  ];

  activeStyle: any = 'state_map';
  stylesOptions: any = [
    {
      type: 'state_map',
      title: 'State map'
    }, {
      type: 'district_map',
      title: 'District map'
    }
  ];

  constructor(private logisticSearchService: LogisticSearchService) {}

  ngOnInit(): void {
    this.isLoading = true;
    
    this.logisticSearchService.getDateRange().subscribe(
      (response: any) => {
        this.logisticSearchService.setDateRange(
          [new Date(response.min_date), new Date(response.max_date)]
        );
        this.logisticSearchService.setChoosableDateRange(
          [new Date(response.min_date), new Date(response.max_date)]
        );
        this.isLoading = false;
      }, (error: Error) => { 
        console.log(error); 
        this.isLoading = true 
      }
    )

    this.logisticSearchService.dateRange$.subscribe(
      (value: any) => {
        this.isLoading = true;
        this.dateRangeInitialized = true;
        this.getMapData();
        this.activeView = this.viewsOptions[0].type;
      }
    )

    this.logisticSearchService.pincodeLevelView$.subscribe(
      (val: boolean) => {
        this.isPincodeLevelView = val;
        this.isPincodeLevelViewInitialized = true;
        if (!val) {
          this.getMapData();
        }
      }
    )
    this.logisticSearchService.activeTimeInterval$.subscribe(
      (val: any) => {
        this.prepareMapData();
      }
    )

    this.logisticSearchService.activeState$.subscribe(
      (state: string) => {
        this.activeStateInitialized = true;
        this.activeState = state;
        this.getMapData();
      }
    );
  }

  getMapData() {
    if (!(
      this.activeStateInitialized && 
      this.isPincodeLevelViewInitialized && 
      this.dateRangeInitialized
    )) {
      return;
    }
    if (!this.isPincodeLevelView) {
      if (this.activeState == 'TT') {
        this.overallData = null;
        this.rawData = null;
        this.logisticSearchService.getOverallData().subscribe(
          (response: any) => {
            this.rawData = response;
            this.prepareMapData();
          },
          (error: Error) => console.log(error)
        )
      }
      else {
        this.stateData = null;
        this.rawData = null;
        this.logisticSearchService.getStateWiseData().subscribe(
          (response: any) => {
            this.rawData = response;
            this.prepareMapData();
          },
          (error: Error) => console.log(error)
        )
      }
    }
  }

  prepareMapData() {
    let data = this.rawData;
    if (!data) {
      return;
    }
    if (this.activeState == 'TT') {
      this.overallData = data.mapdata.filter(
          (item: any) => item.time_of_day === this.logisticSearchService.activeTimeInterval.value
        ).reduce((acc: any, item: any) => {
          acc[item.state] = { 
            'Search count': item.total_searches, 
            'Confirm percentage': item.order_confirmed 
          };
          return acc;
        }, {});
    } else {
      this.stateData = null;
      this.stateData = data.mapdata.filter(
        (item: any) => item.time_of_day === this.logisticSearchService.activeTimeInterval.value
      ).reduce((acc: any, item: any) => {
        acc[item.district] = {
          'Search count': item.total_searches, 
          'Confirm percentage': item.order_confirmed 
        };
        return acc;
      }, {});
    } 
  }

  updateViewSelection(option: any) {
    this.activeView = option.type;
    console.log(option);
  }

  updateStyleSelection(option: any) {
    this.activeStyle = option.type;
  }
}
