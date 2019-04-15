#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : PeriodicVip.py
# @Author: MoonKuma
# @Date  : 2018/10/31
# @Desc  : Check user's vip level at each compute cycle

import util.ReadTable as ReadTable
import util.EasyXls as EasyXls
import util.EasyMysql as EasyMysql
import util.DateList as DateList
from util.WriteStandardForm import write_standard_form
import conf.ConfParameters as ConfParameters
import MySQLdb
import xlwt
import collections


class PeriodicVip(object):
    def __init__(self):
        # environment
        self.conf_path = ConfParameters.ConfParameters().conf_path
        # initialize
        # # mysql
        mysql_para = ConfParameters.ConfParameters().mysql_conf
        self.db = MySQLdb.connect(mysql_para['ip'], mysql_para['users'], mysql_para['password'],
                                  mysql_para['stat_pay'])
        self.cursor = self.db.cursor()
        self.easy_mysql = EasyMysql.EasyMysql()
        # # xls
        self.wbk = xlwt.Workbook()
        self.xls_writer = EasyXls.EasyXls()
        self.style = xlwt.XFStyle()
        self.style.borders = self.xls_writer.borders
        # # others
        self.easy_date = DateList.DateList()
        # local
        self.cycle = 7
        vip_file_name = self.conf_path + 'Vip_Money.txt'
        self.vip_dict = self.__get_vip_table(vip_file_name)

    def get_periodic_vip(self, uid_list, start_date, end_date, *cycle):
        if len(cycle) > 0:
            self.__reset_cycle(cycle[0])
        pay_dict = self.__get_user_pay(uid_list, start_date, end_date)
        cycle_dict = self.__get_cycle_table(start_date, end_date)
        vip_dict = self.vip_dict
        # data_dict
        tmp_data_dict_money = dict()  # {cycle:{uid:payment}}
        for date in pay_dict.keys():
            where_cycle = self.__where_data_in_table(date, cycle_dict)
            if where_cycle not in tmp_data_dict_money.keys():
                tmp_data_dict_money[where_cycle] = dict()
            for uid in pay_dict[date].keys():
                tmp_data_dict_money[where_cycle][uid] = tmp_data_dict_money[where_cycle].setdefault(uid, 0) + pay_dict[date][uid]
        # print(tmp_data_dict_money.keys())
        # print(tmp_data_dict_money)
        # load standard res dict
        # use standard return (see modernship_util.modernship_util_API.xls)
        res_dict_money = dict()  # res_dict money version
        res_dict_vip = dict()  # res_dict vip version
        Y_list = ['StartTime', 'EndTime']
        Y_list = Y_list + uid_list
        Y_trans = {'StartTime': '开始时间', 'EndTime': '结束时间'}
        X_list = list()
        for cycle in cycle_dict.keys():
            X_list.append(cycle)
        # print(X_list)
        X_trans = dict()
        for Y in X_list:
            X_trans[Y] = '第' + str(Y) + '周期'
        data_dict_money = dict()
        data_dict_vip = dict()

        def add_start_end_date(data_dict, cycle_dict, Y_list):
            data_dict['StartTime'] = dict()
            data_dict['EndTime'] = dict()
            for y in Y_list:
                data_dict['StartTime'][y] = cycle_dict[y]
                data_dict['EndTime'][y] = self.easy_date.add_date(cycle_dict[y], self.cycle)
        add_start_end_date(data_dict_money, cycle_dict, X_list)
        add_start_end_date(data_dict_vip, cycle_dict, X_list)
        for uid in uid_list:
            if uid not in data_dict_money.keys():
                data_dict_money[uid] = dict()
            if uid not in data_dict_vip.keys():
                data_dict_vip[uid] = dict()
            for cycle in X_list:
                if cycle in tmp_data_dict_money.keys():
                    value = tmp_data_dict_money[cycle].setdefault(uid, 0)  # get money
                else:
                    value = 0
                data_dict_money[uid][cycle] = value
                vip = int(self.__where_data_in_table(value, vip_dict))
                data_dict_vip[uid][cycle] = vip
        # res1
        res_dict_money['head_name'] = '按付费金额'
        res_dict_money['X_list'] = X_list
        res_dict_money['X_trans'] = X_trans
        res_dict_money['Y_list'] = Y_list
        res_dict_money['Y_trans'] = Y_trans
        res_dict_money['default_value'] = 0
        res_dict_money['data_dict'] = data_dict_money
        # res2
        res_dict_vip['head_name'] = '按折算VIP'
        res_dict_vip['X_list'] = X_list
        res_dict_vip['X_trans'] = X_trans
        res_dict_vip['Y_list'] = Y_list
        res_dict_vip['Y_trans'] = Y_trans
        res_dict_vip['default_value'] = 0
        res_dict_vip['data_dict'] = data_dict_vip

        return [res_dict_money, res_dict_vip]

    # execute
    def execute(self, uid_list, start_date, end_date, *cycle):
        file_name = ConfParameters.ConfParameters().save_path + 'Periodic_Vip_' + start_date + '-' + end_date + '.xls'
        if len(cycle) > 0:
            [res_dict_money, res_dict_vip] = self.get_periodic_vip(uid_list, start_date, end_date, cycle[0])
        else:
            [res_dict_money, res_dict_vip] = self.get_periodic_vip(uid_list, start_date, end_date)

        msg = '*周期：' + str(str(self.cycle)) + '天'
        new_sheet = self.xls_writer.new_sheet('周期付费计算表-按实际付费金额', self.wbk)
        new_sheet.col(0).width = 256 * 20
        line_num = [0]
        write_standard_form(res_dict_money, new_sheet, line_num, self.style)
        self.xls_writer.insert_xls([msg], new_sheet, line_num)
        new_sheet1 = self.xls_writer.new_sheet('周期付费计算表-按折算VIP', self.wbk)
        new_sheet1.col(0).width = 256 * 20
        line_num1 = [0]
        write_standard_form(res_dict_vip, new_sheet1, line_num1, self.style)
        self.xls_writer.insert_xls([msg], new_sheet1, line_num1)
        self.wbk.save(file_name)
        self.db.close()

    def get_top_100_uid(self, start_date, end_date):
        uid_list = list()
        sql_cmd = 'select uid from pay_syn_day where date between \'' + start_date + '\' and  \'' + end_date + '\' group by uid order by sum(money) desc limit 100'
        print sql_cmd
        self.cursor.execute(sql_cmd)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                uid = str(rec[0])
                if uid not in uid_list:
                    uid_list.append(uid)
        return uid_list

    def get_last_cycle_above_x(self, start_date, end_date, limit_x):
        uid_list = list()
        sql_cmd = 'select uid from pay_syn_day where date between \'' + start_date + '\' and  \'' + end_date + '\' group by uid having sum(money/100)>=' + str(limit_x) + ' order by sum(money)'
        print sql_cmd
        self.cursor.execute(sql_cmd)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                uid = str(rec[0])
                if uid not in uid_list:
                    uid_list.append(uid)
        return uid_list

    # private method
    def __reset_cycle(self, new_cycle):
        self.cycle = int(new_cycle)

    def __get_cycle_table(self, start_date, end_date):
        cycle_dict = collections.OrderedDict()  # {c1:date1} # use min date
        add_value = self.cycle + 1
        cycle_num = 1
        current_date = start_date
        while current_date < end_date:
            cycle_dict[cycle_num] = current_date
            current_date = self.easy_date.add_date(current_date, add_value)
            cycle_num += 1
        return cycle_dict

    def __get_vip_table(self, file_name):
        vip_dict = collections.OrderedDict()  # {vip:money} # use min money
        file_table = ReadTable.ReadTable(file_name).read_table_file_coupled()
        for vip in file_table.keys():
            value = int(file_table[vip]['money'])
            vip_dict[vip] = value
        return vip_dict

    def __where_data_in_table(self, data, ordered_table):  # comparing str when search date, int when search vip, require ordered dict
        target_key = ordered_table.keys()[0]
        for key in ordered_table.keys():
            if data >= ordered_table[key]:
                target_key = key
                continue
            else:
                break
        return target_key

    def __get_user_pay(self, uid_list, start_date, end_date):
        pay_dict = dict()  # {date:{uid:payment}}
        uid_str = self.easy_mysql.sql_value_str(uid_list)
        sql_cmd = 'select date,uid,ceil(sum(money/100)) from pay_syn_day where date between \'' + start_date + '\' and \'' + end_date + '\' and uid in (' + uid_str + ') group by date,uid'
        print sql_cmd
        self.cursor.execute(sql_cmd)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                date = str(rec[0])
                uid = str(rec[1])
                money = int(rec[2])
                if date not in pay_dict.keys():
                    pay_dict[date] = dict()
                pay_dict[date][uid] = money
        return pay_dict


# test main
if __name__ == '__main__':
    period_vip = PeriodicVip()
    start_date1 = '2018-03-28'
    end_date1 = '2018-10-30'
    # # test
    # uid_list1 = ['72425045669983143', '72382022982645491', '72510872001514782', '72425144454224194']
    # # top_100
    uid_list = period_vip.get_top_100_uid(start_date1, end_date1)
    # # two week
    # start_date1 = '2018-10-14'
    # end_date1 = '2018-10-30'
    # uid_window1 = '2018-10-14'
    # uid_window2 = '2018-10-21'
    # x_limit = 1000
    # uid_list = period_vip.get_last_cycle_above_x(uid_window1,uid_window2,x_limit)
    period_vip.execute(uid_list, start_date1, end_date1)
