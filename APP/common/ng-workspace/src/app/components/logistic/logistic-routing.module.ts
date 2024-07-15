import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LogisticOverallComponent } from './logistic-overall/logistic-overall.component';
import { LogisticSummaryComponent } from './logistic-summary/logistic-summary.component';
import { ConfigGuard } from '@openData/app/core/guards/config/config.guard';


const routes: Routes = [
  {
    path: '',
    component: LogisticOverallComponent
  },
  {
    path: 'detail',
    component: LogisticSummaryComponent,
    canActivate: [ConfigGuard],
    data: { configKey: 'ENABLE_STAGING_ROUTE' }
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class LogisticRoutingModule { }
