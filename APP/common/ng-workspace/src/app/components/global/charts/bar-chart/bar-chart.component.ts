import { Component, Input, OnInit } from '@angular/core';
import { delay } from 'rxjs';

@Component({
  selector: 'app-bar-chart',
  templateUrl: './bar-chart.component.html',
  styleUrl: './bar-chart.component.scss'
})
export class BarChartComponent implements OnInit {
  @Input() optional: boolean = false;
  @Input() colors: any = [];
  @Input() data: any;
  @Input() fullStackType: boolean = false;
  @Input() showLegends: boolean = true;

  chartOptions: any = {
    legend: {
      show: true,
    },
    grid: {
      yaxis: {
        lines: {
          show: false // Removes horizontal grid lines
        }
      }
    },
    dataLabels: {
      enabled: false // Disable data labels
    },
    series: [],
    chart: {
      type: 'bar',
      height: 350,
      stacked: true,
      toolbar: {
        show: false
      },
      zoom: {
        enabled: true
      }
    },
    plotOptions: {
      bar: {
        horizontal: true,
      },
    },
    xaxis: {
      categories: []
    },
    fill: {
      opacity: 1
    }
  };

  options: any = [];
  selectedOption: any;
  isLoading: boolean = true;

  ngOnInit(): void {
    console.log(this.optional, this.data)
    if (this.optional) {
      this.options = Object.keys(this.data);
      this.selectedOption = this.options[0];
    }

    this.updateChartData();
  }

  chooseOption(option: any) {
    this.selectedOption = option;
    this.updateChartData();
  }

  async updateChartData() {
    this.isLoading = true;
    this.chartOptions.series = this.data[this.selectedOption].series;
    this.chartOptions.xaxis.categories = this.data[this.selectedOption].categories;
    this.chartOptions['colors'] = this.colors;
    this.chartOptions.legend.show = this.showLegends;
    if (this.fullStackType) {
      // this.chartOptions.chart.stackType = '100%';
      this.chartOptions.xaxis.labels = {
        formatter: (value: number) => this.fullStackType ? `${value}%` : `${value}` // Adds '%' to only the last label
      }
      this.chartOptions.tooltip ={
        y: {
          formatter: (value: any) => {console.log(value); return `${value}%`} // Adds '%' to the tooltip value
        }
      }
    }
    await delay(1000);
    this.isLoading = false;
  }
}
