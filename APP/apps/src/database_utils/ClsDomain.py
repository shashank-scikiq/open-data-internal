__author__ = "Shashank Katyayan"

import logging
from abc import ABC, abstractmethod
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

domain_metrics_mapping = {
    "Retail_Overall": ['order', 'seller', 'zonal_commerce'],
    "Logistics_Overall": ['order', 'seller', 'zonal_commerce']
}


class Domain:
    def __init__(self, name, metrics):
        self.name = name
        self.metrics = metrics

    def run_metric_function(self, metric_name, function_name, start_date, end_date, **kwargs):
        for metric in self.metrics:
            if metric.__class__.__name__.lower() == metric_name.lower():
                func = getattr(metric, function_name, None)
                if func:
                    res = func(start_date, end_date, **kwargs)
                    return res
                else:
                    logger.error(f"Function {function_name} not found in metric {metric_name}")
                    return
        logger.error(f"Metric {metric_name} not found in domain {self.name}")

    # def run_specific_metric(self, domain_name, metric_name, function_name, start_date, end_date, **kwargs):
    #     metrics = domain_metrics_mapping.get(domain_name)
    #     if not metrics:
    #         logger.error(f"Domain {domain_name} not found")
    #         return
    #
    #     if metric_name not in metrics:
    #     # metric_functions = metrics.get(metric_name)
    #     # if not metric_functions:
    #         logger.error(f"Metric {metric_name} not found for domain {domain_name}")
    #         return
    #
    #     # Find the correct function based on case-insensitive comparison
    #     func = None
    #     for func_name, function in metric_functions.items():
    #         if func_name.lower() == function_name.lower():
    #             func = function
    #             break
    #
    #     if not func:
    #         logger.error(f"Function {function_name} not found for metric {metric_name} in domain {domain_name}")
    #         return
    #
    #     func(start_date, end_date, **kwargs)

    # @classmethod
    # def run_specific_metric(cls, domain_name, metric_name, function_name, start_date, end_date, **kwargs):
    #     domain = domains.get(domain_name)
    #     if not domain:
    #         logger.error(f"Domain {domain_name} not found")
    #         return
    #
    #     domain.run_metric_function(metric_name, function_name, start_date, end_date, **kwargs)



# domains = {
#                 "Retail_Overall": Domain("Retail_Overall"),
#                 "Logistics_Overall": Domain("Logistics_Overall")
#             }
