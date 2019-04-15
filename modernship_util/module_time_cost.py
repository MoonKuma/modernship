#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : module_time_cost.py
# @Author: MoonKuma
# @Date  : 2018/10/26
# @Desc  : time cost of each module
# db : $big_data:
# sql : select ui_type,vip_level,count(uid),sum(time) from user_exit_ui_time where date='2018-10-24' group by ui_type,vip_level;

import util.EasyMysql as EasyMysql
from is_valid_data import is_legal_input

module_trans = {
    'UserCount': '人数',
    '10010000': '战役',
    '10020000': '实兵对抗',
    '10030000': '军事演习',
    '10040000': '大洋追辑',
    '10050000': '重装突击',
    '10060000': '远洋任务&多线作战',
    '10070000': '军团',
    '10080000': '旗舰养成',
    '10090000': '舰船养成',
    '10100000': '仓库',
    '10110000': '商店',
    '20000000': '闲置',
    '99999999': '在线总时长'}

module_list = ['10010000','10020000','10030000','10040000','10050000','10060000','10070000','10080000','10090000','10100000','10110000','20000000','99999999']



def get_module_time_cost(input_dict):
    global module_list
    global module_trans
    easy_mysql = EasyMysql.EasyMysql()
    is_legal_input(input_dict)
    date_list = input_dict['date_list']
    date_list = sorted(date_list)
    if len(date_list) == 0:
        msg = 'Not date selected, len(date_list)' + str(len(date_list))
        raise RuntimeError(msg)
    date_compute = date_list[len(date_list)-1]  # automatically compute the last date
    zoneid_list = input_dict['zone_list']
    channel_list = input_dict['channel_list']
    cursor = input_dict['cursor']
    sql_where = ' where date=' + easy_mysql.sql_value_str([date_compute])
    if len(zoneid_list) > 0:
        sql_where = sql_where + ' and zoneid in (' + easy_mysql.sql_value_str(zoneid_list) + ') '
    if len(channel_list) > 0:
        sql_where = sql_where + ' and channel in (' + easy_mysql.sql_value_str(channel_list) + ') '
    # vip active
    vip_dict = dict()
    vip_list = list()
    sql_cmd = 'select vip_level, count(distinct uid) from user_active' + sql_where + ' group by vip_level'
    cursor.execute(sql_cmd)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            vip = int(rec[0])
            user = int(rec[1])
            if vip not in vip_list:
                vip_list.append(vip)
            if vip not in vip_dict.keys():
                vip_dict[vip] = user
    vip_list = sorted(vip_list)
    # module time
    module_dict = dict()
    sql_cmd = 'select ui_type,vip_level,sum(time)/(60*count(uid)) from user_exit_ui_time' + sql_where + ' group by ui_type,vip_level'
    cursor.execute(sql_cmd)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            ui_type = str(rec[0])
            vip = int(rec[1])
            data = round(float(rec[2]), 1)
            if ui_type not in module_dict.keys():
                module_dict[ui_type] = dict()
            if vip not in module_dict[ui_type].keys():
                module_dict[ui_type][vip] = data
    # add user_count
    module_dict['UserCount'] = dict()
    for vip in vip_list:
        module_dict['UserCount'][vip] = vip_dict[vip]
    # add trans
    for module_id in module_list:
        if module_id not in module_dict.keys():
            module_dict[module_id] = dict()
        module_dict[module_id]['trans'] = module_trans[module_id]
    module_dict['UserCount']['trans'] = '用户数量'
    # X_trans
    X_trans = dict()
    X_trans['trans'] = '翻译'
    for vip in vip_list:
        X_trans[vip] = 'VIP' + str(vip)
    # compile return value
    res_dict = dict()
    res_dict['data_dict'] = module_dict
    res_dict['X_list'] = ['trans'] + vip_list
    res_dict['Y_list'] = ['UserCount'] + module_list
    res_dict['X_trans'] = X_trans
    res_dict['default_value'] = 0
    res_dict['head_name'] = '模块时长'
    res_dict['note'] = '*取最后计算日的，各VIP用户各项目人均游戏时长（单位：分钟）'
    return res_dict






