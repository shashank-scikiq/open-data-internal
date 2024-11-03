import { Component, Input, OnInit } from '@angular/core';
import { delay } from 'rxjs';

@Component({
  selector: 'app-tree-map-chart',
  templateUrl: './tree-map-chart.component.html',
  styleUrl: './tree-map-chart.component.scss'
})
export class TreeMapChartComponent implements OnInit {
  @Input() series: any = [];
  @Input() colors: any = [];
  
  chartOptions:any = {
    tooltip: {
      y: {
        formatter: (value: any) => `${value}%` // Adds '%' to the tooltip value
      }
    },
    states: {
      hover: {
        filter: {
          type: 'none' // Prevents background color change on hover
        }
      }
    },
    plotOptions: {
      treemap: {
        borderRadius: 0 // Removes rounded corners
      }
    },
    stroke: {
      show: false,
      // curve: "straight",
      lineCap: "butt",
      colors: ["#676565"],
      width: 0.1,
      dashArray: 0,
    },
    series: [],
    colors: [],

    legend: {
      show: false,
    },
    chart: {
      height: 540,
      foreColor: "#f4f4f4",
      type: "treemap",
      animations: {
        enabled: true,
        easing: "linear",
        speed: 800,
        animateGradually: {
          enabled: true,
          delay: 150,
        },
        dynamicAnimation: {
          enabled: true,
          speed: 350,
        },
      },
      toolbar: {
        show: false,
      }
    },
    title: {
      text: "Multi-dimensional Treemap",
      align: "center",
    },
  };
  options: any = ['All'];
  selectedOption: any = 'All';
  activeOptionIndex: any = 0;
  isLoading: boolean = true;

  ngOnInit(): void {
    this.updateChartData();
    this.options = ['All', ...this.series.map((item: any) => item?.name)];
  }

  chooseOption(option: any) {
    console.log(option, "here")
    this.activeOptionIndex = this.options.indexOf(option);
    this.updateChartData();
  }

  async updateChartData() {
    this.isLoading = true;
    this.chartOptions.series = this.activeOptionIndex ? [this.series[this.activeOptionIndex-1]] : this.series;
    this.chartOptions['colors'] = this.activeOptionIndex ? [this.colors[this.activeOptionIndex-1]] : this.colors;
    console.log(this.chartOptions.colors, this.chartOptions.series)
    await delay(1000);
    this.isLoading = false;
  }

}
