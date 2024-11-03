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
      type: 'area',
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
    await delay(1000);
    this.isLoading = false;
  }

}
