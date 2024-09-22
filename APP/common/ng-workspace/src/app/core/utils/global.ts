export const AppApiMap: any = {
  '/retail': 'retail/overall',
  '/retail/b2b': 'retail/b2b',
  '/retail/b2c': 'retail/b2c',
  '/logistics': 'logistics/overall',
  '/logistics/detail': 'logistics/detail',
  '/logistics/search': 'logistics/search'
}

export type MetrixType =
'map_total_orders_metrics' |
'map_total_active_sellers_metrics' |
'map_total_zonal_commerce_metrics'
;

export const METRICS: MetrixType[] = [
    'map_total_orders_metrics',
    'map_total_active_sellers_metrics',
    'map_total_zonal_commerce_metrics'
]

const MetricKeyMap: any = {
    "sellers": [
      { "key": "Registered Sellers", "id": "map_total_active_sellers_metrics" }
    ],
    "orders": [
      { "key": "Total Orders ", "id": "map_total_orders_metrics" },
    ],
    "pincode": [
      { "key": "Intrastate Percentage", "id": "map_total_zonal_commerce_metrics" }
    ],
  }

export const getMetrixKey = (kid: string): string | undefined => {
    const metricMap = MetricKeyMap; // Avoid redundant lookups

    for (const category in metricMap) {
      const lst = metricMap[category];
      for (const item of lst) {
        if (item.id === kid) {
          return item.key;
        }
      }
    }

    return undefined; // Key not found
  }

  export const formatNumber = (num: number) => {
    var num_parts = num.toString().split(".");
    num_parts[0] = num_parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return num_parts.join(".");
  }