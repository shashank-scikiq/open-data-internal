import { METRICS } from './global';
import { getMetrixKey } from './global';

export interface CaseData {
    st_data: number;
    map_order_demand: number;
    map_total_orders_metrics: number;
    map_total_orders_met: number;

    map_tot_item_delivered: number;
    map_total_active_sellers_metrics: number;
    map_total_hyperlocal_delivered: number;
    map_percentage_hyperlocal: number;
    map_total_products_sellers: number;
    map_total_zonal_commerce_metrics: number;
    map_act_pincodes: number;
}

export const NOCASEDATA: CaseData = {
    st_data: 0,
    map_order_demand: 0,
    map_total_orders_metrics: 0,
    map_total_orders_met: 0,

    map_tot_item_delivered: 0,
    map_total_active_sellers_metrics: 0,
    map_total_hyperlocal_delivered: 0,
    map_percentage_hyperlocal: 0,
    map_total_products_sellers: 0,
    map_total_zonal_commerce_metrics: 0,
    map_act_pincodes: 0,
}

export interface MapColorMapper {
    map_total_orders_metrics: string[];
    map_total_active_sellers_metrics: string[];
    map_total_zonal_commerce_metrics: string[];
}

export interface MapStrokeMapper {
    map_total_orders_metrics: string;
    map_total_active_sellers_metrics: string;
    map_total_zonal_commerce_metrics: string;
}


export const mapStrokeMapper: MapStrokeMapper = {
    map_total_orders_metrics: "#FF7722",
    map_total_active_sellers_metrics: "#1c75bc",
    map_total_zonal_commerce_metrics: "#10b759",
}


export const chloroplethcolormapper2: MapColorMapper | any = {
    map_total_orders_metrics: ["#ffffff", "#FF7722"],
    map_total_active_sellers_metrics: ["#ffffff", "#1c75bc"],
    map_total_zonal_commerce_metrics: ["#ffffff", "#10b759"],
}

export const chloroplethcolormapper3: MapColorMapper | any = {
    map_total_orders_metrics: ["#ffffff", "#f9f0e9", "#FF7722"],
    map_total_active_sellers_metrics: ["#ffffff", "#dfebf5", "#1c75bc"],
    map_total_zonal_commerce_metrics: ["#ffffff", "#eefaf3", "#10b759"],
}

export interface MapStatewiseData {
    active_sellers: number;
    confirmed_orders: number;
    intradistrict_orders_percentage: number;
    intrastate_orders_percentage: number;
    orderDemand: number;
    state: string;
    statecode: string;
}

export interface OrderMatrixData {
    active_sellers: number;
    avg_items_per_order: number;
    intradistrict_percentage: number;
    intrastate_percentage: number;
    order_demand: number;
}

export interface MapStateData {
    activeSellers: number;
    confirmedOrders: number;
    intradistrictOrdersPercentage: number;
    intrastateOrdersPercentage: number;
    orderDemand: number;
    state: string;
    statecode: string;
}

export const StateCode: any = {
    "Total": "TT",
    "Maharashtra": "MH",
    "Tamil Nadu": "TN",
    "Andhra Pradesh": "AP",
    "Karnataka": "KA",
    "Delhi": "DL",
    "Uttar Pradesh": "UP",
    "West Bengal": "WB",
    "Bihar": "BR",
    "Telangana": "TG",
    "Gujarat": "GJ",
    "Assam": "AS",
    "Rajasthan": "RJ",
    "Odisha": "OR",
    "Haryana": "HR",
    "Madhya Pradesh": "MP",
    "Kerala": "KL",
    "Punjab": "PB",
    "Jammu and Kashmir": "JK",
    "Jharkhand": "JH",
    "Chhattisgarh": "CT",
    "Uttarakhand": "UT",
    "Goa": "GA",
    "Tripura": "TR",
    "Puducherry": "PY",
    "Manipur": "MN",
    "Himachal Pradesh": "HP",
    "Nagaland": "NL",
    "Arunachal Pradesh": "AR",
    "Andaman and Nicobar Islands": "AN",
    "Ladakh": "LA",
    "Chandigarh": "CH",
    "Dadra and Nagar Haveli and Daman and Diu": "DN",
    "Meghalaya": "ML",
    "Sikkim": "SK",
    "Mizoram": "MZ",
    // "State Unassigned": "UN",
    "Lakshadweep": "LD"
}

