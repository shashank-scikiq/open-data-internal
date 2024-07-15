import './topojson/topojson-client.js'

const state_code = { "Total": "TT", "Maharashtra": "MH", "Tamil Nadu": "TN", "Andhra Pradesh": "AP", "Karnataka": "KA", "Delhi": "DL", "Uttar Pradesh": "UP", "West Bengal": "WB", "Bihar": "BR", "Telangana": "TG", "Gujarat": "GJ", "Assam": "AS", "Rajasthan": "RJ", "Odisha": "OR", "Haryana": "HR", "Madhya Pradesh": "MP", "Kerala": "KL", "Punjab": "PB", "Jammu and Kashmir": "JK", "Jharkhand": "JH", "Chhattisgarh": "CT", "Uttarakhand": "UT", "Goa": "GA", "Tripura": "TR", "Puducherry": "PY", "Manipur": "MN", "Himachal Pradesh": "HP", "Nagaland": "NL", "Arunachal Pradesh": "AR", "Andaman and Nicobar Islands": "AN", "Ladakh": "LA", "Chandigarh": "CH", "Dadra and Nagar Haveli and Daman and Diu": "DN", "Meghalaya": "ML", "Sikkim": "SK", "Mizoram": "MZ", "State Unassigned": "UN", "Lakshadweep": "LD" }

function normalizeString(str) {
    return str.toUpperCase().trim().replace(/\s+/g, '').replace(/[.,'’]/g, '');
}


export async function indiamapdataprocessed(map_state_data) {

    const indiamapdatares = await fetch('/static/map_lib/mapdata/india.json')
    const indiamapdata = await indiamapdatares.json();

    const statecasedata = map_state_data
    indiamapdata.objects.states.geometries.forEach(el => {
        el.properties.st_code = + el.properties.st_code
        let statecode = state_code[el.id];
        
        if (statecasedata[statecode]) {
            let state_case_data = statecasedata[statecode]
            
            let order_demand = state_case_data.total.order_demand ? state_case_data.total.order_demand : 0
            let active_sellers = state_case_data.total.active_sellers ? state_case_data.total.active_sellers : 0
            let total_intrastate_orders_percentage = state_case_data.total.intrastate_percentage 
                ? state_case_data.total.intrastate_percentage : 0;
            
            if (active_sellers <= 3){
                active_sellers = 0
                }
            el.properties['totalcasedata'] = {
                map_order_demand: order_demand,
                map_total_orders_metrics: order_demand,
                map_total_active_sellers_metrics: active_sellers,
                map_total_zonal_commerce_metrics: total_intrastate_orders_percentage,
            }
        }
        else {
            el.properties['totalcasedata'] = nocasedata
        }
    })

    indiamapdata.objects.districts.geometries.forEach(el => {
        el.properties.dt_code = + el.properties.dt_code
        el.properties.st_code = + el.properties.st_code

        let districtname = el.properties.district
        districtname = districtname.toUpperCase(); 
        let statename = el.properties.st_nm
        let statecode = state_code[statename];
        
        if (statecasedata[statecode]) {

            let state_case_data = statecasedata[statecode]
            let district_data = state_case_data.districts

            let order_demand = state_case_data.total.order_demand ? state_case_data.total.order_demand : 0
            let active_sellers = state_case_data.total.active_sellers ? state_case_data.total.active_sellers : 0
            let total_intradistrict_orders_percentage = state_case_data.total.intradistrict_orders_percentage ? state_case_data.total.intradistrict_orders_percentage : 0;

            const state_inside_district_obj= {
                map_order_demand: order_demand,
                map_total_orders_metrics: order_demand,
                map_total_active_sellers_metrics: active_sellers,
                map_total_zonal_commerce_metrics: total_intradistrict_orders_percentage,
            }

            let matchFound = false;
            let each_district_data;
            if (district_data[districtname]) {
                each_district_data = district_data[districtname];
                matchFound = true;
            }

            if (matchFound && each_district_data) {
                let order_demand = each_district_data.order_demand ? each_district_data.order_demand : 0;
                let total_intradistrict_orders_percentage = each_district_data.intradistrict_percentage ? each_district_data.intradistrict_percentage : 0;
                let active_sellers = each_district_data.active_sellers ? each_district_data.active_sellers : 0;
        
                el.properties['totalcasedata'] = {
                    map_order_demand: order_demand,
                    map_total_orders_metrics: order_demand,
                    map_total_active_sellers_metrics: active_sellers,
                    map_total_zonal_commerce_metrics: total_intradistrict_orders_percentage,
                    st_data: state_inside_district_obj
                };
            } else {
                el.properties['totalcasedata'] = nocasedata;
            }
        } else {
            el.properties['totalcasedata'] = nocasedata;
        }
    })
     return indiamapdata
}


