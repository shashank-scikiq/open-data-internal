import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '@openData/env/environment';
import { BehaviorSubject, Subject, of, switchMap, takeUntil } from 'rxjs';
import { AppApiMap } from '../../utils/global';

@Injectable({
  providedIn: 'root'
})
export class LogisticSearchService {
  private baseUrl: string | null = null;

  activeCity = new BehaviorSubject<string>("New Delhi");
  activeCity$ = this.activeCity.asObservable();

  activeTimeInterval = new BehaviorSubject<string>("Overall");
  activeTimeInterval$ = this.activeTimeInterval.asObservable();

  activeState = new BehaviorSubject<string>("TT");
  activeState$ = this.activeState.asObservable();

  pincodeLevelView = new BehaviorSubject<boolean>(false);
  pincodeLevelView$ = this.pincodeLevelView.asObservable();

  dateRange = new BehaviorSubject<any>(null);
  choosableDateRange = new BehaviorSubject<any>(null);
  dateRange$ = this.dateRange.asObservable();
  choosableDateRange$ = this.choosableDateRange.asObservable();

  filterUpdated = new BehaviorSubject<any>(null);
  filterUpdated$ = this.filterUpdated.asObservable();

  constructor(private http: HttpClient) {
    this.baseUrl = `${environment.serverUrl}`;
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

  setChoosableDateRange(value: any) {
    this.choosableDateRange.next(value);
  }
  setDateRange(value: any) {
    this.dateRange.next(value);
  }

  setActiveCity(value: string) {
    this.activeCity.next(value);
  }
  setActiveTimeInterval(value: string) {
    this.activeTimeInterval.next(value);
  }

  private cancelCityWiseDataPrevious$ = new Subject<void>();
  getCityWiseData() {
    this.cancelCityWiseDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = {
      city: this.activeCity.value,
      startDate,
      endDate
    }
    return this.http.get(
      this.baseUrl + `api/logistics/search/city_wise_data/`,
      { params }
    ).pipe(
      takeUntil(this.cancelCityWiseDataPrevious$)
    )
  }


  private cancelstateWiseDataPrevious$ = new Subject<void>();
  getStateWiseData() {
    this.cancelstateWiseDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = {
      state: this.activeState.value,
      startDate,
      endDate
    }
    return this.http.get(
      this.baseUrl + `api/logistics/search/state_wise_data/`,
      { params }
    ).pipe(
      takeUntil(this.cancelstateWiseDataPrevious$)
    )
  }


  private cancelOverallDataPrevious$ = new Subject<void>();
  getOverallData() {
    this.cancelOverallDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = {
      startDate,
      endDate
    }
    return this.http.get(
      this.baseUrl + `api/logistics/search/overall_data/`,
      { params }
    ).pipe(
      takeUntil(this.cancelOverallDataPrevious$)
    )
  }

  private cancelTopCardsDataPrevious$ = new Subject<void>();
  getTopCardsData() {
    this.cancelTopCardsDataPrevious$.next();
    let [startDate, endDate] = this.getFormattedDateRange();
    const params = {
      city: this.activeCity.value,
      startDate,
      endDate
    }
    return this.http.get(
      this.baseUrl + `api/logistics/search/top_card_delta/`,
      { params }
    ).pipe(
      takeUntil(this.cancelTopCardsDataPrevious$)
    );
  }

  getDateRange() {
    return this.http.get(this.baseUrl + 'api/logistics/search/data_date_range/');
  }

}
