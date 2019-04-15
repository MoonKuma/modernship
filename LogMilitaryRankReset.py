#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : LogMilitaryRankReset.py
# @Author: MoonKuma
# @Date  : 2018/9/26
# @Desc  : Guide step pass rate from log

from util.LogQuery import LogQuery
import conf.ConfParameters as ConfParameters
import MySQLdb
import util.EasyXls as EasyXls
import xlwt
import sys


class LogUserGuide(LogQuery):

    def __init__(self, start_date, end_date):
        super(LogUserGuide, self).__init__(start_date, end_date)
        self.key_word = 'MilitaryRankReset'
        # initial mysql-db
        self.mysql_para = ConfParameters.ConfParameters().mysql_conf
        self.db = None  # such is initiate not in constructor but when actually used to ensure db get closed after connect
        self.cursor = None

    def __sift_uid(self, raw_uid):
        sifted_uid = list()
        sql_str = 'select uid from test.MilitaryRankReset;'
        self.cursor.execute(sql_str)
        all_data = self.cursor.fetchall()
        existed_uid = list()
        if all_data:
            for rec in all_data:
                uid = str(rec[0])
                if uid not in existed_uid:
                    existed_uid.append(uid)
        for uid in raw_uid:
            if uid not in existed_uid:
                sifted_uid.append(uid)
        return sifted_uid

    def __insert_table(self, sifted_uid):
        pass


    def analyse_log(self, log_data):
        self.db = MySQLdb.connect(self.mysql_para['ip'], self.mysql_para['users'], self.mysql_para['password'],
                                  self.mysql_para['stat_base'])
        self.cursor = self.db.cursor()
        raw_uid = list()

        self.__sift_uid()



        return data_list


# main
if __name__ == '__main__':
    # start_date = sys[1]
    # end_date = sys[2]
    start_date = '2018-09-26'
    end_date = '2018-09-27'
    # initiate xls
    wbk = xlwt.Workbook()
    xls_writer = EasyXls.EasyXls()
    style = xlwt.XFStyle()
    style.borders = xls_writer.borders
    # get log data
    log_user_guide = LogUserGuide(start_date, end_date)
    file_str = log_user_guide.log_file_str()
    cmd = 'grep -h -s \'' + log_user_guide.key_word + '\' ' + file_str + '|awk -F \',\' \'{if($1>="2018-09-25 12:00:00")max[$3]=$15} END {OFS=",";for(i in max)print i,max[i]}\'|awk -F \',\' \'{sum[$2]=sum[$2]+1} END {OFS=",";for(k in sum)print k,sum[k]}\''
    data_list = log_user_guide.analyse_log(log_user_guide.cmd_compute(cmd))
    # write xls
    sheet = xls_writer.new_sheet('sheet1', wbk)
    line_num = [0]
    head_line = ['编号', '翻译', '人数', '比例']
    xls_writer.insert_xls_style(head_line, sheet, line_num, style)
    for data_line in data_list:
        xls_writer.insert_xls_style(data_line, sheet, line_num, style)
    # save xls
    file_name = ConfParameters.ConfParameters().save_path + 'Guide_Step_' + start_date + '_' + end_date + '.xls'
    wbk.save(file_name)









