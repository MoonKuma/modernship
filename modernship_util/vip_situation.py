#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: mjf
# @Date  : 
# @Desc  :截止最大日期的VIP等级


import util.EasyMysql as EasyMysql
from is_valid_data import is_legal_input

# argv assignment
vip_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,21,22,23,24,25]
vip_trans = map(lambda x:'VIP'+str(x),vip_list)
level_list = ['UserCount']+[i for i in range(100)]

X_list = vip_list
Y_list = level_list
X_listtrans = vip_trans
Y_listtrans = level_list

default_value = ''
# X_first = []
# X_first_trans = ['翻译']
# X_first_trans = []
# X_list = X_first + X_list
# X_listtrans = X_first_trans + X_listtrans
X_trans = dict(zip(X_list, X_listtrans))
Y_trans = dict(zip(Y_list, Y_listtrans))

def vip_level(input_dict):
    data_dict = dict()
    for y in Y_list:
        data_dict[y] = dict()
    head_name = "VIP等级分布"

    easy_mysql = EasyMysql.EasyMysql()
    is_legal_input(input_dict)
    date_list = [max(input_dict['date_list'])]
    date_list = sorted(date_list)
    if len(date_list) == 0:
        msg = 'Not date selected, len(date_list)' + str(len(date_list))
        raise RuntimeError(msg)
    zoneid_list = input_dict['zone_list']
    channel_list = input_dict['channel_list']
    cursor = input_dict['cursor']
    sql_where = ' where date <=' + easy_mysql.sql_value_str(date_list)
    if len(zoneid_list) > 0:
        sql_where = sql_where + ' and zoneid in (' + easy_mysql.sql_value_str(zoneid_list) + ') '
    if len(channel_list) > 0:
        sql_where = sql_where + ' and channel in (' + easy_mysql.sql_value_str(channel_list) + ') '
    sql_str = 'select mvip,count(uid) from(select uid,max(level) as mlevel,max(vip_level) as mvip from user_active '+sql_where+'  group by uid) as a group by mvip;'
    cursor.execute(sql_str)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            vip = int(rec[0])
            user = int(rec[1])
            data_dict['UserCount'][vip] = user

    sql_str = 'select mlevel,mvip,count(uid) from(select uid,max(level) as mlevel,max(vip_level) as mvip from user_active '+sql_where+'  group by uid) as a group by mlevel,mvip;'
    cursor.execute(sql_str)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            data_dict[int(rec[0])][rec[1]] = rec[2]
    # for key in data_dict.keys():
    #     if X_first[0] not in data_dict.keys():
    #         pass
    #         # data_dict[key]['trans'] = Y_trans[key]
    res_dict={'data_dict':data_dict,'X_list':X_list,'Y_list':Y_list,'head_name':head_name,'X_trans':X_trans,'default_value':default_value}
    # print(res_dict)
    res_dict["note"] = "*从开服-截止终止日期的各VIP段的等级分布*"
    return res_dict
