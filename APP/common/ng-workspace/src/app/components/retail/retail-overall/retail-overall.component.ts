import { Component, OnInit } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-retail-overall',
  templateUrl: './retail-overall.component.html',
  styleUrl: './retail-overall.component.scss'
})
export class RetailOverallComponent implements OnInit {

  constructor(
    private appService: AppService
  ) {};

  isLoading: boolean = false; 

  ngOnInit(): void {
    this.getDateRange();
  }

  getDateRange() {
    this.isLoading = true;
    this.appService.getDataDateRange('retail/overall').subscribe(
      (response: any) => {
        this.appService.setDateRange([new Date(response.min_date), new Date(response.max_date)]);
        this.appService.setChoosableDateRange([new Date(response.min_date), new Date(response.max_date)]);
        this.isLoading = false;
      },
      (error: Error) => {
        console.log(error);
        this.isLoading = false;
      }
    )
  }
}
