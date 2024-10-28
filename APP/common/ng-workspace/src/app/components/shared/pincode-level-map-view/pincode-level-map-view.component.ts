import { Component, HostListener, OnInit } from '@angular/core';
import * as d3 from "d3";
import { LogisticSearchService } from '@openData/app/core/api/logistic-search/logistic-search.service';
import { CityWiseGeoJSONPincodeFiles, CityLatLong } from '@openData/app/core/utils/map';


@Component({
  selector: 'app-pincode-level-map-view',
  templateUrl: './pincode-level-map-view.component.html',
  styleUrl: './pincode-level-map-view.component.scss'
})
export class PincodeLevelMapViewComponent implements OnInit {

  city: string = 'Bangalore';
  isLoadingMap: boolean = true;
  width: number = 0;
  height: number = 0;
  selectedInsightOption: any;
  pathProjection: any;
  bubbleRadius: any;
  cityData: any;
  customColorRange: any;


  isBubblesVisible: boolean = true;

  private svg: any;
  private tooltip: any;
  private zoomBehavior: any;

  // Define default zoom settings
  private zoomExtent: any = [1, 8]; // Min, Max zoom levels
  private zoomStep = 1.5; // Zoom scale step for each button press

  mapData: any = [];
  insightData: any = {};
  chloroplethcolormapper3: any = {
    map_total_orders_metrics: ["#ffffff", "#FF7722"],
    map_total_active_sellers_metrics: ["#ffffff", "#1c75bc"],
    map_total_zonal_commerce_metrics: ["#ffffff", "#10b759"],
  }

  bubblecolormapper: any = {
    map_total_active_sellers_metrics: ["rgba(0,123,255,0.8)", "rgba(0,123,255,0.5)", "rgba(0,123,255,0.5)"],
    map_total_orders_metrics: ["rgba(227, 87, 10,0.8)", "rgba(227, 87, 10,0.4)", "rgba(227, 87, 10,0.4)"],
    map_total_zonal_commerce_metrics: ["rgba(16,183,89,0.8)", "rgba(16,183,89,0.5)", "rgba(16,183,89,0.5)"],
  }

  pincodeLevelMapColorMapper: any = ['#0ad10a', '#7b850b', '#da0000'];

  chloroplethcolormapper2: any = {
    map_total_orders_metrics: ["#ffffff", "#f9f0e9", "#FF7722"],
    map_total_active_sellers_metrics: ["#F8F3C5", "#FFCD71", "#FF6F48"],
    map_total_zonal_commerce_metrics: ["#ffffff", "#eefaf3", "#10b759"],
  }
  maxData: any = null;

  viewsOptions: any = [
    {
      type: 'search_only',
      title: 'Search Only'
    }, {
      type: 'conversion_only',
      title: 'Conversion Only'
    }, {
      type: 'search_and_conversion',
      title: 'Search and Conversion'
    },
  ];
  activeView: any = 'search_only';
  insightOptions: any = [
    {
      title: 'Top searched areas',
      tooltip: `Areas with high demand`,
      selected: false,
      type: 'high_demand',
      defaultView: this.viewsOptions[0]
    },
    {
      title: 'Top Conversion rate Areas',
      tooltip: `Areas with high conversion rate`,
      selected: false,
      type: 'high_conversion_rate',
      defaultView: this.viewsOptions[0]
    },
    {
      title: 'Areas with high search and high conversion rate',
      tooltip: `Areas that contribute to 75% of total searches (capped to 30 pincodes). 
            And conversion rates within these areas that are more than average.`,
      selected: false,
      type: 'high_demand_and_high_conversion_rate',
      defaultView: this.viewsOptions[2]
    },
    {
      title: 'Areas with high search and low conversion rate',
      tooltip: `Areas that contribute to 75% of total searches (capped to 30 pincodes) and 
        conversion rates within these areas that are less than average`,
      selected: false,
      type: 'high_demand_and_low_conversion_rate',
      defaultView: this.viewsOptions[2]
    },
    // {
    //   title: 'Areas with high search in peak morning hours',
    //   tooltip: `Areas with high demand between 8am-10am`,
    //   selected: false,
    //   type: 'high_demand_in_morning_hours',
    //   defaultView: this.viewsOptions[0]
    // },
    // {
    //   title: 'Areas with high search in peak evening hours',
    //   tooltip: `Areas with high demand between 6pm-9pm`,
    //   selected: false,
    //   type: 'high_demand_in_evening_hours',
    //   defaultView: this.viewsOptions[0]
    // }
  ];
  activeInsight: any;


