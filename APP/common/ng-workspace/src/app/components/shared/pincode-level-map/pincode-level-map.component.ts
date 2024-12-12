import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { LogisticSearchService } from '@openData/app/core/api/logistic-search/logistic-search.service';
import { StateCode } from '@openData/app/core/utils/map';
import * as d3 from "d3";
import * as topojson from 'topojson-client';

interface Data {
  mapData: any;
  iconData?: any;
}
@Component({
  selector: 'app-pincode-level-map',
  templateUrl: './pincode-level-map.component.html',
  styleUrl: './pincode-level-map.component.scss'
})
export class PincodeLevelMapComponent implements OnChanges {
  @Input() isLoading: boolean = false;
  @Input() visualType: 'chloro' | 'bubble' | 'both' = 'chloro';
  @Input() configData: any = {
    chloroColorRange: ["#F8F3C5", "#FFCD71", "#FF6F48"],
    bubbleColorRange: [],
    bubbleDataKey: '',
    chloroDataKey: '',
    maxChloroData: 0,
    maxBubbleData: 0
  }
  @Input() data: any;

  pincodeMapGeojson: any;

  svg: any;
  width: number = 0;
  height: number = 0;
  private zoomBehavior: any;
  private zoomExtent: any = [1, 8]; // Min, Max zoom levels
  private zoomStep = 1.5; // Zoom scale step for each button press
  pincodeMapData: any = null;
  mapProjectionResult: any;

  customColorRange: any;
  bubbleRadiusMethod: any;
  tooltip: any;
  selectedCity: any;
  updatingData: boolean = false;

