import { ChangeDetectorRef, Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { MapService } from '@openData/app/core/api/map/map.service';
import { AppService } from '@openData/core/api/app/app.service';
import { METRICS, MetrixType } from '@openData/core/utils/global';
import {MapStatewiseData} from '@openData/core/utils/map';

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

  mapVisualOptions: any = {
    isStateMap: true,
    isDistrictMap: false,
    isChloropeth: true,
    isBubble: false,
  }

  constructor(
    private appService: AppService,
    private mapService: MapService,
    private changeDetectionRef: ChangeDetectorRef
  ) { }

  ngOnInit(): void {
    this.appService.dateRange$.subscribe(() => {
      this.mapStateData = null;
      this.mapStatewiseData = null;
      this.fetchMapStateData();
      this.fetchOrderMetricsSummary();
    });
    this.mapService.selectedState$.subscribe((state: string) => {
      if (state != this.selectedState)
      this.selectedState = state;
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if(changes['metrix'] && changes['metrix'].currentValue == "map_total_active_sellers_metrics") {
      this.mapService.setSelectedState('TT');
      this.mapVisualOptions.isStateMap = true;
      this.mapVisualOptions.isDistrictMap = false;
    }
  }

  fetchMapStateData() {
    this.appService.getMapStateData().subscribe(
      (response: any) => {
        if (response) {
          this.mapStatewiseData = response.statewise;
        }
      }, (error: Error) => {
        console.log('Error is ', error);
      }
    )
  }

  fetchOrderMetricsSummary() {
    this.appService.getOrderMetricsSummary().subscribe(
      (response: any) => {
        if (response) {
          this.mapStateData = response;
          this.appService.setStateData(response);
        }
      }, (error: Error) => {
        console.log('Error is ', error);
      }
    )
  }

  backToIndiaMap() {
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
}
