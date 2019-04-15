#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : LogBattleError.py
# @Author: MoonKuma
# @Date  : 2018/10/11
# @Desc  : Battle Error related logs
# cmd = grep -h -s 'context:0-battleError_' event.log|
# grep -h -s 'context:0-battleError_' event.log.2018-09-* event.log.2018-10-*|awk -F ',' '{OFS=",";print substr($1,1,10),$5}'|sort|uniq|awk -F ',' '{sum[$1]=sum[$1]+1} END {OFS=",";for(i in sum)print i,sum[i]}'|sort -t ',' -k 1
# grep -h -s 'context:0_gameConnect_' event.log.2018-09-* event.log.2018-10-*|awk -F ',' '{OFS=",";print substr($1,1,10),$5}'|sort|uniq|awk -F ',' '{sum[$1]=sum[$1]+1} END {OFS=",";for(i in sum)print i,sum[i]}'|sort -t ',' -k 1
# grep -h -s 'context:0-battleError_' event.log.2018-10-2*|grep 'chanel:1099'|awk -F ',' '{OFS=",";print substr($1,1,10),$3,$5}'|sort|uniq|awk -F ',' '{sum[$1","$2]=sum[$1","$2]+1} END {OFS=",";for(i in sum)print i,sum[i]}'|sort -t ',' -k 1
# grep -h -s 'context:0-battleError_' /data/stat/statlog/event.log.2019-01*|awk -F ',' '{OFS=" ";print $1,$4}'|awk -F ' ' '{OFS=",";print substr($2,1,5),$3}'|awk -F ',' '{sum[$1","$2]=sum[$1","$2]+1} END {OFS=",";for(i in sum)print i,sum[i]}'> /data/tmpStatistic/battle_error_201901.txt



import sys
import xlwt
from util.EasyXls import EasyXls
from conf.ConfParameters import ConfParameters
from util.LogQuery import LogQuery
from util.WriteStandardForm import write_standard_form

def execute(start_date, end_date):
    log = LogQuery(start_date,end_date)
    files = log.event_file_str()
    # by time
    # cmd = 'grep -h -s \'context:0-battleError_\' ' + files + '|grep -v \'chanel:1077\'|awk -F \',\' \'{OFS=\" \";print $1,$4}\'|awk -F \' \' \'{OFS=\",\";print substr($2,1,4),$3}\'|awk -F \',\' \'{sum[$1\",\"$2]=sum[$1\",\"$2]+1} END {OFS=\",\";for(i in sum)print i,sum[i]}\''
    # by date
    # cmd = 'grep -h -s \'context:0-battleError_\' ' + files + '|grep -v \'chanel:1077\'|awk -F \',\' \'{OFS=\" \";print $1,$4}\'|awk -F \' \' \'{OFS=\",\";print $1,$3}\'|awk -F \',\' \'{sum[$1\",\"$2]=sum[$1\",\"$2]+1} END {OFS=\",\";for(i in sum)print i,sum[i]}\''
    # xianfeng only
    cmd = 'grep -h -s \'context:0-battleError_\' ' + files + '|grep \'chanel:1077\'|awk -F \',\' \'{OFS=\" \";print $1,$4}\'|awk -F \' \' \'{OFS=\",\";print $1,$3}\'|awk -F \',\' \'{sum[$1\",\"$2]=sum[$1\",\"$2]+1} END {OFS=\",\";for(i in sum)print i,sum[i]}\''
    print(cmd)
    result = log.cmd_compute(cmd)
    time_list = list()
    error_type = list()
    data_dict = dict()
    for line in result:
        line = line.strip()
        array = line.split(',')
        time0 = array[0]
        error = array[1]
        count = int(array[2])
        if time0 not in time_list:
            time_list.append(time0)
        if error not in error_type:
            error_type.append(error)
        if error not in data_dict.keys():
            data_dict[error] = dict()
        data_dict[error][time0] = count
    time_list = sorted(time_list)
    error_type = sorted(error_type)
    print('time_list:' + str(len(time_list)))
    print('error_type:' + str(len(error_type)))

    res_data_raw = dict()
    res_data_raw['data_dict'] = data_dict
    res_data_raw['X_list'] = time_list
    res_data_raw['Y_list'] = error_type
    res_data_raw['default_value'] = 0
    res_data_raw['head_name'] = 'BATTLE_ERROR'
    res_data_raw['note'] = '*时时战斗报错，统计时间:' + start_date + '-' + end_date

    file_name = ConfParameters().save_path + 'BATTLE_ERROR_' + start_date + '-' + end_date + '.xls'

    wbk = xlwt.Workbook()
    xls_writer = EasyXls()
    style = xlwt.XFStyle()
    style.borders = xls_writer.borders


    new_sheet = xls_writer.new_sheet('BATTLE_ERROR', wbk)
    new_sheet.col(0).width = 256 * 20
    line_num = [0]
    write_standard_form(res_data_raw, new_sheet, line_num, style)

    wbk.save(file_name)

date1 = sys.argv[1]
date2 = sys.argv[2]
execute(date1, date2)