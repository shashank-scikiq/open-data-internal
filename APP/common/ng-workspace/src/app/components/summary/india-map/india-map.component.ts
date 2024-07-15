import { Component, ViewEncapsulation, ElementRef, Input, OnChanges, OnInit, SimpleChanges, ViewChild, HostListener, EventEmitter, Output, Renderer2 } from '@angular/core';
import * as d3 from "d3";
import * as topojson from 'topojson-client';
import { StateCode, getDistrictTooltipContent, getStateTooltipContent, NOCASEDATA } from '@openData/app/core/utils/map';
import { getMetrixKey } from '@openData/app/core/utils/global';
import { MapService } from '@openData/app/core/api/map/map.service';
import { NzMessageService } from 'ng-zorro-antd/message';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-india-map',
  templateUrl: './india-map.component.html',
  styleUrl: './india-map.component.scss',
  encapsulation: ViewEncapsulation.None
})
export class IndiaMapComponent implements OnInit, OnChanges {
  @Input() metrix: any = 'map_total_orders_metrics';
  @Input() mapStateData: any;
  @Input() mapStatewiseData: any;
  @Input() mapVisualOptions: any = {};
  @Output() setDistrictView = new EventEmitter<any>();



  showTooltip: boolean = false;
  mapDataInitialized: boolean = false;

  isLoadingMap: boolean = true;

  maxData: any = {};
  statemap_geojson: any = {};
  districtmap_geojson: any = {};
  state_meshData: any = {};
  stateSortedData: any = [];
  districtSortedData: any = [];



  chloroplethcolormapper3: any = {
    map_total_orders_metrics: ["#ffffff", "#FF7722"],
    map_total_active_sellers_metrics: ["#ffffff", "#1c75bc"],
    map_total_zonal_commerce_metrics: ["#ffffff", "#10b759"],
  }

  chloroplethcolormapper2: any = {
    map_total_orders_metrics: ["#ffffff", "#f9f0e9", "#FF7722"],
    map_total_active_sellers_metrics: ["#ffffff", "#dfebf5", "#1c75bc"],
    map_total_zonal_commerce_metrics: ["#ffffff", "#eefaf3", "#10b759"],
  }

  chloroplethStrokeColor: any = {
    map_total_orders_metrics: "#FF7722",
    map_total_active_sellers_metrics: "#1c75bc",
    map_total_zonal_commerce_metrics: "#10b759",
  }

  bubblecolormapper: any = {
    map_total_active_sellers_metrics: ["rgba(0,123,255,0.8)", "rgba(0,123,255,0.5)", "rgba(0,123,255,0.5)"],
    map_total_orders_metrics: ["rgba(227, 87, 10,0.8)", "rgba(227, 87, 10,0.4)", "rgba(227, 87, 10,0.4)"],
    map_total_zonal_commerce_metrics: ["rgba(16,183,89,0.8)", "rgba(16,183,89,0.5)", "rgba(16,183,89,0.5)"],
  }

  map_state_data: any = null;
  map_statewise_data: any = null;
  datajson: any = null;
  startDate: string = "2024-05-01";
  endDate: string = "2024-05-27";
  category: string = '';
  sub_category: string = '';
  state: string = '';

  @ViewChild('map') mapElement: ElementRef | undefined = undefined;

  constructor(
    private mapService: MapService,
    private appService: AppService,
    private message: NzMessageService,
    private renderer: Renderer2
  ) { }

  ngOnInit(): void {
    // this.appService.dateRange$.subscribe((value: any) => {
    //   this.isLoadingMap = true;
    //   this.initializeMap();
    // })
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.isLoadingMap = true;
    // if (this.mapDataInitialized)
    //   this.changeMapVisual();
    // else
      this.initializeMap();
  }

  @HostListener('window:resize', ['$event'])
  onResize() {
    this.isLoadingMap = true;
    this.changeMapVisual();
  }

