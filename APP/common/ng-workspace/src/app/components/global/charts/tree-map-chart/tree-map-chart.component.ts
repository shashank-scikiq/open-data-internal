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
        borderRadius: 0, // Removes rounded corners
        enableShades: false,
      }
    },
    stroke: {
      show: false,
      // curve: "straight",
      lineCap: "butt",
      colors: ["#545454"],
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
    dataLabels: {
      enabled: true,
      style: {
        fontSize: '14px',   // Adjust font size
        fontWeight: 'light', // Set font weight to 'bold' or any other value like 'light', 'normal', etc.
        colors: ['#545454'] // Set the color of the font (e.g., #FF5733 for a reddish color)
      }
    }
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
    this.activeOptionIndex = this.options.indexOf(option);
    this.updateChartData();
  }

  async updateChartData() {
    this.isLoading = true;
    this.chartOptions.series = this.activeOptionIndex ? [this.series[this.activeOptionIndex-1]] : this.series;
    this.chartOptions['colors'] = this.activeOptionIndex ? [this.colors[this.activeOptionIndex-1]] : this.colors;
    await delay(1000);
    this.isLoading = false;
  }

}
