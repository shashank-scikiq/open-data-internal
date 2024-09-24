import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-domain-detail-filters',
  templateUrl: './domain-detail-filters.component.html',
  styleUrl: './domain-detail-filters.component.scss'
})
export class DomainDetailFiltersComponent {
  @Input() domain: string = '';
  @Input() dateRangeChipData: string = '';

}