  async initializeMap() {
    const lstOrderDemand = new Array();
    const lstActiveSellers = new Array();
    const lstTotalIntradistrictOrdersPercentage = new Array();
    const lstTotalIntrastateOrdersPercentage = new Array();

    this.mapStatewiseData.forEach((element: any) => {
      if (element.statecode != 'TT') {

        if (element.active_sellers <= 3) {
          element.active_sellers = 0
        }

        let orderDemand = element.order_demand ? element.order_demand : 0;
        let activeSellers = element.active_sellers ? element.active_sellers : 0;
        let totalIntradistrictOrdersPercentage = element.intradistrict_orders_percentage ? element.intradistrict_orders_percentage : 0;
        let totalIntrastateOrdersPercentage = element.intrastate_orders_percentage ? element.intrastate_orders_percentage : 0;

        lstOrderDemand.push(orderDemand);
        lstActiveSellers.push(activeSellers);
        lstTotalIntradistrictOrdersPercentage.push(totalIntradistrictOrdersPercentage);
        lstTotalIntrastateOrdersPercentage.push(totalIntrastateOrdersPercentage);

      }
    });
    const datajson = {
      cummulative: {
        od: lstOrderDemand,
        as: lstActiveSellers,
        tiso: lstTotalIntradistrictOrdersPercentage,
        tiso2: lstTotalIntrastateOrdersPercentage,
      },
      statewise: this.mapStatewiseData
    }

    this.maxData = {
      // map_total_orders_metrics: d3.max(datajson.cummulative.od, d => +d),
      map_total_active_sellers_metrics: datajson.cummulative.as && datajson.cummulative.as.length > 0 ? d3.max(datajson.cummulative.as, d => +d) : 0,
      map_total_orders_metrics: datajson.cummulative.od && datajson.cummulative.od.length > 0 ? d3.max(datajson.cummulative.od, d => +d) : 0,
      map_total_zonal_commerce_metrics: datajson.cummulative.tiso && datajson.cummulative.tiso.length > 0 ? d3.max(datajson.cummulative.tiso, d => +d) : 0,
    };

    const indiamapdata = await this.indiamapdataprocessed();
    this.statemap_geojson = topojson.feature(indiamapdata, indiamapdata.objects.states);
    this.stateSortedData = this.statemap_geojson.features.sort(
      (a: any, b: any) =>
        b.properties.totalcasedata[this.metrix] -
        a.properties.totalcasedata[this.metrix]
    );

    this.districtmap_geojson = topojson.feature(indiamapdata, indiamapdata.objects.districts);
    this.districtSortedData = this.districtmap_geojson.features.sort(
      (a: any, b: any) =>
        b.properties.totalcasedata[this.metrix] -
        a.properties.totalcasedata[this.metrix]
    );
    this.state_meshData = topojson.mesh(indiamapdata, indiamapdata.objects.states);
    this.mapDataInitialized = true;
    this.changeMapVisual();
  }

  mapprojection(data: any) {
    const el: any = document.getElementById("indiamap");

    const height = el.clientHeight
    const width = el.clientWidth
    const projection = d3.geoMercator();
    const pathGenerator = d3.geoPath().projection(projection);

    projection.scale(1).translate([0, 0])

    const b = pathGenerator.bounds(data),
      s = 0.95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
      t: [number, number] = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];

