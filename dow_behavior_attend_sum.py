#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : dow_behavior_attend.py
# @Author: MoonKuma
# @Date  : 2018/11/6
# @Desc  : dow project, behavior attend


import conf.ConfParameters as ConfParameters
import util.EasyXls as EasyXls
import MySQLdb
import xlwt
from util.WriteStandardForm import write_standard_form
import collections


class DowBehaviorAttend(object):
    def __init__(self):
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
        self.key_list = ['Login','Logout','InstanceBattle','QuickInstance','CreateBuilding','March']
        self.key_pair = collections.OrderedDict()
        self.key_pair['Active'] = ['Login','Logout']
        self.key_pair['PVE'] = ['QuickInstance', 'InstanceBattle']
        self.key_pair['PVP'] = ['CreateBuilding', 'March']

    def write_behavior_attend(self, date_pair, stat_base, sheet_name):
        new_sheet = self.xls_writer.new_sheet(sheet_name, self.wbk)
        new_sheet.col(0).width = 256 * 20
        line_num = [0]

        res_dict = self.get_behavior_attend([0, 0], date_pair, stat_base)
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        line_num[0] += 1

        res_dict = self.get_behavior_attend([1, 3], date_pair, stat_base)
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        line_num[0] += 1

        res_dict = self.get_behavior_attend([4, 8], date_pair, stat_base)
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        line_num[0] += 1

        res_dict = self.get_behavior_attend([9, 12], date_pair, stat_base)
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        line_num[0] += 1

        res_dict = self.get_behavior_attend([13, 15], date_pair, stat_base)
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        line_num[0] += 1
        pass

    def get_behavior_attend(self, vip_pair, date_pair, stat_base):
        name = 'VIP' + str(vip_pair[0]) + '~VIP' + str(vip_pair[1])
        res_dict = dict()
        data_dict = dict()
        key_list = self.key_list
        level_list = list()
        where_clause = 'and vip>=' + str(vip_pair[0]) + ' and vip<=' + str(vip_pair[1]) + ' and date between \'' + str(date_pair[0])  + '\' and \'' + str(date_pair[1]) + '\' '
        cmd = ' select keyword,level_stage,round(sum(uid_count)/count(distinct date)) as avg_user from (select date,keyword,concat(floor(level/10)*10,\'~\',ceil(level/10+0.1)*10) as level_stage,count(distinct uid) as uid_count,sum(times_count) as sum_times from ' + stat_base + '.user_daily_behavior where length(uid)>10 and level>0 and times_count>2 ' + where_clause + ' group by date,keyword,level_stage)a group by keyword,level_stage;'
        print cmd
        self.cursor.execute(cmd)
        all_data = self.cursor.fetchall()
        if all_data:
            for rec in all_data:
                keyword = rec[0]
                if keyword not in key_list:
                    continue
                level_stage = rec[1]
                user = int(rec[2])
                if level_stage not in level_list:
                    level_list.append(level_stage)
                keyword_pair = self.find_key(keyword)
                if keyword_pair not in data_dict.keys():
                    data_dict[keyword_pair] = dict()
                if data_dict[keyword_pair].setdefault(level_stage,0) < user:
                    data_dict[keyword_pair][level_stage] = user
        level_list = sorted(level_list, key=lambda x: self.compare_x(x))
        res_dict['data_dict'] = data_dict
        res_dict['X_list'] = level_list
        res_dict['Y_list'] = self.key_pair.keys()
        res_dict['default_value'] = 0
        res_dict['head_name'] = name
        return res_dict

    def save_and_close(self, date_pair):
        save_file_name = 'dow_behavior_sum_' + date_pair[0] + '_' + date_pair[1] + '.xls'
        save_file = ConfParameters.ConfParameters().save_path + save_file_name
        self.wbk.save(save_file)
        self.db.close()

    def compare_x(self, compare_str):
        array = compare_str.split('~')
        return int(array[0])

    def find_key(self, key_in):
        for key in self.key_pair.keys():
            if key_in in self.key_pair[key]:
                return key

    @staticmethod
    def execute(date_pair):
        obj = DowBehaviorAttend()
        obj.write_behavior_attend(date_pair, obj.stat_jp, 'Japan')
        obj.write_behavior_attend(date_pair, obj.stat_tw, 'Taiwan')
        obj.save_and_close(date_pair)


if __name__ == '__main__':
    DowBehaviorAttend.execute(['2018-10-29', '2018-11-05'])