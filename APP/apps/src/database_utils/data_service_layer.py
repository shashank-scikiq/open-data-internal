class DataService:
    def __init__(self, data_access_layer):
        self.dal = data_access_layer

    ''' Total - Top Orders Chart'''
    def get_retail_overall_orders(self, start_date, end_date, category=None, sub_category=None,
                              domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_retail_overall_orders(start_date, end_date, category, sub_category, domain_name, state)

    '''FetchTopStatesOrders'''
    def get_retail_overall_top_states_orders(self, start_date, end_date, category=None, sub_category=None,
                              domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_retail_overall_top_states_orders(start_date, end_date, category, sub_category, domain_name, state)

    '''FetchCumulativeSellers'''
    def get_overall_cumulative_sellers(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                state=None, seller_type='Total'):
        return self.dal.fetch_overall_cumulative_sellers(start_date, end_date, category, sub_category, domain_name, state, seller_type)

    def get_top_district_sellers(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                state=None, seller_type='Total'):
        return self.dal.fetch_top_district_sellers(start_date, end_date, category, sub_category, domain_name, state,seller_type)

    def get_top_state_sellers(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                state=None, seller_type='Total'):
        return self.dal.fetch_top_state_sellers(start_date, end_date, category, sub_category, domain_name, state, seller_type)

    '''FetchTopDistrictOrders'''
    def get_overall_top_district_orders(self, start_date, end_date, category=None, sub_category=None,
                                domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_overall_top_district_orders(start_date, end_date, category, sub_category, domain_name, state)

    '''FetchTopStatesHyperlocal'''
    def get_overall_top_states_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                         domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_overall_top_states_hyperlocal_orders(start_date, end_date, category, sub_category,
                                                           domain_name, state)
    '''FetchTopDistrictHyperlocal'''
    def get_overall_top_district_hyperlocal_orders(self, start_date, end_date, category=None, sub_category=None,
                                           domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_overall_top_district_hyperlocal_orders(start_date, end_date, category, sub_category,
                                                             domain_name, state)

    '''FetchTop5SellerStates - tree chart states'''
    def get_overall_zonal_commerce_top_states(self, start_date, end_date, category=None, sub_category=None,
                                           domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_overall_top5_seller_states(start_date, end_date, category, sub_category,
                                                             domain_name, state)

    '''FetchTop5SellersDistrict - tree chart district'''
    def get_overall_zonal_commerce_top_districts(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
                                         state=None, district=None, seller_type='Total'):
        return self.dal.fetch_overall_top5_seller_districts(start_date, end_date, category, sub_category, domain_name,
                                                    state, district)
    '''FetchTopCardDeltaData - current orders'''
    def get_total_orders_summary(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_total_orders_summary(start_date, end_date, category, sub_category, domain_name)

    '''FetchMapStateData - orders'''
    def get_cumulative_orders_statedata_summary(self, start_date, end_date, category=None, sub_category=None,
                                            domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_cumulative_orders_statedata_summary(start_date, end_date, category, sub_category,
                                                              domain_name, state)
    '''FetchMapStateWiseData - orders'''
    def get_cumulative_orders_statewise_summary(self, start_date, end_date, category=None, sub_category=None,
                                            domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_cumulative_orders_statewise_summary(start_date, end_date, category, sub_category,
                                                              domain_name, state)

    '''FetchTopCardDeltaData - previous orders'''
    def get_total_orders_summary_prev(self, start_date, end_date, category=None, sub_category=None,
                              domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_total_orders_summary_prev(start_date, end_date, category, sub_category, domain_name, state)

    '''FetchMapStateWiseData - active sellers'''
    def get_overall_active_sellers(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_overall_active_sellers(start_date, end_date, category, sub_category, domain_name, state)

    # '''FetchMapStateData - sellers'''
    # def get_overall_active_sellers_statedata(self, start_date, end_date, category=None, sub_category=None, domain_name=None,
    #                                  state=None, seller_type='Total'):
    #     return self.dal.fetch_overall_active_sellers_statedata(start_date, end_date, category, sub_category, domain_name, state)

    '''FetchTopCardDeltaData - district count'''
    def get_district_count(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_district_count(start_date, end_date, category, sub_category, domain_name, state)


    '''Sunburst-chart for b2c'''
    def get_category_penetration_orders(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_category_penetration_orders(start_date, end_date, category, sub_category, domain_name, state)
    
    def get_category_penetration_sellers(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_category_penetration_sellers(start_date, end_date, category, sub_category, domain_name, state, seller_type)

    def get_states_orders(self, start_date, end_date, category=None, sub_category=None, domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_states_orders(start_date, end_date, category, sub_category, domain_name, state)
    
    def get_max_state_orders(self, start_date, end_date, category=None, sub_category=None,
                             domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_max_state_orders(start_date, end_date, category, sub_category, domain_name, state)
    
    def get_max_district_orders(self, start_date, end_date, category=None, sub_category=None,
                             domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_max_district_orders(start_date, end_date, category, sub_category, domain_name, state)
    
    def get_max_state_sellers(self, start_date, end_date, category=None, sub_category=None,
                             domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_max_state_sellers(start_date, end_date, category, sub_category, domain_name, state)
    
    def get_max_district_sellers(self, start_date, end_date, category=None, sub_category=None,
                             domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_max_district_sellers(start_date, end_date, category, sub_category, domain_name, state)
    
    def get_state_sellers(self, start_date, end_date, category=None, sub_category=None,
                             domain_name=None, state=None, seller_type='Total'):
        return self.dal.fetch_state_sellers(start_date, end_date, category, sub_category, domain_name, state)


    def get_logistic_searched_data(self, start_date, end_date, city):
        return self.dal.fetch_logistic_searched_data(start_date, end_date, city)

    def get_logistic_searched_top_card_data(self, start_date, end_date, city):
        return self.dal.fetch_logistic_searched_top_card_data(start_date, end_date, city)
    
    def get_logistic_searched_data_date_range(self):
        return self.dal.fetch_logistic_searched_data_date_range()