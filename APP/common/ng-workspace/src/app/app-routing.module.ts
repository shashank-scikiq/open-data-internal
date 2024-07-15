import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LicenseComponent } from './components/license/license.component';
import { DataDirectoryComponent } from './components/data-directory/data-directory.component';
import { ConfigGuard } from './core/guards/config/config.guard';
import { DqReportComponent } from './components/dq-report/dq-report.component';
import { LandingPageComponent } from './components/landing-page/landing-page.component';
import { LayoutComponent } from './layout/layout.component';

const routes: Routes = [
  {
    path: '',
    component: LandingPageComponent
  },
  {
    path: '',
    component: LayoutComponent,
    children: [
      {
        path: 'retail',
        loadChildren: () => import('./components/retail/retail.module').then(m => m.RetailModule),
      },
      {
        path: 'logistics',
        loadChildren: () => import('./components/logistic/logistic.module').then(m => m.LogisticModule),

      },
      {
        path: 'data-dictionary',
        component: DataDirectoryComponent
      },
      {
        path: 'license',
        component: LicenseComponent
      },
      // {
      //   path: 'dq-report',
      //   component: DqReportComponent
      // },
    ]
  },
  {
    path: '**',
    redirectTo: ''
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
