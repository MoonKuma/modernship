#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : user_return.py
# @Author: MoonKuma
# @Date  : 2019/2/14
# @Desc  : *定义回流： 当日活跃的用户中，去除新增用户，在最近X日只登陆过一次，记为当日的回流用户

"""
# SQL example as below
select uid,max(date),count(date),max(level),ifnull((select ceil(sum(money/100)) from stat_pay.pay_syn_day where
uid=c.uid and date<'2018-09-01' group by uid),0) as money from user_active_openid_2018 as c where date between
'2018-09-01' and '2018-09-10' and uid not in (select uid from ( select uid from stat_userreg.user_register0
where date between '2018-09-01' and '2018-09-10' union all select uid from stat_userreg.user_register1 where
date between '2018-09-01' and '2018-09-10' union all select uid from stat_userreg.user_register2 where date
between '2018-09-01' and '2018-09-10' union all select uid from stat_userreg.user_register3 where date between
'2018-09-01' and '2018-09-10' union all select uid from stat_userreg.user_register4 where date between '2018-09-01'
and '2018-09-10' union all select uid from stat_userreg.user_register5 where date between '2018-09-01' and
'2018-09-10' union all select uid from stat_userreg.user_register6 where date between '2018-09-01' and '2018-09-10'
union all select uid from stat_userreg.user_register7 where date between '2018-09-01' and '2018-09-10' union all
select uid from stat_userreg.user_register8 where date between '2018-09-01' and '2018-09-10' union all select uid
from stat_userreg.user_register9 where date between '2018-09-01' and '2018-09-10' )a) group by uid having
max(date)='2018-09-10' and count(date)=1 limit 10;
"""


from conf.ConfParameters import ConfParameters
from util.EasyMysql import EasyMysql
from util.DateList import DateList


def user_return(input_dict, money_type_list, between_days=7):  # money_type_list as reception of pay levels
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

    # compute day by day
    result_return_dict = dict()
    result_return_pay_dict = dict()
    result_return_money_dict = dict()
    for date in date_list:
        date_min = easy_date.add_date(date, -1*between_days)
        where_date_between = ' date between \'' + date_min + '\' and \'' + date + '\' ' + where_channel_zone
        where_date_lower = ' date < \'' + date_min + '\' ' + where_channel_zone
        where_date_eq = ' date = \'' + date + '\' ' + where_channel_zone
        sql = 'select uid,ifnull((select ceil(sum(money/100)) from '+stat_pay+'.pay_syn_day where uid=c.uid and '+where_date_lower+' group by uid),0) as money, ifnull((select ceil(sum(money/100)) from '+stat_pay+'.pay_syn_day where uid=c.uid and '+where_date_eq+' group by uid),0) as money from '+stat_base+'.'+user_active_openid+' as c where '+where_date_between+' and uid not in (select uid from ( select uid from '+stat_userreg+'.user_register0 where  '+where_date_between+'  union all select uid from '+stat_userreg+'.user_register1 where '+where_date_between+'  union all select uid from '+stat_userreg+'.user_register2 where '+where_date_between+'  union all select uid from '+stat_userreg+'.user_register3 where '+where_date_between+' union all select uid from '+stat_userreg+'.user_register4 where  '+where_date_between+' union all select uid from '+stat_userreg+'.user_register5 where  '+where_date_between+'  union all select uid from '+stat_userreg+'.user_register6 where  '+where_date_between+'  union all select uid from '+stat_userreg+'.user_register7 where  '+where_date_between+'  union all select uid from '+stat_userreg+'.user_register8 where  '+where_date_between+'  union all select uid from '+stat_userreg+'.user_register9 where  '+where_date_between+'  )a) group by uid having max(date)=\''+date+'\' and count(date)=1;'
        # print(sql)
        cursor.execute(sql)
        all_data = cursor.fetchall()
        if all_data:
            for rec in all_data:
                uid = rec[0]
                money = int(rec[1])
                money_today = int(rec[2])
                money_type = _get_money_type(money, money_list, currency_rate)
                if money_type not in result_return_dict.keys():
                    result_return_dict[money_type] = dict()
                if money_type not in result_return_pay_dict.keys():
                    result_return_pay_dict[money_type] = dict()
                if money_type not in result_return_money_dict.keys():
                    result_return_money_dict[money_type] = dict()
                if money_today > 0:
                    result_return_pay_dict[money_type][date] = result_return_pay_dict[money_type].setdefault(date, 0) + 1
                    result_return_money_dict[money_type][date] = result_return_money_dict[money_type].setdefault(date, 0) + money_today

                result_return_dict[money_type][date] = result_return_dict[money_type].setdefault(date, 0) + 1
    print('[Check1]len(result_return_dict):', len(result_return_dict.keys()))
    x_list = date_list

    res_dict = dict()
    res_dict['data_dict'] = result_return_dict
    res_dict['X_list'] = x_list
    res_dict['Y_list'] = y_list
    res_dict['Y_trans'] = y_trans
    res_dict['default_value'] = ''
    res_dict['head_name'] = '付费用户分段回流'
    res_dict['note'] = '*定义回流： ' + str(between_days) + '日前注册的用户，在最近的连续' + str(between_days-1) + '日都没有活跃，而当日活跃了，记为当日的回流用户'

    res_pay_users = dict()
    res_pay_users['data_dict'] = result_return_pay_dict
    res_pay_users['X_list'] = x_list
    res_pay_users['Y_list'] = y_list
    res_pay_users['Y_trans'] = y_trans
    res_pay_users['default_value'] = ''
    res_pay_users['head_name'] = '回归用户付费人数'
    res_pay_users['note'] = '*表1中回归人数中，在当日发生付费的人数'

    res_pay_money = dict()
    res_pay_money['data_dict'] = result_return_money_dict
    res_pay_money['X_list'] = x_list
    res_pay_money['Y_list'] = y_list
    res_pay_money['Y_trans'] = y_trans
    res_pay_money['default_value'] = ''
    res_pay_money['head_name'] = '回归用户付费金额'
    res_pay_money['note'] = '*表1中回归人数中，在当日发生付费的金额汇总'

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