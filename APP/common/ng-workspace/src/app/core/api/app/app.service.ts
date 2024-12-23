import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '@openData/env/environment';
import { BehaviorSubject, Subject, of, switchMap, takeUntil } from 'rxjs';
import { AppApiMap } from '../../utils/global';


@Injectable({
  providedIn: 'root'
})
export class AppService {
  private baseUrl: string | null = null;

  currentUrl = new BehaviorSubject<any>('');
  currentUrl$ = this.currentUrl.asObservable();

  metrix = new BehaviorSubject<any>('map_total_orders_metrics');
  selectedMetrix$ = this.metrix.asObservable();

  stateData = new BehaviorSubject<any>(null);
  stateData$ = this.stateData.asObservable();

  isDownloadDataDialogOpen = new BehaviorSubject<boolean>(false);
  isDownloadDataDialogOpen$ = this.isDownloadDataDialogOpen.asObservable();

  dateRange = new BehaviorSubject<any>(null);
  choosableDateRange = new BehaviorSubject<any>(null);
  public maxDate: BehaviorSubject<any>;
  dateRange$ = this.dateRange.asObservable();
  choosableDateRange$ = this.choosableDateRange.asObservable();

  selectedCategory: string = 'All';
  selectedSubCategory: string = 'All';
  filters = new BehaviorSubject<any>({
    category: 'All',
    subCategory: 'All' 
  });
  filterUpdated = new BehaviorSubject<any>({updated: false, means: ''});
  filterUpdated$ = this.filterUpdated.asObservable();
  filters$ = this.filters.asObservable()

  private cancelStatewiseBinPrevious$ = new Subject<void>();
  private cancelSummaryCardDataPrevious$ = new Subject<void>();
  private cancelTopSellersDataPrevious$ = new Subject<void>();
  private cancelMetrixMaxDataPrevious$ = new Subject<void>();
  private cancelTopStateOrdersPrevious$ = new Subject<void>();
  private cancelTopDistrictOrdersPrevious$ = new Subject<void>();
  private cancelOverallOrdersPrevious$ = new Subject<void>();
  private cancelMapStateDataPrevious$ = new Subject<void>();
  private cancelMapDataPrevious$ = new Subject<void>();
  private cancelOrderMetricsSummaryPrevious$ = new Subject<void>();

  stateAndDistrictData = new BehaviorSubject<any>(null);

  constructor(private http: HttpClient) {
    this.baseUrl = `${environment.serverUrl}`;
    this.maxDate = new BehaviorSubject<any>(null);
  }

  getCategories() {
    return this.http.get(`${this.baseUrl}api/retail/b2c/categories/`);
  }

  setFilters(category: string, subCategory: string) {
    this.selectedCategory = category;
    this.selectedSubCategory = subCategory;
    this.filters.next({
      category,
      subCategory
    })
  }

  getLandingPageEchartData() {
    return this.http.get(`${this.baseUrl}api/landing-page/echart/`);
  }

  setFilterUpdated(val: any) {
    this.filterUpdated.next(val);
  }

  setMetrix(value: any) {
    this.metrix.next(value);
  }

  setStateAndDistrictData(value: any) {
    this.stateAndDistrictData.next(value);
  }

  getStateAndDistrictData() {
    return this.stateAndDistrictData.getValue();
  }

  getStateDistrictData() {
    return this.http.get(`${this.baseUrl}api/state_district_list/`);
  }

  setStateData(data: any) {
    this.stateData.next(data);
  }

  setCurrentUrl(url: string) {
    this.currentUrl.next(url);
  }

  setIsDownloadDataDialogOpen(value: boolean) {
    this.isDownloadDataDialogOpen.next(value);
  }

  getDataDateRange(uri: string = '') {
    if (uri) {
      return this.http.get(`${this.baseUrl}api/${uri}/get-max-date/`);
    }
    else {
      return this.http.get(`${this.baseUrl}api/retail/overall/get-max-date/`);
    }
  }

  setChoosableDateRange(value: any) {
    this.choosableDateRange.next(value);
  }

  getDateRange() {
    return this.dateRange.getValue();
  }

  getMaxDate() {
    return this.maxDate;
  }

  setDateRange(value: any) {
    this.dateRange.next(value);
  }

  setMaxDate(value: any) {
    this.maxDate.next(value);
  }

  formatDate(date: Date) {
    let d = new Date(date),
      month = '' + (d.getMonth() + 1),
      day = '' + d.getDate(),
      year = d.getFullYear();

    if (month.length < 2)
      month = '0' + month;
    if (day.length < 2)
      day = '0' + day;

    return [year, month, day].join('-');
  }

  getFormattedDateRange() {
    let startDate: any = this.formatDate(this.dateRange.value[0]);
    let endDate: any = this.formatDate(this.dateRange.value[1]);
    return [startDate, endDate];
  }

  getSummaryCardData() {
    this.cancelSummaryCardDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = {
      startDate,
      endDate,
      category: this.selectedCategory,
      subCategory: this.selectedSubCategory
    }
    return this.http.get(
      this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/top_card_delta/`,
      { params }
    ).pipe(
      takeUntil(this.cancelSummaryCardDataPrevious$)
    );
  }

  getTopStateOrders(uri: string, state: string, supplyType: string | null) {
    this.cancelTopStateOrdersPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    state = state == 'TT' ? 'None' : state;
    const params: any = {
      startDate,
      endDate,
      state,
      category: this.selectedCategory,
      subCategory: this.selectedSubCategory
    }
    if (supplyType) {
      params['sellerType'] = supplyType
    }
    return this.http.get(
      this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/top_state_${uri}/`,
      {params}
    ).pipe(
      takeUntil(this.cancelTopStateOrdersPrevious$)
    );
  }

