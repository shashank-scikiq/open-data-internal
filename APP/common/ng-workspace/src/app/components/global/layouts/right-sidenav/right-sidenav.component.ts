import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-right-sidenav',
  templateUrl: './right-sidenav.component.html',
  styleUrl: './right-sidenav.component.scss'
})
export class RightSidenavComponent implements OnInit {
  @Output() selectOption = new EventEmitter<any>();
  sections: any = [];

  constructor(
    private appService: AppService
  ) { }

  selectedUrl: any = '';
  isStagingEnabled: any = '';

  
  ngOnInit(): void {
    // this.isStagingEnabled = this.configService.get('ENABLE_STAGING_ROUTE');

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
            // type: 'default',
            type: 'accordian',
            icon: 'fa-solid fa-cart-shopping',
            url: 'retail',
            disabled: false,
            options: [
              {
                title: 'Overall',
                url: 'retail',
                disabled: false,
                external: false
              },
              {
                title: 'B2B',
                url: 'retail/b2b',
                disabled: false,
                external: false
              },
              {
                title: 'B2C',
                url: 'retail/b2c',
                disabled: false,
                external: false
              },
              {
                title: 'Gift Voucher',
                disabled: true,
                external: false
              }
            ]
          },
          {
            title: 'Logistics',
            type: 'accordian',
            // type: 'default',
            icon: 'fa-solid fa-truck-arrow-right',
            url: 'logistics',
            disabled: false,
            options: [
              {
                title: 'Orders',
                url: 'logistics',
                disabled: false,
                external: false
              },
              {
                title: 'Search by city',
                url: 'logistics/search',
                disabled: false,
                external: false,
                // type: 'accordian',
                // options: [
                //   {
                //     title: 'Delhi',
                //     url: 'logistics/search_by_city',
                //     disabled: false,
                //     external: false,
                //     params: {city: 'Delhi'}
                //   },
                //   {
                //     title: 'Bangalore',
                //     url: 'logistics/search_by_city',
                //     disabled: false,
                //     external: false,
                //     params: {city: 'Bangalore'}
                //   }
                // ] 
              }
            ]
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
            url: 'http://172.31.41.128:8083/s/cm35p9a5t000fhrda5e115fab',
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