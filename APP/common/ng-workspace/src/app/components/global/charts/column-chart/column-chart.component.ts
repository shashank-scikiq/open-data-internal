import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-column-chart',
  templateUrl: './column-chart.component.html',
  styleUrl: './column-chart.component.scss'
})
export class ColumnChartComponent implements OnInit {
  chartOptions: any = {
    series: [
      {
        name: "Total sellers",
        data: [2345, 2445, 2545, 2355, 2605]
      },
      {
        name: "Active sellers %",
        data: [2232, 1232, 1532, 1732, 1432]
      }
      
    ],
    chart: {
      type: "bar",
      height: 280,
      // stacked: true,
      toolbar: {
        show: false
      },
      zoom: {
        enabled: false
      }
    },
    responsive: [
      {
        breakpoint: 480,
        options: {
          // legend: {
          //   position: "bottom",
          //   offsetX: -10,
          //   offsetY: 0
          // }
        }
      }
    ],
    plotOptions: {
      bar: {
        horizontal: false,
      }
    },
    dataLabels: {
      enabled: false  // Disable numbers on the bars
    },
    xaxis: {
      type: "category",
      categories: [
        "04/2024",
        "05/2024",
        "06/2024",
        "07/2024",
        "08/2024"
      ]
    },
    // yaxis: [
    //   {
    //     title: {
    //       text: "Total Sellers"
    //     }
    //   },
    //   {
    //     opposite: true,
    //     title: {
    //       text: "Active Sellers (%)"
    //     }
    //   }
    // ],
    yaxis: [
          {
            title: {
              text: "Total Sellers (Numbers)"
            },
            labels: {
              formatter: (value: any) => {
                return value.toFixed(0); // Display numbers without decimals
              }
            }
          },
          {
            opposite: true,  // Position on the right side
            title: {
              text: "Active Sellers (%)"
            },
            labels: {
              formatter:  (value: any) => {
                return value.toFixed(0) + "%"; // Display percentage
              }
            }
          }
        ],
    // legend: {
    //   position: "top",
    //   offsetY: 40
    // },
    fill: {
      opacity: 1
    },
    tooltip: {
      show: true,
      // y: {
      //   formatter: (val: any) => {
      //     console.log(val)
      //   },
      //   title: {
      //     formatter: (seriesName: any) => seriesName,
      //   },
      // },
    }
  };

  ngOnInit(): void { }

}
