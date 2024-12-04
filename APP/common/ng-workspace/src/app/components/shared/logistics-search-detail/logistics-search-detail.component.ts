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
  rawData: any = null;

  activeStateInitialized: boolean = false;
  isPincodeLevelViewInitialized: boolean = false;
  dateRangeInitialized: boolean = false;

  overallData: any = null;
  stateData: any = null;

  configData: any = {
    chloroColorRange: ["#F8F3C5", "#FFCD71", "#FF6F48"],
    bubbleColorRange: ["RGBA( 0, 139, 139, 0.4)", "RGBA( 0, 139, 139, 0.8)"],
    bubbleDataKey: 'Confirm percentage',
    chloroDataKey: 'Search count',
    maxChloroData: 0,
    maxBubbleData: 0
  }

  loadingData: boolean = false;

  legendConfigData: any = {
    bubbleMaxData: 0,
    bubbleColorRange: ["RGBA( 0, 139, 139, 0.4)", "RGBA( 0, 139, 139, 0.8)"],
    bubbleTitle: "% Search to confirm",
    bubbleSuffixText: "%",

    chloroMaxData: 0,
    chloroColorRange: ["#F8F3C5", "#FFCD71", "#FF6F48"],
    chloroTitle: "Search counts",
    chloroSuffixText: "",
  }


  activeView: any = 'chloro';
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

  constructor(private logisticSearchService: LogisticSearchService) { }

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

    this.logisticSearchService.filterUpdated$.subscribe(
      (val: any) => {
        if(val?.updatedFor && ['timeInterval', 'dayType', 'activeState'].includes(val.updatedFor)) {}

        if (val?.updatedFor && val.updatedFor == 'activeState') {
          this.activeState = this.logisticSearchService.activeState.value;
          this.loadingData = true;
          this.getMapData();
        } else if (val?.updatedFor && val.updatedFor == 'dayType') {
          this.loadingData = true;
          this.getMapData();
        } else if (val?.updatedFor && val.updatedFor == 'isPincodeView') {
          this.isPincodeLevelView = this.logisticSearchService.pincodeLevelView.value;
          if (!this.isPincodeLevelView) {
            this.loadingData = true;
            this.getMapData();
          }
        } else if (val?.updatedFor && val.updatedFor == 'timeInterval') {
          this.loadingData = true;
          this.prepareMapData();
        }
      }
    )

    // this.logisticSearchService.pincodeLevelView$.subscribe(
    //   (val: boolean) => {
    //     this.isPincodeLevelView = val;
    //     this.isPincodeLevelViewInitialized = true;
    //     if (!val) {
    //       this.loadingData = true;
    //       this.getMapData();
    //     }
    //   }
    // )
    // this.logisticSearchService.activeTimeInterval$.subscribe(
    //   (val: any) => {
    //     this.loadingData = true;
    //     this.prepareMapData();
    //   }
    // )

    // this.logisticSearchService.activeState$.subscribe(
    //   (state: string) => {
    //     this.activeStateInitialized = true;
    //     this.activeState = state;
    //     this.loadingData = true;
    //     this.getMapData();
    //   }
    // );
  }

  getMapData() {
    // if (!(
    //   this.activeStateInitialized &&
    //   this.isPincodeLevelViewInitialized &&
    //   this.dateRangeInitialized
    // )) {
    //   return;
    // }
    if (!this.isPincodeLevelView) {
      this.loadingData = true;
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

  async prepareMapData() {
    let data = this.rawData;
    if (!data) {
      return;
    }
    this.loadingData = true;
    let maxSearchCount = 0;
    let maxConfirmPercentage = 0;
    if (this.activeState == 'TT') {
      this.overallData = await data.mapdata.filter(
        (item: any) => (
          item.time_of_day === this.logisticSearchService.activeTimeInterval.value
        ) && (
          this.activeStyle == 'state_map' ? item.district == 'All' : true
        )
      ).reduce((acc: any, item: any) => {
        if (this.activeStyle == 'state_map') {
          acc[item.state] = {
            'Search count': item.total_searches,
            'Confirm percentage': `${item.total_conversion_percentage}%`,
            'Assigned percentage': `${item.total_assigned_percentage}%`
          };
        } else {
          acc[item.district] = {
            'Search count': item.total_searches,
            'Confirm percentage': `${item.total_conversion_percentage}%`,
            'Assigned percentage': `${item.total_assigned_percentage}%`
          };
        }
        if (Number(maxSearchCount) < Number(item.total_searches)) maxSearchCount = item.total_searches
        if (Number(maxConfirmPercentage) < Number(item.total_conversion_percentage)) maxConfirmPercentage = item.total_conversion_percentage
        return acc;
      }, {});

    } else {
      this.stateData = null;
      this.stateData = await data.mapdata.filter(
        (item: any) => item.time_of_day === this.logisticSearchService.activeTimeInterval.value
      ).reduce((acc: any, item: any) => {

        acc[item.district] = {
          'Search count': item.total_searches,
          'Confirm percentage': `${item.total_conversion_percentage}%`,
          'Assigned percentage': `${item.total_assigned_percentage}%`
        };
        if (Number(maxSearchCount) < Number(item.total_searches)) maxSearchCount = item.total_searches
        if (Number(maxConfirmPercentage) < Number(item.total_conversion_percentage)) maxConfirmPercentage = item.total_conversion_percentage
        return acc;
      }, {});
    }

    this.legendConfigData = {
      ...this.legendConfigData,
      bubbleMaxData: maxConfirmPercentage,
      chloroMaxData: maxSearchCount
    }

    this.configData = {
      ...this.configData,
      maxChloroData: maxSearchCount,
      maxBubbleData: maxConfirmPercentage
    }

    this.loadingData = false;
  }

  updateViewSelection(option: any) {
    this.activeView = option.type;
  }

  updateStyleSelection(option: any) {
    this.activeStyle = option.type;
    this.prepareMapData();
  }
}
