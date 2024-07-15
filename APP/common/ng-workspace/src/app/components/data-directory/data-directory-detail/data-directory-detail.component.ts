import { Component, OnInit } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-data-directory-detail',
  templateUrl: './data-directory-detail.component.html',
  styleUrl: './data-directory-detail.component.scss'
})
export class DataDirectoryDetailComponent implements OnInit {
  filteredPincodeData: any = [];
  pincodeData: any = [];
  loading: boolean = true;
  pageSize: number = 10;
  pageIndex: number = 1;
  headers: any = [];

  constructor(private appService: AppService) { }

  ngOnInit(): void {
    this.loading = true;
    this.appService.getDictionaryData().subscribe(
      (response: any) => {
        this.headers = response.headers;
        this.pincodeData = response.rows;
        this.filteredPincodeData = this.pincodeData; //.slice(0, 10);
        this.loading = false;
      },
      (error: Error) => {
        console.log(error);
        this.loading = false;
      }
    )
  }

  async sortArray() {
    this.pincodeData.sort((a: string[], b: string[]) => {
      if (a[1] < b[1]) {
        return -1;
      } else if (a[1] > b[1]) {
        return 1;
      } else {
        return 0;
      }
    });
  }

  sortByIndex(index: number, order: string) {
    return this.pincodeData.sort((a: string[], b: string[]) => {
      let comparison = 0;
      if (a[index] > b[index]) {
        comparison = 1;
      } else if (a[index] < b[index]) {
        comparison = -1;
      }
      return order === 'ascend' ? comparison : -comparison;
    });
  }

  search(event: any): void {
    const searchTerm = event.target.value;
    this.filterData(searchTerm)
  }

  private filterData(searchTerm: any): void {
    if (!searchTerm) {
      this.filteredPincodeData = this.pincodeData;
    } else {
      this.filteredPincodeData = this.pincodeData.filter((row: any) =>
        row.some((cell: any) => cell.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
  }

  onQueryParamsChange($event: any) {
    this.pageSize = $event.pageSize;
    this.pageIndex = $event.pageIndex;
  }


  sort(sortName: string, sortValue: any, index: number): void {
    if (sortName !== null) {
      
      this.pincodeData = this.sortByIndex(index, sortValue);

      this.pincodeData = this.pincodeData.sort((a: string[], b: string[]) => {
        let comparison = 0;
        if (a[index] > b[index]) {
          comparison = 1;
        } else if (a[index] < b[index]) {
          comparison = -1;
        }
        return sortValue === 'ascend' ? comparison : -comparison;
      });

      this.filteredPincodeData = this.filteredPincodeData.sort((a: string[], b: string[]) => {
        let comparison = 0;
        if (a[index] > b[index]) {
          comparison = 1;
        } else if (a[index] < b[index]) {
          comparison = -1;
        }
        return sortValue === 'ascend' ? comparison : -comparison;
      });
    }
  }

}