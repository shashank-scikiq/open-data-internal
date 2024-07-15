import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RetailOverallComponent } from './retail-overall/retail-overall.component';
import { RetailB2bComponent } from './retail-b2b/retail-b2b.component';
import { RetailB2cComponent } from './retail-b2c/retail-b2c.component';
import { ConfigGuard } from '@openData/app/core/guards/config/config.guard';

const routes: Routes = [
  {
    path: '',
    component: RetailOverallComponent
  },
  {
    path: 'b2b',
    component: RetailB2bComponent,
    canActivate: [ConfigGuard],
    data: { configKey: 'ENABLE_STAGING_ROUTE' }
  },
  {
    path: 'b2c',
    component: RetailB2cComponent,
    canActivate: [ConfigGuard],
    data: { configKey: 'ENABLE_STAGING_ROUTE' }
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class RetailRoutingModule { }
