import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';
import { MapService } from '@openData/app/core/api/map/map.service';
import {
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexDataLabels,
  ApexTitleSubtitle,
  ApexStroke
} from 'ng-apexcharts';


export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  dataLabels: ApexDataLabels;
  stroke: ApexStroke;
  title: ApexTitleSubtitle;
};

@Component({
  selector: 'app-detail-charts-section',
  templateUrl: './detail-charts-section.component.html',
  styleUrl: './detail-charts-section.component.scss'
})
export class DetailChartsSectionComponent implements OnInit, OnChanges {
  @Input() metrix: any = 'map_total_orders_metrics';
  @Output() changeMatrix = new EventEmitter<any>();
  matrixUri: any = {
    map_total_orders_metrics: 'orders',
    map_total_zonal_commerce_metrics: 'hyperlocal',
    map_total_active_sellers_metrics: 'sellers'
  };
  dateRange: any = [];
  @Input() selectedState: string = 'TT';

  stateOrdersData: any = {};
  overallOrdersData: any = {};
  districtOrdersData: any = {};
  metrixMaxData: any = [];
  selectedCategory: string = '';
  selectedSubCategory: string = '';

  stateWiseBin: any;

  isLoadingOverall: boolean = false;
  isLoadingTopState: boolean = false;
  isLoadingTopDistrict: boolean = false;
  isLoadingMaxData: boolean = false;
  isLoadingStateWiseBin: boolean = false;

  activeUrl: any = '';

  cummulativeData: any = {
    map_total_orders_metrics: {
      subtitle: 'Confirmed Orders',
      tooltip: 'Sort the Total Orders  (distinct count of Network Order Id) by State, basis the date range and other filters selected. On a state map, it will display only that state orders within the time range'
    },
    map_total_active_sellers_metrics: {
      subtitle: 'Registered Sellers',
      tooltip: 'Sort the Total Orders  (distinct count of Network Order Id) by State, basis the date range and other filters selected. On a state map, it will display only that state orders within the time range',
    }
  }
  topStateData: any = {
    map_total_orders_metrics: {
      subtitle: 'with Highest Confirmed Orders',
      tooltip: 'Sort the Total Orders  (distinct count of Network Order Id) by State, basis the date range and other filters selected. On a state map, it will display only that state orders within the time range'
    },
    map_total_active_sellers_metrics: {
      subtitle: 'with Highest Number Of Registered Sellers',
      tooltip: 'Sort the Registered Sellers by State, basis the date range and other filters selected. On a state map, it will display only that state sellers within the time range'
    },
    map_total_zonal_commerce_metrics: {
      subtitle: 'with Highest Intra State Confirmed Orders',
      tooltip: 'Top 3 States with Highest Intra State Confirmed Orders'
    },
  }

  topDistrictData: any = {
    map_total_orders_metrics: {
      subtitle: 'with Highest Confirmed Orders',
      tooltip: 'Highest Confirmed Orders '
    },
    map_total_active_sellers_metrics: {
      subtitle: 'with Highest Number Of Registered Sellers',
      tooltip: 'Districts Highest Number Of Registered Sellers'
    },
    map_total_zonal_commerce_metrics: {
      subtitle: 'with Highest Intra District Confirmed Orders',
      tooltip: 'Top 3 Districts with Highest Intra State Confirmed Orders'
    }
  }

  sunburstData: any = {
    map_total_orders_metrics: {
      subtitle: 'with Highest Confirmed Orders',
      tooltip: 'Highest Confirmed Orders '
    },
    map_total_active_sellers_metrics: {
      subtitle: 'with Highest Number Of Registered Sellers',
      tooltip: 'Districts Highest Number Of Registered Sellers'
    }
  }

  metrixSunBurstChartData: any = {};
  isLoadingSunBurstChartData: boolean = false;

  constructor(
    private appService: AppService
  ) { }

