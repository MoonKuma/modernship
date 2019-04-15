#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : online_time.py
# @Author: MoonKuma
# @Date  : 2019/1/2
# @Desc  :
from util.is_valid_data import is_legal_input
from util.EasyMysql import EasyMysql
from util.DateList import DateList
import datetime

def online_time(input_dict,stat_active_name,stat_pay_name,currency_rate, *args):
    is_legal_input(input_dict)
    easy_sql = EasyMysql()
    easy_date = DateList()
    cursor = input_dict['cursor']
    where_clause_main = easy_sql.combine_where_clause(input_dict)
    x_list = input_dict['date_list']
    y_list = sorted(list(args))
    # print(y_list)
    res_dict = dict()
    ress_dict =dict()

    if len(input_dict['date_list'])!=0:
        min_time_stamp = min(input_dict['date_list'])
        max_time_stamp = max(input_dict['date_list'])
    # print(max_time_stamp)
    #考察充值情况 距离开服x天
    pay_dict=dict()
    sql_cmd_pay = 'select uid,sum(money/100)*'+str(currency_rate)+' as money from '+stat_pay_name+'.pay_syn_day where date<=\''+max_time_stamp+'\'' +where_clause_main+' group by uid;'
    # print(sql_cmd_pay)
    cursor.execute(sql_cmd_pay)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            pay_dict[rec[0]]=rec[1]
    gettime_dict = dict()
    getnum_dict = dict()
    data_dict = dict()
    # gettime_dict['total'] = dict()
    # getnum_dict['total'] = dict()
    data_dict['total'] = dict()
    for date in input_dict['date_list']:
        # 活跃时间，人数，容器
        for j in range(0, len(y_list)):
    #         gettime_dict[y_list[j]] = dict()
    #         getnum_dict[y_list[j]] = dict()
            data_dict[y_list[j]] = dict()


    for date in input_dict['date_list']:
        # 活跃时间，人数，容器
        time_dict = dict()
        num_dict = dict()
        time_stamp=datetime.datetime.strptime(date,"%Y-%m-%d").strftime("%Y%m%d")
        sql_cmd_active = ''
        if hastable(cursor, 'user_active_' +time_stamp , stat_active_name):
            # print(time_stamp)
            sql_str = 'select uid,online_time/60,1 from ' + stat_active_name + '.user_active_' + time_stamp +' where 1 '+ where_clause_main + ';'
            cursor.execute(sql_str)
            # print(sql_str)
            all_data = cursor.fetchall()
            if all_data:
                for rec in all_data:
                    time_dict[rec[0]] = rec[1]
                    num_dict[rec[0]] = rec[2]

        for key in time_dict.keys():
            gettime_dict['total'][date] = gettime_dict.setdefault('total', dict()).setdefault(date, 0) + time_dict[key]
            getnum_dict['total'][date] = getnum_dict.setdefault('total', dict()).setdefault(date, 0) + num_dict[key]

        # print(len(time_dict))

        for j in range(0, len(y_list)):
            for key in time_dict.keys():
                if pay_dict.has_key(key):
                    if j == 0:
                        if int(pay_dict[key]) <= int(y_list[j]):
                            gettime_dict[y_list[j]][date] = gettime_dict.setdefault(y_list[j],dict()).setdefault(date,0) + time_dict[key]
                            getnum_dict[y_list[j]][date] = getnum_dict.setdefault(y_list[j], dict()).setdefault(date, 0) + \
                                                            num_dict[key]
                        # print("this is 0")
                    elif j!=0 and j<=len(y_list)-1:
                        if int(y_list[j - 1]) < int(pay_dict[key]) <= int(y_list[j]):
                            gettime_dict[y_list[j]][date] = gettime_dict.setdefault(y_list[j], dict()).setdefault(date, 0) + time_dict[key]
                            getnum_dict[y_list[j]][date] = getnum_dict.setdefault(y_list[j], dict()).setdefault(date, 0) + \
                                                           num_dict[key]
        for key in time_dict.keys():
            if pay_dict.has_key(key)== False:
                gettime_dict[y_list[0]][date] = gettime_dict.setdefault(y_list[0], dict()).setdefault(date, 0) + time_dict[key]
                getnum_dict[y_list[0]][date] = getnum_dict.setdefault(y_list[0], dict()).setdefault(date, 0) + \
                                               num_dict[key]
        for key in pay_dict.keys():
            if time_dict.has_key(key) and int(pay_dict[key])>int(y_list[len(y_list)-1]):
                    gettime_dict[str(y_list[len(y_list)-1])+'+'][date] = gettime_dict.setdefault(str(y_list[len(y_list)-1])+'+', dict()).setdefault(date, 0) + time_dict[
                        key]
                    getnum_dict[str(y_list[len(y_list)-1])+'+'][date] = getnum_dict.setdefault(str(y_list[len(y_list)-1])+'+', dict()).setdefault(date, 0) + \
                                                            num_dict[key]

        # print('get5000+'+str(getnum_dict))
        # print('get5000t+' + str(gettime_dict))
        data_dict['total'][date] = gettime_dict['total'][date]/getnum_dict['total'][date]

        for j in range(0, len(y_list)):
            if gettime_dict.has_key(y_list[j]) and gettime_dict[y_list[j]].has_key(date):
                if gettime_dict[y_list[j]][date]!=0:
                    data_dict[y_list[j]][date]=gettime_dict[y_list[j]][date]/getnum_dict[y_list[j]][date]
                else:
                    data_dict[y_list[j]][date]=''
        if gettime_dict.has_key(str(y_list[len(y_list)-1])+'+') and gettime_dict[y_list[j]].has_key(date):
            if gettime_dict[str(y_list[len(y_list)-1])+'+'][date] != 0:
                data_dict[str(y_list[len(y_list)-1])+'+'][date]=data_dict.setdefault(str(y_list[len(y_list)-1])+'+',dict()).setdefault(date,gettime_dict[str(y_list[len(y_list)-1])+'+'][date]/getnum_dict[str(y_list[len(y_list)-1])+'+'][date])
            else:
                data_dict[str(y_list[len(y_list)-1])+'+'][date] = ''

        # print(data_dict)
    res_dict['data_dict'] = data_dict


    # res_dict['data_dict'] = get_dict

    res_dict['X_list'] = x_list
    res_dict['Y_list'] = ['total'] + y_list+[str(y_list[len(y_list)-1])+'+']
    res_dict['Y_trans'] = dict()
    for j in range(0,len(y_list)):
        if j==0:
            res_dict['Y_trans'][y_list[j]]='0--'+str(y_list[j])
        elif j>0 and j<=len(y_list)-1:
            res_dict['Y_trans'][y_list[j]] = str(y_list[j-1])+'--'+str(y_list[j])
    res_dict['Y_trans'][str(y_list[len(y_list)-1])+'+'] = str(y_list[len(y_list)-1])+'以上'
    res_dict['default_value'] = 0
    res_dict['head_name'] = '每日人均在线时长/分钟'
    res_dict['note'] = '每日人均在线时长/分钟'


    ress_dict['data_dict'] = getnum_dict
    ress_dict['X_list'] = x_list
    ress_dict['Y_list'] = ['total'] + y_list+[str(y_list[len(y_list)-1])+'+']
    ress_dict['Y_trans'] = dict()
    for j in range(0,len(y_list)):
        if j==0:
            ress_dict['Y_trans'][y_list[j]]='0--'+str(y_list[j])
        elif j>0 and j<=len(y_list)-1:
            ress_dict['Y_trans'][y_list[j]] = str(y_list[j-1])+'--'+str(y_list[j])
    ress_dict['Y_trans'][str(y_list[len(y_list)-1])+'+'] = str(y_list[len(y_list)-1])+'以上'


    ress_dict['default_value'] = 0
    ress_dict['head_name'] = '每日活跃人数'
    ress_dict['note'] = '每日活跃人数'




    return [res_dict,ress_dict]





def hastable(cursor,tablename,base_name):
    table_dict=dict()
    sql_str = 'select table_name from INFORMATION_SCHEMA.TABLES where TABLE_SCHEMA=\"'+base_name+'\";'
    cursor.execute(sql_str)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            table_dict[rec[0]]=1
    return table_dict.has_key(tablename)