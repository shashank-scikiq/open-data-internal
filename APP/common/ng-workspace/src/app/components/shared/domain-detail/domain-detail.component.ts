import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-domain-detail',
  templateUrl: './domain-detail.component.html',
  styleUrl: './domain-detail.component.scss'
})
export class DomainDetailComponent implements OnInit {

  @Input() domain: string = '';
  @Input() domainTooltip: string = '';
  
  
  ngOnInit(): void {
    
  }
}
