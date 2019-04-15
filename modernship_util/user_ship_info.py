#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : user_ship_info.py
# @Author: MoonKuma
# @Date  : 2018/10/29
# @Desc  : user ship information (only those on battle)
# sql : select viplevel,shipid,shipstar,shipgrade,sum(countuid) from ShipInfo where date = '2018-10-24' and shipid>0 and shipstar>2 and shipgrade>2 group by viplevel,shipid,shipstar,shipgrade


import util.EasyMysql as EasyMysql
from is_valid_data import is_legal_input
import conf.ConfParameters as ConfParameters
import util.ReadTable as ReadTable


def get_ship_info(input_dict):
    data_dict = dict()
    # prepare sql
    easy_mysql = EasyMysql.EasyMysql()
    is_legal_input(input_dict)
    date_list = input_dict['date_list']
    date_list = sorted(date_list)
    if len(date_list) == 0:
        msg = 'Not date selected, len(date_list)' + str(len(date_list))
        raise RuntimeError(msg)
    date_compute = date_list[len(date_list) - 1]  # automatically compute the last date
    zoneid_list = input_dict['zone_list']
    channel_list = input_dict['channel_list']
    cursor = input_dict['cursor']
    sql_where = ' where date=' + easy_mysql.sql_value_str([date_compute])
    if len(zoneid_list) > 0:
        sql_where = sql_where + ' and zoneid in (' + easy_mysql.sql_value_str(zoneid_list) + ') '
    if len(channel_list) > 0:
        sql_where = sql_where + ' and channel in (' + easy_mysql.sql_value_str(channel_list) + ') '
    # ship_dict
    ship_dict = __read_ship_table('ship_info_korea.txt')
    for ship_id in ship_dict.keys():
        if ship_id not in data_dict.keys():
            data_dict[ship_id] = dict()
        if 'ShipName' not in data_dict[ship_id].keys():
            data_dict[ship_id]['ShipName'] = ship_dict.setdefault(ship_id, dict()).setdefault('ship_name', ship_id)
        if 'ShipRank' not in data_dict[ship_id].keys():
            data_dict[ship_id]['ShipRank'] = ship_dict.setdefault(ship_id, dict()).setdefault('ship_rank', ship_id)
    # Y & X
    Y_list = ['UserCount']
    for key in ship_dict.keys():
        Y_list.append(key)
    Y_trans = {'UserCount': '用户数量'}
    X_list = ['ShipName', 'ShipRank', 'TotalCount'] # + sorted(vip_list)
    X_trans = {'ShipName': '船名称', 'ShipRank': '评级', 'TotalCount': '用户总量' } # trans of vip
    # --- vip active
    vip_dict = dict()
    vip_list = list()
    total_user = 0
    sql_cmd_active = 'select vip_level, count(distinct uid) from user_active' + sql_where + ' group by vip_level'
    cursor.execute(sql_cmd_active)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            vip = int(rec[0])
            user = int(rec[1])
            total_user += user
            if vip not in vip_list:
                vip_list.append(vip)
            if 'UserCount' not in data_dict.keys():
                data_dict['UserCount'] = dict()
            data_dict['UserCount'][vip] = user
    data_dict['UserCount']['TotalCount'] = total_user
    data_dict['UserCount']['ShipName'] = '-'
    data_dict['UserCount']['ShipRank'] = '-'
    vip_list = sorted(vip_list)
    X_list = X_list + vip_list
    for vip in vip_list:
        X_trans[vip] = 'VIP' + str(vip)
    # --- ship info
    sql_cmd_ship = 'select viplevel,shipid,sum(countuid) from ShipInfo ' + sql_where + ' and shipid>0 and shipstar>2 and shipgrade>2 group by viplevel,shipid'
    cursor.execute(sql_cmd_ship)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            vip = int(rec[0])
            ship_id = str(rec[1])
            user = int(rec[2])
            if ship_id not in data_dict.keys():
                data_dict[ship_id] = dict()
            data_dict[ship_id][vip] = user
            data_dict[ship_id]['TotalCount'] = data_dict[ship_id].setdefault('TotalCount', 0) + user
    # -- compile return value
    res_dict = dict()
    res_dict['data_dict'] = data_dict
    res_dict['X_list'] = X_list
    res_dict['Y_list'] = Y_list
    res_dict['X_trans'] = X_trans
    res_dict['Y_trans'] = Y_trans
    res_dict['default_value'] = 0
    res_dict['head_name'] = '用户阵容'
    res_dict['note'] = '*取最后计算日的，各VIP用户的战役上阵用阵容，仅3星且3阶以上船被统计了'
    return res_dict


# private
# read ship table
def __read_ship_table(file_name):
    file_path = ConfParameters.ConfParameters().conf_path + file_name
    return ReadTable.ReadTable(file_path).read_table_file_coupled()



