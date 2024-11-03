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
  @Input() showLegend: boolean = true;

  chartOptions: any = {
    colors: [],
    chart: {
      type: "donut"
    },
    legend: {
      show: false // Hide the legend
    },
    labels: [],
    dataLabels: {
      enabled: true
    },
    series: [44, 55]
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
    await delay(2000);
    this.isLoading = false;
  }
}
