import { Component, Input, OnInit } from '@angular/core';
import { delay } from 'rxjs';

@Component({
  selector: 'app-bar-chart',
  templateUrl: './bar-chart.component.html',
  styleUrl: './bar-chart.component.scss'
})
export class BarChartComponent implements OnInit {
  @Input() optional: boolean = false;
  @Input() data: any;

  chartOptions: any = {
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
  responsive: [{
    breakpoint: 480,
    options: {
      legend: {
        position: 'bottom',
        offsetX: -10,
        offsetY: 0
      }
    }
  }],
  plotOptions: {
    bar: {
      horizontal: true,
    },
  },
  xaxis: {
    categories: []
  },
  legend: {
    position: 'right',
    offsetY: 40
  },
  fill: {
    opacity: 1
  }
  };

  options:any = [];
  selectedOption: any;
  isLoading: boolean = true;

  ngOnInit(): void {
    console.log(this.optional, this.data)
    if(this.optional) {
      this.options = Object.keys(this.data);
      this.selectedOption = this.options[0];
    }
    
    this.updateChartData();
  }

  chooseOption(option: any) {
    console.log(option, "here")
    this.selectedOption = option;
    this.updateChartData();
  }

  async updateChartData() {
    this.isLoading = true;
    this.chartOptions.series = this.data[this.selectedOption].series;
    this.chartOptions.xaxis.categories = this.data[this.selectedOption].categories;
    this.chartOptions['colors'] = this.data[this.selectedOption].colors;
    await delay(1000);
    this.isLoading = false;
  }
}
