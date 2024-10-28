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
    colors: ["#9AB187", "#F3C881"],
    series: [
      {
        name: "New Sellers",
        data: [33.7, 23.5, 18.7, 19.8, 16.7]
      },
      {
        name: "Repeat sellers",
        data: [66.3, 76.5, 81.3, 80.2, 83.3]
      }
    ],
    chart: {
      type: "bar",
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
      categories: [
        "May-2024",
        "Jun-2024",
        "Jul-2024",
        "Aug-2024",
        "Sep-2024"
      ]
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
  };
  isLoadingData: boolean = true;


  ngOnChanges(changes: SimpleChanges): void {
    this.metaData = changes['metaData']['currentValue'];
    this.loadData();
  }

  async loadData() {
    this.isLoadingData = true;
    this.chartOptions.series = this.metaData.metaData.data.series;
    this.chartOptions.xaxis.categories = this.metaData.metaData.data.categories;
    this.chartOptions.colors = this.metaData.metaData.data.colors;
    console.log(this.metaData.metaData)

    await delay(1000);
    this.isLoadingData = false;
  }

}