  constructor(
    private logisticSearchService: LogisticSearchService
  ) { }

  queryParamsSubscription: any;

  cityWiseData: any = [];

  ngOnInit(): void {
    this.setDimensions();
    this.logisticSearchService.dateRange$.subscribe(
      (value: any) => {
        this.isLoadingMap = true;
        this.getMapData();
        this.activeInsight = this.insightOptions[0];
        this.activeView = this.viewsOptions[0].type;
      }
    )

    this.logisticSearchService.activeCity$.subscribe(
      (value: string) => {
        this.city = value;
        this.isLoadingMap = true;
        this.getMapData();
        this.activeInsight = this.insightOptions[0];
        this.activeView = this.viewsOptions[0].type;
      }
    )

    this.logisticSearchService.activeTimeInterval$.subscribe(
      (res: any) => {
        if (this.mapData && !this.isLoadingMap) {
          this.isLoadingMap = true;
          this.resetMap();
          this.setData();
        }
      }
    )
  }

  resetMap() {
    d3.select('#bubble-legends').selectAll('svg').remove();
    d3.select('#chloro-legends').selectAll('svg').remove();
    d3.select('#pincode-map').selectAll('svg').remove();
    if (this.svg) {
      this.svg.selectAll('circle').remove();
      this.svg.selectAll('foreignObject').remove();
    }
  }

  setDimensions() {
    const element = document.getElementsByClassName('map-svg')[0];
    this.width = element.clientWidth;
    this.height = element.clientHeight;
  }

  getMapData() {
    this.resetMap();
    this.logisticSearchService.getCityWiseData().subscribe(
      (response: any) => {
        if (response) {
          this.mapData = response.data.mapData;
          this.insightData = response.data.insightData;
          this.resetMap();
          this.setData();
        }
      }
    )
  }

  @HostListener('window:resize', ['$event'])
  onResize() {
    this.setDimensions();
    this.isLoadingMap = true;
    this.resetMap();
    this.setData();
  }

  toggleBubbleView() {
    this.isBubblesVisible = !this.isBubblesVisible;
    d3.selectAll('circle')
      .transition()
      .duration(500) // Optional: Duration of the transition
      .style('visibility', this.isBubblesVisible ? 'visible' : 'hidden');
  }


