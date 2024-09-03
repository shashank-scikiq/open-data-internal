import { Component, OnInit } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-landing-page',
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.scss'
})
export class LandingPageComponent implements OnInit {
  data: any = null;
  bannerData: any;

  constructor(private appService: AppService) {}

  ngOnInit(): void {
    this.loadData();
    this.getBannerData();
  }

  getBannerData() {
    this.appService.getLandingPageCumulativeOrderCount().subscribe(
      (res: any) => {
        this.bannerData = res;
      }, (err: Error) => console.log(err)
    )
  }

  async loadData() {
    const configData = await fetch("static/assets/data/landing-page/data.json");
    this.data = await configData.json();
    // this.bannerData = {"updatedAt": this.data.lastUpdatedDate, "order_count": this.data.netOrderCount}
  }
}
