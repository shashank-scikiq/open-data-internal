// import { Component, OnInit } from '@angular/core';

// @Component({
//   selector: 'app-landing-page-chart',
//   templateUrl: './landing-page-chart.component.html',
//   styleUrl: './landing-page-chart.component.scss'
// })
// export class LandingPageChartComponent implements OnInit {
//   options1: any;

//   isLoading: boolean = false;

//   ngOnInit() {
//     this.isLoading = true;
//     this.loadChartData();
//   }


//   async loadChartData() {
//     let data = await fetch('static/assets/data/landing-page/chart.json');
//     this.options1 = await data.json();
//     this.isLoading = false;
//   }
// }


import { Component, HostListener, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { color, interval } from 'd3';

declare var echarts: any;

@Component({
  selector: 'app-landing-page-chart',
  templateUrl: './landing-page-chart.component.html',
  styleUrl: './landing-page-chart.component.scss'
})
export class LandingPageChartComponent implements OnInit {
  domainConfig: any;
  private data: any;
  lastUpdatedAt: any;
  chartTitle: string = '';
  selectedFilterValue: string = 'Start Date';
  options: string[] = ['Last 6 Months', 'Last 9 Months', 'Last 12 Months', 'Start Date'];

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.http.get(`static/assets/data/landing-page/echart.json`).subscribe((_rawData: any) => {
      this.domainConfig = _rawData.domainConfig;
      this.data = _rawData.data;
      this.chartTitle = _rawData.chartTitle;
      this.lastUpdatedAt = _rawData.lastUpdatedAt;
      this.run();
    });
  }

  updateSelection(option: any) {
    this.selectedFilterValue = option;
    this.run();
  }

  getLineColour(value: any) {
    return {
      color: this.domainConfig.colorDark[this.domainConfig.domains.indexOf(value)],
      width: 3
    }

  }

  @HostListener('window:resize', ['$event'])
  onResize() {
    this.run();
  }

  run() {
    let seriesList: any = [];
    let option: any = {};
    const chartDom = document.getElementById('main')!;
    const myChart = echarts.init(chartDom);
    try {
      //to add new lines add new elements 
      const domains = this.domainConfig?.domains;

      const _rawData = this.data.map((element: any, index: number) => {
        if (index > 0) {
          element[2] = new Date(element[2])
          element[3] = parseInt(element[3])
        }
        if (this.selectedFilterValue == 'Start Date') {
          return element;
        }
        let dateFilter;
        if (this.selectedFilterValue == 'Last 6 Months') {
          dateFilter = Date.now() - (7 * 30 * 24 * 60 * 60 * 1000);
        } else if(this.selectedFilterValue == 'Last 9 Months') {
          dateFilter = Date.now() - (10 * 30 * 24 * 60 * 60 * 1000);
        } else if(this.selectedFilterValue == 'Last 12 Months') {
          dateFilter = Date.now() - (13 * 30 * 24 * 60 * 60 * 1000);
        }

        if (dateFilter && element[2] > dateFilter || index == 0) {
          return element
        }
      })


      const datasetWithFilters: any = [];
      // const seriesList: any = [];
      echarts.util.each(domains, (domain: string) => {
        var datasetId = 'dataset_' + domain;
        datasetWithFilters.push({
          id: datasetId,
          fromDatasetId: 'dataset_raw',
          transform: {
            type: 'filter',
            config: {
              and: [
                //{ dimension: 'weekly_average',gte: 20000}
                //,
                {
                  dimension: 'domain', '=': domain
                }
              ]
            }
          }
        });
        seriesList.push({
          type: 'line',
          datasetId: datasetId,
          showSymbol: false,
          name: domain,
          symbol: 'circle',  // Use 'circle' as the symbol for data points
          lineStyle: this.getLineColour(domain),
          // symbolSize:  (value: any, index: any) {
          //   if (index.dataIndex % 10 == 0) {
          //     return 8
          //   }
          // }
          // ,
          endLabel: {
            show: false,
            fontSize: 10,
            position: 'left'
            , formatter: function (params: any) {
              return params.value[1] + ' : ' + params.value[3].toLocaleString();
            },
            // fontSize: 10, // Set the font size
            fontWeight: 'bold'
          },
          labelLayout: {
            moveOverlap: 'shiftY',
          },
          emphasis: {
            focus: 'series'
          },
          encode: {
            x: 'date',
            y: 'weekly_average',
            label: ['domain', 'weekly_average'],
            itemName: 'date',
            tooltip: ['weekly_average']
          }
        });
      });
      option = {
        // backgroundColor: '#cfcfcf', // Set the background color here
        animationDuration: 5000,
        dataset: [
          {
            id: 'dataset_raw',
            source: _rawData,
          },
          ...datasetWithFilters
        ],
        title: {
          text: '',
          left: 'left', // Align the title to the center
          right: 'center',
          textStyle: {
            fontSize: '16px'
          }
        },
        tooltip: { // data on hover
          order: 'valueDesc',
          trigger: 'axis',
          formatter: function (params: any) {

              let output = '<div class="custom-toottip" style="background-color: white; padding: 10px; color:black">';

              // Extracting the date from the first parameter (assuming all parameters have the same date)
              let date = new Date(params[0].value[2]);
              let monthYear = date.toLocaleString('en-US', { month: 'long', year: 'numeric' });

              // Displaying the formatted date
              output += '<div style="font-weight: bold;color:white; background-color: #1C75BC;  padding: 10px 0 10px 10px; margin: -10px -10px 5px -10px;">' + monthYear + '</div>';

              // Adding data for each series
              params.forEach(function (param: any) {
                output += param.marker + ' ' + param.seriesName + ': <b>' + parseInt(param.value[3]).toLocaleString() + '</b><br>';
              });

              output += '</div>';
              return output;
          },



          padding: 0,
          // Tooltip movement 
          position: function (point: any, params: any, dom: any, rect: any, size: any) {
            // Only apply adjustment for screen widths greater than 768px
            if (size.viewSize[0] < 768) {
              // Horizontal position calculation
              var x = point[0];
              if (x > size.viewSize[0] - 200) {
                // If tooltip is close to the right edge, move it to the left of the chart
                x -= size.contentSize[0] + 5;
              }
            } else {
              // For screen widths greater than or equal to 768px, no adjustment needed
              var x = point[0];
            }
            // Vertical position remains the same
            var y = point[1];
            return [x, y];
          }

        },
        xAxis: {
          type: 'time',
          nameLocation: 'middle',
          boundaryGap: false, // To display the first Month value (boolean will not work for time so use %)
          // splitLine: {
          //   show: true,  // Show both horizontal and vertical grid lines
          // },
          axisLabel: {
            interval: 0,
            color: '#19486D',
            fontWeight: 'bold',
            showMaxLabel: true,
            formatter: function (value: any) {
              // Custom formatting logic for axis labels to show only the mm-yyyy part
              let monthNames = ["Jan'", "Feb'", "Mar'", "Apr'", "May'", "Jun'", "Jul'", "Aug'", "Sep'", "Oct'", "Nov'", "Dec'"];
              let label = monthNames[parseInt(echarts.format.formatTime('MM', value)) - 1] + echarts.format.formatTime('yy', value);
              let label_mob = monthNames[parseInt(echarts.format.formatTime('MM', value)) - 1] + echarts.format.formatTime('yy', value);

              if (window.innerWidth >= 768) {
                /*if (label === "Apr'24") 
                  return "Apr'24\n(Expected)";
                else*/
                return label
              }
              else {
                /*if (label_mob === "Apr'24") 
                  return "Apr'24\n(Expected)";
                else*/
                return label_mob
              }

            },
            rich: {
              a: {
                align: 'center',
                lineHeight: 15, // Adjust the line height as needed
                fontWeight: 'bold',
                fontSize: (window.innerWidth <= 768) ? '10px' : '12px'
              },
              b: {
                align: 'center',
                lineHeight: 15, // Adjust the line height as needed
                fontWeight: 'bold',
                fontSize: (window.innerWidth <= 768) ? '10px' : '12px'
              },
            },
            rotate: (window.innerWidth <= 768) ? 90 : 90,
            fontSize: (window.innerWidth <= 768) ? '10px' : '12px'
          },
        },
        yAxis: {
          name: "in millions",
          nameTextStyle: {
            fontWeight: 'bold' // This makes the y-axis name bold
          },
          min: 1000,
          axisLabel: {
            color: '#19486D',
            fontWeight: 'bold',
            fontSize: (window.innerWidth <= 768) ? '10px' : '12px',
            formatter: function (value: any) {
              // Format the y-axis labels to display values in millions
              //return (value / 1000).toFixed(0) + 'K';
              return (value / 1000000).toFixed(0);
            }
          },
          splitLine: {
            show: true, // Show both horizontal and vertical grid lines
          },

        },
        grid: {
          left: 50,
          right: 20,
          bottom: 90,
          top: 40,
        },
        color: this.domainConfig.colorDark,
        series: seriesList
      };

      myChart.setOption(option);
    } catch (err) {
      console.log(err)
    }
    // Dynamically adjust title text size based on screen width
    function adjustTitleTextSize(seriesList: any, option: any) {
      var window_width = window.innerWidth;

      // Loop through seriesList and update endLabel.show property
      seriesList.forEach(function (series: any) {
        // Update endLabel.show based on window width
        series.endLabel.show = window_width >= 767;
      });

      // Update title text style
      if (option && option.title) {
        option.title.textStyle.fontSize = window_width > 600 ? '16px' : '12px'; // Adjust as needed

      }

      option.grid.right = window_width >= 767 ? 20 : 10;
      option.grid.left = window_width >= 767 ? 60 : 60;
      myChart.setOption(option);
    }
    // Initial adjustment on page load
    if (window.innerWidth <= 767) {
      adjustTitleTextSize(seriesList, option);
    }
    // Adjust on window resize
    // window.addEventListener('resize', adjustTitleTextSize);
    // Dynamically adjust tooltip size based on screen width

    // Adjust Tooltip size
    function adjustTooltipSize() {
      var windowWidth = window.innerWidth;
      var tooltipOptions = {};

      if (windowWidth <= 768) {
        // If screen width is below or equal to 768px, reduce tooltip size
        tooltipOptions = {
          padding: 0,
          textStyle: {
            fontSize: 10
          }
        };
      } else {
        // If screen width is above 768px, use default tooltip size
        tooltipOptions = {
          padding: 0, // Default padding value
          textStyle: {
            fontSize: 12 // Default font size value
          }
        };
      }

      // Apply tooltip options
      option.tooltip = Object.assign({}, option.tooltip, tooltipOptions);

      // Set the updated option to the chart
      myChart.setOption(option);
    }

    // Initial adjustment on page load
    adjustTooltipSize();

    // Adjust tooltip size on window resize
    window.addEventListener('resize', adjustTooltipSize);

  }


}
