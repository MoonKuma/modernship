#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : UserDiamond.py
# @Author: MoonKuma
# @Date  : 2018/9/18
# @Desc  : Check vip based, user active, diamond cost and diamond remain from user_diamond


import util.EasyXls as EasyXls
import conf.ConfParameters as ConfParameters
import MySQLdb
import xlwt


class UserDiamond:
    def __init__(self):
        # conf path
        self.conf_path = ConfParameters.ConfParameters().conf_path
        # initial mysql-db
        mysql_para = ConfParameters.ConfParameters().mysql_conf
        self.db = MySQLdb.connect(mysql_para['ip'], mysql_para['users'], mysql_para['password'], mysql_para['stat_base'])
        self.cursor = self.db.cursor()
        # initial xls writer
        self.wbk = xlwt.Workbook()
        self.xls_writer = EasyXls.EasyXls()
        self.style = xlwt.XFStyle()
        self.style.borders = self.xls_writer.borders
        # local parameter
        self.start_date = '2018-06-01'
        self.end_date = '2018-09-17'

    def __select_table_data(self):
        data_dict = dict()  # {date|vip: {cost:cost, last:last, active:active}}
        vip_list = list()
        date_list = list()
        where_str = ' date between \'' + self.start_date + '\' and \'' + self.end_date + '\' '
        sql_str = 'select vip_level, date, ceil(sum(cost_diamond+cost_cash)/count(distinct uid)), ceil(sum(last_diamond)/count(distinct uid)), count(distinct uid) from user_diamond where' + where_str + ' and uid not in (select uid from user_ban_statistic) group by vip_level, date'
        print sql_str
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                vip = str(rec[0])
                if vip not in vip_list:
                    vip_list.append(vip)
                date = str(rec[1])
                if date not in date_list:
                    date_list.append(date)
                avg_cost = int(rec[2])
                avg_last = int(rec[3])
                count_uid = int(rec[4])
                key = date + '|' + vip
                if key not in data_dict.keys():
                    data_dict[key] = dict()
                    data_dict[key]['avg_cost'] = avg_cost
                    data_dict[key]['avg_last'] = avg_last
                    data_dict[key]['count_uid'] = count_uid
        vip_list = sorted(vip_list, key=lambda x: int(x))
        date_list = sorted(date_list)
        return [vip_list, date_list, data_dict]

    def __write_xls_inside_sheet(self, data_list, table_type, head_name, sheet, line_num):
        [vip_list, date_list, data_dict] = data_list
        head_line = [head_name]
        for date in date_list:
            head_line.append(date)
        self.xls_writer.insert_xls_style(head_line, sheet, line_num, self.style)
        for key_name in vip_list:
            data_line = [key_name]
            for date in date_list:
                key = date + '|' + key_name
                if key not in data_dict.keys():
                    data_line.append(' ')
                    continue
                if key in data_dict.keys():
                    value = data_dict[key].setdefault(table_type, ' ')
                    data_line.append(value)
            self.xls_writer.insert_xls_style(data_line, sheet, line_num, self.style)
        return 1

    def write_xls_sheet(self):
        data_list = self.__select_table_data()
        sheet_name = '钻石消耗表'
        sheet = self.xls_writer.new_sheet(sheet_name, self.wbk)
        sheet.col(0).width = 256 * 20
        line_num = [0]
        name_list = [sheet_name]
        self.xls_writer.insert_xls_style(name_list, sheet, line_num, self.style)
        line_num[0] = line_num[0] + 2
        head_name = '人均钻石消耗'
        table_type = 'avg_cost'
        self.__write_xls_inside_sheet(data_list, table_type, head_name, sheet, line_num)
        line_num[0] = line_num[0] + 2
        head_name = '人均钻石留存'
        table_type = 'avg_last'
        self.__write_xls_inside_sheet(data_list, table_type, head_name, sheet, line_num)
        line_num[0] = line_num[0] + 2
        head_name = '活跃人数'
        table_type = 'count_uid'
        self.__write_xls_inside_sheet(data_list, table_type, head_name, sheet, line_num)
        return 1

    def execute(self):
        file_name = ConfParameters.ConfParameters().save_path + 'User_diamond_' + self.start_date + '-' + self.end_date + '.xls'
        self.write_xls_sheet()
        self.wbk.save(file_name)
        self.db.close()


# test main
if __name__ == '__main__':
    UserDiamond().execute()