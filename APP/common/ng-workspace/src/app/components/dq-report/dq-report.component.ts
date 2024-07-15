import { Component, OnInit } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-dq-report',
  templateUrl: './dq-report.component.html',
  styleUrl: './dq-report.component.scss'
})
export class DqReportComponent implements OnInit {

  topCards: any[] = [];

  radialCharts: any[] = [];

  radialChartOption: any = {
    chart: {
      width: 130,
      type: 'radialBar'
    },
    plotOptions: {
      radialBar: {
        hollow: {
          margin: 0,
          size: '80%',
          background: '#fff',
          position: 'front',
        },
        track: {
          background: '#e5e9f2',
          // strokeWidth: '50px',
          margin: 0,
        },
        dataLabels: {
          show: true,
          name: {
            offsetY: 17,
            show: false,
            color: '#8392a5',
            fontSize: '11px'
          },
          value: {
            color: '#001737',
            fontSize: '12px',
            show: true,
            offsetY: 0,
          }
        }

      }
    },
    fill: {
      colors: ['#ff0000']
    }
  }

  detailCompletedHighestMissingPIDData: any[] = [];

  detailCompletedTableData: any[] = [];

  detailCancelledTableData: any[] = [];

  trend1: any = null;
  trend2: any = null;

  chartOptions: any = {
    type: 'area',
    height: 380,
    stacked: false,
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
  };

  public object = Object;

  dateRange: any = [];

  isDetailCompletedTableDataloaded: boolean = true;

  isLoading: boolean = false;


  // >>>>>>>>>>>>>>>>>>>
  section1Chart1Data: any = null;
  section1Chart2Data: any = null; 
  section1TableData: any = null;

  // >>>>>>>>>>>>>>>>>>>

  constructor(private appService: AppService) { }

  ngOnInit(): void {
    this.getDateRange();
    this.appService.dateRange$.subscribe((value) => {
      this.dateRange = value;

      this.initBoard();

      this.initSanityData();
    })
  }

  initSanityData() {
    this.appService.getDataSanityChart1Data().subscribe(
      (res: any) => {
        this.section1Chart1Data = res;
      },
      (error: Error) => {
        console.log(error);
      }
    )
    this.appService.getDataSanityChart2Data().subscribe(
      (res: any) => {
        this.section1Chart2Data = res;
      },
      (error: Error) => {
        console.log(error);
      }
    )
    this.appService.getDataSanityTableData().subscribe(
      (res: any) => {
        this.section1TableData = res;
      },
      (error: Error) => {
        console.log(error);
      }
    )
  }

  initBoard() {
    this.appService.getTrend1Data().subscribe(
      (response: any) => {
        this.trend1 = response;
      }, (error: Error) => {
        console.log(error);
      }
    );

    this.appService.getTrend2Data().subscribe(
      (response: any) => {
        this.trend2 = response;
      }, (error: Error) => {
        console.log(error);
      }
    );

    this.appService.getDetailCompletedTableData().subscribe(
      (response: any) => {
        this.detailCompletedTableData = response;
      }, (error: Error) => {
        console.log(error);
      }
    );

    this.appService.getDetailCancelTableData().subscribe(
      (response: any) => {
        this.detailCancelledTableData = response;
      }, (error: Error) => {
        console.log(error);
      }
    );

    this.appService.getCancelHighestMissingData().subscribe(
      (response: any) => {
        this.detailCompletedHighestMissingPIDData = response;
      }, (error: Error) => {
        console.log(error);
      }
    );

    this.appService.getRadialChartData().subscribe(
      (response: any) => {
        this.radialCharts = response;
      }, (error: Error) => {
        console.log(error);
      }
    );

    this.appService.getDQTopCardData().subscribe(
      (response: any) => {
        this.topCards = response;
      }, (error: Error) => {
        console.log(error);
      }
    );
  }

  setDateRange(value: any) {
    this.appService.setDateRange(value);
  }

  getDateRange() {
    this.isLoading = true;
    this.appService.getDataDateRange('retail/overall').subscribe(
      (response: any) => {
        this.appService.setDateRange([new Date(response.min_date), new Date(response.max_date)]);
        this.appService.setChoosableDateRange([new Date(response.min_date), new Date(response.max_date)]);
        this.isLoading = false;
      },
      (error: Error) => {
        console.log(error);
        this.isLoading = false;
      }
    )
  }

}
