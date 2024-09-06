// import { Component, OnInit } from '@angular/core';
// import { NzDrawerPlacement } from 'ng-zorro-antd/drawer';

// @Component({
//   selector: 'app-key-insights',
//   templateUrl: './key-insights.component.html',
//   styleUrl: './key-insights.component.scss'
// })
// export class KeyInsightsComponent implements OnInit {
//   data: any = {
//     "seller_card": {
//       "percentage_seller": 7,
//       "percentage_of_orders": "80",
//       "current_period": "Jun 01, 2024 to Jun 06, 2024"
//     },
//     "state_order_volume": {
//       "delta_volume_max_state": 68.0,
//       "state_name": "KARNATAKA",
//       "current_period": "Jun 01, 2024 to Jun 06, 2024",
//       "previous_period": "May 01, 2024 to May 06, 2024"
//     },
//     "state_order_volume_weekwise": {
//       "delta_volume_max_state": 1218.0,
//       "state_name": "BIHAR",
//       "current_period": "Jun 01, 2024 to Jun 06, 2024",
//       "previous_period": "May 01, 2024 to May 06, 2024"
//     },
//     "district_order_volume": {
//       "delta_volume_max_state": 867.0,
//       "district_name": "HISAR",
//       "current_period": "Jun 01, 2024 to Jun 06, 2024",
//       "previous_period": "May 01, 2024 to May 06, 2024"
//     },
//     "district_order_volume_weekwise": {
//       "delta_volume_max_state": 700.0,
//       "district_name": "CHITTOOR",
//       "current_period": "Jun 03, 2024 to Jun 06, 2024",
//       "previous_period": "May 27, 2024 to May 30, 2024"
//     },
//     "subcategory_order_volume": {
//       "delta_volume_max_subcat": 7293,
//       "sub_category": "NUTRITION AND FITNESS SUPPLEMENTS",
//       "current_period": "Jun 01, 2024 - Jun 06, 2024",
//       "previous_period": "May 01, 2024 - May 06, 2024"
//     }
//   }

//   visible = false;
//   placement: NzDrawerPlacement = 'bottom';
//   open(): void {
//     this.visible = true;
//   }

//   close(): void {
//     this.visible = false;
//   }

//   constructor() { }

//   ngOnInit(): void {

//   }

// }


import { Component, AfterViewInit, OnInit } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';
import { delay } from 'rxjs';

@Component({
  selector: 'app-key-insights',
  templateUrl: './key-insights.component.html',
  styleUrl: './key-insights.component.scss'
})
export class KeyInsightsComponent implements OnInit {

  elems: any = [];
  insights: any = [];

  constructor(private appService: AppService) {}

  // ngOnInit(): void {
  //   this.appService.getKeyInsights().subscribe(
  //     (response: any) => {
  //       this.insights = response.insights;
  //       delay(1000)
  //       this.setCards();
  //     }, (error: Error) => {
  //       console.log(error);
  //     }
  //   )
  // }

  // setCards(): void {
  //   const carouselList = document.querySelector('.carousel__list') as HTMLElement;
  //   const carouselItems = document.querySelectorAll('.carousel__item') as NodeListOf<HTMLElement>;
  //   this.elems = Array.from(carouselItems);

  //   carouselList.addEventListener('click', (event: MouseEvent) => {
  //     const newActive = event.target as HTMLElement;
  //     const isItem = newActive.closest('.carousel__item') as HTMLElement;

  //     if (!isItem || newActive.classList.contains('carousel__item_active')) {
  //       return;
  //     }

  //     this.update(isItem);
  //   });
  // }

  // private update(newActive: HTMLElement | any): void {
  //   const newActivePos = parseInt(newActive.dataset.pos || '0', 10);

  //   const current = this.elems.find((elem) => parseInt(elem.dataset['pos'] || '0', 10) === 0);
  //   const prev = this.elems.find((elem) => parseInt(elem.dataset['pos'] || '0', 10) === -1);
  //   const next = this.elems.find((elem) => parseInt(elem.dataset['pos'] || '0', 10) === 1);
  //   const first = this.elems.find((elem) => parseInt(elem.dataset['pos'] || '0', 10) === -2);
  //   const last = this.elems.find((elem) => parseInt(elem.dataset['pos'] || '0', 10) === 2);

  //   if (current) {
  //     current.classList.remove('carousel__item_active');
  //   }

  //   [current, prev, next, first, last].forEach((item) => {
  //     if (item) {
  //       const itemPos = parseInt(item.dataset['pos'] || '0', 10);
  //       item.dataset['pos'] = this.getPos(itemPos, newActivePos).toString();
  //     }
  //   });
  // }

  // private getPos(current: number, active: number): number {
  //   const diff = current - active;

  //   if (Math.abs(diff) > 2) {
  //     return -current;
  //   }

  //   return diff;
  // }

  ngOnInit(): void {
    this.appService.getKeyInsights().subscribe(
      (response: any) => {
        this.elems = response.insights;
        delay(1000)
        this.setCards();
      }, (error: Error) => {
        console.log(error);
      }
    )
  }

  setCards(): void {
    let count = -2;
    this.elems.forEach((ele: any) => {
      ele.pos = count;
      ele.active = Boolean(count == 0);
      count+=1;
    })
  }

  onCardClick(cardPos: number): void {
    const clickedItem = this.elems.find((item: any) => item.pos === cardPos);

    if (clickedItem && !clickedItem.active) {
      this.update(clickedItem);
    }
  }

  private update(newActive: { pos: number; active: boolean }): void {
    const newActivePos = newActive.pos;

    // Find current, prev, next, first, last elements
    const current = this.elems.find((item: any) => item.pos === 0);
    const prev = this.elems.find((item: any) => item.pos === -1);
    const next = this.elems.find((item: any) => item.pos === 1);
    const first = this.elems.find((item: any) => item.pos === -2);
    const last = this.elems.find((item: any) => item.pos === 2);

    if (current) {
      current.active = false;
    }

    // Update the positions of the elements
    [current, prev, next, first, last].forEach(item => {
      if (item) {
        item.pos = this.getPos(item.pos, newActivePos);
        item.active = item.pos === 0; // Mark the current item as active
      }
    });
  }

  private getPos(current: number, active: number): number {
    const diff = current - active;

    if (Math.abs(diff) > 2) {
      return -current;
    }

    return diff;
  }
}

