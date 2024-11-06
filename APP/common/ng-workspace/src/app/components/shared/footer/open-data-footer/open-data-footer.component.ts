import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'open-data-footer',
  templateUrl: './open-data-footer.component.html',
  styleUrl: './open-data-footer.component.scss'
})
export class OpenDataFooterComponent implements OnInit {
  data: any = null;
  @Input() smallView: boolean = false;

  quickLinks: any = [
    {
      title: 'Data dictionary',
      type: 'default',
      icon: 'fa-solid fa-folder-closed',
      url: 'data-dictionary',
      disabled: false
    },
    {
      title: 'License',
      type: 'default',
      icon: 'fa-solid fa-id-card',
      url: 'license',
      disabled: false
    },
  ]

  ngOnInit(): void {
    if (!this.smallView) {
      this.loadData();
    }
  }

  async loadData() {
    const configData = await fetch("static/assets/data/landing-page/data.json");
    this.data = await configData.json();
  }

}
