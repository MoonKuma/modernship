#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : parse_file.py
# @Author: MoonKuma
# @Date  : 2018/12/21
# @Desc  : parse files into shop table and vip table

import os

original = 'Audit'
shop_start = 'shop'
vip_start = 'vip'

file_path = r'C:\Users\7q\PycharmProjects\modernship\conf\ipo_conf'

file_list = os.listdir(file_path)

save_name = 'new_audit_item.txt'
result_set = set()


def file_full_path(file_name):
    return file_path + '\\' + file_name



for file_name in file_list:
    if file_name.startswith(original):
        with open(file_full_path(file_name)) as file_op:
            for line in file_op.readlines():
                line = line.strip()
                array = line.split('\t')
                if array[0].isdigit():
                    result_set.add(array[0])

    elif file_name.startswith(shop_start):
        with open(file_full_path(file_name)) as file_op:
            for line in file_op.readlines():
                line = line.strip()
                array = line.split('\t')
                if array[0].isdigit():
                    result_set.add(array[3])

    elif file_name.startswith(vip_start):
        with open(file_full_path(file_name)) as file_op:
            for line in file_op.readlines():
                line = line.strip()
                array = line.split('\t')
                if array[0].isdigit():
                    modify = '34_' + array[3]
                    result_set.add(modify)

print(result_set)
print(len(result_set))

with open(file_full_path(save_name),'w') as file_wt:
    file_wt.write('id\t#NameTag\n')
    for key in result_set:
        write_str = key +'\t占位\n'
        file_wt.write(write_str)

