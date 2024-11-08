import { Component, Input, OnInit } from '@angular/core';
import { delay } from 'rxjs';

@Component({
  selector: 'app-donut-chart',
  templateUrl: './donut-chart.component.html',
  styleUrl: './donut-chart.component.scss'
})
export class DonutChartComponent implements OnInit {
  @Input() width: any = 380;
  @Input() series = [];
  @Input() labels = [];
  @Input() colors = [];
  @Input() size: any = '60%';
  @Input() showLegend: boolean = true;
  @Input() labelsColor = [];

  chartOptions: any = {
    tooltip: {
      y: {
        formatter: (value: any) => `${value}%` // Adds '%' to the tooltip value
      }
    },
    states: {
      hover: {
        filter: {
          type: 'none' // Remove any filter effects on hover
        },
        opacity: 0.8 // Set opacity level for hover (1 is fully opaque)
      }
    },
    stroke: {
      show: false
    },
    colors: [],
    chart: {
      type: "donut"
    },
    legend: {
      show: false // Hide the legend
    },
    labels: [],
    dataLabels: {
      enabled: true,
      formatter: (val: number) => `${Math.round(val)}%`,
      style: {
        colors: ['#FF4560', '#00E396', '#008FFB', '#FEB019', '#775DD0'], // Colors for each label
        fontWeight: 'normal',
      },
      dropShadow: {
        enabled: false,
      }
    },
    series: [],
    plotOptions: {
      pie: {
        donut: {
          size: '60%'
        }
      }
    }
  };
  isLoading: boolean = true;

  ngOnInit(): void {
    this.updateChart();
  }
  
  async updateChart() {
    this.isLoading = true;
    this.chartOptions.series = this.series;
    this.chartOptions.labels = this.labels;
    this.chartOptions.chart.width = this.width;
    this.chartOptions.legend.show = this.showLegend;
    this.chartOptions.colors = this.colors;
    this.chartOptions.dataLabels.style.colors = this.labelsColor;
    this.chartOptions.plotOptions.pie.donut.size = this.size;
    await delay(2000);
    this.isLoading = false;
  }
}
