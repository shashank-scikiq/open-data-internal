import { Component, OnInit } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';
import { MapService } from '@openData/app/core/api/map/map.service';
import { StateCode } from '@openData/core/utils/map';

@Component({
  selector: 'app-detail-header-card',
  templateUrl: './detail-header-card.component.html',
  styleUrl: './detail-header-card.component.scss'
})
export class DetailHeaderCardComponent implements OnInit {
  upperCardData: any = [];
  isLoading: boolean = false;
  selectedStateCode: string = 'TT';
  topCardsDelta: any = {};
  prevDateRange: string = '';

  constructor(
    private appService: AppService,
    private mapService: MapService,
  ) { }

  ngOnInit(): void {
    this.appService.dateRange$.subscribe(() => {
      this.getCardData();
    });
    this.mapService.selectedState$.subscribe((val: string) => {
      this.selectedStateCode = val == 'TT' ? val : StateCode[val];
      if (this.topCardsDelta)
        this.updateTopCardsDelta();
    })
  }

  formatNumber(num: number) {
    var num_parts = num.toString().split(".");
    num_parts[0] = num_parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return num_parts.join(".");
  }


  getCardData() {
    this.isLoading = true;
    this.appService.getSummaryCardData().subscribe(
      (response: any) => {
        if (Object.keys(response.top_card_data).length) {
          this.topCardsDelta = response.top_card_data;
          this.prevDateRange = response.prev_date_range;
          this.updateTopCardsDelta();
        }

      }, (error: Error) => {
        console.log(error);
        this.isLoading = false;
      }
    )
  }

  updateTopCardsDelta() {
    if (Object.keys(this.topCardsDelta).length) {
      // this.upperCardData = [
      //   {
      //     type: 'default',
      //     count: this.formatNumber(this.topCardsDelta[this.selectedStateCode].total_confirmed_orders),
      //     heading: 'Total Orders',
      //     tooltipText: 'Count of Distinct Network Order Id within the selected range. For Filters, The Total Orders  are within that category/sub_category',
      //     icon: 'trending_down', // trending_up
      //     positive: Boolean(parseFloat(this.topCardsDelta[this.selectedStateCode].cnf_delta) >= 0),
      //     percentageCount: this.topCardsDelta[this.selectedStateCode].cnf_delta,
      //   },
      //   // {
      //   //   count: 220,
      //   //   heading: 'Avg. Items Per Order',
      //   //   tooltipText: 'Total Number of Items ordered / Total Unique Orders',
      //   //   icon: 'trending_down', // trending_up
      //   //   percentageCount: '12',
      //   //   positive: true,
  
      //   // },
      //   {
      //     type: 'default',
      //     count: this.formatNumber(this.topCardsDelta[this.selectedStateCode].total_districts),
      //     heading: 'Total active districts',
      //     tooltipText: 'Unique count of Districts where order has been delivered within the date range. Districts are fetched using districts mapping using End pincode',
      //     icon: 'trending_down', // trending_up
      //     positive: Boolean(parseFloat(this.topCardsDelta[this.selectedStateCode].district_delta) >= 0),
      //     percentageCount: this.topCardsDelta[this.selectedStateCode].district_delta,
      //   },
      //   {
      //     type: 'default',
      //     count: this.formatNumber(this.topCardsDelta[this.selectedStateCode].total_active_sellers),
      //     heading: 'Total registered sellers',
      //     tooltipText: 'Unique count of combination of (Provider ID + Seller App) where order has been delivered within the date range',
      //     icon: 'trending_up', // trending_up
      //     positive: Boolean(parseFloat(this.topCardsDelta[this.selectedStateCode].sellers_delta) >= 0),
      //     percentageCount: this.topCardsDelta[this.selectedStateCode].sellers_delta,
      //   },
      //   {
      //     type: 'max_state',
      //     heading: 'Maximum number of orders delivered to',
      //     tooltipText: `Sort the Total Orders  by State/Districts, basis the date range and other filters selected. 
      //       It will show top districts within a state if a state map is selected. Districts are mapped using delivery pincode.`,
      //     mainText: this.topCardsDelta[this.selectedStateCode].max_orders_delivered_area
      //   }
      // ];
      this.upperCardData = this.topCardsDelta[this.selectedStateCode];
      this.isLoading = false;
    }

  }
}