  async setData() {
    this.isBubblesVisible = false;
    this.isLoadingMap = true;

    this.cityData = [];

    let combinedGeoJSON: any = {
      "type": "FeatureCollection",
      "features": []
    };

    const topojsonFiles = CityWiseGeoJSONPincodeFiles[this.city];
     topojsonFiles.forEach(async (file: string) => {
      d3.json(file).then((data: any) => {
        if (data && data.type === 'Feature' && data.geometry && data.geometry.type === 'MultiPolygon') {
          data.mapData = this.mapData[data.properties.pincode.toString()]
          combinedGeoJSON.features.push(data);
        } else {
          console.error(`Invalid GeoJSON structure in file: ${file}`);
        }
        if (combinedGeoJSON.features.length === topojsonFiles.length) {
          const bounds = d3.geoPath().bounds(combinedGeoJSON);
          renderMap(bounds);
        }
      }).catch(error => {
        console.error(`Error loading file ${file}:`, error);
      });
    });

    // const mapprojectionresult = this.mapprojection(combinedGeoJSON);

    for (const key in this.mapData) {
      const stringKey: any = key.toString();
      let pincodeData: any = this.mapData[stringKey][this.logisticSearchService.activeTimeInterval.value] ?? {

      };
      pincodeData['pincode'] = Number(key);
      this.cityData.push(pincodeData)
    }

    this.tooltip = d3.select(".tooltip")

    this.svg = d3.select('#pincode-map').append('svg')
      .attr('viewBox', `0 0 ${this.width} ${this.height}`)
      .attr('preserveAspectRatio', "xMidYMid meet")
      .attr('class', 'pincode-level-map cursor-grab');

    const sortedSearchedData = this.cityData.sort(
      (a: any, b: any) =>
        (b.searched_data ?? 0) - (a.searched_data ?? 0)

    ).slice(0, 3);
    let maxSearchedData = sortedSearchedData[0].searched_data;
    maxSearchedData = maxSearchedData ? Number(maxSearchedData) : 0;

    const sortedConversionData = this.cityData.sort(
      (a: any, b: any) => b.conversion_rate - a.conversion_rate
    ).slice(0, 3);
    let maxConversionData = sortedConversionData[0].conversion_rate;
    maxConversionData = maxConversionData ? Number(maxConversionData) : 0;
    this.maxData = maxConversionData;


    this.customColorRange = d3.scaleLinear()
      .domain([0, 1, maxSearchedData])
      .range(this.chloroplethcolormapper2['map_total_active_sellers_metrics']);
    const g = this.svg.append('g').attr('id', 'pincodeGroup');

    // const projection: any = d3.geoMercator()
    //   .center(CityLatLong[this.city])
    //   .scale(55000)
    //   .translate([(this.width / 2) - 180, (this.height / 2) - 60]);

    // this.pathProjection = d3.geoPath().projection(projection);
    // const g = d3.select('#pincode-chloro');

    this.zoomBehavior = d3.zoom()
      .scaleExtent(this.zoomExtent)  // Limit zoom to specified extent
      .on('zoom', (event: any) => g.attr("transform", event.transform));

    this.svg.call(this.zoomBehavior);

    this.bubbleRadius = d3.scaleSqrt()
      .domain([0, maxConversionData])
      .range([1, 12]);

    const renderMap = (bounds: any) => {
      const scale = Math.min(
        this.width / (bounds[1][0] - bounds[0][0]),  // Width of the bounding box
        this.height / (bounds[1][1] - bounds[0][1])  // Height of the bounding box
      ) * 50;
      const translate: any = [
        (this.width - scale * (bounds[1][0] + bounds[0][0])) / 2,
        (this.height - scale * (bounds[1][1] + bounds[0][1])) / 2
      ];

      console.log(scale)


      const projection: any = d3.geoMercator()
      .center(CityLatLong[this.city])
      .scale(scale)
      .translate([(this.width / 2) - 180, (this.height / 2) - (this.city == 'Bangalore' ? 30 : 75)]);

      this.pathProjection = d3.geoPath().projection(projection);

      const legendValues = [0, ...Array.from({ length: 4 }, (_, i) => (i + 1) * maxSearchedData / 4)];

      g.selectAll('path')
        .data(combinedGeoJSON.features)
        .enter().append('path')
        .attr('d', this.pathProjection)
        .attr('stroke-width', 0.5)
        // .attr('stroke', this.chloroplethStrokeColor[casetype])
        .attr('stroke', '#545454')
        .attr('class', `cursor-pointer`)
        .on('mouseover', (event: any, d: any) => {
          const mapData = d.mapData ? d.mapData[this.logisticSearchService.activeTimeInterval.value] : null;
          this.tooltip.style('opacity', 1)
            .html(`
                <b>Pincode:</b> ${mapData?.pincode ?? d.properties.pincode}<br>
                <b>Search count:</b> ${mapData?.searched_data ?? 'No data'} <br>
                <b>Confirm percentage:</b> ${mapData?.conversion_rate ?? 0}% <br>
                <b>Assign percentage:</b> ${mapData?.assigned_rate ?? 0}%
          `);
        })
        .on('mousemove', (event: any) => {
          const svgElement: any = document.getElementById('pincode-map')?.getBoundingClientRect();

          // Adjust the position relative to the SVG element, not the whole page
          const offsetX = event.clientX - svgElement.left;
          const offsetY = event.clientY - svgElement.top;
          this.tooltip.style('left', (offsetX + 5) + 'px')
            .style('top', (offsetY - 28) + 'px');
        })
        .on('mouseout', () => {
          this.tooltip.style('opacity', 0);
        })

      // for chloro legends
      d3.select('#chloro-legends').selectAll('svg').remove();
      const newChloroLegendContainer = d3.select('#chloro-legends')
        .append('svg')
        .attr('class', 'legend')
        .attr('width', "180px")
        .attr('height', "100%");

      const legend = newChloroLegendContainer.selectAll('g')
        .data(legendValues)
        .enter()
        .append('g')
        .attr('class', 'legend')
        .attr('transform', (d, i) => `translate(0, ${i * (200 / 9) + 20})`); // Adjust vertical positioning

      legend.append('rect')
        .attr('width', 18)
        .attr('height', 18)
        .style('stroke', 'black')
        .style('stroke-width', '1px')
        .style('fill', (d) => this.customColorRange(d)); // Use customColorRange here

      legend.append('text')
        .attr('x', 25)
        .attr('y', 9)
        .attr('dy', '.35em')
        .style('text-anchor', 'start')
        .style('font-size', '12px')
        .text((d, i) => {
          const startRange = i === 0 ? '0' : Math.floor(legendValues[i - 1]) + 1;
          const endRange = Math.floor(d);

          if (d == 0) { return 'No Data' };
          if (i === 0) {
            return startRange.toLocaleString();
          } else if (i === 1) {
            return `< ${endRange.toLocaleString()}`;
          } else if (i === legendValues.length - 1) {
            return `> ${startRange.toLocaleString()}`;
          } else {
            return `${startRange.toLocaleString()}-${endRange.toLocaleString()}`;
          }
        });
      this.addBubbles();
      this.isLoadingMap = false;
    }
  }

