import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { delay } from 'rxjs';

@Component({
  selector: 'app-radial-bar-chart',
  templateUrl: './radial-bar-chart.component.html',
  styleUrl: './radial-bar-chart.component.scss'
})
export class RadialBarChartComponent implements OnChanges {
  @Input() data: any;

  isLoading: boolean = true;

  chartOptions: any = {
    series: [],
    chart: {
      height: 150,
      type: 'radialBar',
      toolbar: {
        show: false
      }
    },
    plotOptions: {
      radialBar: {
        startAngle: -135,
        endAngle: 225,
        hollow: {
          margin: 0,
          size: '60%',
          background: '#fff',
          position: 'front',
        },
        track: {
          background: '#e5e9f2',
          strokeWidth: '100px',
          margin: 0,
        },
        dataLabels: {
          show: true,
          name: {
            offsetY: 17,
            show: true,
            color: '#8392a5',
            fontSize: '11px'
          },
          value: {
            color: '#001737',
            fontSize: '26px',
            show: true,
            offsetY: -15,
            formatter: () =>{}
          }
        }
      }
    },
    fill: {
      type: 'gradient',
      gradient: {
        shade: 'dark',
        type: 'horizontal',
        shadeIntensity: 0.5,
        gradientToColors: ['#ABE5A1'],
        inverseColors: true,
        opacityFrom: 1,
        opacityTo: 1,
        stops: [0, 100]
      }
    },
    stroke: {
      lineCap: 'round'
    },
    labels: ['STATES'],
    tooltip: {
      enabled: true,
    },
  };

  ngOnChanges(changes: SimpleChanges): void {
    // if (changes['data'] && changes['data'].currentValue != changes['data'].previousValue) {
      this.isLoading = true;
      this.data = this.data ? this.data : [];
      this.updateChartData();
      // console.log(this.data)
    // }
  }

  async updateChartData() {
    this.chartOptions.series = [(this.data.length / 36) * 100];
    this.chartOptions.plotOptions.radialBar.dataLabels.value['formatter'] =  () => {
      return parseInt(this.data.length);
    }

    this.chartOptions.tooltip['custom'] =  () => {
      const text = this.data.join(',')
      return `<div class="radial-bar-tooltip-container">
        <div class="header">State: ${this.data.length}</div>
        <div class="content-body">${text}</div>
        </div>`;
    };
    await delay(100);
    this.isLoading = false;
  }

}
