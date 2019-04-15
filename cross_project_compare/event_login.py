#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : event_login.py
# @Author: MoonKuma
# @Date  : 2019/1/2
# @Desc  : use the count of register device and register users to compute and compare event log in success ratio

from util.is_valid_data import is_legal_input
from util.EasyMysql import EasyMysql

def event_login(input_dict, stat_reg_name):
    is_legal_input(input_dict)
    easy_sql = EasyMysql()
    cursor = input_dict['cursor']
    where_clause_main = easy_sql.combine_where_clause(input_dict, use_zoneids=False)
    x_list = input_dict['date_list']
    y_list = ['n_device', 'n_openid', 'pass_rate']
    y_trans = {'n_device' : '新注册设备数', 'n_openid' : '新注册openid数', 'pass_rate': '转化率'}
    result_dict = dict()

    date_list = input_dict['date_list']
    min_date = date_list[0] + ' 00:00:00'
    max_date = date_list[len(date_list)-1] + ' 23:59:59'
    where_clause = ' where date between \'' + min_date + '\' and \'' + max_date + '\' ' + where_clause_main

    # user reg
    sql_cmd = 'select date,sum(reg_count) from (select date,count(*) as reg_count  from ' + stat_reg_name + '.user_register_openid0 ' + where_clause + ' group by date'
    for i in range(1, 10):
        sql_cmd = sql_cmd + ' union all select date,count(*) as reg_count from ' + stat_reg_name + '.user_register_openid' + str(i) + where_clause + ' group by date'
    sql_cmd = sql_cmd + ')a group by date'
    print(sql_cmd)
    cursor.execute(sql_cmd)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            date = str(rec[0])
            user = int(rec[1])
            if 'n_openid' not in result_dict.keys():
                result_dict['n_openid'] = dict()
            result_dict['n_openid'][date] = user

    # new device
    sql_cmd = 'select date_n,sum(reg_count) from (select date_format(date,\'%Y-%m-%d\') as date_n,count(*) as reg_count  from ' + stat_reg_name + '.user_device0 ' + where_clause + ' group by date_n'
    for i in range(1, 10):
        sql_cmd = sql_cmd + ' union all select date_format(date,\'%Y-%m-%d\') as date_n,count(*) as reg_count from ' + stat_reg_name + '.user_device' + str(
            i) + where_clause + ' group by date_n'
    sql_cmd = sql_cmd + ')a group by date_n'
    print(sql_cmd)
    cursor.execute(sql_cmd)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            date = str(rec[0])
            user = int(rec[1])
            if 'n_device' not in result_dict.keys():
                result_dict['n_device'] = dict()
            result_dict['n_device'][date] = user

    # compute ratio
    result_dict['pass_rate'] = dict()
    for date in date_list:
        if date in result_dict['n_device'].keys() and date in result_dict['n_openid'].keys() and result_dict['n_device'][date]>0:
            result_dict['pass_rate'][date] = result_dict['n_openid'][date] / float(result_dict['n_device'][date])

    res_dict = dict()
    res_dict['data_dict'] = result_dict
    res_dict['X_list'] = x_list
    res_dict['Y_list'] = y_list
    res_dict['Y_trans'] = y_trans
    res_dict['default_value'] = 0
    res_dict['head_name'] = '启动加载项通过率'
    res_dict['note'] = '*按照当日的新增OPEN数/新增设备数，作为设备通过率的通用指标'
    #
    return res_dict


