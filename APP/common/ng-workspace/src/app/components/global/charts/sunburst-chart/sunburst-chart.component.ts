import { Component, OnInit, HostListener, Input, EventEmitter, Output } from '@angular/core';

declare var Plotly: any;

@Component({
  selector: 'app-sunburst-chart',
  templateUrl: './sunburst-chart.component.html',
  styleUrls: ['./sunburst-chart.component.scss']
})
export class SunburstChartComponent implements OnInit {
  @Input() chartData: any = {};
  @Output() clickedCategory = new EventEmitter<any>();
  data: any;
  layout: any;
  config: any;
  isNoData: boolean = true; 

  constructor() {
  }

  ngOnInit(): void {
    this.plotSunburstChart();
  }

  plotSunburstChart() {
    if(!Object.keys(this.chartData).length) {
      this.isNoData = true;
      return;
    }
    this.isNoData = false;
    
    this.data = [{
      type: "sunburst",
      maxdepth: 2,
      ids: this.chartData.ids,
      labels: this.chartData.labels,
      parents: this.chartData.parents,
      values: this.chartData.values,
      hoverlabel: {
        namelength: 0
      },
      hovertemplate: 'Percent: %{customdata}%<br><span style="font-weight:bold;">Category: %{label}</span>',
      customdata: this.chartData.percent,
      insidetextorientation: 'radial',
      outsidetextfont: { size: 20, color: "#377eb8" },
      textposition: 'inside',
      marker: { line: { width: 2 } },
      'branchvalues': 'total',
      leaf: { opacity: 0.4 },
  
    }];
    
    this.layout = {
      margin: { l: 0, r: 0, b: 0, t: 0 },
      sunburstcolorway:["#42b0d8", "#0260A8", "#ffc107", "#19486D", "#00AEEF", "#FF9E40", "#24CD7E"]
    };

    this.config = { displayModeBar: false,responsive: true };

    Plotly.newPlot('sunburst-chart', this.data, this.layout, this.config).then((gd: any) => {
      gd.on('plotly_sunburstclick', (data: any) => {
        const pt = data.points[0];
        // const path = ((pt.currentPath ?? '/') + pt.label).replace('Root', '')
        console.log(data, "clicked")                // path of the clicked element 

        // const clickedTexts = path.split('/');

        if (pt.parent == "" && [... new Set(this.chartData.parents )].length != 2) {
          this.clickedCategory.emit({option: [pt.label], type: 'category'});
        } else {
          this.clickedCategory.emit({option: [pt.parent, pt.label], type: 'subCategory'});
        }       
      })
    });
    
  }
}
