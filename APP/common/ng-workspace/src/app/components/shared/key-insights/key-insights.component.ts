import { Component, OnInit } from '@angular/core';
import { NzDrawerPlacement } from 'ng-zorro-antd/drawer';

@Component({
  selector: 'app-key-insights',
  templateUrl: './key-insights.component.html',
  styleUrl: './key-insights.component.scss'
})
export class KeyInsightsComponent implements OnInit {
  data: any = {
    "seller_card": {
      "percentage_seller": 7,
      "percentage_of_orders": "80",
      "current_period": "Jun 01, 2024 to Jun 06, 2024"
    },
    "state_order_volume": {
      "delta_volume_max_state": 68.0,
      "state_name": "KARNATAKA",
      "current_period": "Jun 01, 2024 to Jun 06, 2024",
      "previous_period": "May 01, 2024 to May 06, 2024"
    },
    "state_order_volume_weekwise": {
      "delta_volume_max_state": 1218.0,
      "state_name": "BIHAR",
      "current_period": "Jun 01, 2024 to Jun 06, 2024",
      "previous_period": "May 01, 2024 to May 06, 2024"
    },
    "district_order_volume": {
      "delta_volume_max_state": 867.0,
      "district_name": "HISAR",
      "current_period": "Jun 01, 2024 to Jun 06, 2024",
      "previous_period": "May 01, 2024 to May 06, 2024"
    },
    "district_order_volume_weekwise": {
      "delta_volume_max_state": 700.0,
      "district_name": "CHITTOOR",
      "current_period": "Jun 03, 2024 to Jun 06, 2024",
      "previous_period": "May 27, 2024 to May 30, 2024"
    },
    "subcategory_order_volume": {
      "delta_volume_max_subcat": 7293,
      "sub_category": "NUTRITION AND FITNESS SUPPLEMENTS",
      "current_period": "Jun 01, 2024 - Jun 06, 2024",
      "previous_period": "May 01, 2024 - May 06, 2024"
    }
  }

  visible = false;
  placement: NzDrawerPlacement = 'bottom';
  open(): void {
    this.visible = true;
  }

  close(): void {
    this.visible = false;
  }

  constructor() { }

  ngOnInit(): void {

  }
}
