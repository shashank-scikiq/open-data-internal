import { Component, OnInit } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-landing-page',
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.scss'
})
export class LandingPageComponent implements OnInit {
  data: any = null;

  ngOnInit(): void {
    this.loadData();
  }

  async loadData() {
    const configData = await fetch("static/assets/data/landing-page/data.json");
    this.data = await configData.json();
  }
}