  getTopDistrictOrders(uri: string, state: string, supplyType: string | null) {
    this.cancelTopDistrictOrdersPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    state = state == 'TT' ? 'None' : state;

    const params: any = {
      startDate,
      endDate,
      state,
      category: this.selectedCategory,
      subCategory: this.selectedSubCategory
    }

    if (supplyType) {
      params['sellerType'] = supplyType
    }
    return this.http.get(
      this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/top_district_${uri}/`,
      {params}
    ).pipe(
      takeUntil(this.cancelTopDistrictOrdersPrevious$)
    );
  }

  getOverallData(uri: string, supplyType: string | null) {
    this.cancelOverallOrdersPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params: any = {startDate, endDate,
      category: this.selectedCategory,
      subCategory: this.selectedSubCategory}
    
    if (supplyType) {
      params['sellerType'] = supplyType
    }

    return this.http.get(
      this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/top_cummulative_${uri}/`,
      {params}
    ).pipe(
      takeUntil(this.cancelOverallOrdersPrevious$)
    );
  }

  getJsonData() {
    return this.http.get('static/assets/data/map/india.json');
  }

  getMapStateData() {
    this.cancelMapStateDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = { endDate, startDate,
      category: this.selectedCategory,
      subCategory: this.selectedSubCategory }
    return this.http.get(
      this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/map_statewise_data/`,
      {params}).pipe(
        takeUntil(this.cancelMapStateDataPrevious$)
      );
  }

  getMapData() {
    this.cancelMapDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = { endDate, startDate,
      category: this.selectedCategory,
      subCategory: this.selectedSubCategory }
    return this.http.get(
      this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/map_data/`,
      {params}).pipe(
        takeUntil(this.cancelMapDataPrevious$)
      );
  }

  getOrderMetricsSummary() {
    this.cancelOrderMetricsSummaryPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = { startDate, endDate,
      category: this.selectedCategory,
      subCategory: this.selectedSubCategory }
    return this.http.get(
      this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/map_state_data/`,
      {params}
    ).pipe(
      takeUntil(this.cancelOrderMetricsSummaryPrevious$)
    );
  }

  getDomainData() {
    return this.http.get(`${this.baseUrl}api/domain/`);
  }

  getDictionaryData() {
    return this.http.get(`${this.baseUrl}api/data_dictionary/`);
  }

  getPincodeData() {
    return this.http.get(`${this.baseUrl}api/pincode/`);
  }

  getDownloadableData(tabName: string) {
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = {
      tabName, startDate, endDate, previewLimit: 5
    }
    return this.http.get(this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/fetch_downloadable_data/`, {params});
  }


  downloadData(tabName: string) {
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = {
      tabName, startDate, endDate
    }
    return this.http.get(this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/fetch_downloadable_data/`, {params});
  }

  getMetrixMaxData(uri: string, state: string) {
    this.cancelMetrixMaxDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    // state = state.replaceAll(' ', '+');

    const params = {
      startDate, endDate, 
      state: state == 'TT' ? '' : state,
      category: this.selectedCategory,
      subCategory: this.selectedSubCategory
    }

    return this.http.get(this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/max_${uri}/`, {params}).pipe(
      takeUntil(this.cancelMetrixMaxDataPrevious$)
    );
  }


  getTopSellersData(type: string, uri: string, state: string, district: string,) {
    this.cancelTopSellersDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = {
      startDate, endDate, 
      state: (state ? state : ''),
      district_name: district ? district : '',
      category: this.selectedCategory,
      subCategory: this.selectedSubCategory
    }
    return this.http.get(this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/top_${type}_${uri}/`, {params}).pipe(
      takeUntil(this.cancelTopSellersDataPrevious$)
    );
  }

  getStatewiseBin(uri: string) {
    this.cancelStatewiseBinPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = { startDate, endDate,
      category: this.selectedCategory,
      subCategory: this.selectedSubCategory }
    return this.http.get(this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/${uri}_per_state/`, {params}).pipe(
      takeUntil(this.cancelStatewiseBinPrevious$)
    );
  }

  private cancelMetrixSunBurstChartDataPrevious$ = new Subject<void>();
  getMetrixSunBurstChartData(uri: string, state: string, supplyType: string | null) {
    this.cancelMetrixSunBurstChartDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    // state = state.replaceAll(' ', '+');
    const params: any = { startDate, endDate, state: state == 'TT' ? '' : state,
      category: this.selectedCategory,
      subCategory: this.selectedSubCategory }

    if (supplyType) {
      params['sellerType'] = supplyType
    }
    return this.http.get(this.baseUrl + `api/retail/b2c/category_penetration_${uri}/`, {params}).pipe(
      takeUntil(this.cancelMetrixSunBurstChartDataPrevious$)
    );
  }

  getLandingPageCumulativeOrderCount() {
    return this.http.get(`${this.baseUrl}api/landing-page/cumulative_orders/`);
  }
  
  getKeyInsights() {
    return this.http.get(`${this.baseUrl}api/key-insight-data/`)
  }
  
}
