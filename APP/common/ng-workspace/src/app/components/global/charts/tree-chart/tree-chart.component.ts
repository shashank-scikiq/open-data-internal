import { Component, HostListener, Input, OnInit } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';
import * as d3 from "d3";
import { StateCode } from '@openData/app/core/utils/map';
import { MapService } from '@openData/app/core/api/map/map.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-tree-chart',
  templateUrl: './tree-chart.component.html',
  styleUrl: './tree-chart.component.scss'
})
export class TreeChartComponent implements OnInit {
  metrix: any = 'map_total_orders_metrics';
  selectedState: any;
  isLoading: boolean = false;
  
  selectedStateOption: string = '';
  selectedDistrictOption: string = '';
  treeData: any = {};
  selectedValue: string = '';

  selectedType: string = 'states';

  districtOptions: string[] = [];
  stateOptions: string[] = [];
  options: string[] = [];
  issueInLoading: boolean = false;
  object = Object;

  private topSellerSubscription$ = new Subject<void>();

  constructor(
    private appService: AppService,
    private mapService: MapService
  ) { }

  ngOnInit(): void {
    this.appService.selectedMetrix$.subscribe((value) => {
      this.metrix = value;
    })
    this.stateOptions = Object.keys(StateCode);
    this.stateOptions.splice(this.stateOptions.indexOf('Total'), 1);
    this.stateOptions.sort();

    this.appService.dateRange$.subscribe((val: any) => {
      this.initChart();
    })

    this.mapService.selectedState$.subscribe(
      (state: any) => {
        this.selectedState = state;
        if (this.selectedState == 'TT') {
          this.selectedType = 'states';
          this.districtOptions = [];
          this.options = this.stateOptions;
          this.selectedStateOption = 'Maharashtra';
          this.selectedValue = this.selectedStateOption;
        } else {
          this.selectedType = 'districts';
          const data = this.appService.getStateAndDistrictData();
          
          this.districtOptions = data[this.selectedState?.toUpperCase()];
          this.districtOptions.sort();
          this.options = this.districtOptions;
          this.selectedDistrictOption = this.districtOptions[0];
          this.selectedStateOption = this.selectedState;
          this.selectedValue = this.selectedDistrictOption;
        }
        this.initChart();
      }
    )
  }

  initChart() {
    if (!this.selectedDistrictOption && !this.selectedStateOption) {
      return;
    }
    if (this.metrix !='map_total_zonal_commerce_metrics')
      return;
    this.topSellerSubscription$.next();
    this.isLoading = true;
    this.appService.getTopSellersData(this.selectedType, this.selectedStateOption, this.selectedDistrictOption).pipe(takeUntil(this.topSellerSubscription$)).subscribe(
      (response: any) => {
        this.treeData = response;
        this.isLoading = false;
        this.create_chart();
      }, (error: Error) => {
        this.isLoading = false;
        console.log(error);
      }
    );
  }

  updateSelection(option: any) {
    this.selectedType == 'states' ? this.selectedStateOption = option : this.selectedDistrictOption = option;
    this.initChart();
  }


  @HostListener('window:resize', ['$event'])
  onResize() {
    this.create_chart();
  }

