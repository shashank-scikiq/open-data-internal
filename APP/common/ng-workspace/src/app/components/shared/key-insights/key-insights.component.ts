
import { Component, AfterViewInit, OnInit } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-key-insights',
  templateUrl: './key-insights.component.html',
  styleUrl: './key-insights.component.scss'
})
export class KeyInsightsComponent implements OnInit {
  isLoading: boolean = true;
  elems: any = [];

  constructor(private appService: AppService) {}

  ngOnInit(): void {
    this.isLoading = true;
    this.appService.getKeyInsights().subscribe(
      (response: any) => {
        if (response ) {
          this.elems = response.insights;
          this.isLoading = false;
        }
      }, (error: Error) => {
          this.isLoading = false;
          console.log(error);
      }
    )
  }
}

