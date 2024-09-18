query_selector= """


            select ls."Date" , ls.pick_up_pincode , ls.time_of_day ,
            sum(ls.searched) as searched, sum(ls.confirmed) as confirmed , sum(ls.assigned) as assigned 
            from ec2_all.logistic_search ls 
            where ls.time_of_day = 'evening'
            group by 1,2,3
            order by 1,2;




"""