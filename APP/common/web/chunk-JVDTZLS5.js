import{R as r,S as f,V as C,j as l,l as v}from"./chunk-ILFPQEWV.js";import{Cb as u,Lb as g,Rb as a,la as p,lb as d,td as h,wa as n,xa as m}from"./chunk-5XXJNCEW.js";function x(e,t){e&1&&a(0,"app-detail",0)}var y=(()=>{let t=class t{constructor(i){this.appService=i,this.isLoading=!1}ngOnInit(){this.getDateRange()}getDateRange(){this.isLoading=!0,this.appService.getDataDateRange("retail/overall").subscribe(i=>{this.appService.setDateRange([new Date(i.min_date),new Date(i.max_date)]),this.appService.setChoosableDateRange([new Date(i.min_date),new Date(i.max_date)]),this.isLoading=!1},i=>{console.log(i),this.isLoading=!1})}};t.\u0275fac=function(o){return new(o||t)(d(v))},t.\u0275cmp=n({type:t,selectors:[["app-retail-overall"]],decls:1,vars:1,consts:[["pageTitle","Retail"]],template:function(o,c){o&1&&u(0,x,1,0,"app-detail",0),o&2&&g(0,c.isLoading?-1:0)},dependencies:[r]});let e=t;return e})();var R=(()=>{let t=class t{};t.\u0275fac=function(o){return new(o||t)},t.\u0275cmp=n({type:t,selectors:[["app-retail-b2b"]],decls:1,vars:0,consts:[["pageTitle","Retail B2B"]],template:function(o,c){o&1&&a(0,"app-detail",0)},dependencies:[r]});let e=t;return e})();var b=(()=>{let t=class t{};t.\u0275fac=function(o){return new(o||t)},t.\u0275cmp=n({type:t,selectors:[["app-retail-b2c"]],decls:1,vars:0,consts:[["pageTitle","Retail B2C"]],template:function(o,c){o&1&&a(0,"app-detail",0)},dependencies:[r]});let e=t;return e})();var M=[{path:"",component:y},{path:"b2b",component:R,canActivate:[f],data:{configKey:"ENABLE_STAGING_ROUTE"}},{path:"b2c",component:b,canActivate:[f],data:{configKey:"ENABLE_STAGING_ROUTE"}}],T=(()=>{let t=class t{};t.\u0275fac=function(o){return new(o||t)},t.\u0275mod=m({type:t}),t.\u0275inj=p({imports:[l.forChild(M),l]});let e=t;return e})();var P=(()=>{let t=class t{};t.\u0275fac=function(o){return new(o||t)},t.\u0275mod=m({type:t}),t.\u0275inj=p({imports:[h,T,C]});let e=t;return e})();export{P as a};
