import { Component, Input, OnInit } from '@angular/core';
import ApexSankey from 'apexsankey';
import { delay } from 'rxjs';

@Component({
  selector: 'app-sankey-chart',
  templateUrl: './sankey-chart.component.html',
  styleUrl: './sankey-chart.component.scss'
})
export class SankeyChartComponent implements OnInit {
  @Input() nodes: any = [];
  @Input() edges: any = [];
  @Input() height: number = 600;
  @Input() id: string = '';

  data: any = {
    nodes: [
      {
        id: 'Tier 1',
        title: 'Tier 1',
        color: "#A8D8B9"
      },
      {
        id: 'Tier 2',
        title: 'Tier 2',
        color: '#6A9BD1'
      },
      {
        id: 'Tier 3',
        title: 'Tier 3',
        color: '#FFA500'
      },
      {
        id: 'F&B',
        title: 'F&B',
        color: '#000000'
      }
    ],
    edges: [
      {
        source: 'Tier 1',
        target: 'F&B',
        value: 45,
      },
      {
        source: 'Tier 2',
        target: 'F&B',
        value: 31,
      },
      {
        source: 'Tier 3',
        target: 'F&B',
        value: 25,
      }
    ]
  };
  graphOptions: any = {
    nodeWidth: 20,
    fontFamily: 'Quicksand, sans-serif',
    canvasStyle: 'border: none',
    fontWeight: 600,
    height: 600,
    fontSize: '32px',
    edgeGradientFill: true,
    enableTooltip: true,
    tooltipId: 'sankey-tooltip-container',
    // tooltipBorderColor: '#BCBCBC',
    tooltipBGColor: '#f4f4f4',
    tooltipTemplate: (e: any) => {
      return `
        <div style='display:flex;align-items:center;gap:5px;'>
          <div style='width:12px;height:12px;background-color:${e.source.color}'></div>
          <div>${e.source.title}</div>
          <i class="fa-solid fa-arrow-right"></i>
          <div style='width:12px;height:12px;background-color:${e.target.color}'></div>
          <div>${e.target.title}</div>
          <div>: ${e.value}%</div> 
        </div>
      `
    }
    
    ,
  };

  ngOnInit() {
    this.setData();
  }

  async setData() {
    this.data.nodes = this.nodes;
    this.data.edges = this.edges;
    this.graphOptions.height = this.height;
    await delay(2000);
    
    const ele: any = document.getElementById(this.id);
    const s = new ApexSankey(ele, this.graphOptions);
    s.render(this.data);
  }

}
