#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : 
# @Author: mjf
# @Date  : 2019/1/3 11:30
# @Desc  :
import MySQLdb
import xlwt
import util.EasyXls as EasyXls
import conf.ConfParameters as ConfParameters
from util.WriteStandardForm import write_standard_form
from util.is_valid_data import is_legal_input
from util.EasyMysql import EasyMysql
from util.DateList import DateList
import datetime
import sys


def renratio(input_dict,stat_active_name,stat_reg_name,stat_pay_name,currency_rate, *args):
    is_legal_input(input_dict)
    easy_sql = EasyMysql()
    easy_date = DateList()
    cursor = input_dict['cursor']
    where_clause_main = easy_sql.combine_where_clause(input_dict)
    #[0,100,500,20,30,40,60]
    y_list = sorted(list(args))
    x_list = [0, 1, 2, 6, 14, 29, 59, 89]
    result_dict = dict()
    get_dict = dict()
    put_dict = dict()
    # 当日有多少人  建造字典
    get_dict['total'] = dict()
    put_dict['total'] = dict()
    for j in range(0, len(y_list)):
        get_dict[y_list[j]] = dict()
        put_dict[y_list[j]] = dict()
    #获得某段时间内的活跃人数
    if len(input_dict['date_list'])!=0:
        min_time_stamp = min(input_dict['date_list'])
        max_time_stamp = max(input_dict['date_list'])
    print(max_time_stamp)
    #考察充值情况 距离开服x天
    pay_dict=dict()
    sql_cmd_pay = 'select uid,sum(money/100)*'+str(currency_rate)+' as money from '+stat_pay_name+'.pay_syn_day where date<=\''+max_time_stamp+'\'' +where_clause_main+' group by uid;'
    print(sql_cmd_pay)
    cursor.execute(sql_cmd_pay)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            pay_dict[rec[0]]=rec[1]


    for date in input_dict['date_list']:
        where_clause =  ' select uid from ( select uid from ' + stat_reg_name + '.user_register0 where date=\''+date+ '\''+where_clause_main
        for i in range(1, 10):
            where_clause = where_clause + ' union all select uid from ' + stat_reg_name + '.user_register' + str(i) + ' where date=\''+date+ '\' '+where_clause_main
        where_clause = where_clause + ')a '
        sql_cmd_regdate = where_clause
        print(sql_cmd_regdate)
        total_dict = dict()
        cursor.execute(sql_cmd_regdate)
        all_data = cursor.fetchall()
        if all_data:
            for rec in all_data:
                total_dict[rec[0]] = dict()
                # total_dict[rec[0]]['regdate']= str(rec[1])
                total_dict[rec[0]]['money'] = pay_dict.setdefault(rec[0],0)

        # print(total_dict)
        for i in range(0,len(x_list)):
            time_stamp = addtime(date,x_list[i]).strftime('%Y%m%d')
            if hastable(cursor,'user_active_'+time_stamp,stat_active_name):
                # print(time_stamp)
                if time_stamp <= addtime(max_time_stamp,0).strftime('%Y%m%d'):
                    sql_str = 'select uid from '+stat_active_name+'.user_active_' + time_stamp +where_clause_main+';'
                    cursor.execute(sql_str)
                    # print(sql_str)
                    all_data = cursor.fetchall()
                    if all_data:
                        for rec in all_data:
                            if total_dict.has_key(rec[0]):
                                if rec[0] in total_dict.keys():
                                    total_dict[rec[0]][x_list[i]]=1
                                else:
                                    total_dict[rec[0]][x_list[i]]=0
                else:
                    if total_dict.has_key(rec[0]):
                        total_dict[rec[0]][x_list[i]]=0
            else:
                if total_dict.has_key(rec[0]):
                    total_dict[rec[0]][x_list[i]] = 0


        # print(total_dict)
        for i in x_list:
            for k in total_dict.keys():
                get_dict['total'][i] = get_dict.setdefault('total',dict()).setdefault(i,0)+ total_dict[k].setdefault(i,0)

        for j in range(0,len(y_list)):
            if j == 0:
                for i in x_list:
                    for k in total_dict.keys():
                         if total_dict[k]['money']<=int(y_list[j]):
                            get_dict[y_list[j]][i] = get_dict.setdefault(y_list[j],dict()).setdefault(i,0)+total_dict[k].setdefault(i,0)
            elif j!=0 and j<=len(y_list)-1:
                for i in x_list:
                    for k in total_dict.keys():
                         if int(y_list[j-1])<total_dict[k]['money']<=int(y_list[j]):
                            get_dict[y_list[j]][i] = get_dict.setdefault(y_list[j],dict()).setdefault(i,0)+total_dict[k].setdefault(i,0)

        for i in x_list:
            for k in total_dict.keys():
                 if total_dict[k]['money']>int(y_list[len(y_list)-1]):
                    get_dict[str(y_list[len(y_list)-1])+'+'][i] = get_dict.setdefault(str(y_list[len(y_list)-1])+'+',dict()).setdefault(i,0)+total_dict[k].setdefault(i,0)

    # 换成占比
    for key in get_dict.keys():
        for keyin in get_dict[key].keys():
            if keyin==x_list[0]:
                put_dict.setdefault(key,dict()).setdefault(keyin,get_dict[key][keyin])
            else:
                put_dict.setdefault(key,dict()).setdefault(keyin,round(float(get_dict[key][keyin])/get_dict[key][x_list[0]],2))
                # put_dict.setdefault(key, dict()).setdefault(keyin, round(get_dict[key][keyin], 2))

    res_dict = dict()
    # res_dict['data_dict'] = get_dict
    res_dict['data_dict'] = put_dict
    res_dict['X_list'] = x_list
    res_dict['X_trans'] = dict(zip(x_list,list(map(lambda x:"第"+str(x+1)+"日留存",x_list))))
    res_dict['Y_list'] = ['total'] + y_list+[str(y_list[len(y_list)-1])+'+']
    res_dict['Y_trans'] = dict()
    for j in range(0,len(y_list)):
        if j==0:
            res_dict['Y_trans'][y_list[j]]='0--'+str(y_list[j])
        elif j>0 and j<=len(y_list)-1:
            res_dict['Y_trans'][y_list[j]] = str(y_list[j-1])+'--'+str(y_list[j])
    res_dict['Y_trans'][str(y_list[len(y_list)-1])+'+'] = str(y_list[len(y_list)-1])+'以上'


    res_dict['default_value'] = 0
    res_dict['head_name'] = '付费段的留存人数'
    res_dict['note'] = '付费段的留存情况'
    return res_dict


def addtime(date_str,interval):
    dateplus = datetime.datetime.strptime(date_str,"%Y-%m-%d")+datetime.timedelta(days=interval)
    return dateplus

def hastable(cursor,tablename,base_name):
    table_dict=dict()
    sql_str = 'select table_name from INFORMATION_SCHEMA.TABLES where TABLE_SCHEMA=\"'+base_name+'\";'
    cursor.execute(sql_str)
    all_data = cursor.fetchall()
    if all_data:
        for rec in all_data:
            table_dict[rec[0]]=1
    return table_dict.has_key(tablename)

