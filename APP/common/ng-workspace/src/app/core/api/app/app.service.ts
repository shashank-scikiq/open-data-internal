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
  private cancelStatewiseBinPrevious$ = new Subject<void>();
  private cancelSummaryCardDataPrevious$ = new Subject<void>();
  private cancelTopSellersDataPrevious$ = new Subject<void>();
  private cancelMetrixMaxDataPrevious$ = new Subject<void>();
  private cancelTopStateOrdersPrevious$ = new Subject<void>();
  private cancelTopDistrictOrdersPrevious$ = new Subject<void>();
  private cancelOverallOrdersPrevious$ = new Subject<void>();
  private cancelMapStateDataPrevious$ = new Subject<void>();
  private cancelOrderMetricsSummaryPrevious$ = new Subject<void>();

  stateAndDistrictData = new BehaviorSubject<any>(null);


  constructor(private http: HttpClient) {
    this.baseUrl = `${environment.serverUrl}`;
    this.maxDate = new BehaviorSubject<any>(null);
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
      return this.http.get(`${this.baseUrl}api/get-max-date/`);
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
  getFormattedChoosableDateRange() {
    let startDate: any = this.formatDate(this.choosableDateRange.value[0]);
    let endDate: any = this.formatDate(this.choosableDateRange.value[1]);
    return [startDate, endDate];
  }

  getFormattedDateRange() {
    let startDate: any = this.formatDate(this.dateRange.value[0]);
    let endDate: any = this.formatDate(this.dateRange.value[1]);
    return [startDate, endDate];
  }

  getSummaryCardData() {
    this.cancelSummaryCardDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    let [choosableStartDate, choosableEndDate] = this.getFormattedChoosableDateRange();

    const params = {
      startDate,
      endDate,
      minDate: choosableStartDate, maxDate: choosableEndDate
    }
    return this.http.get(
      this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/top_card_delta/`,
      { params }
    ).pipe(
      takeUntil(this.cancelSummaryCardDataPrevious$)
    );
  }

  getTopStateOrders(uri: string, state: string) {
    this.cancelTopStateOrdersPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    state = state == 'TT' ? 'None' : state;
    const params = {
      startDate,
      endDate,
      state
    }
    return this.http.get(
      this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/top_state_${uri}/`,
      {params}
    ).pipe(
      takeUntil(this.cancelTopStateOrdersPrevious$)
    );
  }

  getTopDistrictOrders(uri: string, state: string) {
    this.cancelTopDistrictOrdersPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    state = state == 'TT' ? 'None' : state;

    const params = {
      startDate,
      endDate,
      state
    }
    return this.http.get(
      this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/top_district_${uri}/`,
      {params}
    ).pipe(
      takeUntil(this.cancelTopDistrictOrdersPrevious$)
    );
  }

  getOverallOrders(uri: string) {
    this.cancelOverallOrdersPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = {startDate, endDate}

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
    const params = { endDate, startDate }
    return this.http.get(
      this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/map_statewise_data/`,
      {params}).pipe(
        takeUntil(this.cancelMapStateDataPrevious$)
      );
  }

  getOrderMetricsSummary() {
    this.cancelOrderMetricsSummaryPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = { startDate, endDate }
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
    state = state.replaceAll(' ', '+');

    const params = {
      startDate, endDate, 
      state: state == 'TT' ? '' : state
    }

    return this.http.get(this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/max_${uri}/`, {params}).pipe(
      takeUntil(this.cancelMetrixMaxDataPrevious$)
    );
  }


  getTopSellersData(uri: string, state: string, district: string,) {
    this.cancelTopSellersDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = {
      startDate, endDate, 
      state: (state ? state : ''),
      district_name: district ? district : ''
    }
    return this.http.get(this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/top_seller_${uri}/`, {params}).pipe(
      takeUntil(this.cancelTopSellersDataPrevious$)
    );
  }

  getStatewiseBin(uri: string) {
    this.cancelStatewiseBinPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = { startDate, endDate }
    return this.http.get(this.baseUrl + `api/${AppApiMap[this.currentUrl.value]}/${uri}_per_state/`, {params}).pipe(
      takeUntil(this.cancelStatewiseBinPrevious$)
    );
  }
  
  // dq-apis
  private cancelTrend1Previous$ = new Subject<void>();
  getTrend1Data() {
    this.cancelTrend1Previous$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = { startDate, endDate }
    return this.http.get(this.baseUrl + `api/dq_report/trend_1/`, {params}).pipe(
      takeUntil(this.cancelTrend1Previous$)
    );
  }

  private cancelTrend2Previous$ = new Subject<void>();
  getTrend2Data() {
    this.cancelTrend2Previous$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = { startDate, endDate }
    return this.http.get(this.baseUrl + `api/dq_report/trend_2/`, {params}).pipe(
      takeUntil(this.cancelTrend2Previous$)
    );
  }

  private cancelDetailCompletedTableDataPrevious$ = new Subject<void>();
  getDetailCompletedTableData() {
    this.cancelDetailCompletedTableDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = { startDate, endDate }
    return this.http.get(this.baseUrl + `api/dq_report/detail_completed_table_data/`, {params}).pipe(
      takeUntil(this.cancelDetailCompletedTableDataPrevious$)
    );
  }


  private cancelDetailCancelTableDataPrevious$ = new Subject<void>();
  getDetailCancelTableData() {
    this.cancelDetailCancelTableDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = { startDate, endDate }
    return this.http.get(this.baseUrl + `api/dq_report/detail_cancel_table_data/`, {params}).pipe(
      takeUntil(this.cancelDetailCancelTableDataPrevious$)
    );
  }

  private cancelHighestMissingPIDPrevious$ = new Subject<void>();
  getCancelHighestMissingData() {
    this.cancelHighestMissingPIDPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = { startDate, endDate }
    return this.http.get(this.baseUrl + `api/dq_report/cancel_highest_missing_pid_data/`, {params}).pipe(
      takeUntil(this.cancelHighestMissingPIDPrevious$)
    );
  }


  private cancelRadialChartrevious$ = new Subject<void>();
  getRadialChartData() {
    this.cancelRadialChartrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = { date: '2024-05-08' }
    return this.http.get(this.baseUrl + `api/dq/missing_percentage/`, {params}).pipe(
      takeUntil(this.cancelRadialChartrevious$)
    );
  }

  private cancelDQTopCardPrevious$ = new Subject<void>();
  getDQTopCardData() {
    this.cancelDQTopCardPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = { startDate, endDate }
    return this.http.get(this.baseUrl + `api/dq_report/top_card/`, {params}).pipe(
      takeUntil(this.cancelDQTopCardPrevious$)
    );
  }


  getDataSanityChart1Data() {
    return this.http.get(this.baseUrl + `api/dq_report/data_sanity/chart1/`);
  }

  getDataSanityChart2Data() {
    return this.http.get(this.baseUrl + `api/dq_report/data_sanity/chart2/`);
  }

  getDataSanityTableData() {
    return this.http.get(this.baseUrl + `api/dq_report/data_sanity/table/`);
  }
}
