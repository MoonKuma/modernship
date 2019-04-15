#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : CheckRecentBehavior.py
# @Author: MoonKuma
# @Date  : 2018/10/29
# @Desc  : Assembling behavior queries with standard form of input/output and xls writing

import conf.ConfParameters as ConfParameters
import util.EasyXls as EasyXls
import util.DateList as DateList
import MySQLdb
import xlwt
import time
import traceback
from modernship_util.module_time_cost import get_module_time_cost
from modernship_util.user_ship_info import get_ship_info
from modernship_util.module_attend import get_module_attend_rate
from modernship_util.item_buy import get_item_buy
from modernship_util.DiamondCost import *
from modernship_util.vip_situation import *
from modernship_util.buy_oil import *
from modernship_util.tech_info import *
from modernship_util.DailyDiscountItem import *
from modernship_util.DailyActive import *
from modernship_util.shopexchange import *
from util.WriteStandardForm import write_standard_form
import sys

class CheckRecentBehavior(object):
    def __init__(self):
        # initial mysql
        mysql_para = ConfParameters.ConfParameters().mysql_conf_bd
        self.db = MySQLdb.connect(host=mysql_para['ip'], port=mysql_para['port'], user=mysql_para['users'], passwd=mysql_para['password'], db=mysql_para['stat_base'])
        self.cursor = self.db.cursor()
        # initial EasyXls
        self.wbk = xlwt.Workbook()
        self.xls_writer = EasyXls.EasyXls()
        self.style = xlwt.XFStyle()
        self.style.borders = self.xls_writer.borders
        # local parameter
        self.date_list = list()
        self.channel_list = list()
        self.zone_list = list()
        self.input_dict = dict()
        self.__load_input()

    def set_input(self, new_input_dict):
        if 'date_list' in new_input_dict.keys():
            self.date_list = new_input_dict['date_list']
        if 'channel_list' in new_input_dict.keys():
            self.channel_list = new_input_dict['channel_list']
        if 'zone_list' in new_input_dict.keys():
            self.zone_list = new_input_dict['zone_list']
        self.__load_input()

    def write_module_time(self):
        res_dict = get_module_time_cost(self.input_dict)
        new_sheet = self.xls_writer.new_sheet('模块时长', self.wbk)
        new_sheet.col(0).width = 256 * 20
        new_sheet.col(1).width = 256 * 20
        line_num = [0]
        write_standard_form(res_dict, new_sheet, line_num, self.style)


    def write_diamond_cost(self):
        res_dict = get_diamond_times(self.input_dict)
        new_sheet = self.xls_writer.new_sheet('钻石消耗', self.wbk)
        new_sheet.col(0).width = 256 * 20
        new_sheet.col(1).width = 256 * 20
        line_num = [0]
        res_dict = get_diamond_people(self.input_dict)
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        line_num[0] += 1
        # res_dict = get_diamond_times(self.input_dict)
        # write_standard_form(res_dict, new_sheet, line_num, self.style)
        line_num[0] += 1
        res_dict = get_diamond_cost(self.input_dict)
        write_standard_form(res_dict, new_sheet, line_num, self.style)

    def write_ship_info(self):
        res_dict = get_ship_info(self.input_dict)
        new_sheet = self.xls_writer.new_sheet('阵容信息', self.wbk)
        new_sheet.col(0).width = 256 * 20
        new_sheet.col(1).width = 256 * 20
        line_num = [0]
        write_standard_form(res_dict, new_sheet, line_num, self.style)

    def write_buy_oil(self):
        res_dict = buy_oil_people(self.input_dict)
        new_sheet = self.xls_writer.new_sheet('原油购买', self.wbk)
        new_sheet.col(0).width = 256 * 20
        line_num = [0]
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        line_num[0] += 1
        res_dict = buy_oil_times(self.input_dict)
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        line_num[0] += 1
        res_dict = buy_oil_diamond(self.input_dict)
        write_standard_form(res_dict, new_sheet, line_num, self.style)

    def write_vip_level(self):
        self.input_dict['channel_list'] = ['112003']
        res_dict = vip_level(self.input_dict)
        new_sheet = self.xls_writer.new_sheet('最大日期VIP等级信息-112003', self.wbk)
        new_sheet.col(0).width = 256 * 20
        line_num = [0]
        write_standard_form(res_dict, new_sheet, line_num, self.style)

        self.input_dict['channel_list'] = ['212003']
        res_dict = vip_level(self.input_dict)
        new_sheet = self.xls_writer.new_sheet('最大日期VIP等级信息-212003', self.wbk)
        new_sheet.col(0).width = 256 * 20
        line_num = [0]
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        self.input_dict['channel_list']=[]

    def write_tech_info(self):
        res_dict = tech_people(self.input_dict)
        new_sheet = self.xls_writer.new_sheet('最大日期科技人数', self.wbk)
        new_sheet.col(0).width = 256 * 20
        new_sheet.col(1).width = 256 * 20
        line_num = [0]
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        line_num[0] += 1
        res_dict = tech_avglevel(self.input_dict)
        write_standard_form(res_dict, new_sheet, line_num, self.style)

    def write_behavior_attend(self):
        [res_raw, res_ratio] = get_module_attend_rate(self.input_dict)
        new_sheet = self.xls_writer.new_sheet('各玩法参与度', self.wbk)
        new_sheet.col(0).width = 256 * 20
        new_sheet.col(1).width = 256 * 20
        line_num = [0]
        write_standard_form(res_raw, new_sheet, line_num, self.style)
        line_num[0] += 1
        write_standard_form(res_ratio, new_sheet, line_num, self.style)

    def write_item_buy(self):
        res_raw = get_item_buy(self.input_dict)
        new_sheet = self.xls_writer.new_sheet('商品购买', self.wbk)
        new_sheet.col(0).width = 256 * 20
        new_sheet.col(1).width = 256 * 20
        new_sheet.col(2).width = 256 * 20
        line_num = [0]
        write_standard_form(res_raw, new_sheet, line_num, self.style)

    def write_dailydiscount(self):
        res_dict = everyday_buy_people(self.input_dict)
        new_sheet = self.xls_writer.new_sheet('每日折扣', self.wbk)
        new_sheet.col(0).width = 256 * 20
        new_sheet.col(1).width = 256 * 20
        line_num = [0]
        # write_standard_form(res_dict1, new_sheet, line_num, self.style)
        # line_num[0] += 1
        # res_dict2 = everyday_buy(self.input_dict, 2)
        # write_standard_form(res_dict2, new_sheet, line_num, self.style)
        # line_num[0] += 1
        # res_dict3 = everyday_buy(self.input_dict, 3)
        # write_standard_form(res_dict3, new_sheet, line_num, self.style)
        # line_num[0] += 1
        # res_dict4 = everyday_active(self.input_dict)
        # write_standard_form(res_dict4, new_sheet, line_num, self.style)
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        line_num[0] += 1
        res_dict = everyday_buy_times(self.input_dict)
        write_standard_form(res_dict, new_sheet, line_num, self.style)


    def write_shopexchange(self):
        shopidlist = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        new_sheet = self.xls_writer.new_sheet('商场购买', self.wbk)
        new_sheet.col(0).width = 256 * 20
        new_sheet.col(1).width = 256 * 20
        line_num = [0]
        for i in shopidlist:
            res_dict = shop_exchange(self.input_dict, i)
            write_standard_form(res_dict, new_sheet, line_num, self.style)
            line_num[0] += 1

    def execute(self, input_dict, start_date, end_date):
        self.set_input(input_dict)
        file_name = ConfParameters.ConfParameters().save_path + 'CheckRecentBehavior_' + start_date + '-' + end_date + '.xls'
        # content
        # self.write_module_time()  # 模块时长 last day
        # self.write_diamond_cost()  # 钻石消耗 period
        # self.write_ship_info()  # 阵容信息 last day
        # self.write_vip_level()  # VIP等级 period
        # self.write_buy_oil()    # 原油购买
        # self.write_tech_info()  # 科技查询 last day
        # self.write_behavior_attend()  # 玩法参与度 period
        # module list
        module_list = [self.write_module_time,
                       self.write_diamond_cost,
                       self.write_ship_info,
                       self.write_vip_level,
                       self.write_buy_oil,
                       self.write_tech_info,
                       self.write_behavior_attend]
        # module_list = [self.write_diamond_cost] # test

        for module in module_list:
            now_time = time.time()
            try:
                msg = 'Try running ' + module.__name__
                print(msg)
                module()
                msg = 'Finish running ' + module.__name__ + ',time cost:' + str(time.time() - now_time)
                print(msg)
            except Exception:
                msg = 'Error in running' + module.__name__+ ',time cost:' + str(time.time() - now_time)
                print(msg)
                print traceback.format_exc()
        # self.write_item_buy()  # 商品购买 period
        # self.write_dailydiscount() #每日折扣 period
        # self.write_shopexchange()  #商店购买 period
        #
        self.wbk.save(file_name)
        self.db.close()

    # native
    def __load_input(self):
        self.input_dict['cursor'] = self.cursor
        self.input_dict['date_list'] = self.date_list
        self.input_dict['channel_list'] = self.channel_list
        self.input_dict['zone_list'] = self.zone_list


# test main
if __name__ == '__main__':
    # input
    try:
        date1 = sys.argv[1]
        date2 = sys.argv[2]
    except:
        [date1, date2] = DateList.DateList().get_last_week()
        msg = 'No date input detected, compute the last week automatically. Computing date between ' + date1 + ' and ' + date2
        print(msg)
    date_list = DateList.DateList().get_date_list(date1, date2)
    new_input = dict()
    new_input['date_list'] = date_list
    # execute
    CheckRecentBehavior().execute(new_input, date1, date2)