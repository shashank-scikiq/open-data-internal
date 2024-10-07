import { NgModule } from '@angular/core';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzDatePickerModule } from 'ng-zorro-antd/date-picker';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzToolTipModule } from 'ng-zorro-antd/tooltip';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzMessageModule } from 'ng-zorro-antd/message';
import { NzCarouselModule } from 'ng-zorro-antd/carousel';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { NzDropDownModule } from 'ng-zorro-antd/dropdown';
import { NzDrawerModule } from 'ng-zorro-antd/drawer';
import { NzRadioModule } from 'ng-zorro-antd/radio';
import { NzDividerModule } from 'ng-zorro-antd/divider';
import { NzCheckboxModule } from 'ng-zorro-antd/checkbox';


@NgModule({
  declarations: [],
  imports: [
    NzButtonModule,
    NzDatePickerModule,
    NzIconModule,
    NzToolTipModule,
    NzTableModule,
    NzMessageModule,
    NzCarouselModule,
    NzInputModule,
    NzSelectModule,
    NzDropDownModule,
    NzDrawerModule,
    NzRadioModule,
    NzDividerModule,
    NzCheckboxModule
  ],
  exports: [
    NzButtonModule,
    NzDatePickerModule,
    NzIconModule,
    NzToolTipModule,
    NzTableModule,
    NzMessageModule,
    NzCarouselModule,
    NzInputModule,
    NzSelectModule,
    NzDropDownModule,
    NzDrawerModule,
    NzRadioModule,
    NzDividerModule,
    NzCheckboxModule
  ]
})
export class ZorroModule { }
