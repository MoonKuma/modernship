#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : pay_motivation.py
# @Author: MoonKuma
# @Date  : 2019/2/14
# @Desc  : 付费激励，即每日各原先档位的用户的占比，以及他们当日的付费率，和当日付费用户的平均金额


"""
# SQL example as below
select date,uid,ifnull((select ceil(sum(money/100)) from stat_pay.pay_syn_day where uid=c.uid
and date<c.date),0) as money,ifnull((select ceil(sum(money/100)) from stat_pay.pay_syn_day
where uid=c.uid and date=c.date),0) as money_today from user_active_openid_2018 as c where
date between '2018-12-01' and '2018-12-10' limit 100;
"""


from conf.ConfParameters import ConfParameters
from util.EasyMysql import EasyMysql
from util.DateList import DateList


def pay_motivation(input_dict, money_type_list):
    conf = ConfParameters()
    easy_sql = EasyMysql()
    easy_date = DateList()
    currency_rate = conf.current_rate
    mysql_conf = conf.mysql_conf
    stat_base = mysql_conf['stat_base']
    stat_pay = mysql_conf['stat_pay']
    stat_userreg = mysql_conf['stat_userreg']
    user_active_openid = mysql_conf['user_active_openid']

    # argv
    x_list = list()
    y_trans = dict()
    money_list = list()
    y_list = [0]
    if len(money_type_list) > 0:
        money_list = sorted(list(money_type_list))
        y_trans = _money_trans(money_list)
        y_list = list(range(0, len(money_list) + 1))
    print('money_list:', money_list)
    print('currency_rate:', currency_rate)
    # input dict
    date_list = sorted(list(input_dict['date_list']))
    where_channel_zone = easy_sql.combine_where_clause(input_dict)
    cursor = input_dict['cursor']
    where_date_between = ' date between \'' + date_list[0] + '\' and \'' + date_list[len(date_list)-1] + '\' ' + where_channel_zone
    sql = 'select date,uid,ifnull((select ceil(sum(money/100)) from '+stat_pay+'.pay_syn_day where uid=c.uid and date<c.date),0) as money, ifnull((select ceil(sum(money/100)) from '+stat_pay+'.pay_syn_day where uid=c.uid and date=c.date),0) as money_today from '+stat_base+'.'+user_active_openid+' as c where '+where_date_between+' '
    print(sql)
    cursor.execute(sql)
    all_data = cursor.fetchall()
    user_dict = dict()
    pay_dict = dict()
    money_dict = dict()
    if all_data:
        for rec in all_data:
            date = str(rec[0])
            uid = rec[1]
            money = int(rec[2])
            money_today = int(rec[3])
            money_type = _get_money_type(money, money_list, currency_rate)
            if money_type not in user_dict.keys():
                user_dict[money_type] = dict()
            if money_type not in money_dict.keys():
                money_dict[money_type] = dict()
            if money_type not in pay_dict.keys():
                pay_dict[money_type] = dict()
            user_dict[money_type][date] = user_dict[money_type].setdefault(date, 0) + 1
            if money_today > 0:
                pay_dict[money_type][date] = pay_dict[money_type].setdefault(date, 0) + 1
                money_dict[money_type][date] = money_dict[money_type].setdefault(date, 0) + money_today

    print('[Check1]len(user_dict):', len(user_dict.keys()))
    x_list = date_list

    res_dict = dict()
    res_dict['data_dict'] = user_dict
    res_dict['X_list'] = x_list
    res_dict['Y_list'] = y_list
    res_dict['Y_trans'] = y_trans
    res_dict['default_value'] = ''
    res_dict['head_name'] = '活跃用户付费分段'
    res_dict['note'] = '*为避免当前日的付费金额造成的影响，按<当前日的付费金额进行分段'

    res_pay_users = dict()
    res_pay_users['data_dict'] = pay_dict
    res_pay_users['X_list'] = x_list
    res_pay_users['Y_list'] = y_list
    res_pay_users['Y_trans'] = y_trans
    res_pay_users['default_value'] = ''
    res_pay_users['head_name'] = '各付费段当日付费人数'
    res_pay_users['note'] = ''

    res_pay_money = dict()
    res_pay_money['data_dict'] = money_dict
    res_pay_money['X_list'] = x_list
    res_pay_money['Y_list'] = y_list
    res_pay_money['Y_trans'] = y_trans
    res_pay_money['default_value'] = ''
    res_pay_money['head_name'] = '各付费段当日付费金额'
    res_pay_money['note'] = ''

    # print(res_dict)
    return [res_dict, res_pay_users, res_pay_money]




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