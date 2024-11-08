import { Component, Input, OnInit } from '@angular/core';
import { delay } from 'rxjs';

@Component({
  selector: 'app-area-chart',
  templateUrl: './area-chart.component.html',
  styleUrl: './area-chart.component.scss'
})
export class AreaChartComponent implements OnInit {
  @Input() series: any = [];
  @Input() colors: any = [];
  @Input() categories: any = [];
  @Input() height: any = 350;
  @Input() yAxisSuffix: string = '';

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
    yaxis: {
      labels: {

      }
    },
    chart: {
      type: 'area',
      stacked: true,
      stackType: "100%",
      toolbar: {
        show: false,
      },
      zoom: {
        enabled: false,
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

  isLoading: boolean = true;

  ngOnInit(): void {
    this.updateChartData();
  }

  async updateChartData() {
    this.isLoading = true;
    this.chartOptions.series = this.series;
    this.chartOptions.xaxis.categories = this.categories;
    this.chartOptions.chart.height = this.height;
    this.chartOptions['colors'] = this.colors;
    if(this.yAxisSuffix) {
      this.chartOptions.yaxis.labels = {
        formatter: (value: any) => `${value}${this.yAxisSuffix}`
      }
    }
    await delay(1000);
    this.isLoading = false;
  }

}
