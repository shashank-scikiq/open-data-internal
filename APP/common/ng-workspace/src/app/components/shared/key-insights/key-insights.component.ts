
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
  metaDataChecked: boolean = false;
  activeItem: any = null;

  chartOptions: any = {
    series: [
      {
        name: "Active Sellers",
        data: [24,
          90,
          11,
          14,
          35,
          26,
          12,
          8,
          16]
      },
      // {
      //   name: "Sellers",
      //   data: [53, 32, 33, 52, 13]
      // }
    ],
    chart: {
      type: "bar",
      height: 350,
      stacked: true,
      // stackType: "100%",
      toolbar: {
        show: false,
        tools: {
          download: false,
          selection: false,
          zoom: true,
          zoomin: true,
          zoomout: true,
          pan: false,
          reset: true
        }
      },
      zoom: {
        enabled: false,
      }
    },
    plotOptions: {
      bar: {
        horizontal: true
      }
    },
    stroke: {
      width: 1,
      colors: ["#fff"]
    },
    // title: {
    //   text: "Fiction Books Sales"
    // },
    xaxis: {
      categories: [
        "Appliances",
        "Auto Components & Accessories",
        "BPC",
        "Electronics",
        "F&B",
        "Fashion",
        "Grocery",
        "Health & Wellness",
        "Home & Kitchen",
      ],
      labels: {
        formatter: (val: any) => {
          return val ;
        }
      }
    },
    yaxis: {
      title: {
        text: undefined
      }
    },
    tooltip: {
      y: {
        formatter: (val: any) => {
          return val;
        }
      }
    },
    fill: {
      opacity: 1
    },
    legend: {
      position: "top",
      horizontalAlign: "left",
      offsetX: 40
    }
  };

  stateWiseBin: any = {
    "< 1,000": [
        " Jharkhand",
        " Chhattisgarh",
        " Uttarakhand",
        " Himachal Pradesh",
        " Manipur",
        " Tripura",
        " Goa",
        " Meghalaya",
        " Arunachal Pradesh",
        " Nagaland",
        " Mizoram",
        " Chandigarh",
        " Sikkim",
        " Puducherry",
        " Ladakh",
        " Dadra And Nagar Haveli And Daman And Diu",
        " Andaman And Nicobar Islands",
        " Lakshadweep"
    ],
    "1,000 - 5,000": [
        " Rajasthan",
        " Tamil Nadu",
        " Gujarat",
        " Madhya Pradesh",
        " Kerala",
        " Bihar",
        " Andhra Pradesh",
        " Punjab",
        " Assam",
        " Odisha",
        " Jammu And Kashmir"
    ],
    "5,000 - 10,000": [
        " Telangana",
        " West Bengal"
    ],
    "> 10,000": [
        " Karnataka",
        " Delhi",
        " Uttar Pradesh",
        " Maharashtra",
        " Haryana"
    ]
}
chartInitialized: boolean = false;

  constructor(private appService: AppService) {}

  ngOnInit(): void {
    this.appService.getKeyInsights().subscribe(
      (response: any) => {
        if (response ) {
          this.elems = response.insights;
          // this.activeItem = this.elems[0];
          // console.log(this.elems[0], this.activeItem, this.activeItem.metaData.xaxis)
          // this.chartOptions.xaxis.categories = this.activeItem.metaData.xaxis.categories;
          // this.chartOptions.series.data = this.activeItem.metaData.data;

          console.log(this.elems)
          delay(1000)
          this.chartInitialized = true;
          this.setCards();
        }
      }, (error: Error) => {
        console.log(error);
      }
    )
  }

  setCards(): void {
    let count = 0;
    this.elems.forEach((ele: any) => {
      ele.pos = count;
      ele.active = Boolean(count == 0);
      count+=1;
    })
  }

  onCardClick(cardPos: number): void {
    const clickedItem = this.elems.find((item: any) => item.pos === cardPos);
    this.activeItem = clickedItem;


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
      this.metaDataChecked = false;
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