  addBubbles(insightType: any = null) {
    let g = this.svg.selectAll('#pincodeGroup');

    this.svg.selectAll('circle').remove();
    this.svg.selectAll('foreignObject').remove();

    const activeTimeInterval: any = this.logisticSearchService.activeTimeInterval.value;

    // console.log(activeTimeInterval, this.insightData, insightType, this.activeInsight)

    let activeInsightData = this.insightData[insightType ?? this.activeInsight.type][activeTimeInterval];
    let sortedData: any;

    if (this.activeInsight.type == this.insightOptions[0].type) {
      sortedData = Object.values(activeInsightData).sort(
        (a: any, b: any) => (b.searched_data ?? 0) - (a.searched_data ?? 0)
      )
    } else if (this.activeInsight.type == this.insightOptions[1].type) {
      sortedData = Object.values(activeInsightData).sort(
        (a: any, b: any) => (b.conversion_rate ?? 0) - (a.conversion_rate ?? 0)
      )
    } else {
      sortedData = Object.values(activeInsightData).sort(
        (a: any, b: any) => (b.conversion_rate ?? 0) - (a.conversion_rate ?? 0)
      )
    }

    g.selectAll('path')
      .attr('fill',
        (el: any) => {
          if (this.activeView == this.viewsOptions[1].type) {
            return 'white';
          }
          if (el.mapData && this.logisticSearchService.activeTimeInterval.value in el.mapData) {
            const val = Number(
              el.mapData[this.logisticSearchService.activeTimeInterval.value]?.searched_data
            );
            return this.customColorRange(val)
          } else {
            return this.customColorRange(0)
          }
        })
      .each((d: any) => {
        // Compute the centroid of the path for this feature
        const centroid = this.pathProjection.centroid(d);

        const mapData = d.mapData ? d.mapData[activeTimeInterval] : null;
        const pincode = mapData?.pincode;

        // if (pincode && activeInsightData[pincode ?? '']) {
        //   const mapData = activeInsightData[pincode];

          // Append a circle at the centroid position
          this.svg.select('#pincodeGroup').append('circle')
            .attr('cx', centroid[0])
            .attr('cy', centroid[1])
            .attr('r', (el: any) => {
              // return 4;
              if (mapData?.conversion_rate) {
                const value = mapData.conversion_rate;
                return value ? Math.min(12, Math.max(1, this.bubbleRadius(value))) : 1;
              } else {
                return 1
              }
            })
            .attr('fill', 'RGBA( 0, 139, 139, 0.4 )	')
            .attr('stroke', 'RGBA( 0, 139, 139, 0.8)')
            .attr('stroke-width', 0.5)
            .style('visibility', (this.activeView == this.viewsOptions[1].type ||
              this.activeView == this.viewsOptions[2].type) ? 'visible' : 'hidden')
            .on('mouseover', (event: any) => {
              const mapData = d.mapData ? d.mapData[this.logisticSearchService.activeTimeInterval.value] : null;
              this.tooltip.style('opacity', 1)
                .html(`
                        <b>Pincode:</b> ${mapData?.pincode ?? d.properties.pincode}<br>
                        <b>Search count:</b> ${mapData?.searched_data ?? 'No data'} <br>
                        <b>Confirm percentage:</b> ${mapData?.conversion_rate ?? 0}% <br>
                        <b>Assign percentage:</b> ${mapData?.assigned_rate ?? 0}%
                  `);
            })
            .on('mousemove', (event: any) => {
              const svgElement: any = document.getElementById('pincode-map')?.getBoundingClientRect();

              // Adjust the position relative to the SVG element, not the whole page
              const offsetX = event.clientX - svgElement.left;
              const offsetY = event.clientY - svgElement.top;
              this.tooltip.style('left', (offsetX + 5) + 'px')
                .style('top', (offsetY - 28) + 'px');
            })
            .on('mouseout', () => {
              this.tooltip.style('opacity', 0);
            });
        // }



        const topPincodes = sortedData.slice(0, 10).map((d: any) => d.pincode);
        if (d.mapData && topPincodes.includes(d.mapData[this.logisticSearchService.activeTimeInterval.value]?.pincode)) {
          g.append('foreignObject')
            .attr('x', centroid[0] - 35 / 2 + 5)
            .attr('y', centroid[1] - 40)
            .attr('width', 35)
            .attr('height', 35)
            .attr('overflow', 'visible')
            .on('mouseover', (event: any) => {
              const mapData = d.mapData ? d.mapData[this.logisticSearchService.activeTimeInterval.value] : null;
              this.tooltip.style('opacity', 1)
                .html(`<div class='tooltip-container'>
                        <b>Pincode:</b> ${mapData?.pincode ?? d.properties.pincode}<br>
                        <b>Search count:</b> ${mapData?.searched_data ?? 'No data'} <br>
                        <b>Confirm percentage:</b> ${mapData?.conversion_rate ?? 0}% <br>
                        <b>Assign percentage:</b> ${mapData?.assigned_rate ?? 0}%
                      </div>
                `);
            })
            .on('mousemove', (event: any) => {
              const svgElement: any = document.getElementById('pincode-map')?.getBoundingClientRect();

              // Adjust the position relative to the SVG element, not the whole page
              const offsetX = event.clientX - svgElement.left;
              const offsetY = event.clientY - svgElement.top;
              this.tooltip.style('left', (offsetX + 5) + 'px')
                .style('top', (offsetY - 28) + 'px');
            })
            .on('mouseout', () => {
              this.tooltip.style('opacity', 0);
            })
            .html((i: any) => {
              let iconClass = "pointer-icon fa-solid fa-person-biking";
              let metricValue = Number(
                d.mapData[this.logisticSearchService.activeTimeInterval.value]?.searched_data
              );
              return `<div class="pointer">
                  <i class="${iconClass}"></i>
                  </div>
                <div class="pulse"></div>`;
            })

        }
      });

    const bubbleLegendData: any = [
      {
        label: 'Low',
        radius: this.bubbleRadius(0),
        value: 0, color: "RGBA( 0, 139, 139, 0.8)"
      },
      {
        label: 'Medium', radius:
          this.bubbleRadius(
            this.maxData * 0.5
          ),
        value: Math.floor(
          this.maxData * 0.5
        ),
        color: "RGBA( 0, 139, 139, 0.8)"
      },
      {
        label: 'High',
        radius: this.bubbleRadius(this.maxData),
        value: Math.floor(this.maxData),
        color: "RGBA( 0, 139, 139, 0.8)"
      }
    ];

    d3.select('#bubble-legends').selectAll('svg').remove();

    const newLegendContainer = d3.select('#bubble-legends').append('svg')
      .attr('class', 'legend')
      .attr('width', "180px")
      .attr('height', "96px")

    const legendItems = newLegendContainer.selectAll('g')
      .data(bubbleLegendData)
      .enter().append('g')
      .attr('transform', `translate(10, 40)`);

    legendItems.append('circle')
      .attr('cx', 30)
      .attr('cy', (d, i) => `${30 - (i * 15)}`)
      .attr('r', (d, i) => `${i * (1 * 15) + 5}`)
      .attr('fill', (d, i) => 'transparent')
      .attr('stroke', (d: any, i) => d.color)
      .attr('stroke-width', 2);

    legendItems.append('line')
      .attr('x1', (d, i) => `${35 + (i * 15)}`)
      .attr('x2', 90)
      .attr('y1', (d, i) => `${30 - (i * 15)}`)
      .attr('y2', (d, i) => `${30 - (i * 15)}`)
      .attr('stroke', 'black')
      .style('stroke-dasharray', '2,2');

    legendItems.append('text')
      .attr('x', 95)
      .attr('y', (d, i) => `${30 - (i * 15)}`)
      .attr('dy', '.35em')
      .style('text-anchor', 'start')
      .style('font-size', '12px')
      .text((d: any, i: any) => {
        return `>= ${(bubbleLegendData[2].value * ((i) * 0.33)).toLocaleString()}%`
      }
      );

  }

