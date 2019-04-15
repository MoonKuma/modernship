#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : module_attend.py
# @Author: MoonKuma
# @Date  : 2018/11/5
# @Desc  : module attend rate: attending users / those who are capable to attend
# conf : module_attend_level.txt
# sql : select regdate,date,keyword,sum(countuid) from behavior_template group by regdate,date,keyword;


import util.EasyMysql as EasyMysql
from is_valid_data import is_legal_input
import conf.ConfParameters as ConfParameters
import util.ReadTable as ReadTable

file_name = 'module_attend_level.txt'


def get_module_attend_rate(input_dict):
    global file_name
    is_legal_input(input_dict)
    data_dict = dict()
    data_dict_ratio = dict()
    # where clause
    easy_mysql = EasyMysql.EasyMysql()
    is_legal_input(input_dict)
    date_list = input_dict['date_list']
    date_list = sorted(date_list)
    if len(date_list) == 0:
        msg = 'Not date selected, len(date_list)' + str(len(date_list))
        raise RuntimeError(msg)
    date_compute_str = easy_mysql.sql_value_str(date_list)  # automatically compute the last date
    zoneid_list = input_dict['zone_list']
    channel_list = input_dict['channel_list']
    cursor = input_dict['cursor']
    sql_where = ' where date in (' + date_compute_str + ') '
    if len(zoneid_list) > 0:
        sql_where = sql_where + ' and zoneid in (' + easy_mysql.sql_value_str(zoneid_list) + ') '
    if len(channel_list) > 0:
        sql_where = sql_where + ' and channel in (' + easy_mysql.sql_value_str(channel_list) + ') '
    # sql check dau
    user_active_dict = dict()
    cmd = 'select date,level,count(uid) from user_active ' + sql_where + ' group by date,level'
    cursor.execute(cmd)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            date = str(rec[0])
            level = int(rec[1])
            uid_count = int(rec[2])
            if date not in user_active_dict.keys():
                user_active_dict[date] = dict()
            user_active_dict[date][level] = uid_count
    # sql check attending
    user_attend = dict()
    cmd = 'select date,keyword,sum(countuid) from behavior_template ' + sql_where + ' group by date,keyword'
    cursor.execute(cmd)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            date = str(rec[0])
            keyword = str(rec[1])
            uid_count = int(rec[2])
            if date not in user_attend.keys():
                user_attend[date] = dict()
            user_attend[date][keyword] = uid_count
    # attending table
    attend_ref_dict = __read_module_table(file_name)
    key_list = attend_ref_dict.keys()
    # compute data dict
    for date in date_list:
        if date not in data_dict.keys():
            data_dict[date] = dict()
        if date not in data_dict_ratio.keys():
            data_dict_ratio[date] = dict()
        user_active = __get_above_users(user_active_dict, 0, date)
        data_dict[date]['UserActive'] = user_active
        data_dict_ratio[date]['UserActive'] = user_active
        for key in key_list:
            if date in user_attend.keys():
                attend_user = user_attend[date].setdefault(key, 0)
                data_dict[date][key] = attend_user
                refer_level = int(attend_ref_dict[key]['level'])
                refer_user = __get_above_users(user_active_dict, refer_level, date)
                if refer_user > 0:
                    data_dict_ratio[date][key] = round(float(attend_user)/refer_user, 2)
    y_list = date_list
    x_list = ['UserActive'] + key_list
    x_trans = dict()
    x_trans['UserActive'] = '活跃用户'
    for key in key_list:
        x_trans[key] = attend_ref_dict[key]['trans']
    # load res
    res_data_raw = dict()
    res_data_ratio = dict()
    res_data_raw['data_dict'] = data_dict
    res_data_raw['X_list'] = x_list
    res_data_raw['Y_list'] = y_list
    res_data_raw['X_trans'] = x_trans
    res_data_raw['default_value'] = 0
    res_data_raw['head_name'] = '活动参与度-参与人数'
    res_data_raw['note'] = '*各活动的实际参与人数'


    res_data_ratio['data_dict'] = data_dict_ratio
    res_data_ratio['X_list'] = x_list
    res_data_ratio['Y_list'] = y_list
    res_data_ratio['X_trans'] = x_trans
    res_data_ratio['default_value'] = 0
    res_data_ratio['head_name'] = '活动参与度-比例'
    res_data_ratio['note'] = '*各活动的参与比例，注意分母是符合条件的用户，即活跃且等级达到指定等级的用户'

    return [res_data_raw, res_data_ratio]


# private
def __read_module_table(table_file_name):
    file_path = ConfParameters.ConfParameters().conf_path + table_file_name
    return ReadTable.ReadTable(file_path).read_table_file_coupled()


def __get_above_users(active_dict, check_level, compute_date):
    # user above level x
    active_dict_date = active_dict[compute_date]
    user_count = 0
    for level in active_dict_date.keys():
        if int(level) >= check_level:
            user_count = user_count + int(active_dict_date[level])
    return user_count
