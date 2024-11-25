import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { LogisticSearchService } from '@openData/app/core/api/logistic-search/logistic-search.service';
import * as d3 from "d3";
import * as topojson from 'topojson-client';


@Component({
  selector: 'app-pan-india-map',
  templateUrl: './pan-india-map.component.html',
  styleUrl: './pan-india-map.component.scss'
})
export class PanIndiaMapComponent implements OnInit, OnChanges {
  @Input() viewType: 'state_map' | 'district_map' = 'state_map';
  @Input() visualType: 'chloro' | 'bubble' | 'both' = 'chloro';
  @Input() configData: any = {
    chloroColorRange: ["#F8F3C5", "#FFCD71", "#FF6F48"],
    bubbleColorRange: ["RGBA( 0, 139, 139, 0.4)", "RGBA( 0, 139, 139, 0.8)"],
    bubbleDataKey: '',
    chloroDataKey: '',
    maxChloroData: 0,
    maxBubbleData: 0
  }
  @Input() mapData: any;

  statemapGeojson: any;
  districtmapGeojson: any;
  svg: any;
  width: number = 0;
  height: number = 0;
  private zoomBehavior: any;
  private zoomExtent: any = [1, 8]; // Min, Max zoom levels
  private zoomStep = 1.5; // Zoom scale step for each button press
  indiamapdata: any = null;
  mapProjectionResult: any;

  customColorRange: any;
  bubbleRadiusMethod: any;
  tooltip: any;

  constructor(private logisticSearchService: LogisticSearchService) {}


  ngOnInit(): void {
    const element = document.getElementsByClassName('pan-india-map-svg')[0];
    
    this.width = element.clientWidth;
    this.height = element.clientHeight;
    this.initMap();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if(changes['viewType'] && !changes['viewType']['firstChange']) {
      this.initMap();
    }
    if (changes['mapData'] || changes['visualType']) {
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
    d3.select('#pan-india-map').selectAll('svg').remove();
    if (this.svg) {
      this.svg.selectAll('path').remove();
      this.svg.selectAll('circle').remove();
      this.svg.selectAll('foreignObject').remove();
    }
  }

  async initMap() {
    if(!this.indiamapdata) {
      this.indiamapdata = await(await fetch('static/assets/data/map/india.json')).json();

      this.statemapGeojson = await topojson.feature(this.indiamapdata, this.indiamapdata.objects.states);
      this.districtmapGeojson = await topojson.feature(this.indiamapdata, this.indiamapdata.objects.districts);
    }
    this.resetMap();

    const mapGeopJson =
      this.viewType == 'state_map' ? this.statemapGeojson : this.districtmapGeojson;
    this.mapProjectionResult = this.mapprojection(mapGeopJson);

    this.tooltip = d3.select(".tooltip")

    this.svg = d3.select('#pan-india-map').append('svg')
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
      .attr('cursor', 'pointer')
      .attr('stroke-width', 0.5)
      .attr('stroke', 'black')
      .on('click', (event: any, d: any) => {
        this.logisticSearchService.activeState.next(d.properties.st_nm);
      })

      this.updateMapWithData();
  }

  updateMapWithData() {
    if(!this.mapData) return;
    let g = this.svg.selectAll('#pincodeGroup');

    if (this.visualType == 'chloro' || this.visualType=='both') {
      this.customColorRange = d3.scaleLinear()
        .domain([0, 1, this.configData.maxChloroData])
        .range(this.configData.chloroColorRange);
  
      g.selectAll('path')
      .style('fill', (d: any) => {
        let key = this.viewType == 'state_map' ? d.id.toUpperCase() : d.properties.district
        let data = this.mapData[key];
        return data ? this.customColorRange(
            this.mapData[key][this.configData.chloroDataKey]
          ) :
          this.configData.chloroColorRange[0]
      })
      .on('mouseover', (event: any, d: any) => {
        let key = this.viewType == 'state_map' ? d.id.toUpperCase() : d.properties.district
        const data = this.mapData[key];
        let htmlString = this.viewType == 'state_map' ? `<b>State:</b> ${d.id} <br>` :
          `<b>State:</b> ${d.properties.st_nm} <br> <b>District:</b> ${d.properties.district} <br>` 
        if (data) {
          htmlString += Object.entries(data)
          .map(([key, value]) => `<b>${key}:</b> ${value ?? 'No data'} <br>`)
          .join('');
        }
        this.tooltip.style('opacity', 1)
          .html(htmlString);
      })
      .on('mousemove', (event: any) => {
        const svgElement: any = document.getElementById('pan-india-map')?.getBoundingClientRect();
  
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
        let key = this.viewType == 'state_map' ? d.id.toUpperCase() : d.properties.district
        let data = this.mapData[key];

        this.svg.select('#pincodeGroup').append('circle')
            .attr('cx', centroid[0])
            .attr('cy', centroid[1])
            .attr('r', (el: any) => {
              if(!(data && data[this.configData.bubbleDataKey])) {
                return 1;
              }
              const radius = Math.min(12, Math.max(1, this.bubbleRadiusMethod(data[this.configData.bubbleDataKey])));
              return radius
            })
            .attr('fill', this.configData.bubbleColorRange[0])
            .attr('stroke', this.configData.bubbleColorRange[1])
            .attr('stroke-width', 0.5)
            .on('mouseover', (event: any) => {
              const data = this.mapData[key];
              let htmlString = this.viewType == 'state_map' ? `<b>State:</b> ${d.id} <br>` :
              `<b>State:</b> ${d.properties.st_nm} <br> <b>District:</b> ${d.properties.district} <br>` 
              if (data) {
                htmlString += Object.entries(data)
                .map(([key, value]) => `<b>${key}:</b> ${value ?? 'No data'} <br>`)
                .join('');
              }
              this.tooltip.style('opacity', 1)
                .html(htmlString);
            })
            .on('mousemove', (event: any) => {
              const svgElement: any = document.getElementById('pan-india-map')?.getBoundingClientRect();

              // Adjust the position relative to the SVG element, not the whole page
              const offsetX = event.clientX - svgElement.left;
              const offsetY = event.clientY - svgElement.top;
              this.tooltip.style('left', (offsetX + 5) + 'px')
                .style('top', (offsetY - 28) + 'px');
            })
            .on('mouseout', () => {
              this.tooltip.style('opacity', 0);
            })
            .on('click', (event: any) => {
              this.logisticSearchService.activeState.next(d.properties.st_nm);
            });
      })
    }
  }

  mapprojection(data: any) {
    const height = this.height
    const width = this.width
    const projection = d3.geoMercator();
    const pathGenerator = d3.geoPath().projection(projection);

    projection.scale(1).translate([0, 0])
    const b = pathGenerator.bounds(data),
      s = 0.95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
      t: [number, number] = [(width - s * (b[1][0] + b[0][0])) / 1.5, (height - s * (b[1][1] + b[0][1])) / 2];

    projection.scale(s).translate(t);
    return [projection, pathGenerator]
  }

}
