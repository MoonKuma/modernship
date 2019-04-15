#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : merge_month_data.py
# @Author: MoonKuma
# @Date  : 2019/4/1
# @Desc  : merge monthly data


"""
data like:
reg_month	active_month	channel	count(distinct uid)
2018-03	2018-03	1006	3557
2018-03	2018-03	1007	2924
2018-03	2018-03	1009	472

after merging

table1:original
reg_month   1006    1007    1008
2018-03 value1  value2  value3
2018-04 ...

table2:compare next month
value = (value_next_month - value_month)/value_month

table2:compare third month
value = (value_third_month - value_month)/value_month
"""

from util.DateList import DateList
import os
import collections

easy_date = DateList()
default_name = 'conf/final_month_pay_users_active.txt'
default_col = collections.OrderedDict()
default_col['1045'] = 'ios'
default_col['1007'] = '华为'
default_col['1012'] = 'vivo'
default_col['1006'] = 'UC'
default_col['1009'] = 'oppo'
default_col['1043'] = '应用宝'
default_col['1100'] = '钢铁帝国（锦游）'
default_col['1098'] = '意游IOS'
default_col['1099'] = '超级海战'
default_col['109906'] = '超级战舰'
default_col['109913'] = '超级海战2'
default_col['109902'] = '荣耀海战1'
default_col['109905'] = '荣耀海战2'

# pay_month	reg_month	channel	money	payUsers
def read_table(file_name=default_name, col_name=['active_month','reg_month', 'channel', 'money', 'data'], delimiter='\t', headline=1):
    """
    read in table
    :param file_name:  data file
    :param col_name: the default col structure is reg_month, active_month, channel, data
    :param delimiter: delimiter
    :return: dict data {reg_month|active_month|channel:data}
    """
    result = dict()
    line_count=0
    with open(file_name,'r') as data_file:
        for line in data_file.readlines():
            if line_count<headline:
                line_count += 1
                continue
            line = line.strip()
            array = line.split(delimiter)
            reg_month = array[list(col_name).index('reg_month')]
            active_month = array[list(col_name).index('active_month')]
            channel = array[list(col_name).index('channel')]
            key = reg_month + '|' + active_month + '|' + channel
            data = 0
            try:
                data = float(array[list(col_name).index('data')])
            except:
                print('WRONG DATA DETECTED, KEY:',key,',data:',data)
            if key not in result.keys():
                result[key] = data
    return result


def draw_table(tabled_data, data_file=default_name, col_rank=default_col,data_spliter='|', file_spliter= '\t', reset=False):
    # data should be like month|col : data
    reg_month_list = list()
    for key in tabled_data.keys():
        array = key.split(data_spliter)
        if array[0] not in reg_month_list:
            reg_month_list.append(array[0])
    reg_month_list = sorted(reg_month_list)
    save_path = os.path.splitext(data_file)[0] + '-result' + os.path.splitext(data_file)[1]
    if reset:
        with open(save_path, 'w') as file_name:
            pass
    with open(save_path,'a') as save_file:
        # header
        save_file.write('\n')
        header = ['注册月'] + list(col_rank.values())
        header_str = file_spliter.join(header) + '\n'
        save_file.write(header_str)
        # data
        for month in reg_month_list:
            data_list = [month]
            for key in col_rank.keys():
                data_key = month + data_spliter + key
                data = str(tabled_data.setdefault(data_key,0))
                data_list.append(data)
            data_wri = file_spliter.join(data_list) + '\n'
            save_file.write(data_wri)


def compute_value(data, month_split=0):
    """
    compute monthly difference
    :param data: data dict {reg_month|active_month|channel:data}
    :param month_split: if 0 report original data, else report month diff
    :return: data dict for table , month|channel:data
    """
    # compute original
    data_original = dict() # reg_month|channel : data
    data_target = dict()
    for key in data.keys():
        array = key.split('|')
        reg = array[0]
        tar = array[1]
        channel = array[2]
        data_now = data[key]
        if reg==tar:
            key = reg + '|' + channel
            data_original[key] = data_now
        if month_split>0:
            tar_month = reg
            for i in range(0,month_split):
                tar_month = easy_date.get_next_month(tar_month)
            new_key = reg + '|' + tar_month + '|' + channel
            refer_key = reg + '|' + reg + '|' + channel
            new_data = data.setdefault(new_key, 0)/data.setdefault(refer_key, 1)
            key2 = reg + '|' + channel
            if key2 not in data_target.keys():
                data_target[key2] = new_data
    if month_split>0:
        return data_target
    else:
        return data_original


def main_exe(data_file=default_name):
    data_orig = read_table(file_name=data_file)
    value1 = compute_value(data=data_orig, month_split=0)
    value2 = compute_value(data=data_orig, month_split=1)
    value3 = compute_value(data=data_orig, month_split=2)
    draw_table(tabled_data=value1, data_file=data_file, reset=True)
    draw_table(tabled_data=value2, data_file=data_file)
    draw_table(tabled_data=value3, data_file=data_file)



main_exe()
