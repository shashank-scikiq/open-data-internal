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

  filterUpdated = new BehaviorSubject<any>(null);
  filterUpdated$ = this.filterUpdated.asObservable();

  constructor(private http: HttpClient) {
    this.baseUrl = `${environment.serverUrl}`;
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

    const params = {
      city: this.activeCity.value
    }
    return this.http.get(
      this.baseUrl + `api/logistics/search/city_wise_data/`,
      { params }
    ).pipe(
      takeUntil(this.cancelCityWiseDataPrevious$)
    )


  }

  private cancelTopCardsDataPrevious$ = new Subject<void>();
  getTopCardsData() {
    this.cancelTopCardsDataPrevious$.next();
    const params = {
      city: this.activeCity.value
    }
    return this.http.get(
      this.baseUrl + `api/logistics/search/top_card_delta/`,
      { params }
    ).pipe(
      takeUntil(this.cancelTopCardsDataPrevious$)
    );
  }

}
