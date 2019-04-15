#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : life_time.py
# @Author: MoonKuma
# @Date  : 2019/1/2
# @Desc  : life time compute on different pay level

from conf.ConfParameters import ConfParameters
from util.EasyMysql import EasyMysql



def life_time_compute(input_dict, *argv):  # *argv as reception of pay levels
    conf = ConfParameters()
    easy_sql = EasyMysql()
    currency_rate = conf.current_rate
    mysql_conf = conf.mysql_conf
    stat_base = mysql_conf['stat_base']
    stat_pay = mysql_conf['stat_pay']
    user_active_openid = mysql_conf['user_active_openid']
    # argv\
    x_list = list()
    y_trans = dict()
    money_list = list()
    y_list = [0]
    if len(argv) > 0:
        money_list = sorted(list(argv[0]))
        y_trans = _money_trans(money_list)
        y_list = list(range(0,len(money_list)+1))
    print('money_list:',money_list)
    print('currency_rate:', currency_rate)
    # input dict
    date_list = sorted(list(input_dict['date_list']))
    where_clause_main = easy_sql.combine_where_clause(input_dict)
    min_date = date_list[0]
    max_date = date_list[len(date_list)-1]
    cursor = input_dict['cursor']
    # where clause
    where_clause = 'where date between \'' + min_date + '\' and \'' + max_date + '\' '
    where_clause = where_clause + where_clause_main
    user_count_dict = dict()  # user count
    user_count_remain_dict = dict()  # user remain count
    user_count_remain_ratio_dict = dict()  # user remain ratio
    user_count_lost_dict = dict()  # user lost life time
    user_count_lost_user_dict = dict()  # user lost count
    sql_cmd = 'select uid,count(distinct date), max(date), min(date),ifnull((select ceil(sum(money/100)) from ' + stat_pay + '.pay_syn_day ' + where_clause + ' and uid=a.uid group by uid),0) as money from '+ stat_base + '.' + user_active_openid + ' as a ' + where_clause + ' group by uid'
    print(sql_cmd)
    cursor.execute(sql_cmd)
    one_data = cursor.fetchone()
    while one_data:
        rec = one_data
        uid = str(rec[0])
        life_time = int(rec[1])
        last_date = str(rec[2])
        reg_date = str(rec[3])
        money = int(rec[4])
        money_type = _get_money_type(money, money_list, currency_rate)
        lost = 1
        if max_date == last_date:
            lost = 0
        if reg_date not in x_list:
            x_list.append(reg_date)
        if money_type not in user_count_dict.keys():
            user_count_dict[money_type] = dict()
            user_count_remain_dict[money_type] = dict()
            user_count_remain_ratio_dict[money_type] = dict()
            user_count_lost_dict[money_type] = dict()
            user_count_lost_user_dict[money_type] = dict()
        user_count_dict[money_type][reg_date] = user_count_dict[money_type].setdefault(reg_date, 0) + 1
        if lost == 1:
            user_count_lost_dict[money_type][reg_date] = user_count_lost_dict[money_type].setdefault(reg_date, 0) + life_time
            user_count_lost_user_dict[money_type][reg_date] = user_count_lost_user_dict[money_type].setdefault(reg_date,
                                                                                                     0) + 1
        else:
            user_count_remain_dict[money_type][reg_date] = user_count_remain_dict[money_type].setdefault(reg_date, 0) + 1
            user_count_remain_ratio_dict[money_type][reg_date] = user_count_remain_ratio_dict[money_type].setdefault(reg_date, 0) + 1
        one_data = cursor.fetchone()
    print('[Check1]len(user_count_dict):', len(user_count_dict.keys()))
    x_list = sorted(x_list)
    for money_type in user_count_lost_dict.keys():
        for reg_date in user_count_lost_dict[money_type].keys():
            value = 0
            if user_count_lost_dict[money_type][reg_date] > 0 and user_count_lost_user_dict[money_type].setdefault(reg_date,0)>0 :
                value = float(user_count_lost_dict[money_type][reg_date])/(user_count_lost_user_dict[money_type].setdefault(reg_date,0))
            user_count_lost_dict[money_type][reg_date] = value

    for money_type in user_count_remain_ratio_dict.keys():
        for reg_date in user_count_remain_ratio_dict[money_type].keys():
            value = 0
            if user_count_remain_ratio_dict[money_type][reg_date] > 0 and user_count_dict[money_type].setdefault(reg_date,0)>0 :
                value = float(user_count_remain_ratio_dict[money_type][reg_date])/user_count_dict[money_type][reg_date]
            user_count_remain_ratio_dict[money_type][reg_date] = value

    res_dict = dict()
    res_dict['data_dict'] = user_count_dict
    res_dict['X_list'] = x_list
    res_dict['Y_list'] = y_list
    res_dict['Y_trans'] = y_trans
    res_dict['default_value'] = ''
    res_dict['head_name'] = '注册用户按付费分层'
    res_dict['note'] = ''

    res_dict_remain = dict()
    res_dict_remain['data_dict'] = user_count_remain_dict
    res_dict_remain['X_list'] = x_list
    res_dict_remain['Y_list'] = y_list
    res_dict_remain['Y_trans'] = y_trans
    res_dict_remain['default_value'] = ''
    res_dict_remain['head_name'] = '付费段留存人数'
    res_dict_remain['note'] = ''

    res_dict_remain_ratio = dict()
    res_dict_remain_ratio['data_dict'] = user_count_remain_ratio_dict
    res_dict_remain_ratio['X_list'] = x_list
    res_dict_remain_ratio['Y_list'] = y_list
    res_dict_remain_ratio['Y_trans'] = y_trans
    res_dict_remain_ratio['default_value'] = ''
    res_dict_remain_ratio['head_name'] = '付费段留存率'
    res_dict_remain_ratio['note'] = ''

    res_dict_lost = dict()
    res_dict_lost['data_dict'] = user_count_lost_user_dict
    res_dict_lost['X_list'] = x_list
    res_dict_lost['Y_list'] = y_list
    res_dict_lost['Y_trans'] = y_trans
    res_dict_lost['default_value'] = ''
    res_dict_lost['head_name'] = '付费段流失人数'
    res_dict_lost['note'] = ''

    res_dict_lost_life = dict()
    res_dict_lost_life['data_dict'] = user_count_lost_dict
    res_dict_lost_life['X_list'] = x_list
    res_dict_lost_life['Y_list'] = y_list
    res_dict_lost_life['Y_trans'] = y_trans
    res_dict_lost_life['default_value'] = ''
    res_dict_lost_life['head_name'] = '付费段流失用户生命周期'
    res_dict_lost_life['note'] = ''

    return [res_dict, res_dict_remain, res_dict_remain_ratio, res_dict_lost, res_dict_lost_life]


def _money_trans(money_list):
    y_trans = dict()
    y_trans[0] = '<=' + str(money_list[0])
    for i in range(1, len(money_list)):
        y_trans[i] = str(money_list[i-1]) + "~" + str(money_list[i])
    y_trans[len(money_list)] = '>=' + str(money_list[len(money_list)-1])
    return y_trans

def _get_money_type(money, type_list, currency_rate):
    if len(type_list) == 0:
        return 0
    else:
        money_new = money * currency_rate
        if money_new <= type_list[0]:
            return 0
        for i in range(1,len(type_list)):
            if type_list[i-1] < money_new <= type_list[i]:
                return i
        return len(type_list)