export const getStateTooltipContent = (d: any, casetype: any, color: any, top3Data: any) => {
    const metricKey = getMetrixKey(casetype);

    let colorValue = "";
    if (casetype === "map_total_zonal_commerce_metrics") {
        colorValue = "#10b759";
    } else if (casetype === "map_total_orders_metrics") {
        colorValue = "#e3570a";
    } else if (casetype === "map_total_active_sellers_metrics") {
        colorValue = "#1C75BC";
    }


    return `
       
            <p class="margin-0 upper-title open-data-grey-700">
                ${metricKey} in
            </div>
            <p class="font-bolder selection-name margin-0"><i class="margin-right-2 fa-solid fa-location-dot"></i>  ${d.id}</p>
            <h3 class="font-bolder margin-bottom-1 count-section" style="
                color: ${colorValue};">
                    ${metricKey === 'Registered Sellers' && d.properties.totalcasedata[casetype] === 0
            ? 'No Data'
            : (metricKey === 'Intrastate Percentage'
                ? new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]) + '%'
                : new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]))
            }
            </h3>

            <div class="top-data">
                <h6 class="margin-0 font-xs font-bold">TOP STATES</h6>
                <div>
                    ${getTopStateHTML(top3Data, casetype)}
                </div>
            </div>
        
    `;
}

const getTopStateHTML = (top3Data: any, casetype: any) => {
    return top3Data.map((d: any) => {
        const metricValue = casetype === 'map_total_active_sellers_metrics' && d.properties.totalcasedata[casetype] === 0
            ? 'No Data'
            : (casetype === 'map_total_zonal_commerce_metrics'
                ? new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]) + '%'
                : new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]));

        return `
            <div class="entry-container">
                <i class="loc-icon fa-solid fa-location-dot"></i>
                <div class="entry-section">
                    <h6 class="margin-0 title open-data-grey-800">${d.id}</h6>
                    <h4 class="margin-0 font-bold count open-data-blue-700">${metricValue}</h4>
                </div>
            </div>
        `;
    }).join('');
}

export const getDistrictTooltipContent = (d: any, casetype: any, color: any, top3Data: any) => {
    const metricKey = getMetrixKey(casetype);

    let colorValue = "";
    if (casetype === "map_total_zonal_commerce_metrics") {
        colorValue = "#10b759";
    } else if (casetype === "map_total_orders_metrics") {
        colorValue = "#e3570a";
    } else if (casetype === "map_total_active_sellers_metrics") {
        colorValue = "#1C75BC";
    }

    const isNoData = metricKey === 'Registered Sellers' && d.properties.totalcasedata[casetype] === 0;

    const metricValue = isNoData
        ? 'No Data'
        : (metricKey === 'Intrastate Percentage'
            ? new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]) + '%'
            : new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]));

    return `
        

        <p class="margin-0 upper-title open-data-grey-700">
                ${metricKey} in
            </div>
            <p class="font-bolder selection-name margin-0"><i class="margin-right-2 fa-solid fa-location-dot"></i>  ${d.properties.district}</p>
            <h3 class="font-bolder margin-bottom-1 count-section" style="
                color: ${colorValue};">
                ${metricValue}
            </h3>

            <div class="top-data">
                <h6 class="margin-0 font-xs font-bold">TOP DISTRICTS</h6>
                <div>
                    ${getTopDistrictsHTML(top3Data, casetype)}
                </div>
            </div>
    `;
}

const getTopDistrictsHTML = (top3Data: any, casetype: any) => {
    return top3Data.map((d: any) => {
        const metricValue = casetype === 'map_total_active_sellers_metrics' && d.properties.totalcasedata[casetype] === 0
            ? 'No Data'
            : (casetype === 'map_total_zonal_commerce_metrics'
                ? new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]) + '%'
                : new Intl.NumberFormat().format(d.properties.totalcasedata[casetype]));

        return `
            <div class="entry-container">
                <i class="loc-icon fa-solid fa-location-dot"></i>
                <div class="entry-section">
                    <h6 class="margin-0 title open-data-grey-800">${d.properties.district}</h6>
                    <h4 class="margin-0 font-bold count open-data-blue-700">${metricValue}</h4>
                </div>
            </div>
        `;
    }).join('');
}