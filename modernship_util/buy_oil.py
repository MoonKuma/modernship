#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: mjf
# @Date  : 
# @Desc  :
# | mvip | count(uid) | sum(ttimes) | sum(tcost) |
# +------+------------+-------------+------------+
# |    0 |       5000 |       11453 |     572650 |
# |    1 |       1812 |        9938 |     496900 |
# |    2 |        429 |        3218 |     192950 |
# |    3 |        360 |        3592 |     239300 |


import util.EasyMysql as EasyMysql
from is_valid_data import is_legal_input

# argv assignment
times_list = ['UserCount']+[i for i in range(1)]

X_first = ['trans']
Y_list = times_list
Y_listtrans = times_list
default_value = ''
Y_trans = dict(zip(Y_list, Y_listtrans))

def buy_oil_people(input_dict):
    global X_list
    X_list = []
    data_dict = dict()
    for y in Y_list:
        data_dict[y] = dict()
    head_name = "VIP等级购买原油人数"

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
    sql_where = ' where date in(' + easy_mysql.sql_value_str(date_list) + ')'
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
            X_list.append(vip)
        X_list=sorted(list(set(X_list)))


    global X_trans
    X_listtrans =['翻译'] + map(lambda x: 'VIP' + str(x), X_list)
    X_list = X_first + X_list
    X_trans = dict(zip(X_list, X_listtrans))



    sql_str = 'select mvip,count(uid),sum(ttimes),sum(tcost) from(select uid,max(viplevel) as mvip,sum(times) as ttimes,sum(cash+diamond) as tcost from OilBuy '+sql_where+'  group by uid) as a group by mvip;'
    cursor.execute(sql_str)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            data_dict[Y_list[1]][rec[0]] = rec[1]
    for key in data_dict.keys():
        if X_first[0] not in data_dict.keys():
            data_dict[key]['trans'] = Y_trans[key]
    res_dict={'data_dict':data_dict,'X_list':X_list,'Y_list':Y_list,'head_name':head_name,'X_trans':X_trans,'default_value':default_value}
    res_dict["note"] = "*起始日期-终止日期的各VIP段的原油购买人数*"
    # print(res_dict)
    return res_dict

def buy_oil_times(input_dict):
    data_dict = dict()
    for y in Y_list:
        data_dict[y] = dict()
    head_name = "VIP等级购买原油次数"

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
    sql_where = ' where date in(' + easy_mysql.sql_value_str(date_list)+')'
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

    sql_str = 'select mvip,count(uid),sum(ttimes),sum(tcost) from(select uid,max(viplevel) as mvip,sum(times) as ttimes,sum(cash+diamond) as tcost from OilBuy '+sql_where+'  group by uid) as a group by mvip;'
    cursor.execute(sql_str)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            data_dict[Y_list[1]][rec[0]] = rec[2]
    for key in data_dict.keys():
        if X_first[0] not in data_dict.keys():
            data_dict[key]['trans'] = Y_trans[key]
    res_dict={'data_dict':data_dict,'X_list':X_list,'Y_list':Y_list,'head_name':head_name,'X_trans':X_trans,'default_value':default_value}
    res_dict["note"] = "*起始日期-终止日期的各VIP段的原油购买次数*"
    # print(res_dict)
    return res_dict

def buy_oil_diamond(input_dict):
    data_dict = dict()
    for y in Y_list:
        data_dict[y] = dict()
    head_name = "VIP等级购买原油钻石消耗"

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
    sql_where = ' where date in(' + easy_mysql.sql_value_str(date_list) + ')'
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

    sql_str = 'select mvip,count(uid),sum(ttimes),sum(tcost) from(select uid,max(viplevel) as mvip,sum(times) as ttimes,sum(cash+diamond) as tcost from OilBuy '+sql_where+'  group by uid) as a group by mvip;'
    cursor.execute(sql_str)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            data_dict[Y_list[1]][rec[0]] = rec[3]
    for key in data_dict.keys():
        if X_first[0] not in data_dict.keys():
            data_dict[key]['trans'] = Y_trans[key]
    res_dict={'data_dict':data_dict,'X_list':X_list,'Y_list':Y_list,'head_name':head_name,'X_trans':X_trans,'default_value':default_value}
    res_dict["note"] = "*起始日期-终止日期的各VIP段的原油购买消耗钻石数*"
    # print(res_dict)
    return res_dict