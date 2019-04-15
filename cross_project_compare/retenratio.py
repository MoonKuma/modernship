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

    get_dict_list=list()
    for i in range(0, len(x_list)):
        get_dict_list.append(dict())
    # 当日有多少人  建造字典
    # get_dict['total'] = dict()
    # put_dict['total'] = dict()
    # for j in range(0, len(y_list)):
    #     get_dict[y_list[j]] = dict()
    #     put_dict[y_list[j]] = dict()
    #获得某段时间内的活跃人数
    if len(input_dict['date_list'])!=0:
        min_time_stamp = min(input_dict['date_list'])
        max_time_stamp = max(input_dict['date_list'])
    # print(max_time_stamp)
    #考察充值情况 距离开服x天
    pay_dict=dict()
    sql_cmd_pay = 'select uid,sum(money/100)*'+str(currency_rate)+' as money from '+stat_pay_name+'.pay_syn_day where date<=\''+max_time_stamp+'\'' +where_clause_main+' group by uid;'
    # print(sql_cmd_pay)
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
        # print(sql_cmd_regdate)
        total_dict = dict()
        cursor.execute(sql_cmd_regdate)
        all_data = cursor.fetchall()
        if all_data:
            for rec in all_data:
                total_dict[rec[0]] = dict()
                total_dict[rec[0]]['money'] = pay_dict.setdefault(rec[0],0)

        # print(total_dict)
        for i in range(0,len(x_list)):
            time_stamp = addtime(date,x_list[i]).strftime('%Y%m%d')
            if hastable(cursor,'user_active_'+time_stamp,stat_active_name):
                # print(time_stamp)
                if time_stamp <= addtime(max_time_stamp,0).strftime('%Y%m%d'):
                    sql_str = 'select uid from '+stat_active_name+'.user_active_' + time_stamp +' where 1 '+where_clause_main+';'
                    # print(sql_str)
                    cursor.execute(sql_str)
                    all_data = cursor.fetchall()
                    if all_data:
                        for rec in all_data:
                            if total_dict.has_key(rec[0]):
                                if rec[0] in total_dict.keys():
                                    total_dict[rec[0]][x_list[i]]=1
                                else:
                                    total_dict[rec[0]][x_list[i]]=0

        # print(total_dict)


        for i in range(0,len(x_list)):
            for k in total_dict.keys():
                if total_dict[k].has_key(x_list[i]):
                    get_dict_list[i]['total'][date] = get_dict_list[i].setdefault('total',dict()).setdefault(date,0)+ total_dict[k].setdefault(x_list[i],0)

            for j in range(0, len(y_list)):
                if j == 0:
                    for k in total_dict.keys():
                        if total_dict[k]['money'] <= int(y_list[j]):
                            if total_dict[k].has_key(x_list[i]):
                                get_dict_list[i][y_list[j]][date] = get_dict_list[i].setdefault(y_list[j], dict()).setdefault(date, 0) + \
                                                     total_dict[k].setdefault(x_list[i], 0)
                elif j != 0 and j <= len(y_list) - 1:
                    for k in total_dict.keys():
                        if int(y_list[j - 1]) < total_dict[k]['money'] <= int(y_list[j]):
                            if total_dict[k].has_key(x_list[i]):
                                get_dict_list[i][y_list[j]][date] = get_dict_list[i].setdefault(y_list[j], dict()).setdefault(date, 0) + \
                                                     total_dict[k].setdefault(x_list[i], 0)


            for k in total_dict.keys():
                if total_dict[k]['money'] > int(y_list[len(y_list) - 1]):
                    if total_dict[k].has_key(x_list[i]):
                        get_dict[str(y_list[len(y_list) - 1]) + '+'][date] = get_dict.setdefault(str(y_list[len(y_list) - 1]) + '+', dict()).setdefault(date, 0) + total_dict[k].setdefault(i,0)


    # print(get_dict_list)

    put_dict_list=[]
    for i in range(0, len(get_dict_list)):
        put_dict = dict()
        for key in get_dict_list[i].keys():
            for keyin in get_dict_list[i][key].keys():
                if i == 0:
                    put_dict.setdefault(key, dict()).setdefault(keyin, get_dict_list[i][key][keyin])
                else:
                    put_dict.setdefault(key, dict()).setdefault(keyin, round(float(get_dict_list[i][key][keyin]) / get_dict_list[0][key][keyin], 2))
        put_dict_list.append(put_dict)

    # print(put_dict_list)

    res_dict_list=[]
    for i in range(0,len(put_dict_list)):
        res_dict = dict()
        # res_dict['data_dict'] = get_dict
        res_dict['data_dict'] = put_dict_list[i]
        res_dict['X_list'] = sorted(input_dict['date_list'])
        # res_dict['X_trans'] = dict(zip(x_list,list(map(lambda x:"第"+str(x+1)+"日留存",x_list))))
        res_dict['Y_list'] = ['total'] + y_list+[str(y_list[len(y_list)-1])+'+']
        res_dict['Y_trans'] = dict()
        for j in range(0,len(y_list)):
            if j==0:
                res_dict['Y_trans'][y_list[j]]='0--'+str(y_list[j])
            elif j>0 and j<=len(y_list)-1:
                res_dict['Y_trans'][y_list[j]] = str(y_list[j-1])+'--'+str(y_list[j])
        res_dict['Y_trans'][str(y_list[len(y_list)-1])+'+'] = str(y_list[len(y_list)-1])+'以上'


        res_dict['default_value'] = ''
        res_dict['head_name'] = '第'+str(x_list[i]+1)+'日留存情况'
        res_dict['note'] = '付费段的留存情况'
        res_dict_list.append(res_dict)
    return res_dict_list


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

