#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : user_guidance.py
# @Author: MoonKuma
# @Date  : 2019/1/2
# @Desc  : use max level of new register users as mark of user guidance passing rate

from util.is_valid_data import is_legal_input
from util.EasyMysql import EasyMysql
from util.DateList import DateList


def user_guidance(input_dict, level_pass, stat_reg_name):
    is_legal_input(input_dict)
    easy_sql = EasyMysql()
    easy_date = DateList()
    cursor = input_dict['cursor']
    where_clause_main = easy_sql.combine_where_clause(input_dict)
    x_list = input_dict['date_list']
    y_list = range(1, level_pass+1)
    result_dict = dict()

    for date in input_dict['date_list']:
        time_stamp = easy_date.trans_date_form(date, '%Y%m%d')
        where_clause = '1 ' + where_clause_main + ' and uid in (select uid from ( select uid from ' + stat_reg_name + '.user_register0 where date=\'' + date + '\''
        for i in range(1,10):
            where_clause = where_clause + ' union all select uid from ' + stat_reg_name + '.user_register' + str(i) + ' where date=\'' + date + '\''
        where_clause = where_clause + ')a)'
        sql_cmd = 'select level,count(uid) from user_active_' + time_stamp + ' where ' + where_clause + ' group by level'
        # print sql_cmd
        cursor.execute(sql_cmd)
        all_data = cursor.fetchall()
        level_map = dict()
        if all_data:
            for rec in all_data:
                level = int(rec[0])
                users = int(rec[1])
                level_map[level] = users
        for level in y_list:
            if level not in result_dict.keys():
                result_dict[level] = dict()
            result_dict[level][date] = _pass_certain_lv(level_map, level)[0]
        if 'TotalReg' not in result_dict.keys():
            result_dict['TotalReg'] = dict()
        result_dict['TotalReg'][date] = _pass_certain_lv(level_map, 0)[1]

    res_dict = dict()
    res_dict['data_dict'] = result_dict
    res_dict['X_list'] = x_list
    res_dict['Y_list'] = ['TotalReg'] + y_list
    res_dict['default_value'] = 0
    res_dict['head_name'] = '新用户新手引导通过率'
    res_dict['note'] = '*按等级处理新手引导通过率，大于等于' + str(level_pass) + '认为通过新手引导'

    return res_dict


def _pass_certain_lv(level_map, lv):
    total_count = 1
    current_count = 0
    for level in level_map.keys():
        if lv<=level:
            current_count = current_count + level_map[level]
        total_count = total_count + level_map[level]
    return [float(current_count)/total_count, current_count]


# test
# key_list_dict = {'date_list': ['2018-11-12','2018-11-13','2018-11-14','2018-11-15'], 'zone_list': list(), 'channel_list': [1000,1001,1045], 'cursor': None}
# user_guidance(key_list_dict, 5, 'stat_userreg'  )