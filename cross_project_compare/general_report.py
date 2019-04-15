#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : general_report.py
# @Author: MoonKuma
# @Date  : 2019/2/15
# @Desc  : general report across time
"""
select date,sum(activeUsers),sum(newUsers),sum(payUsers)/sum(activeUsers),sum(money),
ceil(sum(online_time)/(60*sum(activeUsers))) from
day_summary where date between '2019-02-11' and '2019-02-14' group by date;
"""


from conf.ConfParameters import ConfParameters
from util.EasyMysql import EasyMysql
from util.DateList import DateList


def general_report(input_dict):
    conf = ConfParameters()
    easy_sql = EasyMysql()
    easy_date = DateList()
    mysql_conf = conf.mysql_conf
    stat_base = mysql_conf['stat_base']

    # argv
    x_list = list()

    y_list = ['DAU', 'NewUsers', 'PayRate', 'Money', 'OnlineTime']

    # input dict
    date_list = sorted(list(input_dict['date_list']))
    where_channel_zone = easy_sql.combine_where_clause(input_dict)
    cursor = input_dict['cursor']
    where_date_between = ' date between \'' + date_list[0] + '\' and \'' + date_list[len(date_list)-1] + '\' ' + where_channel_zone
    sql = 'select date,sum(activeUsers),sum(newUsers),sum(payUsers)/sum(activeUsers),ceil(sum(money)/100),ceil(sum(online_time)/(60*sum(activeUsers))) from day_summary where '+where_date_between+' group by date;'
    print(sql)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    result_dict = dict()
    for y in y_list:
        result_dict[y] = dict()
    if all_data:
        for rec in all_data:
            date = str(rec[0])
            DAU = int(rec[1])
            NewUsers = int(rec[2])
            PayRate = float(rec[3])
            Money = int(rec[4])
            OnlineTime = int(rec[5])
            tmp = [DAU, NewUsers, PayRate, Money, OnlineTime]
            for i in range(0, len(tmp)):
                result_dict[y_list[i]][date] = result_dict[y_list[i]].setdefault(date,0) + tmp[i]
    print('[Check1]len(result_dict):', len(result_dict.keys()))
    x_list = date_list
    res_dict = dict()
    res_dict['data_dict'] = result_dict
    res_dict['X_list'] = x_list
    res_dict['Y_list'] = y_list
    res_dict['default_value'] = ''
    res_dict['head_name'] = '概览'
    res_dict['note'] = ''

    # print(res_dict)
    return res_dict

