#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : item_buy.py
# @Author: MoonKuma
# @Date  : 2018/11/9
# @Desc  : shop buy item counts, also try first pay

import util.EasyMysql as EasyMysql
from is_valid_data import is_legal_input
import conf.ConfParameters as ConfParameters
import util.ReadTable as ReadTable

file_name = 'shop_data_trans.txt'


def get_item_buy(input_dict):
    global file_name
    is_legal_input(input_dict)
    data_dict = dict()
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
    # sql item buying
    user_buy = dict()
    vip_list = list()
    item_list = list()
    cmd = 'select viplevel, itemid, sum(buy_times) from (select uid,itemid,(select max(vip_level) from user_active ' + sql_where + ' and uid=a.uid ) as viplevel,count(uid) as buy_times from pay_syn_day_extend as a ' + sql_where + ' group by uid,itemid)a group by viplevel,itemid'
    print(cmd)
    if cursor == None:
        msg = 'Cursor is None. Return empty.'
        return None
    cursor.execute(cmd)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            vip = str(rec[0])
            item_id = str(rec[1])
            uid_count = int(rec[2])
            if vip not in vip_list:
                vip_list.append(vip)
            if item_id not in item_list:
                item_list.append(item_id)
            if item_id not in user_buy.keys():
                user_buy[item_id] = dict()
            user_buy[item_id][vip] = uid_count
    vip_list = sorted(vip_list, key=lambda x: int(x))
    item_list = sorted(item_list, key=lambda x: int(x))
    # shop table
    shop_ref_dict = __read_table(file_name)
    # compute data dict
    for item in user_buy.keys():
        user_buy[item]['trans'] = shop_ref_dict.setdefault(item, dict()).setdefault('trans', '')
        user_buy[item]['value'] = int(shop_ref_dict.setdefault(item, dict()).setdefault('value', '0'))
    # compute other elements
    y_list = item_list
    x_list = ['trans', 'value'] + vip_list
    x_trans = dict()
    x_trans['trans'] = '翻译'
    x_trans['value'] = '价值'
    for vip in vip_list:
        x_trans[vip] = 'vip' + str(vip)
    # load res
    res_data_raw = dict()
    res_data_raw['data_dict'] = user_buy
    res_data_raw['X_list'] = x_list
    res_data_raw['Y_list'] = y_list
    res_data_raw['X_trans'] = x_trans
    res_data_raw['default_value'] = 0
    res_data_raw['head_name'] = '各VIP档商品购买笔数'
    res_data_raw['note'] = '*取一段时间的各VIP档购买各货品的笔数合计（VIP取时间段内单位UID的最大VIP, 按活跃表计算），翻译和价值是根据配表的，如果发现翻译或价值问题，请提示我更新配表，商品ID是实际的商品ID'
    return res_data_raw


# private
def __read_table(table_file_name):
    file_path = ConfParameters.ConfParameters().conf_path + table_file_name
    return ReadTable.ReadTable(file_path).read_table_file_coupled()

# test
if __name__ == '__main__':
    input_dict = dict()
    input_dict['date_list'] = ['2018-11-12', '2018-11-13', '2018-11-14']
    input_dict['cursor'] = None
    input_dict['channel_list'] = list()
    input_dict['zone_list'] = list()
    get_item_buy(input_dict)
