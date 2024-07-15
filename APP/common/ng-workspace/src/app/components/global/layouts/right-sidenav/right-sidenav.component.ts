import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { Router } from '@angular/router';
import { AppService } from '@openData/app/core/api/app/app.service';
import { ConfigService } from '@openData/app/core/api/config/config.service';

@Component({
  selector: 'app-right-sidenav',
  templateUrl: './right-sidenav.component.html',
  styleUrl: './right-sidenav.component.scss'
})
export class RightSidenavComponent implements OnInit {
  @Output() selectOption = new EventEmitter<any>();
  sections: any = [];

  constructor(
    private configService: ConfigService,
    private appService: AppService
  ) { }

  selectedUrl: any = '';
  isStagingEnabled: any = '';

  
  ngOnInit(): void {
    this.isStagingEnabled = this.configService.get('ENABLE_STAGING_ROUTE');

    this.sections = [
      // {
      //   title: 'NAVIGATION',
      //   subSections: [
      //     {
      //       title: 'Home',
      //       type: 'default',
      //       icon: 'fa-solid fa-house',
      //       url: '',
      //       disabled: false
      //     }
      //   ]
      // },
      {
        title: 'DOMAIN',
        subSections: [
          {
            title: 'Retail',
            type: 'default',
            icon: 'fa-solid fa-cart-shopping',
            url: 'retail',
            disabled: false
            // options: [
            //   {
            //     title: 'Retail',
            //     url: 'retail',
            //     disabled: false,
            //     external: false
            //   },
            //   {
            //     title: 'Retail B2B',
            //     url: 'retail/b2b/',
            //     disabled: Boolean(this.isStagingEnabled == 'False'),
            //     external: false
            //   },
            //   {
            //     title: 'Retail B2C',
            //     url: 'retail/b2c/',
            //     disabled: Boolean(this.isStagingEnabled == 'False'),
            //     external: false
            //   }
            // ]
          },
          {
            title: 'Logistics',
            // type: 'accordian',
            type: 'default',
            icon: 'fa-solid fa-truck-arrow-right',
            url: 'logistics',
            disabled: false
            // options: [
            //   {
            //     title: 'Logistic Overall',
            //     url: 'logistics',
            //     disabled: Boolean(this.isStagingEnabled == 'False'),
            //     external: false
            //   },
            //   {
            //     title: 'Logistic Detail',
            //     url: 'logistics/detail/',
            //     disabled: Boolean(this.isStagingEnabled == 'False'),
            //     external: false
            //   }
            // ]
          }
        ]
      },
      {
        title: 'QUICK LINKS',
        subSections: [
          {
            title: 'Feedback',
            type: 'default',
            icon: 'fa-solid fa-message',
            url: 'https://docs.google.com/forms/d/1SqqmejmJm36yY5cwH9ZL9QtBbc64f2uRHcZUzi0wbBE/edit?ts=65dee03c',
            disabled: false,
            external: true
          },
          {
            title: 'Data dictionary',
            type: 'default',
            icon: 'fa-solid fa-folder-closed',
            url: 'data-dictionary',
            disabled: false
          },
          // {
          //   title: 'Download data',
          //   type: 'static',
          //   icon: 'fa-solid fa-file-arrow-down',
          //   url: '',
          //   disabled: false
          // },
          {
            title: 'License',
            type: 'default',
            icon: 'fa-solid fa-id-card',
            url: 'license',
            disabled: false
          },
        ]
      }
    ];

    this.appService.currentUrl$.subscribe((val: any) => {
      this.selectedUrl = val.replace('/', '');
    })
  }

  setOpenDownloadDataDialog() {
    this.appService.setIsDownloadDataDialogOpen(true);
    this.selectOption.emit({openDialog: true});
  }

  closeNavigation() {
    this.selectOption.emit();
  }

}