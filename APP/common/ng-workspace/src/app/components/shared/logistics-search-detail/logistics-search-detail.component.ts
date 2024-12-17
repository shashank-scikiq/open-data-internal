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
  cityData: any = null;

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


  activeView: any = 'both';
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

  insightOptions: any = [
    {
      title: 'Top searched areas',
      tooltip: `Areas with high demand`,
      selected: false,
      type: 'high_demand',
      defaultView: this.viewsOptions[0]
    },
    {
      title: 'Top Conversion rate Areas',
      tooltip: `Areas with high conversion rate`,
      selected: false,
      type: 'high_conversion_rate',
      defaultView: this.viewsOptions[0]
    },
    {
      title: 'Areas with high search and high conversion rate',
      tooltip: `Areas that contribute to 75% of total searches (capped to 30 pincodes). 
            And conversion rates within these areas that are more than average.`,
      selected: false,
      type: 'high_demand_and_high_conversion_rate',
      defaultView: this.viewsOptions[2]
    },
    {
      title: 'Areas with high search and low conversion rate',
      tooltip: `Areas that contribute to 75% of total searches (capped to 30 pincodes) and 
        conversion rates within these areas that are less than average`,
      selected: false,
      type: 'high_demand_and_low_conversion_rate',
      defaultView: this.viewsOptions[2]
    },
    // {
    //   title: 'Areas with high search in peak morning hours',
    //   tooltip: `Areas with high demand between 8am-10am`,
    //   selected: false,
    //   type: 'high_demand_in_morning_hours',
    //   defaultView: this.viewsOptions[0]
    // },
    // {
    //   title: 'Areas with high search in peak evening hours',
    //   tooltip: `Areas with high demand between 6pm-9pm`,
    //   selected: false,
    //   type: 'high_demand_in_evening_hours',
    //   defaultView: this.viewsOptions[0]
    // }
  ];
  activeInsight: any;

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
        this.activeInsight = this.insightOptions[0];
      }
    )

    this.logisticSearchService.filterUpdated$.subscribe(
      (val: any) => {

        if (val?.updatedFor && val.updatedFor == 'activeState') {
          this.activeState = this.logisticSearchService.activeState.value;
          this.loadingData = true;
          this.getMapData();
        } else if (val?.updatedFor && val.updatedFor == 'dayType') {
          this.loadingData = true;
          this.getMapData();
        } else if (val?.updatedFor == 'isPincodeView') {
          this.isPincodeLevelView = this.logisticSearchService.pincodeLevelView.value;
          this.loadingData = true;
          this.getMapData();
        } else if (val?.updatedFor && val.updatedFor == 'timeInterval') {
          this.loadingData = true;
          if (this.logisticSearchService.pincodeLevelView.value) {
            (async () => {

              await this.preparePincodeLevelViewData();
              this.loadingData = false;
            })()
          } else {
            this.prepareMapData();
          }
        } else if (val?.updatedFor == 'city') {
          this.loadingData = true;
          this.getMapData();
        }
      }
    )
  }

  getMapData() {
      this.loadingData = true;
      if (this.isPincodeLevelView) {
        this.cityData = null;
        this.rawData = null;
        this.logisticSearchService.getCityWiseData().subscribe(
          async (response: any) => {
            this.rawData = response.data;
            await this.preparePincodeLevelViewData();
            this.loadingData = false;
          },
          (error: Error) => {
            console.log(error);
          }
        )
      }
      else if (this.activeState == 'TT') {
        this.overallData = null;
        this.rawData = null;
        this.logisticSearchService.getOverallData().subscribe(
          (response: any) => {
            this.rawData = response;
            this.prepareMapData();
          },
          (error: Error) => {
            console.log(error);
          }
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
          (error: Error) => {
            console.log(error);
          }
        )
      }
  }

  async preparePincodeLevelViewData() {
    let data = this.rawData;

    if(!data || !Object.keys(data).length) {
      // this.isLoading = false;
      return;
    }

    this.loadingData = true;
    let maxSearchCount = 0;
    let maxConfirmPercentage = 0;

    const cityLevelData: any = {};
    const pincodeData: any = Object.entries(data.mapData);
    const insightData: any = Object.entries(
      data.insightData[this.activeInsight.type][this.logisticSearchService.activeTimeInterval.value]
    );
    const iconData: any = {}


    for (const [pincode, timeData] of pincodeData) {
      const data = timeData[this.logisticSearchService.activeTimeInterval.value];
      cityLevelData[pincode] = {
        "Search count": data?.searched_data ?? 'No Data',
        "Confirm percentage": `${parseFloat(data?.conversion_rate) ?? 0}%`,
        "Assigned percentage": `${parseFloat(data?.assigned_rate ?? 0)}%`,
      };

      if (data?.searched_data && maxSearchCount < data.searched_data) 
        maxSearchCount = data.searched_data;

      if (data?.conversion_rate && maxConfirmPercentage < parseFloat(data.conversion_rate)) 
        maxConfirmPercentage = parseFloat(data.conversion_rate);
    }
    
    if (insightData) {
      for (const [pincode, timeData] of insightData) {
        iconData[pincode] = {
          "Search count": timeData?.searched_data ?? 'No Data',
          "Confirm percentage": `${parseFloat(timeData?.conversion_rate) ?? 0}%`,
          "Assigned percentage": `${parseFloat(timeData?.assigned_rate ?? 0)}%`,
        };
      }
    }
    this.cityData = {mapData: cityLevelData, iconData };

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
        if (Number(maxSearchCount) < Number(item.total_searches)) 
          maxSearchCount = item.total_searches;

        if (Number(maxConfirmPercentage) < Number(item.total_conversion_percentage)) 
          maxConfirmPercentage = item.total_conversion_percentage;

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
        if (Number(maxSearchCount) < Number(item.total_searches)) 
          maxSearchCount = item.total_searches;

        if (Number(maxConfirmPercentage) < Number(item.total_conversion_percentage)) 
          maxConfirmPercentage = item.total_conversion_percentage;

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

  updateInsightSelection(option: any) {
    this.activeInsight = option;
    this.activeView = option.defaultView.type;
    (async () => {

      await this.preparePincodeLevelViewData();
      this.loadingData = false;
    })()
  }
}
