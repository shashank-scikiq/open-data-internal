import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-map-legends',
  templateUrl: './map-legends.component.html',
  styleUrl: './map-legends.component.scss'
})
export class MapLegendsComponent implements OnInit, OnChanges {
  @Input() legendType: 'chloro' | 'bubble' | 'both' = 'chloro';
  @Input() configData: any;

  ngOnInit(): void {
    this.setLegends();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['legendType'], this.configData) {
      this.setLegends();
    }
  }

  setLegends() {
    
  }

}
