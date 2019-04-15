#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : dow_battle_match.py
# @Author: MoonKuma
# @Date  : 2018/11/8
# @Desc  : check battle match condition for each battle id
# sql :  select battle_id,sum(level)/count(uid) as x_avg, max(level)-min(level) as x_range,count(uid) as uid_count from user_battle_finish group by battle_id having min(gold)>=3 and count(uid)>1 limit 100;
import conf.ConfParameters as ConfParameters
import util.EasyXls as EasyXls
import MySQLdb
import xlwt
from util.WriteStandardForm import write_standard_form


class DowBattleMatch(object):
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
        self.check_key_list = ['level', 'vip_level']
        self.min_gold = 3
        self.x_list = ['x_avg', 'x_range', 'u_count']
        self.start_date = start_date
        self.end_date = end_date

    def get_battle_info(self, check_key, stat_base, head_name):
        res_dict = dict()
        data_dict = dict()
        battle_list = list()
        if check_key not in self.check_key_list:
            return dict()
        sql_cmd = 'select battle_id,sum(' + check_key + ')/count(uid) as x_avg, max(' + check_key + ')-min(' + check_key + ') as x_range,count(uid) as uid_count from ' + stat_base + '.user_battle_finish group by battle_id having min(gold)>=' + str(self.min_gold) + ' and count(uid)>1 '
        print(sql_cmd)
        self.cursor.execute(sql_cmd)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                battle_id = str(rec[0])
                x_avg = float(rec[1])
                x_range = int(rec[2])
                u_count = int(rec[3])
                if battle_id not in data_dict.keys():
                    battle_list.append(battle_id)
                    data_dict[battle_id] = dict()
                data_dict[battle_id]['x_avg'] = x_avg
                data_dict[battle_id]['x_range'] = x_range
                data_dict[battle_id]['u_count'] = u_count
        res_dict['data_dict'] = data_dict
        res_dict['X_list'] = self.x_list
        res_dict['Y_list'] = battle_list
        res_dict['default_value'] = 0
        res_dict['head_name'] = head_name
        return res_dict

    def write_xls(self):
        sheet_name = '日本_等级差异'
        new_sheet = self.xls_writer.new_sheet(sheet_name, self.wbk)
        new_sheet.col(0).width = 256 * 20
        line_num = [0]
        res_dict = self.get_battle_info('level', self.stat_jp, sheet_name)
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        sheet_name = '日本_VIP差异'
        new_sheet = self.xls_writer.new_sheet(sheet_name, self.wbk)
        new_sheet.col(0).width = 256 * 20
        line_num = [0]
        res_dict = self.get_battle_info('vip_level', self.stat_jp, sheet_name)
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        sheet_name = '台湾_等级差异'
        new_sheet = self.xls_writer.new_sheet(sheet_name, self.wbk)
        new_sheet.col(0).width = 256 * 20
        line_num = [0]
        res_dict = self.get_battle_info('level', self.stat_tw, sheet_name)
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        sheet_name = '台湾_VIP差异'
        new_sheet = self.xls_writer.new_sheet(sheet_name, self.wbk)
        new_sheet.col(0).width = 256 * 20
        line_num = [0]
        res_dict = self.get_battle_info('vip_level', self.stat_tw, sheet_name)
        write_standard_form(res_dict, new_sheet, line_num, self.style)

    def close(self):
        save_file_name = 'dow_behavior_battle_match_' + self.start_date + '_' + self.end_date + '.xls'
        save_file = ConfParameters.ConfParameters().save_path + save_file_name
        self.wbk.save(save_file)
        self.db.close()

    @staticmethod
    def execute(start_date, end_date):
        obj = DowBattleMatch(start_date, end_date)
        obj.write_xls()
        obj.close()


if __name__ == '__main__':
    DowBattleMatch.execute('2018-10-29','2018-11-05')






