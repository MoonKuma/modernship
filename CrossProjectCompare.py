#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : CrossProjectCompare.py
# @Author: MoonKuma
# @Date  : 2019/1/2
# @Desc  : framework for calling methods


import MySQLdb
import xlwt
import traceback
import time
import sys


import util.EasyXls as EasyXls
import util.DateList as DateList
from util.WriteStandardForm import write_standard_form
from cross_project_compare.user_guidance import user_guidance
from cross_project_compare.event_login import event_login
from cross_project_compare.retenratio import renratio
from cross_project_compare.online_time import online_time
from cross_project_compare.life_time import life_time_compute
from cross_project_compare.user_return import user_return
from cross_project_compare.pay_motivation import pay_motivation
from cross_project_compare.general_report import general_report
import conf.ConfParameters as ConfParameters

class CallMethod(object):

    def __init__(self):
        # initial mysql
        mysql_para = ConfParameters.ConfParameters().mysql_conf
        self.db = MySQLdb.connect(host=mysql_para['ip'], port=mysql_para['port'], user=mysql_para['users'], passwd=mysql_para['password'], db=mysql_para['stat_base'])
        self.cursor = self.db.cursor()
        self.act_stat_base = mysql_para['stat_base']
        self.reg_stat_base = mysql_para['stat_userreg']
        self.pay_base = mysql_para['stat_pay']
        #initial rate
        self.current_rate = ConfParameters.ConfParameters().current_rate
        # self.levellist = [0, 1000, 2000, 3000, 4000, 5000]
        self.levellist = [0,100,250,500,1000,2500,5000,10000,25000,50000,100000,250000,500000,1000000]
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

    def __set_input(self, new_input_dict):
        if 'date_list' in new_input_dict.keys():
            self.date_list = new_input_dict['date_list']
        if 'channel_list' in new_input_dict.keys():
            self.channel_list = new_input_dict['channel_list']
        if 'zone_list' in new_input_dict.keys():
            self.zone_list = new_input_dict['zone_list']
        self.__load_input()

    def __load_input(self):
        self.input_dict['cursor'] = self.cursor
        self.input_dict['date_list'] = self.date_list
        self.input_dict['channel_list'] = self.channel_list
        self.input_dict['zone_list'] = self.zone_list

    def __get_input(self):
        new_dict = dict()
        new_dict['cursor'] = self.cursor
        new_dict['date_list'] = self.date_list
        new_dict['channel_list'] = self.channel_list
        new_dict['zone_list'] = self.zone_list
        return new_dict

    def __user_guidance(self):
        res_dict = user_guidance(self.input_dict, 6, self.reg_stat_base)
        # print(res_dict)
        if res_dict is not None:
            new_sheet = self.xls_writer.new_sheet('新用户等级与通过率', self.wbk)
            new_sheet.col(0).width = 256 * 20
            line_num = [0]
            write_standard_form(res_dict, new_sheet, line_num, self.style)

    def __retenratio(self):

        res_dict_list = renratio(self.input_dict, self.act_stat_base, self.reg_stat_base,self.pay_base,self.current_rate,*self.levellist)
        if res_dict_list is not None:
            new_sheet = self.xls_writer.new_sheet('付费等级留存', self.wbk)
            new_sheet.col(0).width = 256 * 20
            line_num = [0]
            for i in res_dict_list:
                write_standard_form(i, new_sheet, line_num, self.style)
                line_num[0]+=2

    def __online_time(self):
        res_dict_list = online_time(self.input_dict, self.act_stat_base, self.pay_base,self.current_rate,*self.levellist)
        if res_dict_list is not None:
            new_sheet = self.xls_writer.new_sheet('人均在线时长', self.wbk)
            new_sheet.col(0).width = 256 * 20
            line_num = [0]
            for i in res_dict_list:
                write_standard_form(i, new_sheet, line_num, self.style)
                line_num[0] += 2

    def __life_time(self):
        [res_dict, res_dict_remain, res_dict_remain_ratio, res_dict_lost, res_dict_lost_life] = life_time_compute(self.input_dict, self.levellist)
        new_sheet = self.xls_writer.new_sheet('用户生命周期', self.wbk)
        new_sheet.col(0).width = 256 * 20
        line_num = [0]
        write_standard_form(res_dict, new_sheet, line_num, self.style)
        line_num[0] += 2
        write_standard_form(res_dict_remain, new_sheet, line_num, self.style)
        line_num[0] += 2
        write_standard_form(res_dict_remain_ratio, new_sheet, line_num, self.style)
        line_num[0] += 2
        write_standard_form(res_dict_lost, new_sheet, line_num, self.style)
        line_num[0] += 2
        write_standard_form(res_dict_lost_life, new_sheet, line_num, self.style)
        line_num[0] += 2

    def __event_login(self):
        res_dict = event_login(self.input_dict, self.reg_stat_base)
        # print(res_dict)
        if res_dict is not None:
            new_sheet = self.xls_writer.new_sheet('启动加载项', self.wbk)
            new_sheet.col(0).width = 256 * 20
            line_num = [0]
            write_standard_form(res_dict, new_sheet, line_num, self.style)

    def __user_return(self):
        res_dict, res_pay_users, res_pay_money = user_return(self.input_dict, self.levellist)
        if res_dict is not None:
            new_sheet = self.xls_writer.new_sheet('老用户回归', self.wbk)
            new_sheet.col(0).width = 256 * 20
            line_num = [0]
            write_standard_form(res_dict, new_sheet, line_num, self.style)

            line_num[0] = line_num[0] + 2
            write_standard_form(res_pay_users, new_sheet, line_num, self.style)

            line_num[0] = line_num[0] + 2
            write_standard_form(res_pay_money, new_sheet, line_num, self.style)
        pass

    def __pay_motivation(self):
        res_dict, res_pay_users, res_pay_money = pay_motivation(self.input_dict, self.levellist)
        if res_dict is not None:
            new_sheet = self.xls_writer.new_sheet('付费激励', self.wbk)
            new_sheet.col(0).width = 256 * 20
            line_num = [0]
            write_standard_form(res_dict, new_sheet, line_num, self.style)

            line_num[0] = line_num[0] + 2
            write_standard_form(res_pay_users, new_sheet, line_num, self.style)

            line_num[0] = line_num[0] + 2
            write_standard_form(res_pay_money, new_sheet, line_num, self.style)
        pass

    def __general_report(self):
        res_dict = general_report(self.input_dict)
        if res_dict is not None:
            new_sheet = self.xls_writer.new_sheet('概览', self.wbk)
            new_sheet.col(0).width = 256 * 20
            line_num = [0]
            write_standard_form(res_dict, new_sheet, line_num, self.style)
        pass

    def execute(self, input_dict):
        self.__set_input(input_dict)
        date_list = self.__get_input()['date_list']
        start_date = date_list[0]
        end_date = date_list[len(date_list)-1]
        exc_time = int(time.time())
        time_stamp = exc_time - 10000*(exc_time/10000)
        file_name = ConfParameters.ConfParameters().save_path + 'CrossProjectCompare_' + ConfParameters.ConfParameters().project_name + '_' + start_date + '-' + end_date + '_' + str(time_stamp) +'.xls'
        # module list
        module_list = [
            self.__general_report, # 概览
            self.__user_guidance,  # 新手引导
            self.__event_login,  # 启动加载项
            self.__retenratio, #留存
            self.__online_time, #在线时长
            # # self.__life_time, # 生命周期 # this only works when computing from the beginning
            self.__user_return, # 老用户回归
            self.__pay_motivation # 付费激励

        ]
        for module in module_list:
            now_time = time.time()
            try:
                msg = 'Try running ' + module.__name__
                print(msg)
                module()
                msg = 'Finish running ' + module.__name__ + ',time cost:' + str(time.time() - now_time)
                print(msg)
            except Exception:
                msg = 'Error in running' + module.__name__ + ',time cost:' + str(time.time() - now_time)
                print(msg)
                print traceback.format_exc()
        self.wbk.save(file_name)
        self.db.close()

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
    # expect possible channel
    if len(sys.argv) > 3:
        channel_list = sys.argv[3:]
        new_input['channel_list'] = channel_list
    # execute
    CallMethod().execute(new_input)