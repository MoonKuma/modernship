#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : NewUserLtvByDate.py
# @Author: MoonKuma
# @Date  : 2018/10/10
# @Desc  : Daily user increase, and their ltv

import util.EasyXls as EasyXls
import util.EasyMysql as EasyMysql
import conf.ConfParameters as ConfParameters
import MySQLdb
import xlwt


class NewUserLtvByDate(object):

    def __init__(self, start_date, end_date, *channel):
        # conf path
        self.conf_path = ConfParameters.ConfParameters().conf_path
        # initial mysql-db
        self.mysql_para = ConfParameters.ConfParameters().mysql_conf
        self.stat_base = self.mysql_para['stat_base']
        self.db = None  # such is initiate not in constructor but when actually used to ensure db get closed after connect
        self.cursor = None
        self.easy_sql = EasyMysql.EasyMysql()
        # initial xls writer
        self.wbk = xlwt.Workbook()
        self.xls_writer = EasyXls.EasyXls()
        self.style = xlwt.XFStyle()
        self.style.borders = self.xls_writer.borders
        # local parameter
        self.start_date = start_date
        self.end_date = end_date
        self.channel = ['-1']
        self.zone = ['-1']
        self.period_limit = '30'
        if len(channel) > 0:
            self.channel = list(channel[0])
        # self.date_list = DateList.DateList().get_date_list(self.start_date, self.end_date)

    def __select_sql_data(self, table_name, *query_type):  # such functions are no longer exposed to outsides
        # table_name : user_reten_pay, user_reten_pay_openid
        # return : [reg_date_list,check_date_list,{reg_date|check_date:money}, {reg_date: reg_users}]
        reg_date_list = list()
        check_date_list = list()
        data_dict = dict()
        reg_user_dict = dict()
        #
        where_clause = ' where period<=' + str(self.period_limit) + ' and date between \'' + self.start_date + '\' and \'' + self.end_date + '\''
        if self.channel[0] != '-1':
            channel_str = self.easy_sql.sql_value_str(self.channel)
            where_clause += ' and channel in (' + channel_str + ') '
        if self.zone[0] != '-1':
            zone_str = self.easy_sql.sql_value_str(self.zone)
            where_clause += ' and zoneid in (' + zone_str + ') '
        sql_str = 'select concat(date),period,concat(date_add(date, interval period day)),sum(count),ceil(sum(money/100)) from ' + table_name + where_clause + ' group by date,period;'
        print(sql_str)
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                reg_date = rec[0]
                check_date = str(rec[1])
                date_mark = rec[2]
                user_count = rec[3]
                money = rec[4]
                if reg_date not in reg_date_list:
                    reg_date_list.append(reg_date)
                if check_date not in check_date_list:
                    check_date_list.append(check_date)
                key = reg_date + '|' + check_date
                if key not in data_dict.keys():
                    if len(query_type) == 0 or query_type[0] == 'ltv':
                        data_dict[key] = int(money)
                    elif query_type[0] == 'reten':
                        data_dict[key] = int(user_count)
                if reg_date == date_mark:
                    reg_user_dict[reg_date] = int(user_count)
        reg_date_list = sorted(reg_date_list)
        check_date_list = sorted(check_date_list, key=lambda x: int(x))
        log = 'Sql query finished, with len(reg_date_list): ' + str(len(reg_date_list)) + ', len(check_date_list):' + str(len(check_date_list)) + ', len(data_dict.keys()):' + str(len(data_dict.keys())) + ', len(reg_user_dict.keys()):' + str(len(reg_user_dict.keys()))
        print(log)
        return [reg_date_list, check_date_list, data_dict, reg_user_dict]

    def __write_ltv_sheet(self, table_name, sheet_name, *query_type):
        # sql data
        [reg_date_list, check_date_list, data_dict, reg_user_dict] = self.__select_sql_data(table_name, *query_type)
        # write sheet
        sheet = self.xls_writer.new_sheet(sheet_name, self.wbk)
        line_num = [0]
        sheet.col(0).width = 256 * 20
        # title
        name_list = [sheet_name]
        self.xls_writer.insert_xls_style(name_list, sheet, line_num, self.style)
        line_num[0] = line_num[0] + 2
        # head
        head_line = ['注册日期', '注册人数']
        for date in check_date_list:
            date_str = '第' + str(int(date)+1) + '日'
            head_line.append(date_str)
        self.xls_writer.insert_xls_style(head_line, sheet, line_num, self.style)
        # content
        for reg_date in reg_date_list:
            data_line = list()
            data_line.append(reg_date)
            reg_user = reg_user_dict.setdefault(reg_date, 0)
            data_line.append(reg_user)
            if reg_user == 0:
                reg_user = 1
            for check_date in check_date_list:
                key = reg_date + '|' + check_date
                if key not in data_dict.keys():
                    data_line.append('')
                    continue
                ltv = round(data_dict.setdefault(key, 0)/float(reg_user), 2)
                data_line.append(ltv)
            self.xls_writer.insert_xls_style(data_line, sheet, line_num, self.style)

    def execute(self, file_name):
        # file_name = ConfParameters.ConfParameters().save_path + 'User_diamond_' + self.start_date + '-' + self.end_date + '.xls'
        self.db = MySQLdb.connect(self.mysql_para['ip'], self.mysql_para['users'], self.mysql_para['password'],
                                  self.mysql_para['stat_base'])
        self.cursor = self.db.cursor()
        try:
            self.zone = [10001]
            self.channel = [1045]
            self.__write_ltv_sheet('user_reten_pay', '1服UID新增按日留存', 'reten')
            self.wbk.save(file_name)
        finally:
            self.db.close()


# Main
if __name__ == '__main__':
    start = '2018-03-28'
    end = '2018-05-18'

    channel_name = 'IOS'
    save_name = ConfParameters.ConfParameters().save_path + 'NewUserLtvRetenByDate_' + start + '_' + end + '_' + channel_name + '.xls'
    # NewUserLtvByDate(start, end, channel_id).execute(save_name)
    NewUserLtvByDate(start, end).execute(save_name)
