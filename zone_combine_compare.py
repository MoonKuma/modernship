#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : zone_combine_compare.py
# @Author: MoonKuma
# @Date  : 2019/3/21
# @Desc  : zone combine compare

target_dict = dict()
target_dict['12,13']='2017-12-14'
target_dict['11,14']='2018-03-23'
target_dict['9,10']='2018-03-23'
target_dict['3,4']='2018-05-11'
target_dict['15,16']='2018-05-11'
target_dict['17,18']='2018-05-11'
target_dict['19,20']='2018-06-08'
target_dict['21,22']='2018-06-08'
target_dict['23,24']='2018-06-08'


target_dict_2 = dict()
target_dict_2['1,2']='2018-01-04'
target_dict_2['3,4']='2018-01-11'
target_dict_2['5,6']='2018-01-11'
target_dict_2['7,8']='2018-01-17'
target_dict_2['9,10']='2018-01-17'
target_dict_2['11,12']='2018-01-18'
target_dict_2['13,14']='2018-01-18'
target_dict_2['15,16']='2018-01-22'
target_dict_2['17,18']='2018-01-22'
target_dict_2['19,20']='2018-02-28'
target_dict_2['21,22']='2018-02-28'
target_dict_2['23,24']='2018-02-28'
target_dict_2['25,26']='2018-03-01'
target_dict_2['27,28']='2018-03-01'
target_dict_2['29,30']='2018-03-01'
target_dict_2['31,32']='2018-03-05'
target_dict_2['33,34']='2018-03-05'
target_dict_2['35,36']='2018-03-05'
target_dict_2['37,38']='2018-03-07'
target_dict_2['39,40']='2018-03-07'
target_dict_2['41,42']='2019-03-08'
target_dict_2['43,44']='2019-03-08'
target_dict_2['45,46']='2019-03-08'






sql_str_tmp = 'select zone_mark, sum(case when day_diff<0 then money else 0 end)/sum(case when day_diff<0 then 1 else 0 end)' \
          ' as money_before, sum(case when day_diff<0 then active else 0 end)/sum(case when day_diff<0 then 1 else 0 end)' \
          ' as active_before, sum(case when day_diff<0 then newUsers else 0 end)/sum(case when day_diff<0 then 1' \
          ' else 0 end) as newUsers_before, sum(case when day_diff<0 then payUsers else 0 end)/sum(case when ' \
          'day_diff<0 then 1 else 0 end) as payUsers_before,  sum(case when day_diff>0 then money else 0 end)' \
          '/sum(case when day_diff>0 then 1 else 0 end) as money_after, sum(case when day_diff>0 then active' \
          ' else 0 end)/sum(case when day_diff>0 then 1 else 0 end) as active_after, sum(case when day_diff>0 ' \
          'then newUsers else 0 end)/sum(case when day_diff>0 then 1 else 0 end) as newUsers_after, sum(case ' \
          'when day_diff>0 then payUsers else 0 end)/sum(case when day_diff>0 then 1 else 0 end) as payUsers_after ' \
          ' from ( select "%zone_combine%" as zone_mark, date, datediff(date, \'%target_date%\') as day_diff, ' \
          'sum(money/100) as money, sum(activeUsers) as active, sum(newUsers) as newUsers, sum(payUsers) as payUsers' \
          ' from day_summary where zoneid in (%zone_combine%) group by date having day_diff<14 and day_diff>-14 )a'



sql_all = list()
for key in target_dict_2.keys():
    sql = sql_str_tmp.replace('%zone_combine%', key).replace('%target_date%',target_dict_2[key])
    sql_all.append(sql)

sql_in_use = 'select * from (' + ' union all '.join(sql_all) + ')sql_full'