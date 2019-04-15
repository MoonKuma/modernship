#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : combine_compute.py
# @Author: MoonKuma
# @Date  : 2019/1/16
# @Desc  :



conf_path = 'conf/ship_adv_conf.txt'
data_path = 'conf/ShipAdv.txt'
result = 'result/ShipUpgrade_combine.txt'
final_file = 'result/ShipUpgrade_combine_final.txt'

'''
#compute
file_conf = open(conf_path, 'r')
conf_dict = dict()
for line in file_conf.readlines():
    line = line.strip()
    array = line.split('\t')
    key = array[0] + '|' + array[1]
    item_list = array[2].split('|')
    count_list = array[3].split('|')
    if len(item_list) != len(count_list):
        print('[Error]Len mis match')
        raise RuntimeError
    reward_list = list()
    for index in range(0, len(item_list)):
        if item_list[index]=="" or item_list[index]=="0":
            continue
        reward_list.append(item_list[index])
        reward_list.append('1')
        reward_list.append(count_list[index])
    reward_str = ';'.join(reward_list)
    conf_dict[key] = reward_str

file_conf.close()

file_data = open(data_path, 'r')
gift_dict = dict()
for line in file_data.readlines():
    line = line.strip()
    array = line.split(',')
    uid = array[0]
    key = array[1] + '|' + array[2]
    gift = conf_dict[key]
    if uid not in gift_dict.keys():
        gift_dict[uid] = list()
    gift_dict[uid].append(gift)
file_data.close()


result_file = open(result, 'w')
for uid in gift_dict.keys():
    str_wri = uid + ',' + ';'.join(gift_dict[uid]) + '\n'
    result_file.write(str_wri)
result_file.close()

'''
# merge
result_file = open(result, 'r')
final_f = open(final_file, 'w')
for line in result_file.readlines():
    line = line.strip()
    array = line.split(',')
    uid = array[0]
    gift_dict = dict()
    gift_list = array[1].split(';')
    if len(gift_list)%3 != 0:
        print('Len mis match', line)
        raise RuntimeError
    current_item = ''
    current_count = 0
    for index in range(0,len(gift_list)):
        if index%3 == 0:
            current_item = gift_list[index]
        if index%3 == 2:
            current_count = int(gift_list[index])
            if current_item == '':
                print('Wrong item')
                raise RuntimeError
            gift_dict[current_item] = gift_dict.setdefault(current_item,0) + current_count
            current_item = ''
            current_count = 0
    gift_list_new = list()
    for item in gift_dict.keys():
        gift_list_new.append(item)
        gift_list_new.append('1')
        gift_list_new.append(str(gift_dict[item]))
    msg = uid + ',' + ';'.join(gift_list_new) + '\n'
    final_f.write(msg)
result_file.close()
final_f.close()




