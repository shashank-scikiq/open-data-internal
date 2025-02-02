import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { LogisticRoutingModule } from './logistic-routing.module';
import { LogisticOverallComponent } from './logistic-overall/logistic-overall.component';
import { LogisticSummaryComponent } from './logistic-summary/logistic-summary.component';
import { SharedModule } from '../shared/shared.module';
import { LogisticSearchComponent } from './logistic-search/logistic-search.component';


@NgModule({
  declarations: [
    LogisticOverallComponent,
    LogisticSummaryComponent,
    LogisticSearchComponent
  ],
  imports: [
    CommonModule,
    LogisticRoutingModule,
    SharedModule
  ]
})
export class LogisticModule { }