  constructor(private logisticSearchService: LogisticSearchService) { }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['data'] || changes['visualType']) {
      this.updatingData = true;
      this.initMap();
    }
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

  resetMap() {
    d3.select('#pincode-level-map').selectAll('svg').remove();
    if (this.svg) {
      this.svg.selectAll('path').remove();
      this.svg.selectAll('circle').remove();
      this.svg.selectAll('foreignObject').remove();
    }
  }

  async initMap() {
    this.updatingData = true;
    if (!this.pincodeMapData || this.selectedCity != this.logisticSearchService.activeCity.value) {
      this.selectedCity = this.logisticSearchService.activeCity.value;
      this.pincodeMapData = await d3.json(`static/assets/data/map/pincode/${this.selectedCity.toLowerCase()}-pincodes.json`);
    }
    const element = document.getElementsByClassName('pincode-level-map-svg')[0];

    this.width = element.clientWidth;
    this.height = element.clientHeight;
    this.resetMap();
    const mapGeopJson = this.pincodeMapData;
    this.mapProjectionResult = this.mapprojection(mapGeopJson);

    this.tooltip = d3.select(".tooltip")

    this.svg = d3.select('#pincode-level-map').append('svg')
      .attr('viewBox', `0 0 ${this.width} ${this.height}`)
      .attr('preserveAspectRatio', "xMidYMid meet")
      .attr('class', 'pincode-level-map');

    this.zoomBehavior = d3.zoom()
      .scaleExtent(this.zoomExtent)  // Limit zoom to specified extent
      .on('zoom', (event: any) => g.attr("transform", event.transform));

    this.svg.call(this.zoomBehavior);

    const g = this.svg.append('g').attr('id', 'pincodeGroup');

    g.selectAll('path')
      .data(mapGeopJson.features)
      .enter().append('path')
      .attr('d', (data: any) => this.mapProjectionResult[1](data))
      .attr('fill', '#f4f4f400')
      .attr('stroke-width', 0.5)
      .attr('stroke', 'black')

    this.updateMapWithData();
  }

  updateMapWithData() {
    if (!this.data?.mapData) {
      this.updatingData = false;
      return;
    }
    let g = this.svg.selectAll('#pincodeGroup');
    if (this.visualType == 'chloro' || this.visualType == 'both') {
      this.customColorRange = d3.scaleLinear()
        .domain([0, 1, this.configData.maxChloroData])
        .range(this.configData.chloroColorRange);

      g.selectAll('path')
        .style('fill', (d: any) => {
          if (d.properties.pincode == "110039") {
            console.log(this.data.mapData[d.properties.pincode])
          }
          let color = this.configData.chloroColorRange[0];
          if (this.data.mapData[d.properties.pincode]) {
            color = this.customColorRange(
              this.data.mapData[d.properties.pincode][this.configData.chloroDataKey]
            )
          } else {
            color = this.configData.chloroColorRange[0];
          }
          return color
        })
        .on('mouseover', (event: any, d: any) => {
          let htmlString = `<b>City:</b> ${this.selectedCity} <br> <b>Pincode:</b> ${d.properties.pincode} <br>`
          if (this.data.mapData[d.properties.pincode]) {
            htmlString += Object.entries(this.data.mapData[d.properties.pincode])
              .map(([key, value]) => `<b>${key}:</b> ${value ?? 'No data'} <br>`)
              .join('');
          }
          this.tooltip.style('opacity', 1)
            .html(htmlString);
        })
        .on('mousemove', (event: any) => {
          const svgElement: any = document.getElementById('pincode-level-map')?.getBoundingClientRect();

          // Adjust the position relative to the SVG element, not the whole page
          const offsetX = event.clientX - svgElement.left;
          const offsetY = event.clientY - svgElement.top;
          this.tooltip.style('left', (offsetX + 5) + 'px')
            .style('top', (offsetY - 28) + 'px');
        })
        .on('mouseout', () => {
          this.tooltip.style('opacity', 0);
        })
    }

    if (this.visualType == 'bubble' || this.visualType == 'both') {
      this.bubbleRadiusMethod = d3.scaleSqrt()
        .domain([0, this.configData.maxBubbleData])
        .range([1, 12]);

      g.selectAll('path')
        .each((d: any) => {
          const centroid = this.mapProjectionResult[0](d3.geoCentroid(d));

          this.svg.select('#pincodeGroup').append('circle')
            .attr('cx', centroid[0])
            .attr('cy', centroid[1])
            .attr('r', (el: any) => {
              if (
                !(this.data.mapData[d.properties.pincode] && 
                  this.data.mapData[d.properties.pincode][this.configData.bubbleDataKey])
                ) {
                return 1;
              }
              const radius = Math.min(12, Math.max(1, this.bubbleRadiusMethod(
                Number(this.data.mapData[d.properties.pincode][this.configData.bubbleDataKey].slice(0, -1))
              )));
              return radius;
            })
            .attr('fill', this.configData.bubbleColorRange[0])
            .attr('stroke', this.configData.bubbleColorRange[1])
            .attr('stroke-width', 0.5)
            .on('mouseover', (event: any) => {
              let htmlString = `<b>City:</b> ${this.selectedCity} <br> <b>Pincode:</b> ${d.properties.pincode} <br>`
              if (this.data.mapData[d.properties.pincode]) {
                htmlString += Object.entries(this.data.mapData[d.properties.pincode])
                  .map(([key, value]) => `<b>${key}:</b> ${value ?? 'No data'} <br>`)
                  .join('');
              }
              this.tooltip.style('opacity', 1)
                .html(htmlString);
            })
            .on('mousemove', (event: any) => {
              const svgElement: any = document.getElementById('pincode-level-map')?.getBoundingClientRect();

              // Adjust the position relative to the SVG element, not the whole page
              const offsetX = event.clientX - svgElement.left;
              const offsetY = event.clientY - svgElement.top;
              this.tooltip.style('left', (offsetX + 5) + 'px')
                .style('top', (offsetY - 28) + 'px');
            })
            .on('mouseout', () => {
              this.tooltip.style('opacity', 0);
            });
        })
    }
    if (!this.data.iconData) {
      this.updatingData = false;
      return;
    }
    this.setIconContainer();
  }

  setIconContainer() {
    let g = this.svg.selectAll('#pincodeGroup');

    const iconWidth = 35;
    const iconHeight = 35;

    g.selectAll('path')
      .each((d: any) => {
        const centroid = this.mapProjectionResult[0](d3.geoCentroid(d));
        const iconData = this.data?.iconData[d.properties.pincode];

        if (!iconData) return;

        this.svg.select('#pincodeGroup').append('foreignObject')
          .attr('x', centroid[0] - iconWidth / 2 + 5)
          .attr('y', centroid[1] - 40)
          .attr('width', iconWidth)
          .attr('height', iconHeight)
          .attr('overflow', 'visible')
          .attr('d', (data: any) => this.mapProjectionResult[1](data))
          .html((i: any) => {
            let iconClass = "pointer-icon fa-solid fa-person-biking";
            return `<div class="pointer bounce">
                  <i class="${iconClass}"></i>
                  </div>
                <div class="pulse"></div>`;
          })
      })
      this.updatingData = false;
  }

  mapprojection(data: any) {
    const height = this.height
    const width = this.width

    const projection = d3.geoMercator();
    const pathGenerator = d3.geoPath().projection(projection);

    projection.scale(1).translate([0, 0])
    const b = pathGenerator.bounds(data),
      s = 0.95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
      t: [number, number] = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];

    projection.scale(s).translate(t);
    return [projection, pathGenerator]
  }
}