  ngOnInit() {
    this.appService.currentUrl$.subscribe((val: any) => {
      this.activeUrl = val;
    })
    this.appService.dateRange$.subscribe((val: any) => {
      this.dateRange = val;
      this.initCardData();
      this.getSunBurstChartData();
    });

    this.appService.filterUpdated$.subscribe((val: any) => {
      if (val.updated) {
        this.initCardData();
        if (val.means == 'choosed') {
          this.getSunBurstChartData();
        }
      }
    })
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.dateRange.length) {
      this.initCardData();
      this.getSunBurstChartData();
    }
  }

  initCardData() {
    if (this.metrix != "map_total_zonal_commerce_metrics")
      this.getOverallOrdersData();
    // this.getMaxData();
    // this.getStatewiseBin();
    this.getTopStateOrdersData();
    this.getTopDistrictOrdersData();
    // this.getSunBurstChartData();
  }

  getStatewiseBin() {
    if (this.activeUrl.includes('retail/b2c') && this.metrix != 'map_total_zonal_commerce_metrics') {
      this.isLoadingStateWiseBin = true;
      this.appService.getStatewiseBin(this.matrixUri[this.metrix]).subscribe(
        (response: any) => {
          this.stateWiseBin = response;
          this.isLoadingStateWiseBin = false;
        }
      ), (error: Error) => {
        console.log(error);
        this.isLoadingStateWiseBin = false
      }
    }
  }

  getTopStateOrdersData() {
    this.isLoadingTopState = true;
    this.appService.getTopStateOrders(this.matrixUri[this.metrix], this.selectedState).subscribe(
      (response: any) => {
        this.stateOrdersData = response;
        this.isLoadingTopState = false;
      }, (error: Error) => {
        this.isLoadingTopState = false;
        console.log(error);
      }
    )
  }

  getOverallOrdersData() {
    this.isLoadingOverall = true;
    this.appService.getOverallOrders(this.matrixUri[this.metrix]).subscribe(
      (response: any) => {
        this.overallOrdersData = response;
        this.isLoadingOverall = false;
      }, (error: Error) => {
        this.isLoadingOverall = false;
        console.log(error);
      }
    )
  }

  getTopDistrictOrdersData() {
    this.isLoadingTopDistrict = true;
    this.appService.getTopDistrictOrders(this.matrixUri[this.metrix], this.selectedState).subscribe(
      (response: any) => {
        this.districtOrdersData = response;
        this.isLoadingTopDistrict = false;
      }, (error: Error) => {
        console.log(error);
        this.isLoadingTopDistrict = false;
      }
    )
  }

  changeMetrix(metrix: string) {
    if (this.metrix == metrix)
      return;
    this.metrix = metrix;

    this.changeMatrix.emit(metrix);
  }


  getMaxData() {
    if (this.metrix == "map_total_zonal_commerce_metrics" || !this.activeUrl.includes('retail/b2c')) {
      this.metrixMaxData = [];
      return;
    }

    this.isLoadingMaxData = true;
    this.appService.getMetrixMaxData(this.matrixUri[this.metrix], this.selectedState).subscribe(
      (response: any) => {
        if (response) {
          this.metrixMaxData = response;
          this.isLoadingMaxData = false;
        }
      }, (error: Error) => {
        console.log(error);
        this.isLoadingMaxData = false;
      }
    )
  }

  getSunBurstChartData() {
    if (this.metrix == "map_total_zonal_commerce_metrics" || !this.activeUrl.includes('retail/b2c')) {
      this.metrixSunBurstChartData = {};
      this.isLoadingSunBurstChartData = false;
      return;
    }

    this.isLoadingSunBurstChartData = true;
    this.appService.getMetrixSunBurstChartData(this.matrixUri[this.metrix], this.selectedState).subscribe(
      (response: any) => {
        if (response) {
          this.metrixSunBurstChartData = response;
          this.isLoadingSunBurstChartData = false;
        }
      }, (error: Error) => {
        console.log(error);
        this.isLoadingSunBurstChartData = false;
      }
    )
  }

  updateSelectedCategory(option: any) {
    if (option == this.appService.selectedCategory) {
      this.appService.setFilters('All', 'All')
    } else {
      this.appService.setFilters(option, 'All');
    }
    this.appService.setFilterUpdated({updated: true, means: 'click'});
  }
}
