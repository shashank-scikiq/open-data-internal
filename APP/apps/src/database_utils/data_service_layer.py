class DataService:
    def __init__(self, data_access_layer):
        self.dal = data_access_layer

    def get_top_states_orders(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                              state=None):
        return self.dal.fetch_top_states_orders(start_date, end_date, category, sub_category, domain_name, state)
    
    def get_states_orders(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None):
        return self.dal.fetch_states_orders(start_date, end_date, category, sub_category, domain_name, state)

    def get_cumulative_orders(self, start_date, end_date, category=None, sub_category=None,
                              domain_name=None, state=None):
        return self.dal.fetch_cumulative_orders(start_date, end_date, category, sub_category, domain_name, state)


    def get_retail_overall_orders(self, start_date, end_date, category=None, sub_category=None,
                              domain_name=None, state=None):
        return self.dal.fetch_retail_overall_orders(start_date, end_date, category, sub_category, domain_name, state)

    def get_retail_overall_top_states_orders(self, start_date, end_date, category=None, sub_category=None,
                              domain_name=None, state=None):
        return self.dal.fetch_retail_overall_top_states_orders(start_date, end_date, category, sub_category, domain_name, state)



    def get_cumulative_orders_rv(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                 state=None):
        return self.dal.fetch_cumulative_orders_rv(start_date, end_date, category, sub_category, domain_name, state)

    def get_cummulative_sellers(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                state=None):
        return self.dal.fetch_cummulative_sellers(start_date, end_date, category, sub_category, domain_name, state)


    def get_overall_cumulative_sellers(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                state=None):
        return self.dal.fetch_overall_cumulative_sellers(start_date, end_date, category, sub_category, domain_name, state)


    def get_top_district_orders(self, start_date, end_date, category=None, sub_category=None,
                                domain_name=None, state=None):
        return self.dal.fetch_top_district_orders(start_date, end_date, category, sub_category, domain_name, state)

    def get_overall_top_district_orders(self, start_date, end_date, category=None, sub_category=None,
                                domain_name=None, state=None):
        return self.dal.fetch_overall_top_district_orders(start_date, end_date, category, sub_category, domain_name, state)


    def get_overall_top_states_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                         domain_name=None, state=None):
        return self.dal.fetch_overall_top_states_hyperlocal_orders(start_date, end_date, category, sub_category,
                                                           domain_name, state)

    def get_overall_top_district_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                           domain_name=None, state=None):
        return self.dal.fetch_overall_top_district_hyperlocal_orders(start_date, end_date, category, sub_category,
                                                             domain_name, state)


    def get_overall_zonal_commerce_top_states(self, start_date, end_date, category=None, sub_category=None,
                                           domain_name=None, state=None):
        return self.dal.fetch_overall_top5_seller_states(start_date, end_date, category, sub_category,
                                                             domain_name, state)


    def get_top_states_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                         domain_name=None, state=None):
        return self.dal.fetch_top_states_hyperlocal_orders(start_date, end_date, category, sub_category,
                                                           domain_name, state)

    def get_top_district_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                           domain_name=None, state=None):
        return self.dal.fetch_top_district_hyperlocal_orders(start_date, end_date, category, sub_category,
                                                             domain_name, state)

    def get_zonal_commerce_top_states(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                      state=None):
        return self.dal.fetch_top5_seller_states(start_date, end_date, category, sub_category, domain_name, state)

    def get_zonal_commerce_top_districts(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                         state=None, district=None):
        return self.dal.fetch_top5_seller_districts(start_date, end_date, category, sub_category, domain_name,
                                                    state, district)

    def get_overall_zonal_commerce_top_districts(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                         state=None, district=None):
        return self.dal.fetch_overall_top5_seller_districts(start_date, end_date, category, sub_category, domain_name,
                                                    state, district)

    def get_category_penetration_orders(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                        state=None):
        return self.dal.fetch_category_penetration_orders(start_date, end_date, category, sub_category, domain_name,
                                                          state)

    def get_category_penetration_sellers(self, start_date, end_date, category=None, sub_category=None,
                                         domain_name=None, state=None):
        return self.dal.fetch_category_penetration_sellers(start_date, end_date, category, sub_category,
                                                           domain_name, state)

    def get_cumulative_orders_statewise(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                        state=None):
        return self.dal.fetch_cumulative_orders_statewise(start_date, end_date, category, sub_category, domain_name,
                                                          state)

    def get_cumulative_orders_statewise_b2b(self, start_date, end_date, category=None, sub_category=None,
                                            domain_name=None, state=None):
        return self.dal.fetch_cumulative_orders_statewise_b2b(start_date, end_date, category, sub_category,
                                                              domain_name, state)

    def get_cumulative_orders_statewise_logistics(self, start_date, end_date, category=None, sub_category=None,
                                            domain_name=None, state=None):
        return self.dal.fetch_cumulative_orders_statewise_logistics(start_date, end_date, category, sub_category,
                                                              domain_name, state)

    def get_total_orders(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None):
        return self.dal.fetch_total_orders(start_date, end_date, category, sub_category, domain_name)

    def get_total_orders_summary(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None):
        return self.dal.fetch_total_orders_summary(start_date, end_date, category, sub_category, domain_name)

    def get_district_count_summary(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None):
        return self.dal.fetch_district_count_summary(start_date, end_date, category, sub_category, domain_name, state)

    def get_most_orders_delivered_to_summary(self, start_date, end_date, category=None, sub_category=None,
                                         domain_name=None, state=None):
        return self.dal.fetch_most_orders_delivered_to_summary(start_date, end_date, category, sub_category,
                                                           domain_name, state)

    def get_cumulative_orders_statedata_summary(self, start_date, end_date, category=None, sub_category=None,
                                            domain_name=None, state=None):
        return self.dal.fetch_cumulative_orders_statedata_summary(start_date, end_date, category, sub_category,
                                                              domain_name, state)

    def get_cumulative_orders_statewise_summary(self, start_date, end_date, category=None, sub_category=None,
                                            domain_name=None, state=None):
        return self.dal.fetch_cumulative_orders_statewise_summary(start_date, end_date, category, sub_category,
                                                              domain_name, state)

    def get_total_orders_prev(self, start_date, end_date, category=None, sub_category=None,
                              domain_name=None, state=None):
        return self.dal.fetch_total_orders_prev(start_date, end_date, category, sub_category, domain_name, state)


    def get_total_orders_summary_prev(self, start_date, end_date, category=None, sub_category=None,
                              domain_name=None, state=None):
        return self.dal.fetch_total_orders_summary_prev(start_date, end_date, category, sub_category, domain_name, state)

    def get_total_orders_rv(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None):
        return self.dal.fetch_total_orders_rv(start_date, end_date, category, sub_category, domain_name, state)

    def get_total_orders_b2b(self, start_date, end_date, category=None, sub_category=None,
                             domain_name=None, state=None):
        return self.dal.fetch_total_orders_b2b(start_date, end_date, category, sub_category, domain_name, state)

    def get_total_orders_logistics(self, start_date, end_date, category=None, sub_category=None,
                             domain_name=None, state=None):
        return self.dal.fetch_total_orders_logistics(start_date, end_date, category, sub_category, domain_name, state)


    def get_most_orders_delivered_to(self, start_date, end_date, category=None, sub_category=None,
                                     domain_name=None, state=None):
        return self.dal.fetch_most_orders_delivered_to(start_date, end_date, category, sub_category, domain_name, state)

    def get_most_orders_delivered_to_b2b(self, start_date, end_date, category=None, sub_category=None,
                                         domain_name=None, state=None):
        return self.dal.fetch_most_orders_delivered_to_b2b(start_date, end_date, category, sub_category,
                                                           domain_name, state)

    def get_most_orders_delivered_to_logistics(self, start_date, end_date, category=None, sub_category=None,
                                         domain_name=None, state=None):
        return self.dal.fetch_most_orders_delivered_to_logistics(start_date, end_date, category, sub_category,
                                                           domain_name, state)

    def get_cumulative_orders_statedata(self, start_date, end_date, category=None, sub_category=None,
                                        domain_name=None, state=None):
        return self.dal.fetch_cumulative_orders_statedata(start_date, end_date, category, sub_category,
                                                          domain_name, state)

    def get_cumulative_orders_statedata_b2b(self, start_date, end_date, category=None, sub_category=None,
                                            domain_name=None, state=None):
        return self.dal.fetch_cumulative_orders_statedata_b2b(start_date, end_date, category, sub_category,
                                                              domain_name, state)

    def get_cumulative_orders_statedata_logistics(self, start_date, end_date, category=None, sub_category=None,
                                            domain_name=None, state=None):
        return self.dal.fetch_cumulative_orders_statedata_logistics(start_date, end_date, category, sub_category,
                                                              domain_name, state)

    def get_comprehensive_data(self, start_date, end_date, category=None, sub_category=None,
                               domain_name=None, state=None):
        return self.dal.fetch_comprehensive_data(start_date, end_date, category, sub_category, domain_name, state)

    def get_max_subcategory_overall(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                    state=None):
        return self.dal.fetch_max_subcategory_overall(start_date, end_date, category, sub_category, domain_name, state)

    def get_active_sellers(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None):
        return self.dal.fetch_active_sellers(start_date, end_date, category, sub_category, domain_name, state)

    def get_overall_active_sellers(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None):
        return self.dal.fetch_overall_active_sellers(start_date, end_date, category, sub_category, domain_name, state)


    def get_active_sellers_b2b(self, start_date, end_date, category=None, sub_category=None,
                               domain_name=None, state=None):
        return self.dal.fetch_active_sellers_b2b(start_date, end_date, category, sub_category, domain_name, state)

    def get_total_sellers(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None):
        return self.dal.fetch_total_sellers(start_date, end_date, category, sub_category, domain_name, state)

    def get_total_sellers_b2b(self, start_date, end_date, category=None, sub_category=None,
                              domain_name=None, state=None):
        return self.dal.fetch_total_sellers_b2b(start_date, end_date, category, sub_category, domain_name, state)

    def get_max_sub_category(self, start_date, end_date, category=None, sub_category=None,
                             domain_name=None, state=None):
        return self.dal.fetch_max_sub_category(start_date, end_date, category, sub_category, domain_name, state)

    def get_active_sellers_statedata(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                     state=None):
        return self.dal.fetch_active_sellers_statedata(start_date, end_date, category, sub_category, domain_name, state)

    def get_overall_active_sellers_statedata(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                     state=None):
        return self.dal.fetch_overall_active_sellers_statedata(start_date, end_date, category, sub_category, domain_name, state)


    def get_active_sellers_statedata_b2b(self, start_date, end_date, category=None, sub_category=None,
                                         domain_name=None, state=None):
        return self.dal.fetch_active_sellers_statedata_b2b(start_date, end_date, category, sub_category,
                                                           domain_name, state)

    def get_max_orders_district_state(self, start_date, end_date, category=None, sub_category=None,
                                      domain_name=None, state=None):
        return self.dal.fetch_max_orders_district_and_state(start_date, end_date, category, sub_category,
                                                            domain_name, state)

    def get_max_state_orders(self, start_date, end_date, category=None, sub_category=None,
                             domain_name=None, state=None):
        return self.dal.fetch_max_state_orders(start_date, end_date, category, sub_category, domain_name, state)

    def get_max_district_orders(self, start_date, end_date, category=None, sub_category=None,
                                domain_name=None, state=None):
        return self.dal.fetch_max_district_orders(start_date, end_date, category, sub_category, domain_name, state)

    def get_max_subcategory(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None):
        return self.dal.fetch_max_subcategory(start_date, end_date, category, sub_category, domain_name, state)

    def get_district_count(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None):
        return self.dal.fetch_district_count(start_date, end_date, category, sub_category, domain_name, state)

    def get_district_count_b2b(self, start_date, end_date, category=None, sub_category=None,
                               domain_name=None, state=None):
        return self.dal.fetch_district_count_b2b(start_date, end_date, category, sub_category, domain_name, state)

    def get_district_count_logistics(self, start_date, end_date, category=None, sub_category=None,
                               domain_name=None, state=None):
        return self.dal.fetch_district_count_logistics(start_date, end_date, category, sub_category, domain_name, state)

    def get_total_district_count(self, start_date, end_date, category=None, sub_category=None,
                                 domain_name=None, state=None):
        return self.dal.fetch_total_district_count(start_date, end_date, category, sub_category, domain_name, state)

    def get_total_district_count1(self, start_date, end_date, category=None, sub_category=None,
                                  domain_name=None, state=None):
        return self.dal.fetch_total_district_count(start_date, end_date, category, sub_category, domain_name, state)

    def get_cummulative_confirmed_orders_statewise(self, start_date, end_date, category=None, sub_category=None,
                                                   domain_name=None, state=None):
        return self.dal.fetch_cummulative_confirmed_orders_statewise(start_date, end_date, category, sub_category,
                                                                     domain_name, state)

    def get_max_district_per_state(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                   state=None):
        return self.dal.fetch_max_district_per_state(start_date, end_date, category, sub_category, domain_name, state)


