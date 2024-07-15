import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { RetailRoutingModule } from './retail-routing.module';
import { RetailOverallComponent } from './retail-overall/retail-overall.component';
import { RetailB2bComponent } from './retail-b2b/retail-b2b.component';
import { RetailB2cComponent } from './retail-b2c/retail-b2c.component';
import { SharedModule } from '../shared/shared.module';


@NgModule({
  declarations: [
    RetailOverallComponent,
    RetailB2bComponent,
    RetailB2cComponent
  ],
  imports: [
    CommonModule,
    RetailRoutingModule,
    SharedModule
  ]
})
export class RetailModule { }
