#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : __init__.py.py
# @Author: mjf
# @Date  : 
# @Desc  :



import util.EasyMysql as EasyMysql
from is_valid_data import is_legal_input
import util.ReadTable as ReadTable
import sys

X_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,21,22,23,24,25]
X_listtrans = map(lambda x:'VIP'+str(x),X_list)


X_first = ['trans']
X_first_trans = ['翻译']
X_list = X_first + X_list
X_listtrans = X_first_trans + X_listtrans
X_trans = dict(zip(X_list, X_listtrans))

default_value = ''

def shop_exchange(input_dict,*flag):
    Y_list = []
    Y_trans = dict()
    data_dict = dict()

    head_name = "商店"+str(flag[0])

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


    if len(flag)>0:
        sqlstr = 'select mvip,itemid,sum(times) from(select uid,max(viplevel) as mvip from shopexchange'+sql_where+' and shopid='+str(flag[0])+' group by uid) as a left join (select uid,itemid,sum(times) as times from shopexchange'+sql_where+' and shopid='+str(flag[0])+' group by uid,itemid) as b on a.uid=b.uid group by mvip,itemid;'
        # print(sqlstr)
        cursor.execute(sqlstr)
        alldata = cursor.fetchall()
        if alldata:
            for rec in alldata:
                Y_list.append(str(rec[1]))
        Y_list = sorted(list(set(Y_list)))
        for y in Y_list:
            data_dict[y] = dict()
        if alldata:
            for rec in alldata:
                data_dict[str(rec[1])][int(rec[0])] = rec[2]

        Y_trans_origin = ReadTable.ReadTable("./conf/item.txt").read_table_file_coupled([1,1])
        for i in Y_list:
            Y_trans[i] = Y_trans_origin.setdefault(i,dict()).setdefault("游戏内名称","-")

    for key in data_dict.keys():
            data_dict[key]['trans'] = Y_trans[key]
    res_dict = {'data_dict': data_dict, 'X_list': X_list, 'Y_list': Y_list, 'head_name': head_name, 'X_trans': X_trans,
                'default_value': default_value}
    # print(res_dict)
    res_dict['note'] = "开始-终止日的"+str(flag[0])+"商城购买次数"
    return res_dict
