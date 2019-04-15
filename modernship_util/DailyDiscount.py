#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: mjf
# @Date  : 
# @Desc  :

import util.EasyMysql as EasyMysql
from is_valid_data import is_legal_input
import util.DateList as DateList
import sys

X_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,21,22,23,24,25]
try:
    date1 = sys.argv[1]
    date2 = sys.argv[2]
except:
    [date1, date2] = DateList.DateList().get_last_week()
    msg = 'No date input detected, compute the last week automatically. Computing date between ' + date1 + ' and ' + date2
    print(msg)
Y_list = DateList.DateList().get_date_list(date1, date2)
X_listtrans =  map(lambda x:'VIP'+str(x),X_list)
Y_listtrans =  Y_list
X_first = ['trans']
X_first_trans = ['翻译']
X_list = X_first + X_list
X_listtrans = X_first_trans + X_listtrans
X_trans = dict(zip(X_list, X_listtrans))
Y_trans = dict(zip(Y_list, Y_listtrans))
default_value = ''

def everyday_buy(input_dict,*flag):
    data_dict = dict()
    for y in Y_list:
        data_dict[y] = dict()

    head_name = "第"+str(flag[0])+"档位购买"

    easy_mysql = EasyMysql.EasyMysql()
    is_legal_input(input_dict)
    date_list = input_dict['date_list']
    date_list = sorted(date_list)
    if len(date_list) == 0:
        msg = 'Not date selected, len(date_list)' + str(len(date_list))
        raise RuntimeError(msg)
    zoneid_list = input_dict['zone_list']
    channel_list = input_dict['channel_list']
    cursor = input_dict['cursor']
    sql_where = ' where date in (' + easy_mysql.sql_value_str(date_list) + ') '
    if len(zoneid_list) > 0:
        sql_where = sql_where + ' and zoneid in (' + easy_mysql.sql_value_str(zoneid_list) + ') '
    if len(channel_list) > 0:
        sql_where = sql_where + ' and channel in (' + easy_mysql.sql_value_str(channel_list) + ') '

#select date,viplevel,sum(num) from DailyDiscount where rechargeType=1 group by date,viplevel;
    if len(flag)>0:
        sqlstr = 'select date,viplevel,sum(num) from DailyDiscount '+sql_where+'and rechargeType='+str(flag[0])+' group by date,viplevel;'
        print(sqlstr)
        cursor.execute(sqlstr)
        alldata = cursor.fetchall()
        if alldata:
            for rec in alldata:
                data_dict[str(rec[0])][rec[1]] = rec[2]

    for key in data_dict.keys():
            data_dict[key]['trans'] = Y_trans[key]
    res_dict = {'data_dict': data_dict, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name, 'X_trans': X_trans,
                'default_value': default_value}
    # print(res_dict)
    res_dict['note'] = "每日"+str(flag[0])+"档位消耗"
    return res_dict
