const months = {
    'January': 0, 'February': 1, 'March': 2, 'April': 3, 'May': 4, 'June': 5, 'July': 6,
    'August': 7, 'September': 8, 'October': 9, 'November': 10, 'December': 11
}




export async function fetchdatajson(map_statewise_data) {

    const resjson = map_statewise_data
    const allstate_list = resjson.statewise;

    const lst_order_demand = new Array();
    const lst_active_sellers = new Array();
    const lst_total_interstate_orders = new Array();
    const lst_total_intrastate_orders = new Array();
    const lst_total_interdistrict_orders = new Array();
    const lst_total_intradistrict_orders = new Array();

    allstate_list.forEach(element => {
        if(element.statecode !='TT'){

            let order_demand = element.order_demand ? element.order_demand : 0
            let active_sellers = element.active_sellers ? element.active_sellers : 0

            let total_interstate_orders = element.total_interstate_orders ? element.total_interstate_orders : 0
            let total_intrastate_orders = element.total_intrastate_orders ? element.total_intrastate_orders : 0
            let total_interdistrict_orders = element.total_interdistrict_orders ? element.total_interdistrict_orders : 0
            let total_intradistrict_orders = element.total_intradistrict_orders ? element.total_intradistrict_orders : 0

            lst_order_demand.push(order_demand);
            lst_active_sellers.push(active_sellers);
            lst_total_interstate_orders.push(total_interstate_orders);
            lst_total_intrastate_orders.push(total_intrastate_orders);
            lst_total_interdistrict_orders.push(total_interdistrict_orders);
            lst_total_intradistrict_orders.push(total_intradistrict_orders);

        }
    });



    return {
        cummulative:{ 
            od: lst_order_demand,
            as: lst_active_sellers,
            tiso: lst_total_interstate_orders ,
            tiso2: lst_total_intrastate_orders ,
            tido: lst_total_interdistrict_orders ,
            tido2: lst_total_intradistrict_orders
        },
        statewise:resjson.statewise

    }


}
