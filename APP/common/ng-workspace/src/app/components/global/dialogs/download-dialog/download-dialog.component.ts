import { Component, Inject, OnDestroy, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatTableDataSource } from '@angular/material/table';
import { AppService } from '@openData/app/core/api/app/app.service';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { saveAs } from 'file-saver';

@Component({
  selector: 'app-download-dialog',
  templateUrl: './download-dialog.component.html',
  styleUrl: './download-dialog.component.scss'
})
export class DownloadDialogComponent implements OnInit, OnDestroy {
  private unsubscribe$ = new Subject<void>();
  constructor(
    private appService: AppService,
    public dialogRef: MatDialogRef<DownloadDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  stateWiseHeaders: any = [];
  stateWiseDataSource = new MatTableDataSource<any>();
  isLoadingStateData: boolean = false;

  districtWiseHeaders: any = [];
  districtWiseDataSource = new MatTableDataSource<any>();
  isLoadingDistrictData: boolean = false;
  isDownloading: boolean = false;

  digitalVoucherDataSource = new MatTableDataSource<any>();
  digitalVoucherHeaders: any = [];
  isLoadingVoucherData: boolean = false;

  tabs: string[] = ['State wise orders', 'District wise orders', 'Digital Voucher'];
  choosedTab: string = '';
  activeUrl: any = '';

  ngOnInit(): void {
    this.loadStateData();
    this.loadDistrictData();
    this.loadVoucherData();
    this.choosedTab = this.tabs[0];
    this.appService.currentUrl$.subscribe((val: any) => {
      this.activeUrl = val;
    })
  }

  setActiveTab(value: any) {
    this.choosedTab = this.tabs[value.index];
  }

  loadStateData() {
    this.isLoadingStateData = true;
    this.appService.getDownloadableData('State wise orders').pipe(takeUntil(this.unsubscribe$)).subscribe(
      (response: any) => {
        this.stateWiseHeaders = response.length ? Object.keys(response[0]) : [];
        this.stateWiseDataSource.data = response;
        this.isLoadingStateData = false;
      },
      (error: Error) => {
        console.log(error);
        this.isLoadingStateData = false;
      }
    )
  }

  loadDistrictData() {
    this.isLoadingDistrictData = true;
    this.appService.getDownloadableData('District wise orders').pipe(takeUntil(this.unsubscribe$)).subscribe(
      (response: any) => {
        this.districtWiseDataSource.data = response;
        this.districtWiseHeaders = response.length ? Object.keys(response[0]) : [];
        this.isLoadingDistrictData = false;
      },
      (error: Error) => {
        console.log(error);
        this.isLoadingDistrictData = false;
      }
    )
  }

  loadVoucherData() {
    this.isLoadingVoucherData = true;
    this.appService.getDownloadableData('Digital Voucher').pipe(takeUntil(this.unsubscribe$)).subscribe(
      (response: any) => {
        this.digitalVoucherDataSource.data = response;
        this.digitalVoucherHeaders = response.length ? Object.keys(response[0]) : [];
        this.isLoadingVoucherData = false;
      },
      (error: Error) => {
        console.log(error);
        this.isLoadingVoucherData = false;
      }
    )
  }

  close(): void {
    this.dialogRef.close();
  }

  ngOnDestroy() {
    this.unsubscribe$.next();
    this.unsubscribe$.complete();
  }
  download(): void {
    this.isDownloading = true;
    this.appService.downloadData(this.choosedTab).subscribe((response: any) => {
      if (response) {
        const data = response;
  
        if (data.length === 0) {
          console.error('No data available for download.');
          return;
        }
  
        const columns = Object.keys(data[0]);
        let csv = columns.map(this.escapeCsvValue).join(',') + '\n';
  
        data.forEach((item: any) => {
          csv += columns.map(column => this.escapeCsvValue(item[column])).join(',') + '\n';
        });
  
        const blob = new Blob([csv], { type: 'text/csv' });
        saveAs(blob, `${this.choosedTab}_data.csv`);
      }
      this.isDownloading = false;
    }, error => {
      console.error('Download error:', error);
      this.isDownloading = false;

    });
  }

  escapeCsvValue(value: any): string {
    if (value === null || value === undefined) {
      return '';
    }
    value = value.toString();
    if (value.includes('"') || value.includes(',') || value.includes('\n')) {
      value = '"' + value.replace(/"/g, '""') + '"';
    }
    return value;
  }
}
