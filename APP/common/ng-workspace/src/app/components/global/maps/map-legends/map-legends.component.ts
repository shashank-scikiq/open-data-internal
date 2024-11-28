import { Component, Input, OnChanges, OnDestroy, OnInit, SimpleChanges } from '@angular/core';
import * as d3 from 'd3';


@Component({
  selector: 'app-map-legends',
  templateUrl: './map-legends.component.html',
  styleUrl: './map-legends.component.scss'
})
export class MapLegendsComponent implements OnInit, OnChanges, OnDestroy {
  @Input() legendType: 'chloro' | 'bubble' | 'both' = 'chloro';
  @Input() isLoading: boolean = false;
  @Input() configData: any = {
    bubbleMaxData: 0,
    bubbleColorRange: [],
    bubbleTitle: "",
    bubbleSuffixText: "",

    chloroMaxData: 0,
    chloroColorRange: [],
    chloroTitle: "",
    chloroSuffixText: "",
  };

  ngOnInit(): void {
    this.setLegends();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['legendType'] || changes['configData']) {
      this.setLegends();
    }
  }

  setLegends() {
    this.removeLegends()

    if (this.legendType != 'chloro') {
      this.setBubbleLegend();
    }
    if (this.legendType != 'bubble') {
      this.setChloroLegend();
    }
  }

  setBubbleLegend() {
    const bubbleRadius = d3.scaleSqrt()
      .domain([0, this.configData.bubbleMaxData])
      .range([1, 12]);

    const bubbleLegendData: any = [
      {
        label: 'Low',
        radius: bubbleRadius(0),
        value: 0, color: this.configData.bubbleColorRange[1]
      },
      {
        label: 'Medium', radius:
          bubbleRadius(
            this.configData.bubbleMaxData * 0.5
          ),
        value: Math.floor(
          this.configData.bubbleMaxData * 0.5
        ),
        color: this.configData.bubbleColorRange[1]
      },
      {
        label: 'High',
        radius: bubbleRadius(this.configData.bubbleMaxData),
        value: Math.floor(this.configData.bubbleMaxData),
        color: this.configData.bubbleColorRange[1]
      }
    ];
    d3.select('#bubble-legends').append('p')
      .attr('class', 'font-xxs font-bolder margin-0')
      .text(this.configData.bubbleTitle)

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

  setChloroLegend() {
    const legendValues = [0, ...Array.from(
      { length: 4 }, (_, i) => (i + 1) * this.configData.chloroMaxData / 4
    )];

    const customColorRange = d3.scaleLinear()
      .domain([0, 1, this.configData.chloroMaxData])
      .range(this.configData.chloroColorRange);
    
    d3.select('#chloro-legends').append('p')
      .attr('class', 'font-xxs font-bolder margin-0')
      .text(this.configData.chloroTitle)

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
  }

  removeLegends() {
    d3.select('#bubble-legends').selectAll('svg').remove();
    d3.select('#chloro-legends').selectAll('svg').remove();
    d3.select('#bubble-legends').selectAll('p').remove();
    d3.select('#chloro-legends').selectAll('p').remove();
  }

  ngOnDestroy(): void {
    this.removeLegends();
  }

}
