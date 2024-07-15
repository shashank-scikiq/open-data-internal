import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-date-range-picker',
  templateUrl: './date-range-picker.component.html',
  styleUrl: './date-range-picker.component.scss'
})
export class DateRangePickerComponent implements OnInit, OnChanges {
  @Input() dateRange: any = [];
  @Output() selectedDateRange = new EventEmitter<any>();
  availableDateRange: any = [];

  date: any = null;

  constructor(private appService: AppService) {}

  ngOnInit(): void {
    this.date = this.dateRange;
    this.appService.choosableDateRange$.subscribe((val: any) => {
      this.availableDateRange = val;
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.date = changes['dateRange'].currentValue;
  }

  checkClear() {
    return !(this.date[0].toString()==this.availableDateRange[0].toString() && this.date[1].toString() == this.availableDateRange[1].toString())
  }

  onChange(result: Date[]): void {
    if (result.length == 0 || result == null || result == undefined) {
      result = this.availableDateRange;
    }
    this.selectedDateRange.emit(result);
  }

  disabledDate = (current: Date): boolean => {
    if (!this.availableDateRange)
      return false;
    return current && (current < this.availableDateRange[0] || current > this.availableDateRange[1]);
  };
}


