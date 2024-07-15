import { Component, Input, OnInit } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-summary',
  templateUrl: './summary.component.html',
  styleUrl: './summary.component.scss'
})
export class SummaryComponent implements OnInit{
  @Input() pageTitle: string = 'Retail';
  dateRange: any = [];

  metrics : any = [
    {
      title: "map_total_orders_metrics",
      disabled: false
    },
    {
      title: "map_total_active_sellers_metrics",
      disabled: false
    },
    {
      title: "map_total_zonal_commerce_metrics",
      disabled: false
    },
  ];

  activeMetric: any = '';
  availableDateRange: any = null;


  constructor(private appService: AppService) {}


  ngOnInit() {
    this.appService.dateRange$.subscribe((value) => {
      this.dateRange = value;
    })
    this.activeMetric= this.metrics[0].title;
   }

  handleClick(clickedMetric: any) {
    if (clickedMetric.disabled)
      return;
    
    this.activeMetric = clickedMetric.title;
  }

  setDateRange(value: any) {
    this.appService.setDateRange(value);
  }

  setMetrix(value: any) {
    this.activeMetric = value;
  }
}
