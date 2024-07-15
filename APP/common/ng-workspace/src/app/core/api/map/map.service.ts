import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '@openData/env/environment';
import { BehaviorSubject, Observable } from 'rxjs';


@Injectable({
  providedIn: 'root'
})
export class MapService {
  private baseUrl: string | null = null;
  selectedState = new BehaviorSubject<string>('TT');
  selectedState$ = this.selectedState.asObservable();

  constructor(private http: HttpClient) {
    this.baseUrl = `${environment.serverUrl}`;
  }

  setSelectedState(state: string) {
    this.selectedState.next(state);
  }
}
