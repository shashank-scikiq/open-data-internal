__author__ = "Shashank Katyayan"

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Metric(ABC):
    @abstractmethod
    def run(self, start_date, end_date, **kwargs):
        pass

    @abstractmethod
    def top_card_delta(self, start_date, end_date, **kwargs):
        pass

    @abstractmethod
    def map_state_data(self, start_date, end_date, **kwargs):
        pass

    @abstractmethod
    def map_statewise_data(self, start_date, end_date, **kwargs):
        pass

    @abstractmethod
    def top_cumulative_chart(self, start_date, end_date, **kwargs):
        pass

    @abstractmethod
    def top_states_chart(self, start_date, end_date, **kwargs):
        pass

    @abstractmethod
    def top_district_chart(self, start_date, end_date, **kwargs):
        pass

    @abstractmethod
    def state_tree_chart(self, start_date, end_date, **kwargs):
        pass

    @abstractmethod
    def district_tree_chart(self, start_date, end_date, **kwargs):
        pass


# Specific Metric Classes

# # Domain Class
# class Domain:
#     def __init__(self, name, metrics):
#         self.name = name
#         self.metrics = metrics

    # async def run_metrics(self, start_date, end_date, **kwargs):
    #     logger.info(f"Running metrics for {self.name}")
    #     try:
    #         await asyncio.gather(*(metric.run(start_date, end_date, **kwargs) for metric in self.metrics))
    #         logger.info(f"Completed running metrics for {self.name}")
    #     except Exception as e:
    #         logger.error(f"Error running metrics for {self.name}: {e}")

# # Create instances of specific metrics
# order_metric = OrderMetric()
# seller_metric = SellerMetric()
# zonal_commerce_metric = ZonalCommerceMetric()

# # # Define domains with different metrics
# domains = {
#     "Domain 1": Domain("Domain 1", [order_metric, seller_metric]),
#     "Domain 2": Domain("Domain 2", [order_metric, zonal_commerce_metric]),
#     "Domain 3": Domain("Domain 3", [seller_metric]),
#     "Domain 4": Domain("Domain 4", [order_metric, seller_metric, zonal_commerce_metric])
# }

# Function to run metrics for a specific domain based on filter
# async def run_metrics_for_domain(domain_name, start_date, end_date, **kwargs):
#     domain = domains.get(domain_name)
#     if domain:
#         await domain.run_metrics(start_date, end_date, **kwargs)
#     else:
#         logger.error(f"Domain {domain_name} not found")
#
# # Example of triggering metrics based on API calls
# async def example_usage():
#     start_date = '2023-01-01'
#     end_date = '2023-12-31'
#     domain_to_run = "Domain 2"  # Example domain filter
#     await run_metrics_for_domain(domain_to_run, start_date, end_date)
#
# # Run the example usage
# if __name__ == "__main__":
#     asyncio.run(example_usage())
#
