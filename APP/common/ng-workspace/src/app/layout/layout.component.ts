import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { MatDrawer, MatDrawerContainer } from '@angular/material/sidenav';
import { NzButtonSize } from 'ng-zorro-antd/button';
import { AppService } from '../core/api/app/app.service';
import { NavigationEnd, Router } from '@angular/router';
import { Subject } from 'rxjs';
import { ConfigService } from '../core/api/config/config.service';

@Component({
  selector: 'app-layout',
  templateUrl: './layout.component.html',
  styleUrl: './layout.component.scss'
})
export class LayoutComponent implements OnInit, OnDestroy {
  title = 'open-data';
  size: NzButtonSize = 'large';
  dateRange: any = null;
  apiUrl: any;
  activeRoute: string = '';
  pathname: string = '';

  private configuredSubscriber$ = new Subject<void>();

  @ViewChild('rightnav') rightnav: MatDrawer | null = null;
  @ViewChild('matdrawer') matdrawer: MatDrawerContainer | null = null;

  constructor(
    private appService: AppService,
    private router: Router,
    private configService: ConfigService
  ) { 
  }

  ngOnInit() {
    this.appService.getStateDistrictData().subscribe(
      (res: any) => {
        if(res) {
          this.appService.setStateAndDistrictData(res);
        }
      }, (error: Error) => {
        console.log(error);
      }
    )
    this.configService.configured$.subscribe(
      (resp: boolean) => {
        if (resp) {
          this.initData();
        }
      }, (error: Error) => console.log(error)
    )

    this.pathname = window.location.pathname;
  }

  initData() {
    // this.getDateRange();
    this.appService.dateRange$.subscribe((value: any) => {
      this.dateRange = value;
    });
    this.appService.currentUrl$.subscribe((val) => {
      this.activeRoute = val;
      // if (this.activeRoute.includes('retail') || this.activeRoute.includes('logistics')) {
      //   this.getDateRange();
      // }
    });

    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.appService.setCurrentUrl(event.urlAfterRedirects);
      }
    });
  }

  getDateRange() {
    this.appService.getDataDateRange().subscribe(
      (response: any) => {
        this.appService.setDateRange([new Date(response.min_date), new Date(response.max_date)]);
        this.appService.setChoosableDateRange([new Date(response.min_date), new Date(response.max_date)]);
      },
      (error: Error) => {
        console.log(error);
      }
    )
  }

  closeBackdrop(): void {
    if (this.rightnav)
      this.rightnav.toggle();
    if (this.matdrawer)
      this.matdrawer.hasBackdrop = false;
  }

  rightToggle(): void {
    if (this.matdrawer && !this.matdrawer.hasBackdrop) {
      this.matdrawer.hasBackdrop = true;
    }
    if (this.rightnav)
      this.rightnav.toggle();
  }

  ngOnDestroy(): void {
    
  }
}
