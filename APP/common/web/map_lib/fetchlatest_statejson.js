export const statenametostatecode={
                                    "Total":"TT",
                                    "Maharashtra":"MH",
                                    "Tamil Nadu":"TN",
                                    "Andhra Pradesh":"AP",
                                    "Karnataka":"KA",
                                    "Delhi":"DL",
                                    "Uttar Pradesh":"UP",
                                    "West Bengal":"WB",
                                    "Bihar":"BR",
                                    "Telangana":"TG",
                                    "Gujarat":"GJ",
                                    "Assam":"AS",
                                    "Rajasthan":"RJ",
                                    "Odisha":"OR",
                                    "Haryana":"HR",
                                    "Madhya Pradesh":"MP",
                                    "Kerala":"KL",
                                    "Punjab":"PB",
                                    "Jammu and Kashmir":"JK",
                                    "Jharkhand":"JH",
                                    "Chhattisgarh":"CT",
                                    "Uttarakhand":"UT",
                                    "Goa":"GA",
                                    "Tripura":"TR",
                                    "Puducherry":"PY",
                                    "Manipur":"MN",
                                    "Himachal Pradesh":"HP",
                                    "Nagaland":"NL",
                                    "Arunachal Pradesh":"AR",
                                    "Andaman and Nicobar Islands":"AN",
                                    "Ladakh":"LA",
                                    "Chandigarh":"CH",
                                    "Dadra and Nagar Haveli and Daman and Diu":"DN",
                                    "Meghalaya":"ML",
                                    "Sikkim":"SK",
                                    "Mizoram":"MZ",
                                    "State Unassigned":"UN",
                                    "Lakshadweep":"LD"
                                    }


async function fetchOrderMetricsSummary() {
    try {
        const response = await fetch('/dashboard/api/map_state_data/');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

export async function lateststatefetch() {
    const resjson = await fetchOrderMetricsSummary();
    return resjson

}
export function statetocodename(statename){
    return statenametostatecode[statename]
}

