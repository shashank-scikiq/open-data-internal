import { TestBed } from '@angular/core/testing';

import { LogisticSearchService } from './logistic-search.service';

describe('LogisticSearchService', () => {
  let service: LogisticSearchService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LogisticSearchService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
