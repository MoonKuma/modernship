#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Camp_remend_1225.py
# @Author: MoonKuma
# @Date  : 2018/12/25
# @Desc  :

'''
20154  雇佣声望
20155  银星声望
20156  黑鹰声望
20157  蓝狮声望
20158  西盟声望
'''

import os
from conf.ConfParameters import ConfParameters
uid_dict = dict() #uid:num
accept_list = ['20155', '20156', '20157','20158']

# load file
conf = ConfParameters().conf_path
conf_file = conf + '/Camp_reward_task.txt'
check_map = dict()
with open(conf_file, 'r') as filr_r:
    for line in filr_r.readlines():
        line = line.strip()
        array = line.split('\t')
        check_map[array[0]] = int(array[1])


# compute task
cmd_str = 'grep -h -s \'CampTaskReward\' /data/stat/Log_?????/ModernShipStat_2018-12-2[0-6]*|awk -F \',\' \'{OFS=\",\";print $3,$16\"|\"$17}\''
print(cmd_str)
val = os.popen(cmd_str).readlines()
for line in val:
    line = line.strip()
    array = line.split(',')
    uid = array[0]
    task = array[1]
    uid_dict[uid] = uid_dict.setdefault(uid, 0) + check_map[task]

# compute buy
cmd_str = 'grep -h -s \'AddProp\' /data/stat/Log_?????/ModernShipStat_2018-12-2[0-6]*|awk -F \',\' \'{OFS=\",\";if($15==138 && ($16==20155||$16==20156||$16==20157||$16==20158))print $3,$17}\''
print(cmd_str)
val = os.popen(cmd_str).readlines()
for line in val:
    line = line.strip()
    array = line.split(',')
    uid = array[0]
    count = array[1]
    uid_dict[uid] = uid_dict.setdefault(uid, 0) + int(count)

# compute mail
cmd_str = 'grep -h -s \'AddProp\' /data/stat/Log_?????/ModernShipStat_2018-12-2[0-6]*|awk -F \',\' \'{OFS=\",\";if($16==20154)print $3,$17}\''
print(cmd_str)
val = os.popen(cmd_str).readlines()
for line in val:
    line = line.strip()
    array = line.split(',')
    uid = array[0]
    count = array[1]
    uid_dict[uid] = uid_dict.setdefault(uid, 0) + int(count)


# write_file

file_write_path = '/data/tmpStatistic/camp_bug_1225/'
file_write_name = 'user_camp_total_1225.txt'

file_save = file_write_path + file_write_name

with open(file_save, 'w') as file_wri:
    for uid in uid_dict:
        str_wri = uid + ',' + str(uid_dict[uid]) + '\n'
        file_wri.write(str_wri)




