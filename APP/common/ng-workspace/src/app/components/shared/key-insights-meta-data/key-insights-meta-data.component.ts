import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { delay } from 'rxjs';

@Component({
  selector: 'app-key-insights-meta-data',

  templateUrl: './key-insights-meta-data.component.html',
  styleUrl: './key-insights-meta-data.component.scss'
})
export class KeyInsightsMetaDataComponent implements OnChanges {
  @Input() metaData: any;

  chartOptions: any = {
    colors: [],
    series: [],
    grid: {
      yaxis: {
        lines: {
          show: false // Removes horizontal grid lines
        }
      }
    },
    chart: {
      height: 350,
      stacked: true,
      stackType: "100%",
      toolbar: {
        show: false,
      }
    },
    responsive: [
      {
        breakpoint: 480,
        options: {
          legend: {
            position: "bottom",
            offsetX: -10,
            offsetY: 0
          }
        }
      }
    ],
    xaxis: {
      categories: []
    },
    fill: {
      opacity: 1
    },
    legend: {
      position: "top",
      horizontalAlign: "left",
      offsetX: 40
    },
    noData: {
      text: 'No Data to Display'
    },
    dataLabels: {
      enabled: false
    },
    markers: {
      size: 5,
      hover: {
        size: 9
      }
    },
  };
  isLoadingData: boolean = true;
  object=Object;


  ngOnChanges(changes: SimpleChanges): void {
    this.metaData = changes['metaData']['currentValue'];
    this.loadData();
  }

  async loadData() {
    this.isLoadingData = true;
    this.chartOptions.chart.type = this.metaData.metaData.type;
    this.chartOptions.series = this.metaData.metaData.data.series;
    this.chartOptions.xaxis.categories = this.metaData.metaData.data.categories;
    this.chartOptions.colors = this.metaData.metaData.data.colors;

    await delay(2000);
    this.isLoadingData = false;
  }

}
