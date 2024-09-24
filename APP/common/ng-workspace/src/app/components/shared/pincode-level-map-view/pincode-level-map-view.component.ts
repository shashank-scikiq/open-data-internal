import { Component, HostListener, OnInit } from '@angular/core';
import * as L from "leaflet";
import * as d3 from "d3";
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
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


  isBubblesVisible: boolean = false;

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
    map_total_active_sellers_metrics: ["#ffffff", "#dfebf5", "#1c75bc"],
    map_total_zonal_commerce_metrics: ["#ffffff", "#eefaf3", "#10b759"],
  }
  maxData: any = null;

  insightOptions: any = [
    {
      title: 'Areas with high demand & high conversion rates',
      tooltip: `Areas that contribute to 75% of total searches (capped to 30 pincodes). 
            And conversion rates within these areas that are more than average.`,
      selected: false,
      type: 'high_demand_and_high_conversion_rate'
    },
    {
      title: 'Areas with high demand, but low conversion rates',
      tooltip: `Areas that contribute to 75% of total searches (capped to 30 pincodes) and 
        conversion rates within these areas that are less than average`,
      selected: false,
      type: 'high_demand_and_low_conversion_rate'
    },
    // {
    //   title: 'Areas with low demand but good conversions on the existing dmand',
    //   tooltip: `Areas that contribute to not more than 25% of total searches 
    //     (capped to 30 pincodes) and conversion rates are higehr than average. Minimum threshold of 100`,
    //   selected: false
    // }
  ]
  activeInsight: any;

  constructor(
    private logisticSearchService: LogisticSearchService
  ) { }

  queryParamsSubscription: any;

  cityWiseData: any = [];

  ngOnInit(): void {
    this.setDimensions();

    this.logisticSearchService.activeCity$.subscribe(
      (value: string) => {
        this.city = value;
        this.isLoadingMap = true;
        this.getMapData();
        this.activeInsight = this.insightOptions[0].type;
      }
    )

    this.logisticSearchService.activeTimeInterval$.subscribe(
      (res: any) => {
        if (this.mapData && !this.isLoadingMap) {
          this.isLoadingMap = true;
          this.setData();
        }
      }
    )
  }

  setDimensions() {
    const element = document.getElementsByClassName('map-svg')[0];
    this.width = element.clientWidth;
    this.height = element.clientHeight;
  }

  getMapData() {
    this.logisticSearchService.getCityWiseData().subscribe(
      (response: any) => {
        if (response) {
          this.mapData = response.data.mapData;
          this.insightData = response.data.insightData;
          this.setData();
        }
      }
    )
  }

  @HostListener('window:resize', ['$event'])
  onResize() {
    this.setDimensions();
    this.isLoadingMap = true;
    this.setData();
  }

  toggleBubbleView() {
    this.isBubblesVisible = !this.isBubblesVisible;
    d3.selectAll('circle')
      .transition()
      .duration(500) // Optional: Duration of the transition
      .style('visibility', this.isBubblesVisible ? 'visible' : 'hidden');
  }


  setData() {
    this.isBubblesVisible = false;
    this.isLoadingMap = true;
    
    d3.select('#bubble-legends').selectAll('svg').remove();
    d3.select('#chloro-legends').selectAll('svg').remove();
    d3.select('#pincode-map').selectAll('svg').remove();
    if (this.svg) {
      this.svg.selectAll('circle').remove();
      this.svg.selectAll('foreignObject').remove();
    }

    this.cityData = [];

    let combinedGeoJSON: any = {
      "type": "FeatureCollection",
      "features": []
    };

    const topojsonFiles = CityWiseGeoJSONPincodeFiles[this.city];
    topojsonFiles.forEach((file: string) => {
      d3.json(file).then((data: any) => {
        if (data && data.type === 'Feature' && data.geometry && data.geometry.type === 'MultiPolygon') {
          data.mapData = this.mapData[data.properties.pincode.toString()]
          combinedGeoJSON.features.push(data);
        } else {
          console.error(`Invalid GeoJSON structure in file: ${file}`);
        }
        if (combinedGeoJSON.features.length === topojsonFiles.length) {
          renderMap();
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
      .attr('class', 'pincode-level-map');
      
      const sortedSearchedData = this.cityData.sort(
        (a: any, b: any) => 
          (b.searched_data ?? 0) - (a.searched_data ?? 0)
        
      ).slice(0, 3);
    let maxSearchedData = sortedSearchedData[0].searched_data;
    maxSearchedData = maxSearchedData ? Number(maxSearchedData) : 0;

    const sortedConversionData = this.cityData.sort(
      (a: any, b: any) => b.total_conversion_percentage - a.total_conversion_percentage
    ).slice(0, 3);
    let maxConversionData = sortedConversionData[0].total_conversion_percentage;
    maxConversionData = maxConversionData ? Number(maxConversionData) : 0;

    let customColorRange: any;
    customColorRange = d3.scaleLinear()
      .domain([0, 1, maxSearchedData])
      .range(this.chloroplethcolormapper2['map_total_active_sellers_metrics']);
    const g = this.svg.append('g').attr('id', 'pincodeGroup');

    const projection: any = d3.geoMercator()
      .center(CityLatLong[this.city])
      .scale(50000)
      .translate([(this.width / 2) + 80, (this.height / 2) - 60]);

    this.pathProjection = d3.geoPath().projection(projection);
    // const g = d3.select('#pincode-chloro');

    this.zoomBehavior = d3.zoom()
      .scaleExtent(this.zoomExtent)  // Limit zoom to specified extent
      .on('zoom', (event: any) => g.attr("transform", event.transform));

    this.svg.call(this.zoomBehavior);

    this.bubbleRadius = d3.scaleSqrt()
      .domain([0, maxConversionData])
      .range([1, 7]);

    const renderMap = () => {
      const legendValues = [0, ...Array.from({ length: 4 }, (_, i) => (i + 1) * maxSearchedData / 4)];

      g.selectAll('path')
        .data(combinedGeoJSON.features)
        .enter().append('path')
        .attr('d', this.pathProjection)
        .attr('fill',
          (el: any) => {
            if (el.mapData && this.logisticSearchService.activeTimeInterval.value in el.mapData) {
              const val = Number(
                el.mapData[this.logisticSearchService.activeTimeInterval.value]?.searched_data
              );
              return customColorRange(val)
            } else {
              return customColorRange(0)
            }
          })
        .attr('stroke-width', 0.5)
        // .attr('stroke', this.chloroplethStrokeColor[casetype])
        .attr('stroke', 'rgba(0,123,255,0.5)')
        .attr('class', `cursor-pointer`)
        .on('mouseover', (event: any, d: any) => {
          const mapData = d.mapData ? d.mapData[this.logisticSearchService.activeTimeInterval.value] : null;
          this.tooltip.style('opacity', 1)
            .html(`<b>Pincode:</b> ${mapData?.pincode ?? d.properties.pincode}<br>
                <b>Search count:</b> ${mapData?.searched_data ?? 'No data'}`);
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
        .style('fill', (d) => customColorRange(d)); // Use customColorRange here

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
    let activeInsightData = this.insightData[insightType ?? this.activeInsight][activeTimeInterval];
    const sortedConversionData: any = Object.values(activeInsightData).sort(
      (a: any, b: any) => (b.total_conversion_percentage ?? 0) - (a.total_conversion_percentage ?? 0)
    )
    const maxConversionData = sortedConversionData[0]?.total_conversion_percentage ?? 0;

    g.selectAll('path').each((d: any) => {
      // Compute the centroid of the path for this feature
      const centroid = this.pathProjection.centroid(d);

      const mapData = d.mapData ? d.mapData[activeTimeInterval] : null;
      const pincode = mapData?.pincode;

      if (pincode && activeInsightData[pincode ?? '']) {
        const mapData = activeInsightData[pincode];

        // Append a circle at the centroid position
        this.svg.select('#pincodeGroup').append('circle')
          .attr('cx', centroid[0])
          .attr('cy', centroid[1])
          .attr('r', (el: any) => {
            // return 4;
            if (mapData.total_conversion_percentage) {
              const value = mapData.total_conversion_percentage;
              return value ? Math.min(7, Math.max(1, this.bubbleRadius(value))) : 1;
            } else {
              return 1
            }
          })
          .attr('fill', 'rgba(255, 142, 0, 0.4)')
          .attr('stroke', 'rgba(255, 142, 0, 1)')
          .attr('stroke-width', 1)
          .style('visibility', this.isBubblesVisible ? 'visible' : 'hidden')
          .on('mouseover', (event: any) => {
            const mapData = d.mapData ? d.mapData[this.logisticSearchService.activeTimeInterval.value] : null;
            this.tooltip.style('opacity', 1)
              .html(`<b>Pincode:</b> ${mapData?.pincode ?? d.properties.pincode}<br>
                    <b>Confirm percentage:</b> ${mapData?.total_conversion_percentage ?? 0}% <br>
                    <b>Search count:</b> ${mapData?.searched_data ?? 'No data'}`);
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
      }



      const topPincodes = sortedConversionData.slice(0, 5).map((d: any) => d.pincode);
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
              .html(`<b>Pincode:</b> ${mapData?.pincode ?? d.properties.pincode}<br>
                    <b>Confirm percentage:</b> ${mapData?.total_conversion_percentage ?? 0} % <br>
                    <b>Search count:</b> ${mapData?.searched_data ?? 'No data'}`);
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
            let iconClass = "pointer-icon fa-solid fa-cart-shopping";
            let metricValue = Number(
              d.mapData[this.logisticSearchService.activeTimeInterval.value]?.searched_data
            );
            return `<div class="pointer" nz-tooltip nzTooltipPlacement="top" 
              nzTooltipTitle="
                <br/>top data: ${metricValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}">
                <i class="${iconClass}"></i>
                </div><div class="pulse"></div>`;
          })

      }
    });

    const bubbleLegendData: any = [
      {
        label: 'Low',
        radius: this.bubbleRadius(0),
        value: 0, color: this.bubblecolormapper['map_total_active_sellers_metrics'][0]
      },
      {
        label: 'Medium', radius:
          this.bubbleRadius(
            maxConversionData * 0.5
          ),
        value: Math.floor(
          maxConversionData * 0.5
        ),
        color: this.bubblecolormapper['map_total_active_sellers_metrics'][0]
      },
      {
        label: 'High',
        radius: this.bubbleRadius(maxConversionData),
        value: Math.floor(maxConversionData),
        color: this.bubblecolormapper['map_total_active_sellers_metrics'][1]
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
        .attr('stroke', (d, i) => 'rgba(255, 142, 0, 1)')
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


  updateInsightSelection(type: any) {
    this.addBubbles(type);
  }
}