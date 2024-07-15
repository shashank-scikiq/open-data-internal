import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';
import { delay } from 'rxjs';

@Component({
  selector: 'app-line-chart',
  templateUrl: './line-chart.component.html',
  styleUrl: './line-chart.component.scss'
})
export class LineChartComponent implements OnChanges, OnInit {
  metrix: string = '';
  @Input() chartType: string = 'multi';
  @Input() options: any;
  @Input() isLoading: boolean = false;

  chartOptions: any = {
    series: [],
    legend: {
      show: true,
    },
    chart: {
      type: 'area',
      height: 180,
      stacked: false,
      toolbar: {
        show: false,
        tools: {
          download: false,
          selection: false,
          zoom: true,
          zoomin: true,
          zoomout: true,
          pan: false,
          reset: true
        }
      },
      zoom: {
        enabled: false,
      }
    },
    xaxis: {
      categories: [],
      labels: {
        show: false,
        offsetX: 10
      }
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      show: true,
      curve: 'smooth',
      width: [3, 3, 3, 0],
    },
    fill: {
      type: "gradient",
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.1,
        opacityTo: 0.9,
        stops: [0, 90, 100]
      }
    },
    noData: {
      text: 'No Data to Display'
    },
    yaxis: [
        {
            tickAmount: 5,
            min: 0,
            labels: {
                show: true,
                minWidth: 0,
                maxWidth: 'auto',
                // offsetX: -15,
                offsetY: 0,
                rotate: 0,
                padding: 20,
                style: {
                    colors: [
                        null,
                        null,
                        null,
                        null,
                        null,
                        null
                    ],
                    fontSize: '11px',
                    fontWeight: 400,
                    cssClass: ''
                }
            },
            axisBorder: {
                show: false,
                color: '#e0e0e0',
                width: 1,
                offsetX: 0,
                offsetY: 0
            },
            axisTicks: {
                show: false,
                color: '#e0e0e0',
                width: 6,
                offsetX: 0,
                offsetY: 0
            },
            title: {
                rotate: -90,
                offsetY: 0,
                offsetX: 0,
                style: {
                    fontSize: '11px',
                    fontWeight: 900,
                    cssClass: ''
                }
            },
            tooltip: {
                enabled: false,
                offsetX: 0
            },
            crosshairs: {
                show: true,
                position: 'front',
                stroke: {
                    color: '#b6b6b6',
                    width: 1,
                    dashArray: 0
                }
            }
        }
    ],
  };

  constructor(private appService: AppService) {}

  ngOnInit(): void {
    this.appService.selectedMetrix$.subscribe((value) => {
      this.metrix = value;
    })
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['options'] && changes['options'].currentValue != changes['options'].previousValue) {
      this.updateOptions();
    }
  }

  roundUpToNearestPattern(number: any) {
    if (number === 0) return 0;

    const length = number.toString().length;
    const factor = this.metrix == "map_total_zonal_commerce_metrics" ? Math.pow(10, length - 1) : Math.pow(10, length - 2);

    // Divide the number by the factor, round it up, then multiply back by the factor
    const rounded = Math.ceil(number / factor) * factor;

    return rounded;
}

  async updateOptions() {
    this.chartOptions.series = this.options.series;
    if (this.chartOptions.series?.length) {
      const max = Math.max(...this.chartOptions.series?.flatMap((item: any) => item.data));
      this.chartOptions['yaxis'][0]['max'] = await this.roundUpToNearestPattern(max);
    }
    this.chartOptions['colors'] = this.chartType == 'cumulative' ? ["#00b8d4"] : ['#FF7722', '#26a0fc', '#32cd32'];
    this.chartOptions['markers'] =  this.chartType == 'cumulative' ? { size: 3, strokeWidth: 2 } : {};
    this.chartOptions['tooltip'] = {
      show: true,
      y: {
        formatter: (val: any) => {
          if (this.metrix == "map_total_zonal_commerce_metrics") {
            return val ? `${val}%` : '0%';
          }
          return val ? val : 0;
        },
        title: {
          formatter: (seriesName: any) => seriesName,
        },
      },
    },
    this.chartOptions.xaxis.categories = this.options.categories;
    await delay(100);
  }
}
