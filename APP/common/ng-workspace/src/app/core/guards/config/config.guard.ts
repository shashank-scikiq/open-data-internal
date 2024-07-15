import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { ConfigService } from '../../api/config/config.service';

@Injectable({
    providedIn: 'root'
})
export class ConfigGuard implements CanActivate {

    constructor(private configService: ConfigService) {}

    canActivate(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot
    ): boolean | UrlTree | Observable<boolean | UrlTree> | Promise<boolean | UrlTree> {
        const routeConfigKey = route.data['configKey'];
        if (routeConfigKey) {
            return Boolean(this.configService.get(routeConfigKey) == 'True');
        }
        return true;
    }
}

