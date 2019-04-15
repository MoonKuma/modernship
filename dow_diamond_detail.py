#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : dow_diamond_detail.py
# @Author: MoonKuma
# @Date  : 2018/11/8
# @Desc  : VIP and diamond cost


import conf.ConfParameters as ConfParameters
import util.EasyXls as EasyXls
import MySQLdb
import xlwt
from util.WriteStandardForm import write_standard_form


class DowDiamondDetail(object):
    def __init__(self, start_date, end_date):
        # initial mysql
        mysql_para = ConfParameters.ConfParameters().mysql_conf_bd
        self.db = MySQLdb.connect(host=mysql_para['ip'], user=mysql_para['users'],
                                  passwd=mysql_para['password'], db=mysql_para['stat_base'])
        self.cursor = self.db.cursor()
        # initial xls
        self.wbk = xlwt.Workbook()
        self.xls_writer = EasyXls.EasyXls()
        self.style = xlwt.XFStyle()
        self.style.borders = self.xls_writer.borders
        # local
        self.stat_jp = 'zhanguo_jp_stat_base'
        self.stat_tw = 'zhanguo_stat_base'
        self.start_date = start_date
        self.end_date = end_date

    def get_battle_info(self, stat_base, head_name):
        res_dict = dict()
        data_dict = dict()
        vip_list = list()
        type_list = list()
        sql_cmd = 'select vip_level,cost_type,sum(diamond),count(distinct uid) from ' + stat_base + '.user_diamond_detail where date between \'' + self.start_date + '\' and \'' + self.end_date + '\' group by vip_level, cost_type'
        print(sql_cmd)
        self.cursor.execute(sql_cmd)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                vip = int(rec[0])
                cost_type = int(rec[1])
                diamond = int(rec[2])
                if vip not in data_dict.keys():
                    data_dict[vip] = dict()
                    vip_list.append(vip)
                if cost_type not in type_list:
                    type_list.append(cost_type)
                data_dict[vip][cost_type] = diamond
        vip_list = sorted(vip_list)
        type_list = sorted(type_list)

        res_dict['data_dict'] = data_dict
        res_dict['X_list'] = type_list
        res_dict['Y_list'] = vip_list
        res_dict['default_value'] = 0
        res_dict['head_name'] = head_name
        return res_dict

    def write_xls(self):
        sheet_name = '日本_VIP钻石'
        new_sheet = self.xls_writer.new_sheet(sheet_name, self.wbk)
        new_sheet.col(0).width = 256 * 20
        line_num = [0]
        res_dict = self.get_battle_info(self.stat_jp, sheet_name)
        write_standard_form(res_dict, new_sheet, line_num, self.style)

        sheet_name = '台湾_VIP钻石'
        new_sheet = self.xls_writer.new_sheet(sheet_name, self.wbk)
        new_sheet.col(0).width = 256 * 20
        line_num = [0]
        res_dict = self.get_battle_info(self.stat_tw, sheet_name)
        write_standard_form(res_dict, new_sheet, line_num, self.style)

    def close(self):
        save_file_name = 'dow_behavior_diamond_cost_' + self.start_date + '_' + self.end_date + '.xls'
        save_file = ConfParameters.ConfParameters().save_path + save_file_name
        self.wbk.save(save_file)
        self.db.close()

    @staticmethod
    def execute(start_date, end_date):
        obj = DowDiamondDetail(start_date, end_date)
        obj.write_xls()
        obj.close()


if __name__ == '__main__':
    DowDiamondDetail.execute('2018-10-29','2018-11-05')