#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : LogInTestResult.py
# @Author: MoonKuma
# @Date  : 2018/10/17
# @Desc  : log in analysis

import os
import sys
import time # time.mktime(time_obj)


def query_log():
    try:
        file_name = sys.argv[1]
    except:
        print('Need input a file')
        return None
    if not os.path.exists(file_name):
        msg = 'Illegal file name' + file_name
        print(msg)
        return None
    cmd = 'grep -h -s -E \'LogInWeb|LogInGame|Register\' ' + file_name + '|awk -F \',\' \'{OFS=\",\";print $1,$3,$4}\''
    print cmd
    val = os.popen(cmd).readlines()
    uid_dict = dict()
    # {uid:{log_key1:time1,log_key2:time2, rate1:1, rate2:1, time_diff1:1, time_diff2:2}}
    for line in val:
        line = line.strip()
        array = line.split(',')
        log_time = array[0]
        uid = array[1]
        log_key = array[2]
        if uid not in uid_dict.keys():
            uid_dict[uid] = dict()
        if log_key not in uid_dict[uid].keys():
            uid_dict[uid][log_key] = log_time
    for uid in uid_dict.keys():
        tmp_dict = uid_dict[uid]
        rate1 = 0
        rate2 = 0
        time_diff1 = 0.0
        time_diff2 = 0.0
        if 'LogInWeb' not in tmp_dict.keys():
            continue
        min_time = time.strftime('%Y-%m-%d %H:%M', time.strptime(tmp_dict['LogInWeb'], '%Y-%m-%d %H:%M:%S'))
        time0 = time.mktime(time.strptime(tmp_dict['LogInWeb'], '%Y-%m-%d %H:%M:%S'))
        if 'LogInGame' in tmp_dict.keys():
            rate1 = 1
            time_diff1 = time.mktime(time.strptime(tmp_dict['LogInGame'], '%Y-%m-%d %H:%M:%S')) - time0
        if 'Register' in tmp_dict.keys():
            rate2 = 1
            time_diff2 = time.mktime(time.strptime(tmp_dict['Register'], '%Y-%m-%d %H:%M:%S')) - time0
        tmp_dict['min_time'] = min_time
        tmp_dict['rate1'] = rate1
        tmp_dict['rate2'] = rate2
        tmp_dict['time_diff1'] = time_diff1
        tmp_dict['time_diff2'] = time_diff2
    print 'Succeed! len(uid_dict.keys()):', str(len(uid_dict.keys()))
    return uid_dict

current_date = time.strftime('%Y-%m-%d', time.localtime())
file_name = 'Login_check_report_' + current_date + '.txt'
file_open = open(file_name, 'w')
key_list = ['min_time', 'LogInWeb', 'LogInGame', 'Register', 'rate1', 'rate2', 'time_diff1', 'time_diff2']
result_dict = query_log()
if result_dict != None:
    for uid in result_dict.keys():
        str_wrt = uid
        for item in key_list:
            str_wrt = str_wrt + ',' + str(result_dict[uid].setdefault(item, ''))
        str_wrt += '\n'
        file_open.write(str_wrt)
file_open.close()

minute_dict = dict()
if result_dict != None:
    for uid in result_dict.keys():
        min_time = result_dict[uid].setdefault('min_time', '0')
        reten2 = result_dict[uid].setdefault('rate2', 0)
        time_diff2 = result_dict[uid].setdefault('time_diff2', 0)
        if time_diff2 < 0 or time_diff2 > 30:
            reten2 = 0
            time_diff2 = 0
        if min_time not in minute_dict.keys():
            minute_dict[min_time] = dict()
        minute_dict[min_time]['count'] = minute_dict[min_time].setdefault('count', 0) + 1
        minute_dict[min_time]['rate2'] = minute_dict[min_time].setdefault('rate2', 0) + reten2
        minute_dict[min_time]['time_diff2'] = minute_dict[min_time].setdefault('time_diff2', 0) + time_diff2


file_name = 'Login_check_sum_' + current_date + '.txt'
file_open = open(file_name, 'w')
key_list = ['count', 'rate2', 'time_diff2']
if len(minute_dict.keys()) != 0:
    for minute in minute_dict.keys():
        str_wrt = minute
        for item in key_list:
            str_wrt = str_wrt + ',' + str(minute_dict[minute].setdefault(item, ''))
        str_wrt += '\n'
        file_open.write(str_wrt)
file_open.close()
