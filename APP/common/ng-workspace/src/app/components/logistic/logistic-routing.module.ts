import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LogisticOverallComponent } from './logistic-overall/logistic-overall.component';
import { LogisticSummaryComponent } from './logistic-summary/logistic-summary.component';
import { LogisticSearchComponent } from './logistic-search/logistic-search.component';

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
    path: 'search',
    component: LogisticSearchComponent
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class LogisticRoutingModule { }
