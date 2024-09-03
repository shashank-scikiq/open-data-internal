import { Component, OnInit } from '@angular/core';
import { AppService } from '@openData/app/core/api/app/app.service';

@Component({
  selector: 'app-detail-category-filter',
  templateUrl: './detail-category-filter.component.html',
  styleUrl: './detail-category-filter.component.scss'
})
export class DetailCategoryFilterComponent implements OnInit {
  categories: any;
  categoryOptions: string[] = [];
  subCategoryOptions: string[] = [];

  selectedCategory: string = 'All';
  choosedCategory: string = 'All';
  selectedSubCategory: string = 'All';
  choosedSubCategory: string = 'All';

  showOptions: boolean = false;

  constructor(private appService: AppService) {}

  ngOnInit(): void {
    this.appService.filters$.subscribe((val: any) => {
      this.selectedCategory = val.category;
      this.selectedSubCategory = val.subCategory;
      this.choosedCategory = this.selectedCategory;
      this.choosedSubCategory = this.selectedSubCategory;
    })
    this.appService.filterUpdated$.subscribe((val: any) => {
      if (val?.means == 'click' && val?.updated) {
        const filter: any = this.appService.filters.value;
        if (val.type == 'category') {
          this.setChoosedSubCategory('c', filter.category);
        }
        if (val.type == 'subCategory') {
          this.setChoosedSubCategory('sc', filter.subCategory);
        }
      }
    })
    this.appService.getCategories().subscribe(
      (response: any) => {
        this.categories = response;
        this.categoryOptions = [...new Set( ['All', ...this.categories.map((category: any) => category.category)])];
        this.subCategoryOptions = [...new Set( ['All', ...this.categories.map((category: any) => category.sub_category)])];
      }
    )
  }

  removeChoice(type: string) {
    if (type == 'category') {
      this.appService.setFilters('All', 'All');
      this.appService.setFilterUpdated({updated: true, type: 'category', means: 'choosed'});
    }
    if (type == 'subCategory') {
      this.appService.setFilters(this.choosedCategory, 'All')
      this.appService.setFilterUpdated({updated: true, type: 'subCategory', means: 'choosed'});
    }
  }

  setChoosedSubCategory(type: string, option: any) {
    if (type == 'sc') {
      if (this.selectedCategory == 'All' && option !== 'All') {
        this.selectedCategory = this.categories.find((category: any) => category.sub_category === option).category;
        this.subCategoryOptions = [...new Set( ['All', ...this.categories
          .filter((item: any) => item.category === this.selectedCategory)
          .map((item: any) => item.sub_category)])];
      }
    } else {
      if (option == 'All') {
        this.subCategoryOptions = [...new Set( ['All', ...this.categories.map((category: any) => category.sub_category)])];
      } else {
        this.subCategoryOptions = [...new Set( ['All', ...this.categories
        .filter((item: any) => item.category === option)
        .map((item: any) => item.sub_category)])];
      }
      this.selectedSubCategory = 'All';
    }
  }

  toggleOptions() {
    this.showOptions = !this.showOptions;
  }

  apply() {
    this.choosedCategory = this.selectedCategory;
    this.choosedSubCategory = this.selectedSubCategory;
    this.appService.setFilters(this.choosedCategory, this.choosedSubCategory);
    this.showOptions = false;
    this.appService.setFilterUpdated({updated: true, means: 'choosed'});
  }

  close() {
    this.selectedCategory = this.choosedCategory;
    this.selectedSubCategory = this.choosedSubCategory;
    this.showOptions = false;
  }
}
