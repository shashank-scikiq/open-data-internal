import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DetailComponent } from './detail/detail.component';
import { ZorroModule } from '@openData/app/zorro/zorro.module';
import { MaterialModule } from '@openData/app/material/material.module';
import { MonthRangePickerComponent } from '../global/forms/month-range-picker/month-range-picker.component';
import { DetailHeaderCardComponent } from './detail-header-card/detail-header-card.component';
import { MapComponent } from '../summary/map/map.component';
import { StateMapComponent } from '../summary/state-map/state-map.component';
import { DetailChartsSectionComponent } from './detail-charts-section/detail-charts-section.component';
import { LineChartComponent } from '../global/charts/line-chart/line-chart.component';
import { NgApexchartsModule } from 'ng-apexcharts';
import { FormsModule } from '@angular/forms';
import { IndiaMapComponent } from '../summary/india-map/india-map.component';
import { DateRangePickerComponent } from '../global/forms/date-range-picker/date-range-picker.component';
import { DownloadDialogComponent } from '../global/dialogs/download-dialog/download-dialog.component';
import { TreeChartComponent } from '../global/charts/tree-chart/tree-chart.component';
import { RadialBarChartComponent } from '../global/charts/radial-bar-chart/radial-bar-chart.component';
import { SunburstChartComponent } from '../global/charts/sunburst-chart/sunburst-chart.component';
import { DetailCategoryFilterComponent } from './detail-category-filter/detail-category-filter.component';
import { KeyInsightsComponent } from './key-insights/key-insights.component';
import { ColumnChartComponent } from '../global/charts/column-chart/column-chart.component';
import { RouterModule } from '@angular/router';
import { BarChartComponent } from '../global/charts/bar-chart/bar-chart.component';
import { PincodeLevelMapViewComponent } from './pincode-level-map-view/pincode-level-map-view.component';
// import { PlotlyModule } from 'angular-plotly.js';

@NgModule({
  declarations: [
    DetailComponent,
    MonthRangePickerComponent,
    DateRangePickerComponent,
    DetailHeaderCardComponent,
    MapComponent,
    StateMapComponent,
    IndiaMapComponent,
    DetailChartsSectionComponent,
    LineChartComponent,
    ColumnChartComponent,
    TreeChartComponent,
    DownloadDialogComponent,
    RadialBarChartComponent,
    SunburstChartComponent,
    DetailCategoryFilterComponent,
    KeyInsightsComponent,
    BarChartComponent,
    PincodeLevelMapViewComponent
  ],
  imports: [
    CommonModule,
    ZorroModule,
    MaterialModule,
    NgApexchartsModule,
    FormsModule,
    // PlotlyModule
    RouterModule
  ],
  exports: [
    DetailComponent,
    MonthRangePickerComponent,
    DateRangePickerComponent,
    DetailHeaderCardComponent,
    MapComponent,
    StateMapComponent,
    DetailChartsSectionComponent,
    LineChartComponent,
    ColumnChartComponent,
    TreeChartComponent,
    IndiaMapComponent,
    DownloadDialogComponent,
    RadialBarChartComponent,
    SunburstChartComponent,
    DetailCategoryFilterComponent,
    BarChartComponent, 
    PincodeLevelMapViewComponent
  ]
})
export class SharedModule { }
