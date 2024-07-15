import { Component, OnInit } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-data-directory',
  templateUrl: './data-directory.component.html',
  styleUrl: './data-directory.component.scss'
})
export class DataDirectoryComponent implements OnInit {
  filteredPincodeData: any = [];
  pincodeData: any = [];
  loading: boolean = true;
  pageSize: number = 20;
  pageIndex: number = 1;
  headers: any = [];

  constructor(private appService: AppService) { }

  ngOnInit(): void {
  }
}
