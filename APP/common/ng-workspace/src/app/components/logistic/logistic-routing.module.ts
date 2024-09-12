import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LogisticOverallComponent } from './logistic-overall/logistic-overall.component';
import { LogisticSummaryComponent } from './logistic-summary/logistic-summary.component';
import { PincodeLevelMapViewComponent } from '../shared/pincode-level-map-view/pincode-level-map-view.component';

const routes: Routes = [
  {
    path: '',
    component: LogisticOverallComponent
  },
  {
    path: 'detail',
    component: LogisticSummaryComponent
  },
  {
    path: 'search_by_city',
    component: PincodeLevelMapViewComponent
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class LogisticRoutingModule { }
