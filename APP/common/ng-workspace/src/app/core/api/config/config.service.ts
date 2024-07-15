import { Injectable } from '@angular/core';
import * as crypto from 'crypto-js';
import { BehaviorSubject } from 'rxjs';
import { environment } from '@openData/env/environment';

@Injectable({
    providedIn: 'root'
})
export class ConfigService {
    private config: any;
    private signature: string;
    private secretKey = environment.projectString;
    configured = new BehaviorSubject<boolean>(false);
    configured$ = this.configured.asObservable();

    constructor() {
        this.config = (window as any).appConfig;
        this.signature = (window as any).appConfigSignature;
        this.verifyConfig();
    }

    get(key: string): any {
        return this.config[key];
    }

    private verifyConfig() {
        const configString = JSON.stringify(this.config);
        const computedSignature = crypto.HmacSHA256(configString, this.secretKey).toString();

        // if (computedSignature !== this.signature) {
        //     console.error('Configuration signature mismatch!');
        //     this.configured.next(false);
        // } else {
        //   console.log("Configuration signature match!")
        //   this.configured.next(true);
        // }
        this.configured.next(true);
    }
}
