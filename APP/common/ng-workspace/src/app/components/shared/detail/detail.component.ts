import { Component, Input, OnInit } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';
import { DownloadDialogComponent } from '../../global/dialogs/download-dialog/download-dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { MapService } from '@openData/app/core/api/map/map.service';
import { ConfigService } from '@openData/app/core/api/config/config.service';

@Component({
  selector: 'app-detail',
  templateUrl: './detail.component.html',
  styleUrl: './detail.component.scss'
})
export class DetailComponent implements OnInit {
  @Input() pageTitle: string = '';
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
  selectedState: string = 'TT';
  isStagingEnabled: any = '';


  constructor(
    private appService: AppService,
    public dialog: MatDialog,
    private mapService: MapService,
    private configService: ConfigService
  ) {}


  ngOnInit() {
    this.isStagingEnabled = this.configService.get('ENABLE_STAGING_ROUTE');
    this.appService.dateRange$.subscribe((value) => {
      this.dateRange = value;
    })
    this.activeMetric= this.metrics[0].title;
    this.mapService.selectedState$.subscribe((val: any) => {
      this.selectedState = val;
    });
   }

  handleClick(clickedMetric: any) {
    if (clickedMetric.disabled)
      return;
    
    this.setMetrix(clickedMetric.title)
  }

  setDateRange(value: any) {
    this.appService.setDateRange(value);
  }

  setMetrix(value: any) {
    this.activeMetric = value;
    this.appService.setMetrix(value);
  }

  openDownloadDialog(): void {
    const dialogRef = this.dialog.open(DownloadDialogComponent, {
      data: {}
    });
    dialogRef.afterClosed().subscribe(
      (response) => {
        this.appService.setIsDownloadDataDialogOpen(false);
      }
    )
  }
}
