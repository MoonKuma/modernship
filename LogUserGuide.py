#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : LogUserGuide.py
# @Author: MoonKuma
# @Date  : 2018/9/26
# @Desc  : Guide step pass rate from log
# grep -h -s 'DceGuide' ../Log_?????/ModernShipStat_2018-09-2[5-6]*|awk -F ',' '{if($1>="2018-09-25 12:00:00")max[$3]=$15} END {OFS=",";for(i in max)print i,max[i]}'|awk -F ',' '{sum[$2]=sum[$2]+1} END {OFS=",";for(k in sum)print k,sum[k]}'|sort -t ',' -k 1|more

from util.LogQuery import LogQuery
import conf.ConfParameters as ConfParameters
import util.ReadTable as ReadTable
import util.EasyXls as EasyXls
import xlwt
import sys


class LogUserGuide(LogQuery):

    def __init__(self, start_date, end_date):
        super(LogUserGuide, self).__init__(start_date, end_date)
        self.key_word = 'DceGuide'
        guide_table_name = ConfParameters.ConfParameters().conf_path + 'GuideStep.txt'
        self.guide_table = ReadTable.ReadTable(guide_table_name).read_table_file()

    def analyse_log(self, log_data):
        data_list = list()  # return data list
        pass_data = dict()
        total_user = 0.0
        for line in log_data:
            line = line.strip()
            array = line.split(',')
            guide_step = array[0]
            pass_uid = int(array[1])
            total_user += pass_uid
            if guide_step not in pass_data.keys():
                pass_data[guide_step] = pass_uid
        print 'total user:', total_user
        for guide_table_id in self.guide_table.keys():
            table_key = guide_table_id.replace('|Trans', '')
            tmp_list = [table_key]
            tmp_list.append(self.guide_table.setdefault(guide_table_id,table_key))
            pass_uid = pass_data.setdefault(table_key, 0)
            rate = 0
            if total_user != 0:
                rate = float(pass_uid)/total_user
            tmp_list.append(pass_uid)
            tmp_list.append(rate)
            data_list.append(tmp_list)
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









