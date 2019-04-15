#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : UserRetenVipLevelWriteXls.py
# @Author: MoonKuma
# @Date  : 2018/9/14
# @Desc  : Write xls files based on table created in UserRetenVipLevel

import MySQLdb
import xlwt
import conf.ConfParameters as ConfParameters
import util.EasyXls as EasyXls


class UserRetenVipLevelWriteXls:

    def __init__(self):
        # initial mysql-db
        mysql_para = ConfParameters.ConfParameters().mysql_conf
        self.db = MySQLdb.connect(mysql_para['ip'], mysql_para['users'], mysql_para['password'], mysql_para['stat_base'])
        self.cursor = self.db.cursor()
        # initial xls writer
        self.wbk = xlwt.Workbook()
        self.xls_writer = EasyXls.EasyXls()
        self.borders = xlwt.Borders()
        self.style = xlwt.XFStyle()
        self.__load_borders()
        self.style.borders = self.borders
        # local parameter
        self.key_level = 'level'
        self.key_vip = 'vip_level'
        self.table_name = 'user_reten_lv_vip'
        self.start_date = '2018-03-28'
        self.end_date = '2018-09-22'

    def __load_borders(self):
        self.borders.left = 1
        self.borders.right = 1
        self.borders.top = 1
        self.borders.bottom = 1
        self.borders.bottom_colour = 0x3A

    def __load_table_data(self, search_key):
        # compute activeUsers,retenUsers,retenUsers/activeUsers
        sql_str = 'select date,' + search_key + ',sum(activeUsers),sum(retenUsers),sum(retenUsers)/sum(activeUsers) from ' + self.table_name + ' group by date,' + search_key
        print sql_str
        date_list = list()
        key_list = list()
        result_dict = dict()
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                date = str(rec[0])
                if date not in date_list:
                    date_list.append(date)
                key_name = str(rec[1])
                if key_name not in key_list:
                    key_list.append(key_name)
                active = int(rec[2])
                reten = int(rec[3])
                reten_ratio = float(rec[4])
                key = date + '|' + key_name
                if key not in result_dict.keys():
                    result_dict[key] = dict()
                    result_dict[key]['active'] = active
                    result_dict[key]['reten'] = reten
                    result_dict[key]['reten_ratio'] = reten_ratio
        date_list = sorted(date_list)
        key_list = sorted(key_list, key=lambda x: int(x))
        return_list = [date_list, key_list, result_dict]
        return return_list

    def __write_xls_inside_sheet(self, data_list, table_type, head_name, sheet, line_num):
        [date_list, key_list, result_dict] = data_list
        head_line = [head_name]
        for date in date_list:
            head_line.append(date)
        self.xls_writer.insert_xls_style(head_line, sheet, line_num, self.style)
        for key_name in key_list:
            data_line = [key_name]
            for date in date_list:
                key = date + '|' + key_name
                if key not in result_dict.keys():
                    data_line.append(' ')
                    continue
                if key in result_dict.keys():
                    value = result_dict[key].setdefault(table_type, ' ')
                    data_line.append(value)
            self.xls_writer.insert_xls_style(data_line, sheet, line_num, self.style)
        return 1

    def write_xls_sheet(self, search_key):
        sheet_name = search_key
        sheet = self.xls_writer.new_sheet(sheet_name, self.wbk)
        sheet.col(0).width = 256 * 20
        line_num = [0]
        title = '按' + search_key + '三日留存'
        name_list = [title]
        self.xls_writer.insert_xls_style(name_list, sheet, line_num, self.style)
        line_num[0] = line_num[0] + 2
        data_list = self.__load_table_data(search_key)
        head_name = '当日活跃人数'
        table_type = 'active'
        self.__write_xls_inside_sheet(data_list, table_type, head_name, sheet, line_num)
        line_num[0] = line_num[0] + 2
        head_name = '三日内留存人数'
        table_type = 'reten'
        self.__write_xls_inside_sheet(data_list, table_type, head_name, sheet, line_num)
        line_num[0] = line_num[0] + 2
        head_name = '留存率'
        table_type = 'reten_ratio'
        self.__write_xls_inside_sheet(data_list, table_type, head_name, sheet, line_num)
        return 1

    def execute(self):
        file_name = ConfParameters.ConfParameters().save_path + 'User_reten_vip_lv_' + self.start_date + '_' + self.end_date + '.xls'
        self.write_xls_sheet(self.key_level)
        self.write_xls_sheet(self.key_vip)
        self.wbk.save(file_name)
        self.db.close()


# test main
if __name__ == '__main__':
    UserRetenVipLevelWriteXls().execute()





