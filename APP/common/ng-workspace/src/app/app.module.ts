import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HeaderComponent } from './components/global/layouts/header/header.component';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { MaterialModule } from './material/material.module';
import { HttpClientModule } from '@angular/common/http';
import { ZorroModule } from './zorro/zorro.module';
import { FormsModule } from '@angular/forms';


import { registerLocaleData } from '@angular/common';
import en from '@angular/common/locales/en';
registerLocaleData(en);

import { provideNzI18n, en_US } from 'ng-zorro-antd/i18n';
import { NgApexchartsModule } from 'ng-apexcharts';
import { DataDirectoryComponent } from './components/data-directory/data-directory.component';
import { LicenseComponent } from './components/license/license.component';
import { RightSidenavComponent } from './components/global/layouts/right-sidenav/right-sidenav.component';
import { LogisticModule } from './components/logistic/logistic.module';
import { RetailModule } from './components/retail/retail.module';
import { SharedModule } from './components/shared/shared.module';
import { PincodeMappingComponent } from './components/data-directory/pincode-mapping/pincode-mapping.component';
import { DomainMappingComponent } from './components/data-directory/domain-mapping/domain-mapping.component';
import { DataDirectoryDetailComponent } from './components/data-directory/data-directory-detail/data-directory-detail.component';
import { DqReportComponent } from './components/dq-report/dq-report.component';
import { LandingPageComponent } from './components/landing-page/landing-page.component';
import { CommonLayoutComponent } from './components/common-layout/common-layout.component';
import { LayoutComponent } from './layout/layout.component';
import { LandingPageChartComponent } from './components/landing-page/landing-page-chart/landing-page-chart.component';
import { DatePickerComponent } from './components/global/forms/date-picker/date-picker.component';


@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    DataDirectoryComponent,
    LicenseComponent,
    RightSidenavComponent,
    PincodeMappingComponent,
    DomainMappingComponent,
    DataDirectoryDetailComponent,
    DqReportComponent,
    LandingPageComponent,
    CommonLayoutComponent,
    LayoutComponent,
    LandingPageChartComponent,
    DatePickerComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    MaterialModule,
    ZorroModule,
    FormsModule,
    HttpClientModule,
    NgApexchartsModule,
    LogisticModule,
    RetailModule,
    SharedModule
  ],
  providers: [
    provideAnimationsAsync(),
    provideNzI18n(en_US)
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