    projection.scale(s).translate(t);
    return [projection, pathGenerator]
  }

  setMapDatatitle(data: any, mapType: string = 'State') {
    const value = data.properties.totalcasedata[this.metrix];
    const metrixText = getMetrixKey(this.metrix);

    let state = `State: ${mapType == 'State' ? data.id : data.properties.st_nm}`;
    let district = `District: ${mapType == 'State' ? '' : data.properties.district}`;
    let metricValue;

    if (metrixText === "Registered Sellers" && (value <= 0 || value < 3)) {
      metricValue = 'No data available';
    } else if (metrixText === "Intrastate Percentage") {
      metricValue = `${value}%`;
    } else {
      metricValue = value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    return `<p class="margin-0 font-xxs text-center open-data-white"> ${state} <br/> ` + (mapType == 'District' ? ` ${district} <br/> ` : '') + `${metrixText} : ${metricValue} </p>`;

  }

  setIconContainer(caseType: any, mapprojectionresult: any, mapType: any, metrixText: any, mapVisualType: any, top3data: any) {
    const iconWidth = 35;
    const iconHeight = 35;
    const iconContainer = d3.select(`#india-${mapVisualType}`).append('g');
    iconContainer.html('');

    iconContainer
      .attr('class', 'icon-container')
      .style('fill', 'transparent')

    // .data(mapType == 'State' ? this.stateSortedData.slice(0, 3) : this.districtSortedData.slice(0, 3))
    iconContainer.selectAll('.topstMapIcon')
      .data(top3data)
      .enter()
      .filter((i: any) => i.properties.totalcasedata[caseType] > 0)
      .append('foreignObject')
      .attr('x', (el: any) => mapprojectionresult[0](d3.geoCentroid(el))[0] - iconWidth / 2 + 5)
      .attr('y', (el: any) => mapprojectionresult[0](d3.geoCentroid(el))[1] - 40)
      .attr('width', iconWidth)
      .attr('height', iconHeight)
      .attr('overflow', 'visible')
      .attr('d', (data: any) => mapprojectionresult[1](data))
      .attr("data-title", (i: any) => {
        return this.setMapDatatitle(i, mapType);
      })
      .html((i: any) => {
        let iconClass;
        let metricValue;
        let image;

        if (metrixText === "Registered Sellers") {
          iconClass = "pointer-icon fa-solid fa-user";
          metricValue = i.properties.totalcasedata[caseType];
        } else if (metrixText === "Intrastate Percentage") {
          iconClass = "pointer-icon fa-solid fa-truck-arrow-right";
          image = 'logistics-icon.svg';
          metricValue = `${i.properties.totalcasedata[caseType]}%`;
        } else {
          iconClass = "pointer-icon fa-solid fa-cart-shopping";
          metricValue = i.properties.totalcasedata[caseType];
        }

        return `<div class="pointer" nz-tooltip nzTooltipPlacement="top" 
        nzTooltipTitle="State: ${i.id}
          <br/>${metrixText}: ${metricValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}">
          <i class="${iconClass}"></i>
          </div><div class="pulse"></div>`;
      })
      .on('mouseover', function (event: any, d: any) {
        d3.select(this).attr('stroke-width', 2);
        const mouseX = event.offsetX;
        const mouseY = event.offsetY;
        const bbox = this.getBBox();

        // Calculate tooltip position (top center)
        const tooltipX = bbox.x + bbox.width / 2;
        const tooltipY = bbox.y;

        const tooltipContent = d3.select(this).attr("data-title");

        d3.select('.map-tooltip')
          .html(tooltipContent)
          .style('left', `${tooltipX}px`)
          .style('top', `${tooltipY - 20}px`)
          .transition()
          .duration(200)
          .style('visibility', 'visible');
      })
      .on('mouseout', function () {
        d3.select(this).attr('stroke-width', 0.5);
        d3.select('.map-tooltip').transition()
          .duration(200)
          .style('visibility', 'hidden');
      });
  }


  setChloroMap(caseType: any, mapType: string = 'State') {
    const mapGeopJson =
      mapType == 'State' ? this.statemap_geojson : this.districtmap_geojson;
    const mapprojectionresult: any = this.mapprojection(mapGeopJson);
    const color = d3.scaleSequentialLog(
      this.chloroplethcolormapper3[caseType]).domain([1, this.maxData[caseType]]
      );
    const sorteddata = mapGeopJson.features.sort((a: any, b: any) => b.properties.totalcasedata[this.metrix] - a.properties.totalcasedata[this.metrix]);
    const top3Data = sorteddata.slice(0, 3);

    const g = d3.select('#india-chloro');
    this.removeSvgContent();

    let customColorRange;

    const metrixText = getMetrixKey(caseType);

    if (metrixText === "map_total_zonal_commerce_metrics") {
      if (this.maxData[caseType] === 0) {
        let defaultRange: any = ["#ffffff", "#ffffff"];
        customColorRange = d3.scaleSequentialLog()
          .domain([0.1, 0.1])
          .range(defaultRange);
      } else {
        customColorRange = d3.scaleSequentialLog()
          .domain([0.1, this.maxData[caseType]])
          .range(this.chloroplethcolormapper3[caseType]);
      }
    } else {
      customColorRange = d3.scaleLinear()
        .domain([0, 1, this.maxData[caseType]])
        .range(this.chloroplethcolormapper2[caseType]);
    }

    // Append paths for the chloro map
    g.selectAll('path')
      .data(mapGeopJson.features)
      .enter()
      .append('path')
      .attr('d', (data: any) => mapprojectionresult[1](data))
      .attr('fill', (el: any) => customColorRange(el.properties.totalcasedata[caseType]))
      .attr('stroke-width', 0.5)
      // .attr('stroke', this.chloroplethStrokeColor[casetype])
      .attr('stroke', 'black')
      .attr('class', `cursor-pointer ${mapType == 'State' ? 'country' : 'district'}`)
      .attr("data-title", (i: any) => {
        return this.setMapDatatitle(i, mapType);
      })
      // .each((d: any, i: any, nodes: any) => {
      //   // console.log(dat, "here")
      //   const element = nodes[i];
      //   this.renderer.setAttribute(element, 'nz-tooltip', '');
      //   this.renderer.setAttribute(element, 'nzTooltipTitle', this.setMapDatatitle(d, mapType));
      // })
      // nz-tooltip nzTooltipTitle="prompt text"
      .on('mouseover', function (event: any, d: any) {
        d3.select(this).attr('stroke-width', 2);
        const bbox = this.getBBox();
        // console.log(bbox)

        // Calculate tooltip position (top center)
        const tooltipX = bbox.x + (bbox.width /2);
        // const tooltipY = mapType == 'District' ? bbox.y - 30 : bbox.y;
        const tooltipY = bbox.y;

        const tooltipContent = d3.select(this).attr("data-title");

        d3.select('.map-tooltip')
          .html(tooltipContent)
          .style('left', `${tooltipX}px`)
          .style('top', `${tooltipY -10}px`)
          .transition()
          .duration(200)
          .style('visibility', 'visible');

        d3.select('.desktop-tooltip').html(
          mapType == 'State' ?
            getStateTooltipContent(d, caseType, color, top3Data) :
            getDistrictTooltipContent(d, caseType, color, top3Data)
        ).style('visibility', 'visible');
      })
      .on('mouseout', function () {
        d3.select(this).attr('stroke-width', 0.5);
        d3.select('.map-tooltip').transition()
          .duration(200)
          .style('visibility', 'hidden');
        d3.select('.desktop-tooltip').style('visibility', 'hidden');
      })
      .on('click', (event: any, d: any) => {
        this.setState(d);
      })

    this.setIconContainer(caseType, mapprojectionresult, mapType, metrixText, 'chloro', top3Data);

    this.addLegend(customColorRange, caseType, this.maxData[caseType], metrixText);
  }

  addLegend(customColorRange: any, casetype: any, maxdata: any, metricText: any) {
    const legendContainer = d3.select('#mapLegends');
    legendContainer.html('');

    // Define legend values for 8 sections
    const legendValues = [0, ...Array.from({ length: 4 }, (_, i) => (i + 1) * maxdata / 4)];

    const newLegendContainer = legendContainer.append('svg')
      .attr('class', 'legend')
      .attr('width', '100%')

    // newLegendContainer.append('text')
    //   .attr('x', 0)
    //   .attr('y', 10)
    //   .attr('transform', 'translate(0, 0)')
    //   .style('text-anchor', 'start')
    //   .style('fill', 'black')
    //   .style('font-size', '10px')
    //   .text(`${metricText}`);

    const legend = newLegendContainer.selectAll('g')
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

        if (casetype === "map_total_zonal_commerce_metrics") {
          if (i === 0) {
            return startRange.toLocaleString();
          } else if (i === 1) {
            return `< ${endRange.toLocaleString()}%`;
          } else if (i === legendValues.length - 1) {
            return `> ${endRange.toLocaleString()}%`;
          } else {
            return `${startRange.toLocaleString()}%-${endRange.toLocaleString()}%`;
          }
        } else if (casetype === "map_total_active_sellers_metrics" && d === 0) {
          return 'No Data';
        } else {
          if (i === 0) {
            return startRange.toLocaleString();
          } else if (i === 1) {
            return `< ${endRange.toLocaleString()}`;
          } else if (i === legendValues.length - 1) {
            return `> ${startRange.toLocaleString()}`;
          } else {
            return `${startRange.toLocaleString()}-${endRange.toLocaleString()}`;
          }
        }
      });

    legend.attr('transform', (d, i) => `translate(0, ${i * (200 / 9) + 20})`);
    this.isLoadingMap = false;
  }

  async indiamapdataprocessed() {
    const indiamapdatares = await fetch('static/assets/data/map/india.json');
    const indiamapdata = await indiamapdatares.json();

    const statecasedata = this.mapStateData;
    indiamapdata.objects.states.geometries.forEach((el: any) => {
      el.properties.st_code = + el.properties.st_code
      let statecode = StateCode[el.id];

      if (statecasedata[statecode]) {
        let state_case_data = statecasedata[statecode]

        let order_demand = state_case_data.total.order_demand ? state_case_data.total.order_demand : 0
        let active_sellers = state_case_data.total.active_sellers ? state_case_data.total.active_sellers : 0
        let total_intrastate_orders_percentage = state_case_data.total.intrastate_percentage
          ? state_case_data.total.intrastate_percentage : 0;

        if (active_sellers <= 3) {
          active_sellers = 0
        }
        el.properties['totalcasedata'] = {
          map_order_demand: order_demand,
          map_total_orders_metrics: order_demand,
          map_total_active_sellers_metrics: active_sellers,
          map_total_zonal_commerce_metrics: total_intrastate_orders_percentage,
        }
      }
      else {
        el.properties['totalcasedata'] = NOCASEDATA
      }
    })

    indiamapdata.objects.districts.geometries.forEach((el: any) => {
      el.properties.dt_code = + el.properties.dt_code
      el.properties.st_code = + el.properties.st_code

      let districtname = el.properties.district
      districtname = districtname.toUpperCase();
      let statename = el.properties.st_nm
      let statecode = StateCode[statename];

      if (statecasedata[statecode]) {

        let state_case_data = statecasedata[statecode]
        let district_data = state_case_data.districts

        let order_demand = state_case_data.total.order_demand ? state_case_data.total.order_demand : 0
        let active_sellers = state_case_data.total.active_sellers ? state_case_data.total.active_sellers : 0
        let total_intradistrict_orders_percentage = state_case_data.total.intradistrict_orders_percentage ? state_case_data.total.intradistrict_orders_percentage : 0;

        const state_inside_district_obj = {
          map_order_demand: order_demand,
          map_total_orders_metrics: order_demand,
          map_total_active_sellers_metrics: active_sellers,
          map_total_zonal_commerce_metrics: total_intradistrict_orders_percentage,
        }

        let matchFound = false;
        let each_district_data;
        if (district_data[districtname]) {
          each_district_data = district_data[districtname];
          matchFound = true;
        }

        if (matchFound && each_district_data) {
          let order_demand = each_district_data.order_demand ? each_district_data.order_demand : 0;
          let total_intradistrict_orders_percentage = each_district_data.intradistrict_percentage ? each_district_data.intradistrict_percentage : 0;
          let active_sellers = each_district_data.active_sellers ? each_district_data.active_sellers : 0;

          el.properties['totalcasedata'] = {
            map_order_demand: order_demand,
            map_total_orders_metrics: order_demand,
            map_total_active_sellers_metrics: active_sellers,
            map_total_zonal_commerce_metrics: total_intradistrict_orders_percentage,
            st_data: state_inside_district_obj
          };
        } else {
          el.properties['totalcasedata'] = NOCASEDATA;
        }
      } else {
        el.properties['totalcasedata'] = NOCASEDATA;
      }
    })
    return indiamapdata;
  }


  renderstateborder() {
    const mapprojectionresult = this.mapprojection(this.statemap_geojson)
    d3.select('#state-border')
      .append("path")
      .attr("stroke", this.bubblecolormapper[this.metrix][2])
      .attr("stroke-width", 1.5)
      .style('z-index', 5)
      .attr('fill', 'none')
      .attr("d", mapprojectionresult[1](this.state_meshData));
  }

  bubbleLegend(bubbleradius: any) {
    const legendContainer = d3.select('#mapLegends');
    legendContainer.html('');

    const legendData = [
      { label: 'Low', radius: bubbleradius(0), value: 0, color: this.bubblecolormapper[this.metrix][0] },
      { label: 'Medium', radius: bubbleradius(this.maxData[this.metrix] * 0.5), value: Math.floor(this.maxData[this.metrix] * 0.5), color: this.bubblecolormapper[this.metrix][0] },
      { label: 'High', radius: bubbleradius(this.maxData[this.metrix]), value: Math.floor(this.maxData[this.metrix]), color: this.bubblecolormapper[this.metrix][1] }
    ];

    const newLegendContainer = legendContainer.append('svg')
      .attr('class', 'legend')
      .attr('width', "100%")
      .attr('height', "100%")

    const legendItems = newLegendContainer.selectAll('g')
      .data(legendData)
      .enter().append('g')
      .attr('class', 'legend-item')
      .attr('transform', `translate(20, 80)`);

    legendItems.append('circle')
      .attr('cx', 30)
      .attr('cy', (d, i) => `${30 - (i * 15)}`)
      .attr('r', (d, i) => `${i * (1 * 15) + 5}`)
      .attr('fill', 'transparent')
      .attr('stroke', d => d.color)
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
      .text(d => {
        if (this.metrix === 'map_total_zonal_commerce_metrics') {
          // return `${d.label}: ${d.value.toLocaleString()}%`;
          return `${d.value.toLocaleString()}%`;
        } else if (this.metrix === 'map_total_active_sellers_metrics' && d.value < 3) {
          // return `${d.label}: No Data`;
          return `0`;
        } else {
          // return `${d.label}: ${d.value.toLocaleString()}`;
          return `${d.value.toLocaleString()}`;
        }
      });

    this.isLoadingMap = false;
  }

  setbubblemap(caseType: any, mapType: any) {
    this.renderstateborder();
    const mapGeopJson =
      mapType == 'State' ? this.statemap_geojson : this.districtmap_geojson;
    const mapprojectionresult: any = this.mapprojection(mapGeopJson);
    const metrixText = getMetrixKey(this.metrix);
    const color = d3.scaleSequentialLog(this.chloroplethcolormapper2[this.metrix]).domain([1, this.maxData[this.metrix]]);

    const bubbleradius = d3.scaleSqrt()
      .domain([0, this.maxData[this.metrix]])
      .range([3, 40]);

    const sortedData = mapGeopJson.features.sort((a: any, b: any) => b.properties.totalcasedata[caseType] - a.properties.totalcasedata[this.metrix]);
    const top3Data = sortedData.slice(0, 3);

    const g = d3.select('#india-bubble');

    g.selectAll('circle')
      .data(sortedData)
      .enter()
      .append('circle')
      .attr('cx', (el: any) => mapprojectionresult[0](d3.geoCentroid(el))[0])
      .attr('cy', (el: any) => mapprojectionresult[0](d3.geoCentroid(el))[1])
      // .attr('r', (el) => bubbleradius(el.properties.totalcasedata[casetype]))
      .attr('r', (el: any) => {
        const value = el.properties.totalcasedata[this.metrix];
        return value ? Math.min(40, Math.max(3, bubbleradius(value))) : 3;
      })
      .attr('stroke', this.bubblecolormapper[this.metrix][0])
      .attr('fill', this.bubblecolormapper[this.metrix][0])
      .attr('fill-opacity', 0.25)
      .attr('class', 'cursor-pointer')
      .attr('stroke-width', 1)
      .attr("data-title", (i: any) => {
        return this.setMapDatatitle(i, mapType);
      })
      .on('mouseover', function (event: any, d: any) {
        d3.select(this).attr('stroke-width', 2);
        const mouseX = event.offsetX;
        const mouseY = event.offsetY;
        const bbox = this.getBBox();

        // Calculate tooltip position (top center)
        const tooltipX = bbox.x + (bbox.width /2);
        // const tooltipY = mapType == 'District' ? bbox.y - 30 : bbox.y;
        const tooltipY = bbox.y;

        const tooltipContent = d3.select(this).attr("data-title");

        d3.select('.map-tooltip')
          .html(tooltipContent)
          .style('left', `${tooltipX}px`)
          .style('top', `${tooltipY - 10}px`)
          .transition()
          .duration(200)
          .style('visibility', 'visible');

        d3.select('.desktop-tooltip').html(
          mapType == 'State' ?
            getStateTooltipContent(d, caseType, color, top3Data) :
            getDistrictTooltipContent(d, caseType, color, top3Data)
        ).style('visibility', 'visible');
      })
      .on('mouseout', function () {
        d3.select(this).attr('stroke-width', 1);
        d3.select('.map-tooltip').transition()
          .duration(200)
          .style('visibility', 'hidden');
        d3.select('.desktop-tooltip').style('visibility', 'hidden');
      })
      .on('click', (event: any, d: any) => {
        this.setState(d);
      })
    this.setIconContainer(caseType, mapprojectionresult, mapType, metrixText, 'bubble', top3Data);

    this.bubbleLegend(bubbleradius);
  }

  removeSvgContent() {
    d3.select('#state-border').selectAll('path').remove();
    d3.select('#district-border').selectAll('path').remove();
    d3.select('#india-chloro').selectAll('path').remove();
    d3.select('#india-bubble').selectAll('circle').remove();
    d3.select('#india-chloro').select('.icon-container').remove();
    d3.select('#india-bubble').select('.icon-container').remove();
  }

  setState(data: any) {
    if (this.metrix == "map_total_active_sellers_metrics") {
      this.message.create('error', 'State click is not available on Active Seller', { nzDuration: 1000 });
      return;
    }
    const stateName = data.properties.st_nm;
    this.mapService.setSelectedState(stateName);
  }

  changeMapVisual() {
    this.removeSvgContent();
    if (this.mapVisualOptions.isDistrictMap && this.mapVisualOptions.isChloropeth) {
      this.setChloroMap(this.metrix, 'District');
    }
    else if (this.mapVisualOptions.isDistrictMap && this.mapVisualOptions.isBubble) {
      this.setbubblemap(this.metrix, 'District');
    }
    else if (this.mapVisualOptions.isStateMap && this.mapVisualOptions.isChloropeth) {
      this.setChloroMap(this.metrix);
    }
    else {
      this.setbubblemap(this.metrix, 'State');
    }
  }

}