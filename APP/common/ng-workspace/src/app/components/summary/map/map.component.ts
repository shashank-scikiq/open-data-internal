import { ChangeDetectorRef, Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { MapService } from '@openData/app/core/api/map/map.service';
import { AppService } from '@openData/core/api/app/app.service';
import { METRICS, MetrixType } from '@openData/core/utils/global';
import { MapStatewiseData } from '@openData/core/utils/map';

@Component({
  selector: 'app-map',
  templateUrl: './map.component.html',
  styleUrl: './map.component.scss'
})
export class MapComponent implements OnInit, OnChanges {
  @Input() metrix: MetrixType = 'map_total_zonal_commerce_metrics';
  mapStatewiseData: MapStatewiseData | any;
  mapStateData: any;
  selectedState: string = 'TT';
  mapData: any = null;
  isLoading: boolean = true;

  mapVisualOptions: any = {
    isStateMap: true,
    isDistrictMap: false,
    isChloropeth: true,
    isBubble: false,
  }

  overallData: any = null;

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

  configData: any = {
    chloroColorRange: ["#F8F3C5", "#FFCD71", "#FF6F48"],
    bubbleColorRange: ["RGBA( 0, 139, 139, 0.4)", "RGBA( 0, 139, 139, 0.8)"],
    bubbleDataKey: '',
    chloroDataKey: '',
    maxChloroData: 0,
    maxBubbleData: 0,
    showBackButton: false
  }

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

  constructor(
    private appService: AppService,
    private mapService: MapService,
    private changeDetectionRef: ChangeDetectorRef
  ) { }

  ngOnInit(): void {
    this.appService.dateRange$.subscribe(() => {
      // this.mapStateData = null;
      // this.mapStatewiseData = null;
      this.mapData = null;
      // this.fetchMapStateData();
      // this.fetchOrderMetricsSummary();
      this.isLoading = true;
      this.fetchMapData();
    });
    this.appService.filterUpdated$.subscribe((val) => {
      if (val.updated) {
        // this.mapStateData = null;
        // this.mapStatewiseData = null;
        this.mapData = null;
        this.isLoading = true;
        this.fetchMapData();
        // this.fetchMapStateData();
        // this.fetchOrderMetricsSummary();
      }
    });
    this.mapService.selectedState$.subscribe((state: string) => {
      if (state != this.selectedState)
        this.selectedState = state;
        (async () => {
          await this.prepareMapData();
          this.isLoading = false;
        })();
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['metrix'] && changes['metrix'].currentValue == "map_total_active_sellers_metrics") {
      this.mapService.setSelectedState('TT');
      this.mapVisualOptions.isStateMap = true;
      this.mapVisualOptions.isDistrictMap = false;
    }
    (async () => {
      await this.prepareMapData();
      this.isLoading = false;
    })();
  }

  fetchMapData() {
    this.isLoading = true;
    this.appService.getMapData().subscribe(
      (response: any) => {
        if (response) {
          this.mapData = response;
          // console.log(this.mapData);
          (async () => {
            await this.prepareMapData();
            this.isLoading = false;
          })();
        }
      }, (error: Error) => {
        console.log('Error is ', error);
      }
    )
  }

  async prepareMapData() {
    let data = this.mapData;
    if (!data) {
      return;
    }

    this.isLoading = true;
    this.overallData = null;
    let maxValue = 0;
    let key = '';
    console.log(this.selectedState);
    this.overallData = await data.filter(
      (item: any) => {
        if (this.selectedState == 'TT') {
          return  this.activeStyle == 'state_map' ? item.delivery_district == 'AGG' : item.delivery_district != 'AGG';
        } else {
          return item.delivery_state == this.selectedState.toUpperCase() && item.delivery_district != 'AGG';
        }
      }
    ).reduce((acc: any, item: any) => {
      console.log(item);
      let mainKey = '';
      if (this.mapService.selectedState.value == 'TT' && this.activeStyle == 'state_map') {
        mainKey = item.delivery_state;
      } else {
        mainKey = item.delivery_district;
      }

      if (this.metrix == METRICS[0]) {
        acc[mainKey] = {
          'Total Orders': item.total_order
        }
        key = 'Total Orders';

        if (item.total_order > maxValue) {
          maxValue = item.total_order;
        }
      } else if (this.metrix == METRICS[1]) {
        acc[mainKey] = {
          'Sellers': item.total_sellers
        }
        key = 'Sellers';
        if (item.total_sellers > maxValue) {
          maxValue = item.total_sellers;
        }
      } else if (this.metrix == METRICS[2]) {
        key = this.mapVisualOptions.isDistrictMap || this.selectedState != 'TT' ?
          'Intradistrict Percentage' : 'Intrastate Percentage';
        acc[mainKey] =
          key == 'Intradistrict Percentage' ?
            { 'Intradistrict Percentage': item.intradistrict_orders } :
            { 'Intrastate Percentage': item.intrastate_orders }

        if (key == 'Intradistrict Percentage' && item.intradistrict_orders > maxValue) {
          maxValue = item.intradistrict_orders;
        } else if (key == 'Intrastate Percentage' && item.intrastate_orders > maxValue) {
          maxValue = item.intrastate_orders;
        }
      }

      return acc;
    }, {});

    this.legendConfigData = {
      ...this.legendConfigData,
      bubbleMaxData: maxValue,
      chloroMaxData: maxValue
    }

    this.configData = {
      ...this.configData,
      bubbleDataKey: key,
      chloroDataKey: key,
      maxChloroData: maxValue,
      maxBubbleData: maxValue
    }
  }

  // fetchMapStateData() {
  //   this.appService.getMapStateData().subscribe(
  //     (response: any) => {
  //       if (response) {
  //         this.mapStatewiseData = response.statewise;
  //       }
  //     }, (error: Error) => {
  //       console.log('Error is ', error);
  //     }
  //   )
  // }

  // fetchOrderMetricsSummary() {
  //   this.appService.getOrderMetricsSummary().subscribe(
  //     (response: any) => {
  //       if (response) {
  //         this.mapStateData = response;
  //         this.appService.setStateData(response);
  //       }
  //     }, (error: Error) => {
  //       console.log('Error is ', error);
  //     }
  //   )
  // }

  backToIndiaMap($event: any = null) {
    this.selectedState = 'TT';
    this.mapService.setSelectedState('TT');
  }

  handleMapChange(option: string) {
    const newOptions = JSON.parse(JSON.stringify(this.mapVisualOptions));
    if (option === 'chloropeth') {
      newOptions.isChloropeth = true;
      newOptions.isBubble = false;
    }
    if (option === 'bubble') {
      newOptions.isChloropeth = false;
      newOptions.isBubble = true;
    }

    if (option === 'state') {
      newOptions.isStateMap = true;
      newOptions.isDistrictMap = false;
    }

    if (option === 'district') {
      newOptions.isStateMap = false;
      newOptions.isDistrictMap = true;
    }
    this.mapVisualOptions = newOptions;
    // this.changeDetectionRef.detectChanges();
  }

  onStateChange(event: any) {
    this.mapService.selectedState.next(event.state);
  }

  updateViewSelection(option: any) {
    this.activeView = option.type;
  }

  updateStyleSelection(option: any) {
    this.activeStyle = option.type;
    this.prepareMapData();
  }
}
