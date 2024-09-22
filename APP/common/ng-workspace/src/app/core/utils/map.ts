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

export const CityLatLong: any = {
    'Bangalore': [77.5946, 12.9716],
    'New Delhi': [77.1025, 28.7041]
}

export const CityWiseGeoJSONPincodeFiles: any = {
    'Bangalore': [
        'static/assets/data/pincode-level/bangalore/560001.geojson', 'static/assets/data/pincode-level/bangalore/560002.geojson',
        'static/assets/data/pincode-level/bangalore/560003.geojson', 'static/assets/data/pincode-level/bangalore/560004.geojson', 'static/assets/data/pincode-level/bangalore/560005.geojson',
        'static/assets/data/pincode-level/bangalore/560006.geojson', 'static/assets/data/pincode-level/bangalore/560007.geojson', 'static/assets/data/pincode-level/bangalore/560008.geojson',
        'static/assets/data/pincode-level/bangalore/560009.geojson', 'static/assets/data/pincode-level/bangalore/560010.geojson',
        'static/assets/data/pincode-level/bangalore/560011.geojson', 'static/assets/data/pincode-level/bangalore/560012.geojson', 'static/assets/data/pincode-level/bangalore/560013.geojson',
        'static/assets/data/pincode-level/bangalore/560014.geojson', 'static/assets/data/pincode-level/bangalore/560015.geojson', 'static/assets/data/pincode-level/bangalore/560016.geojson',
        'static/assets/data/pincode-level/bangalore/560017.geojson', 'static/assets/data/pincode-level/bangalore/560018.geojson', 'static/assets/data/pincode-level/bangalore/560019.geojson',
        'static/assets/data/pincode-level/bangalore/560020.geojson', 'static/assets/data/pincode-level/bangalore/560021.geojson', 'static/assets/data/pincode-level/bangalore/560022.geojson',
        'static/assets/data/pincode-level/bangalore/560023.geojson', 'static/assets/data/pincode-level/bangalore/560024.geojson', 'static/assets/data/pincode-level/bangalore/560025.geojson',
        'static/assets/data/pincode-level/bangalore/560026.geojson', 'static/assets/data/pincode-level/bangalore/560027.geojson',
        'static/assets/data/pincode-level/bangalore/560029.geojson', 'static/assets/data/pincode-level/bangalore/560030.geojson',
        'static/assets/data/pincode-level/bangalore/560032.geojson', 'static/assets/data/pincode-level/bangalore/560033.geojson', 'static/assets/data/pincode-level/bangalore/560034.geojson', 'static/assets/data/pincode-level/bangalore/560035.geojson',
        'static/assets/data/pincode-level/bangalore/560036.geojson', 'static/assets/data/pincode-level/bangalore/560037.geojson', 'static/assets/data/pincode-level/bangalore/560038.geojson', 'static/assets/data/pincode-level/bangalore/560039.geojson',
        'static/assets/data/pincode-level/bangalore/560040.geojson', 'static/assets/data/pincode-level/bangalore/560041.geojson', 'static/assets/data/pincode-level/bangalore/560042.geojson', 'static/assets/data/pincode-level/bangalore/560043.geojson',
        'static/assets/data/pincode-level/bangalore/560045.geojson', 'static/assets/data/pincode-level/bangalore/560046.geojson', 'static/assets/data/pincode-level/bangalore/560047.geojson',
        'static/assets/data/pincode-level/bangalore/560048.geojson', 'static/assets/data/pincode-level/bangalore/560049.geojson', 'static/assets/data/pincode-level/bangalore/560050.geojson',
    
        'static/assets/data/pincode-level/bangalore/560051.geojson', 'static/assets/data/pincode-level/bangalore/560052.geojson', 'static/assets/data/pincode-level/bangalore/560053.geojson', 'static/assets/data/pincode-level/bangalore/560054.geojson',
        'static/assets/data/pincode-level/bangalore/560055.geojson', 'static/assets/data/pincode-level/bangalore/560056.geojson', 'static/assets/data/pincode-level/bangalore/560057.geojson', 'static/assets/data/pincode-level/bangalore/560058.geojson',
        'static/assets/data/pincode-level/bangalore/560059.geojson', 'static/assets/data/pincode-level/bangalore/560060.geojson', 'static/assets/data/pincode-level/bangalore/560061.geojson', 'static/assets/data/pincode-level/bangalore/560062.geojson',
        'static/assets/data/pincode-level/bangalore/560063.geojson', 'static/assets/data/pincode-level/bangalore/560064.geojson', 'static/assets/data/pincode-level/bangalore/560065.geojson', 'static/assets/data/pincode-level/bangalore/560066.geojson',
        'static/assets/data/pincode-level/bangalore/560067.geojson', 'static/assets/data/pincode-level/bangalore/560068.geojson', 'static/assets/data/pincode-level/bangalore/560069.geojson', 'static/assets/data/pincode-level/bangalore/560070.geojson',
        'static/assets/data/pincode-level/bangalore/560071.geojson', 'static/assets/data/pincode-level/bangalore/560072.geojson', 'static/assets/data/pincode-level/bangalore/560073.geojson', 'static/assets/data/pincode-level/bangalore/560074.geojson',
        'static/assets/data/pincode-level/bangalore/560075.geojson', 'static/assets/data/pincode-level/bangalore/560076.geojson', 'static/assets/data/pincode-level/bangalore/560077.geojson', 'static/assets/data/pincode-level/bangalore/560078.geojson',
        'static/assets/data/pincode-level/bangalore/560079.geojson', 'static/assets/data/pincode-level/bangalore/560080.geojson', 'static/assets/data/pincode-level/bangalore/560081.geojson', 'static/assets/data/pincode-level/bangalore/560082.geojson',
        'static/assets/data/pincode-level/bangalore/560083.geojson', 'static/assets/data/pincode-level/bangalore/560084.geojson', 'static/assets/data/pincode-level/bangalore/560085.geojson', 'static/assets/data/pincode-level/bangalore/560086.geojson',
        'static/assets/data/pincode-level/bangalore/560087.geojson', 'static/assets/data/pincode-level/bangalore/560088.geojson', 'static/assets/data/pincode-level/bangalore/560089.geojson', 'static/assets/data/pincode-level/bangalore/560090.geojson',
        'static/assets/data/pincode-level/bangalore/560091.geojson', 'static/assets/data/pincode-level/bangalore/560092.geojson', 'static/assets/data/pincode-level/bangalore/560093.geojson', 'static/assets/data/pincode-level/bangalore/560094.geojson',
        'static/assets/data/pincode-level/bangalore/560095.geojson', 'static/assets/data/pincode-level/bangalore/560096.geojson', 'static/assets/data/pincode-level/bangalore/560097.geojson', 'static/assets/data/pincode-level/bangalore/560098.geojson',
        'static/assets/data/pincode-level/bangalore/560099.geojson', 'static/assets/data/pincode-level/bangalore/560100.geojson', 'static/assets/data/pincode-level/bangalore/560102.geojson',
        'static/assets/data/pincode-level/bangalore/560103.geojson', 'static/assets/data/pincode-level/bangalore/560104.geojson', 'static/assets/data/pincode-level/bangalore/560105.geojson', 'static/assets/data/pincode-level/bangalore/560107.geojson',
        'static/assets/data/pincode-level/bangalore/560108.geojson', 'static/assets/data/pincode-level/bangalore/560109.geojson', 'static/assets/data/pincode-level/bangalore/560110.geojson', 'static/assets/data/pincode-level/bangalore/560111.geojson',
        'static/assets/data/pincode-level/bangalore/560112.geojson', 'static/assets/data/pincode-level/bangalore/560113.geojson', 'static/assets/data/pincode-level/bangalore/560114.geojson', 'static/assets/data/pincode-level/bangalore/560115.geojson',
        'static/assets/data/pincode-level/bangalore/560116.geojson', 'static/assets/data/pincode-level/bangalore/560117.geojson', 'static/assets/data/pincode-level/bangalore/560500.geojson', 'static/assets/data/pincode-level/bangalore/562106.geojson',
        'static/assets/data/pincode-level/bangalore/562107.geojson', 'static/assets/data/pincode-level/bangalore/562123.geojson', 'static/assets/data/pincode-level/bangalore/562125.geojson', 'static/assets/data/pincode-level/bangalore/562130.geojson',
        'static/assets/data/pincode-level/bangalore/562149.geojson', 'static/assets/data/pincode-level/bangalore/562157.geojson', 'static/assets/data/pincode-level/bangalore/562162.geojson'
    ],
    "New Delhi": [
        'static/assets/data/pincode-level/delhi/110001.geojson','static/assets/data/pincode-level/delhi/110002.geojson','static/assets/data/pincode-level/delhi/110003.geojson','static/assets/data/pincode-level/delhi/110004.geojson',
        'static/assets/data/pincode-level/delhi/110005.geojson', 'static/assets/data/pincode-level/delhi/110006.geojson','static/assets/data/pincode-level/delhi/110007.geojson','static/assets/data/pincode-level/delhi/110008.geojson',
        'static/assets/data/pincode-level/delhi/110009.geojson', 'static/assets/data/pincode-level/delhi/110010.geojson','static/assets/data/pincode-level/delhi/110011.geojson','static/assets/data/pincode-level/delhi/110012.geojson',
        'static/assets/data/pincode-level/delhi/110013.geojson', 'static/assets/data/pincode-level/delhi/110014.geojson','static/assets/data/pincode-level/delhi/110015.geojson','static/assets/data/pincode-level/delhi/110016.geojson',
        'static/assets/data/pincode-level/delhi/110017.geojson','static/assets/data/pincode-level/delhi/110018.geojson','static/assets/data/pincode-level/delhi/110019.geojson','static/assets/data/pincode-level/delhi/110020.geojson',
        'static/assets/data/pincode-level/delhi/110021.geojson','static/assets/data/pincode-level/delhi/110022.geojson','static/assets/data/pincode-level/delhi/110023.geojson','static/assets/data/pincode-level/delhi/110024.geojson',
        'static/assets/data/pincode-level/delhi/110025.geojson','static/assets/data/pincode-level/delhi/110026.geojson','static/assets/data/pincode-level/delhi/110027.geojson','static/assets/data/pincode-level/delhi/110028.geojson',
        'static/assets/data/pincode-level/delhi/110029.geojson','static/assets/data/pincode-level/delhi/110030.geojson','static/assets/data/pincode-level/delhi/110031.geojson', 'static/assets/data/pincode-level/delhi/110032.geojson',
        'static/assets/data/pincode-level/delhi/110033.geojson','static/assets/data/pincode-level/delhi/110034.geojson','static/assets/data/pincode-level/delhi/110035.geojson','static/assets/data/pincode-level/delhi/110036.geojson',
        'static/assets/data/pincode-level/delhi/110037.geojson','static/assets/data/pincode-level/delhi/110038.geojson','static/assets/data/pincode-level/delhi/110039.geojson','static/assets/data/pincode-level/delhi/110040.geojson',
        'static/assets/data/pincode-level/delhi/110041.geojson','static/assets/data/pincode-level/delhi/110042.geojson','static/assets/data/pincode-level/delhi/110043.geojson','static/assets/data/pincode-level/delhi/110044.geojson',
        'static/assets/data/pincode-level/delhi/110045.geojson','static/assets/data/pincode-level/delhi/110046.geojson','static/assets/data/pincode-level/delhi/110047.geojson','static/assets/data/pincode-level/delhi/110048.geojson',
        'static/assets/data/pincode-level/delhi/110049.geojson','static/assets/data/pincode-level/delhi/110050.geojson','static/assets/data/pincode-level/delhi/110051.geojson',
        'static/assets/data/pincode-level/delhi/110052.geojson','static/assets/data/pincode-level/delhi/110053.geojson','static/assets/data/pincode-level/delhi/110054.geojson','static/assets/data/pincode-level/delhi/110055.geojson',
        'static/assets/data/pincode-level/delhi/110056.geojson', 'static/assets/data/pincode-level/delhi/110057.geojson','static/assets/data/pincode-level/delhi/110058.geojson','static/assets/data/pincode-level/delhi/110059.geojson',
        'static/assets/data/pincode-level/delhi/110060.geojson', 'static/assets/data/pincode-level/delhi/110061.geojson','static/assets/data/pincode-level/delhi/110062.geojson','static/assets/data/pincode-level/delhi/110063.geojson',
        'static/assets/data/pincode-level/delhi/110064.geojson', 'static/assets/data/pincode-level/delhi/110065.geojson','static/assets/data/pincode-level/delhi/110066.geojson','static/assets/data/pincode-level/delhi/110067.geojson',
        'static/assets/data/pincode-level/delhi/110068.geojson','static/assets/data/pincode-level/delhi/110069.geojson','static/assets/data/pincode-level/delhi/110070.geojson','static/assets/data/pincode-level/delhi/110071.geojson',
        'static/assets/data/pincode-level/delhi/110072.geojson','static/assets/data/pincode-level/delhi/110073.geojson','static/assets/data/pincode-level/delhi/110074.geojson','static/assets/data/pincode-level/delhi/110075.geojson',
        'static/assets/data/pincode-level/delhi/110076.geojson','static/assets/data/pincode-level/delhi/110077.geojson','static/assets/data/pincode-level/delhi/110078.geojson',
        'static/assets/data/pincode-level/delhi/110080.geojson','static/assets/data/pincode-level/delhi/110081.geojson','static/assets/data/pincode-level/delhi/110082.geojson', 'static/assets/data/pincode-level/delhi/110083.geojson',
        'static/assets/data/pincode-level/delhi/110084.geojson','static/assets/data/pincode-level/delhi/110085.geojson','static/assets/data/pincode-level/delhi/110086.geojson','static/assets/data/pincode-level/delhi/110087.geojson',
        'static/assets/data/pincode-level/delhi/110088.geojson','static/assets/data/pincode-level/delhi/110089.geojson','static/assets/data/pincode-level/delhi/110090.geojson','static/assets/data/pincode-level/delhi/110091.geojson',
        'static/assets/data/pincode-level/delhi/110092.geojson','static/assets/data/pincode-level/delhi/110093.geojson','static/assets/data/pincode-level/delhi/110094.geojson','static/assets/data/pincode-level/delhi/110095.geojson',
        'static/assets/data/pincode-level/delhi/110096.geojson','static/assets/data/pincode-level/delhi/110097.geojson','static/assets/data/pincode-level/delhi/110098.geojson','static/assets/data/pincode-level/delhi/110099.geojson',
        'static/assets/data/pincode-level/delhi/110100.geojson'
    ]
}