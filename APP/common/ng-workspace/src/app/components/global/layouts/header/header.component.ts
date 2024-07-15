import { Component, ViewChild , AfterViewInit, Output, EventEmitter, OnInit, Input} from '@angular/core';
import { MatDrawer, MatDrawerContainer } from '@angular/material/sidenav';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent implements OnInit {
  @Output() rightSidenav = new EventEmitter<any>();
  updatedDate: Date | null = null;
  homeUrl: string = '';
  activeRoute: any;

  constructor(private appService: AppService) {
    this.homeUrl = window.location.origin;
  }

  ngOnInit() {
    this.appService.dateRange$.subscribe((value: any) => {
      if (value)
      this.updatedDate = value[1]
    });
    this.appService.currentUrl$.subscribe((val) => {
      this.activeRoute = val;
    })
  }

  toggleRightSidenav(): void {
    this.rightSidenav.emit();
  } 
}
