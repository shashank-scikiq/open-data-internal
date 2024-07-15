import { Component, HostListener, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import * as topojson from 'topojson-client';
import * as d3 from "d3";
import { MapService } from '@openData/app/core/api/map/map.service';
import { NOCASEDATA, StateCode, getDistrictTooltipContent } from '@openData/app/core/utils/map';
import { getMetrixKey } from '@openData/core/utils/global';

@Component({
  selector: 'app-state-map',
  templateUrl: './state-map.component.html',
  styleUrl: './state-map.component.scss'
})
export class StateMapComponent implements OnInit, OnChanges {
  @Input() metrix: any = '';
  @Input() mapStateData: any;
  @Input() mapVisualOptions: any = {};


  selectedStateName: string = 'TT';
  selectedStateCode: string = 'TT';
  maxData: any = {};
  isLoadingMap: boolean = false;
  mapDataInitialized: boolean = false;


  bubblecolormapper: any = {
    map_total_active_sellers_metrics: ["rgba(0,123,255,0.8)", "rgba(0,123,255,0.5)", "rgba(0,123,255,0.5)"], // Product
    map_total_orders_metrics: ["rgba(253,127,58,0.8)", "rgba(253,127,58,0.5)", "rgba(253,127,58,0.5)"], // Seller
    map_total_zonal_commerce_metrics: ["rgba(16,183,89,0.8)", "rgba(16,183,89,0.5)", "rgba(16,183,89,0.5)"], // Pincode
  }


  chloroplethcolormapper3: any = {
    map_total_orders_metrics: ["#ffffff", "#FF7722"],
    map_total_active_sellers_metrics: ["#ffffff", "#1c75bc"],
    map_total_zonal_commerce_metrics: ["#ffffff", "#10b759"],
  }
  chloroplethcolormapper2: any = {
    map_total_orders_metrics: ["#ffffff", "#f9f0e9", "#FF7722"],
    map_total_active_sellers_metrics: ["#ffffff", "#dfebf5", "#1c75bc"],
    map_total_zonal_commerce_metrics: ["#ffffff", "#71d49c", "#10b759"],
  }

  top3Data: any = [];

  eachStateTopo: any;
  eachStateGeojson: any;
  eachStateMesh: any

  constructor(
    private mapService: MapService
  ) { }

  ngOnInit(): void {
    this.mapService.selectedState$.subscribe(
      (value: any) => {
        this.selectedStateName = value;
        this.plotStateMap();
      }
    );
  }

  ngOnChanges(changes: SimpleChanges): void {
    // if (this.mapDataInitialized)
    //   this.changeMapVisual();
    this.plotStateMap();
  }

  @HostListener('window:resize', ['$event'])
  onResize() {
    this.changeMapVisual();
  }


  async plotStateMap() {
    let latest_state_json = this.mapStateData;
    this.selectedStateCode = StateCode[this.selectedStateName];

    let state_card_data: any = {};
    let lst_order_demand: any = [];
    let lst_active_sellers: any = [];
    let lst_total_intradistrict_percentage: any = [];

    if (this.selectedStateCode in latest_state_json) {
      if (typeof latest_state_json[this.selectedStateCode].districts === 'object' && latest_state_json[this.selectedStateCode].districts !== null) {
        Object.keys(latest_state_json[this.selectedStateCode].districts).forEach(key => {
          const element = latest_state_json[this.selectedStateCode].districts[key];
          if (element.active_sellers <= 3) {
            element.active_sellers = 0;
          }
          let order_demand_st = element.order_demand || 0;
          let active_sellers_st = element.active_sellers || 0;
          let total_intradistrict_percentage_st = element.intradistrict_percentage || 0;

          lst_order_demand.push(order_demand_st);
          lst_active_sellers.push(active_sellers_st);
          lst_total_intradistrict_percentage.push(total_intradistrict_percentage_st);
        });

        state_card_data['active_sellers'] = lst_active_sellers;
        state_card_data['order_demand'] = lst_order_demand;
        state_card_data['intradistrict_percentage'] = lst_total_intradistrict_percentage;

      }
    } else {
      latest_state_json[this.selectedStateCode] = {};
      latest_state_json[this.selectedStateCode]["districts"] = {};
      latest_state_json[this.selectedStateCode]["districts"][this.selectedStateName] = {
        "order_demand": "0",
        "total_items_delivered": "0",
        "active_sellers": 0,
        "intradistrict_orders": "0",
        "intrastate_orders": "0",
        "intradistrict_percentage": "0",
        "intrastate_percentage": "0"
      };
      latest_state_json[this.selectedStateCode]["total"] = {
        "order_demand": "0",
        "total_items_delivered": "0",
        "active_sellers": 0,
        "intradistrict_orders": "0",
        "intrastate_orders": "0",
        "intradistrict_percentage": "0",
        "intrastate_percentage": "0"
      };
      state_card_data = latest_state_json[this.selectedStateCode].total;
    }

    if (state_card_data.active_sellers <= 3) {
      state_card_data.active_sellers = 0;
    }

    this.maxData = {
      map_total_active_sellers_metrics: state_card_data.active_sellers && state_card_data.active_sellers.length > 0 ? d3.max(state_card_data.active_sellers, (d: any) => +d) : 0,
      map_total_orders_metrics: state_card_data.order_demand && state_card_data.order_demand.length > 0 ? d3.max(state_card_data.order_demand, (d: any) => +d) : 0,
      map_total_zonal_commerce_metrics: state_card_data.intradistrict_percentage && state_card_data.intradistrict_percentage.length > 0 ? d3.max(state_card_data.intradistrict_percentage, (d: any) => +d) : 0
    };
    if (this.selectedStateName !== 'TT') {
      await this.fetchspecificmapdata();
      // this.setChloroMap(this.metrix);
      this.mapDataInitialized = true;
      this.changeMapVisual();
    }
    // this.buttontoggle(this.maxData);
  }

  setChloroMap(caseType: any) {
    const mapprojectionresult = this.mapprojection(this.eachStateGeojson);
    const color = d3.scaleSequentialLog(this.chloroplethcolormapper3[caseType]).domain([1, this.maxData[caseType]]);
    const sortedData = this.eachStateGeojson.features.sort((a: any, b: any) => b.properties.totalcasedata[caseType] - a.properties.totalcasedata[caseType]);
    const top3Data = sortedData.slice(0, 3);

    const iconWidth = 35;
    const iconHeight = 35;

    let customColorRange;

    const metricText = getMetrixKey(caseType);

    if (metricText === "map_total_orders_metrics") {
      customColorRange = d3.scaleLinear()
        .domain([0, 1, this.maxData[caseType]])
        .range(this.chloroplethcolormapper2[caseType]);
    } else if (metricText === "map_total_active_sellers_metrics") {
      customColorRange = d3.scaleLinear()
        .domain([0, 1, this.maxData[caseType]])
        .range(this.chloroplethcolormapper2[caseType]);
    } else if (metricText === "map_total_zonal_commerce_metrics") {
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

    const g = d3.select('#each-state-chloro');

    if (getMetrixKey(caseType) === "Intrastate Percentage") {
      var metricTextKey: any = "Intradistricts Percentage";
    } else {
      var metricTextKey: any = getMetrixKey(caseType);
    }
    g.selectAll('path')
      .data(this.eachStateGeojson.features)
      .enter()
      .append('path')
      .attr('d', (data: any) => mapprojectionresult[1](data))
      .attr('fill', (el: any) => customColorRange(el.properties.totalcasedata[caseType]))
      .attr('stroke-width', 0.5)
      .attr('stroke', 'black')
      .attr('class', 'state cursor-pointer')
      .attr("data-title", (i: any) => {
        return this.setMapDatatitle(i);
      })
      .on('mouseover', function (event, d) {
        // handleMouseover.call(this, event, d, caseType, color, top3Data);
        d3.select(this).attr('stroke-width', 2);

        const bbox = this.getBBox();

        // Calculate tooltip position (top center)
        const tooltipX = bbox.x + (bbox.width / 2);
        const tooltipY = bbox.y;

        const tooltipContent = d3.select(this).attr("data-title");
        d3.select('.map-tooltip')
          .html(tooltipContent)
          .style('left', `${tooltipX}px`)
          .style('top', `${tooltipY + 10}px`)
          .transition()
          .duration(200)
          .style('visibility', 'visible');

        d3.select('.desktop-tooltip').html(
          getDistrictTooltipContent(d, caseType, color, top3Data)
        ).style('visibility', 'visible');

      })
      .on('mouseout', function () {
        d3.select(this).attr('stroke-width', 0.5);
        d3.select('.map-tooltip').transition()
          .duration(200)
          .style('visibility', 'hidden');
        d3.select('.desktop-tooltip').style('visibility', 'hidden');

      });

    this.setIconContainer(caseType, mapprojectionresult, getMetrixKey(caseType), 'chloro', top3Data);

    this.addLegend(customColorRange, caseType, this.maxData[caseType]);
  }

  addLegend(customColorRange: any, caseType: any, maxdata: any) {
    const legendContainer = d3.select('#mapLegends');
    legendContainer.html('');

    const maxDivisions: any = maxdata < 50 ? 2 : 5;

    const divisionFactor = maxDivisions === 1 ? maxdata : maxdata / (maxDivisions - 1);

    const legendValues = [0, ...Array.from({ length: maxDivisions - 1 }, (_, i) => (i + 1) * divisionFactor)];

    const legendHeight = 20;
    const newLegendContainer = legendContainer.append('svg')
      .attr('class', 'legend')
      .attr('width', "100%")
      .attr('height', legendHeight * maxDivisions + 40)

    // newLegendContainer.append('text')
    //   .attr('x', 0)
    //   .attr('y', 10)
    //   .attr('transform', 'translate(0, 0)')
    //   .style('text-anchor', 'start')
    //   .style('fill', 'black')
    //   .text(`${getMetrixKey(caseType)}`);


    const legend = newLegendContainer.selectAll('g')
      .data(legendValues)
      .enter()
      .append('g')
      .attr('class', 'legend')
      .attr('transform', (d, i) => `translate(0, ${i * (200 / 8) + 20})`);

    legend.append('rect')
      .attr('width', 18)
      .attr('height', 18)
      .style('stroke', 'black')
      .style('stroke-width', '1px')
      .style('fill', (d) => customColorRange(d, maxdata));

    legend.append('text')
      .attr('x', 25)
      .attr('y', 9)
      .attr('dy', '.35em')
      .style('text-anchor', 'start')
      .style('font-size', '12px')
      .text((d, i) => {
        const startRange = i === 0 ? '0' : Math.floor(legendValues[i - 1]) + 1;
        const endRange = Math.floor(d);

        if (caseType === "map_total_zonal_commerce_metrics") {
          if (i === 0) {
            return `${startRange.toLocaleString()}%`;
          } else if (i === 1) {
            return `< ${endRange.toLocaleString()}%`;
          } else if (i === legendValues.length - 1) {
            return `> ${startRange.toLocaleString()}%`;
          } else {
            return `${startRange.toLocaleString()}%-${endRange.toLocaleString()}%`;
          }
        } else if (caseType === "map_total_active_sellers_metrics" && d === 0) {
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
  }

  setMapDatatitle(data: any) {
    const value = data.properties.totalcasedata[this.metrix];
    const metrixText = getMetrixKey(this.metrix);

    let state = `State: ${data.properties.st_nm}`;
    let district = `District: ${data.properties.district}`;
    let metricValue;

    if (metrixText === "Registered Sellers" && (value <= 0 || value < 3)) {
      metricValue = 'No data available';
    } else if (metrixText === "Intrastate Percentage") {
      metricValue = `${value}%`;
    } else {
      metricValue = value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    return `<p class="margin-0 font-xxs text-center open-data-white">
      ${state} <br/> ${district} <br/> ${metrixText} : ${metricValue} </p>`;

  }

  setIconContainer(caseType: any, mapprojectionresult: any, metrixText: any, mapVisualType: any, top3Data: any) {
    const iconWidth = 35;
    const iconHeight = 35;
    const iconContainer = d3.select(`#each-state-${mapVisualType}`).append('g');
    iconContainer.html('');

    iconContainer
      .attr('class', 'icon-container')
      .style('fill', 'transparent')

    iconContainer.selectAll('.topstMapIcon')
      .data(top3Data)
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
        return this.setMapDatatitle(i);
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
        const bbox = this.getBBox();

        // Calculate tooltip position (top center)
        const tooltipX = bbox.x + (bbox.width / 2);
        const tooltipY = bbox.y;

        const tooltipContent = d3.select(this).attr("data-title");

        d3.select('.map-tooltip')
          .html(tooltipContent)
          .style('left', `${tooltipX}px`)
          .style('top', `${tooltipY - 10}px`)
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

  mapprojection(data: any) {
    const el: any = document.getElementById("statemap")
    const height = el.clientHeight
    const width = el.clientWidth
    const projection = d3.geoMercator();
    const pathGenerator = d3.geoPath().projection(projection);

    projection.scale(1).translate([0, 0])

    const b = pathGenerator.bounds(data),
      s = 0.95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
      t: any = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];

    projection.scale(s).translate(t);

    return [projection, pathGenerator]
  }

  plotEachStateBorder(casetype: any) {
    let mapprojectionresult = this.mapprojection(this.eachStateGeojson)

    d3.select('#each-state-border')
      .append("path")
      .attr("stroke", this.bubblecolormapper[casetype][2])
      .attr("stroke-width", 1.5)
      .style('z-index', 5)
      .attr('fill', 'none')
      .attr("d", mapprojectionresult[1](this.eachStateMesh));
  }

  normalizeString(str: string) {
    return str.toUpperCase().trim().replace(/\s+/g, '').replace(/[.,'’]/g, '');
  }

  async fetchspecificmapdata() {
    const formattedStateFileName = this.selectedStateName.replaceAll(' ', '').toLowerCase();
    let res = await fetch(`static/assets/data/map/${formattedStateFileName}.json`);
    let each_state_map_data = await res.json();
    let latest_state_json = this.mapStateData;

    let each_district_data = latest_state_json[this.selectedStateCode].districts;

    each_state_map_data.objects.districts.geometries.forEach((el: any) => {
      let districtName = (el.properties.district).toUpperCase().trim().replace(/\s+/g, ' ').replace(/[.,'’]/g, '');
      let normalizedDistrictName = this.normalizeString(districtName);

      let matchFound = false;
      let total_data;

      if (each_district_data[districtName]) {
        total_data = each_district_data[districtName];
        matchFound = true;
      } else if (each_district_data[normalizedDistrictName]) {
        total_data = each_district_data[normalizedDistrictName];
        matchFound = true;
      }

      if (matchFound) {
        if (total_data.active_sellers <= 3) {
          total_data.active_sellers = 0
        }

        el.properties['totalcasedata'] = {
          map_total_orders_metrics: total_data.order_demand ? total_data.order_demand : 0,
          map_total_active_sellers_metrics: total_data.active_sellers ? total_data.active_sellers : 0,
          map_total_zonal_commerce_metrics: total_data.intradistrict_percentage ? total_data.intradistrict_percentage : 0,
        };
      } else {
        el.properties['totalcasedata'] = NOCASEDATA;
      }
    });


    this.eachStateTopo = each_state_map_data;
    this.eachStateGeojson = topojson.feature(this.eachStateTopo, this.eachStateTopo.objects.districts);
    this.eachStateMesh = topojson.mesh(this.eachStateTopo, this.eachStateTopo.objects.districts);

    // this.each_state_border(each_state_geojson, each_state_mesh, metricValue);
  }
  removeSvgContent() {
    d3.select('#each-state-border').selectAll('path').remove();
    d3.select('#each-state-chloro').selectAll('path').remove();
    d3.select('#each-state-bubble').selectAll('circle').remove();
    d3.select('#each-state-chloro').select('.icon-container').remove();
    d3.select('#each-state-bubble').select('.icon-container').remove();
  }

  setBubbleMap(caseType: any) {
    d3.select('#each-state-chloro').select('.icon-container').remove();

    const color = d3.scaleSequentialLog(this.chloroplethcolormapper2[caseType]).domain([1, this.maxData[caseType]]);
    const sortedData = this.eachStateGeojson.features.sort(
      (a: any, b: any) => b.properties.totalcasedata[caseType] - a.properties.totalcasedata[caseType]
    );
    const top3Data = sortedData.slice(0, 3);
    const iconWidth = 35;
    const iconHeight = 35;

    let customColorRange;
    const metricText = getMetrixKey(caseType);
    if (metricText === "Total Orders ") {
      customColorRange = d3.scaleLinear()
        .domain([0, 1, this.maxData[caseType]])
        .range(this.chloroplethcolormapper2[caseType]);
    } else if (metricText === "Registered Sellers") {
      customColorRange = d3.scaleLinear()
        .domain([0, 1, this.maxData[caseType]])
        .range(this.chloroplethcolormapper2[caseType]);
    } else if (metricText === "Intrastate Percentage") {
      customColorRange = d3.scaleLinear()
        .domain([0, 1, this.maxData[caseType]])
        .range(this.chloroplethcolormapper2[caseType]);
    } else {
      customColorRange = d3.scaleLinear()
        .domain([0, 0.1, this.maxData[caseType]])
        .range(this.chloroplethcolormapper2[caseType]);
    }
    let metricTextKey: any;
    if (getMetrixKey(caseType) === "Intrastate Percentage") {
      metricTextKey = "Intradistricts Percentage";
    } else {
      metricTextKey = getMetrixKey(caseType);
    }


    const g = d3.select('#each-state-bubble')

    const bubbleradius = d3.scaleSqrt()
      .domain([0, this.maxData[caseType]])
      .range([3, 40]);

    const mapprojectionresult: any = this.mapprojection(this.eachStateGeojson)

    

    g.selectAll('circle')
      .data(sortedData)
      .enter()
      .append('circle')
      .attr('cx', (el: any) => mapprojectionresult[0](d3.geoCentroid(el))[0])
      .attr('cy', (el: any) => mapprojectionresult[0](d3.geoCentroid(el))[1])
      // .attr('r', (el) => bubbleradius(el.properties.totalcasedata[casetype]))
      .attr('r', (el: any) => {
        const value = el.properties.totalcasedata[caseType];
        return value ? Math.min(40, Math.max(3, bubbleradius(value))) : 3;
      })
      .attr('stroke', this.bubblecolormapper[caseType][0])
      .attr('fill', this.bubblecolormapper[caseType][0])
      .attr('fill-opacity', 0.25)
      .attr('stroke-width', 1)

      .attr("data-title", (i: any) => {
        return this.setMapDatatitle(i);
      })
      .on('mouseover', function (event, d) {
        // handleMouseover.call(this, event, d, caseType, color, top3Data);
        const bbox = this.getBBox();

        // Calculate tooltip position (top center)
        const tooltipX = bbox.x + (bbox.width / 2);
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
          getDistrictTooltipContent(d, caseType, color, top3Data)
        ).style('visibility', 'visible');

      })
      .on('mouseout', function () {
        d3.select(this).attr('stroke-width', 0.5);
        d3.select('.map-tooltip').transition()
          .duration(200)
          .style('visibility', 'hidden');
        d3.select('.desktop-tooltip').style('visibility', 'hidden');

      });

    this.setIconContainer(caseType, mapprojectionresult, getMetrixKey(caseType), 'bubble', top3Data);

    this.bubbleLegend(bubbleradius);
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
          return `${d.value.toLocaleString()}%`;
        } else if (this.metrix === 'map_total_active_sellers_metrics' && d.value < 3) {
          return `0`;
        } else {
          return `${d.value.toLocaleString()}`;
        }
      });

    this.isLoadingMap = false;
  }

  setDistrictBorder() {
    let mapprojectionresult = this.mapprojection(this.eachStateGeojson)

    d3.select('#each-state-border')
      .append("path")
      .attr("stroke", this.bubblecolormapper[this.metrix][2])
      .attr("stroke-width", 1.5)
      .style('z-index', 5)
      .attr('fill', 'none')
      .attr("d", mapprojectionresult[1](this.eachStateMesh));
  }

  changeMapVisual() {
    // this.isLoadingMap = false;
    this.removeSvgContent();
    if (this.mapVisualOptions.isChloropeth) {
      this.setChloroMap(this.metrix);
    }
    else {
      this.setDistrictBorder();
      this.setBubbleMap(this.metrix);
    }
  }
}