  create_chart() {
    const container: any = d3.select("#inntraDistrictTree");
    const containerWidth: any = container.node().getBoundingClientRect().width;
    const width_wd = containerWidth; // Use the container's width
    const margin_mr = { top: 0, right: 0, bottom: 0, left: 0 }, // Remove left margin
      width_w = width_wd - margin_mr.left - margin_mr.right,
      height_t = 250 - margin_mr.top - margin_mr.bottom;
  
    d3.select("#inntraDistrictTree").selectAll("*").remove();
    let path = null;
  
    let svg_d3 = container
      .append("svg")
      .attr("width", width_wd)
      .attr("height", height_t + margin_mr.top + margin_mr.bottom)
      .append("g")
      .attr("class", "intd")
      .attr("transform", "translate(" + ((width_wd / 2) + 70) + "," + margin_mr.top + ")");
  
    let i = 0,
      duration = 750,
      root: any;
  
    let treemap = d3.tree().size([height_t, width_w]);
  
    root = d3.hierarchy(this.treeData, function (d) {
      return d.children;
    });
    root.x0 = height_t / 2;
    root.y0 = 0;
  
    root.children.forEach(collapse);
  
    update(root);
  
    function collapse(d: any) {
      if (d.children) {
        d._children = d.children;
        d._children.forEach(collapse);
        d.children = null;
      }
    }
  
    function update(source: any) {
      let treeData = treemap(root);
  
      let nodes = treeData.descendants(),
        links = treeData.descendants().slice(1);
  
      nodes.forEach(function (d: any) {
        d.y = d.depth * -80;
      });
  
      let node = svg_d3.selectAll("g.node").data(nodes, function (d: any) {
        return d.id || (d.id = ++i);
      });
  
      let nodeEnter: any = node
        .enter()
        .append("g")
        .attr("class", "node")
        .attr("transform", function (d: any) {
          return "translate(" + source.y0 + "," + source.x0 + ")";
        })
        .on("click", click);
  
      nodeEnter
        .append("circle")
        .attr("class", "node")
        .attr("r", 1e-6)
        .style("fill", function (d: any) {
          return d._children ? "lightgreen" : "#fff";
        });
  
      nodeEnter
        .append("foreignObject")
        .attr("x", function (d: any) {
          return -12;
        })
        .attr("y", -12)
        .attr("width", 24)
        .attr("height", 24)
        .attr("class", "node-icon")
        .html(function (d: any) {
          if (d.depth === 0) {
            return '<i class="fa-solid fa-house"></i>';
          } else {
            return '<i class="fa-solid fa-truck-arrow-right"></i>';
          }
        });
  
      nodeEnter
        .append("text")
        .attr("dy", ".35em")
        .attr("x", function (d: any) {
          return d.children || d._children ? 20 : -20;
        })
        .attr("text-anchor", function (d: any) {
          return d.children || d._children ? "start" : "end";
        })
        .text(function (d: any) {
          return d.data.name;
        });
  
      let nodeUpdate = nodeEnter.merge(node);
  
      nodeUpdate
        .transition()
        .duration(duration)
        .attr("transform", function (d: any) {
          return "translate(" + d.y + "," + d.x + ")";
        });
  
      nodeUpdate
        .select("circle.node")
        .attr("r", 12)
        .style("fill", function (d: any) {
          return d._children ? "lightgreen" : "#fff";
        })
        .attr("cursor", "pointer");
  
      let nodeExit = node.exit().transition().duration(duration).attr("transform", function (d: any) {
        return "translate(" + source.y + "," + source.x + ")";
      }).remove();
  
      nodeExit.select("circle").attr("r", 1e-6);
  
      nodeExit.select("text").style("fill-opacity", 1e-6);
  
      let link: any = svg_d3.selectAll("path.link").data(links, function (d: any) {
        return d.id;
      });
  
      let linkEnter = link
        .enter()
        .insert("path", "g")
        .attr("class", "link")
        .attr("d", function (d: any) {
          const o = { x: source.x0, y: source.y0 };
          return diagonal(o, o);
        });
  
      let linkUpdate = linkEnter.merge(link);
  
      linkUpdate
        .transition()
        .duration(duration)
        .attr("d", function (d: any) {
          return diagonal(d, d.parent);
        });
  
      let linkExit = link.exit().transition().duration(duration).attr("d", function (d: any) {
        const o = { x: source.x, y: source.y };
        return diagonal(o, o);
      }).remove();
  
      nodes.forEach(function (d: any) {
        d.x0 = d.x;
        d.y0 = d.y;
      });
  
      function diagonal(s: any, d: any) {
        path = `M ${s.y} ${s.x}
              C ${(s.y + d.y) / 2} ${s.x},
                ${(s.y + d.y) / 2} ${d.x},
                ${d.y} ${d.x}`;
  
        return path;
      }
  
      function click(d: any) {
        if (d.children) {
          d._children = d.children;
          d.children = null;
        } else {
          d.children = d._children;
          d._children = null;
        }
        update(d);
      }
    }
    this.isLoading = false;
  }
  
  
}