  // Zoom in method
  zoomIn(): void {
    this.svg.transition().duration(500).call(this.zoomBehavior.scaleBy, this.zoomStep);
  }

  // Zoom out method
  zoomOut(): void {
    this.svg.transition().duration(500).call(this.zoomBehavior.scaleBy, 1 / this.zoomStep);
  }

  // Reset zoom method
  resetZoom(): void {
    this.svg.transition().duration(500).call(this.zoomBehavior.transform, d3.zoomIdentity); // Reset to original view
  }

  mapprojection(data: any) {
    const el: any = document.getElementById("pincode-map");

    const height = el.clientHeight
    const width = el.clientWidth
    const projection = d3.geoMercator();
    const pathGenerator = d3.geoPath().projection(projection);

    projection.scale(1).translate([0, 0])

    const b = pathGenerator.bounds(data),
      s = 0.95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
      t: [number, number] = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];

    projection.scale(s).translate(t);
    return [projection, pathGenerator];
  }


  updateInsightSelection(option: any) {
    this.activeInsight = option;
    // if (option.type == "high_demand_in_morning_hours") {
    //   this.logisticSearchService.setActiveTimeInterval("8am-10am");
    //   this.logisticSearchService.filterUpdated.next({updated: true, updatedFor: 'timeInterval'});
    //   return;
    // } else if (option.type == "high_demand_in_evening_hours") {
    //   this.logisticSearchService.setActiveTimeInterval("6pm-9pm");
    //   this.logisticSearchService.filterUpdated.next({updated: true, updatedFor: 'timeInterval'});
    //   return;
    // }
    this.activeView = option.defaultView.type;
    this.addBubbles(option.type);
  }

  updateViewSelection(option: any) {
    this.activeView = option.type;
    this.addBubbles();
  }
}