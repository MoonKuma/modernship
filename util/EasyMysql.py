#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : EasyMysql.py
# @Author: MoonKuma
# @Date  : 2018/9/12
# @Desc  : Some useful tools in in mysql computing

from is_valid_data import is_legal_input


class EasyMysql:

    def __init__(self):
        self.cycle = 100

    def set_cycle(self, cycle):
        self.cycle = cycle

    def sql_value_str(self, value_list):
        value_str = '\'' + str(value_list[0]) + '\''
        if len(value_list) > 1:
            for value_index in range(1, len(value_list)):
                value_str = value_str + ',\'' + str(value_list[value_index]) + '\''
        return value_str

    def batch_commit(self, sql_str_list, cursor, db):
        print '[Batch Commit] Start committing to db with ' + str(len(sql_str_list)) + ' commend lines'
        cycle = self.cycle
        count = 0
        list_len = len(sql_str_list)
        for line in sql_str_list:
            count += 1
            cursor.execute(line)
            if count % cycle == 0 or count >= list_len:
                db.commit()
        db.commit()

    def combine_where_clause(self, input_dict, use_channels=True, use_zoneids=True):

        # only applied for standard input dict
        is_legal_input(input_dict)
        where_clause = ''
        if len(input_dict['channel_list']) and use_channels:
            where_clause = where_clause + 'and channel in (' + self.sql_value_str(input_dict['channel_list']) + ')'
        if len(input_dict['zone_list']) and use_zoneids:
            where_clause = where_clause + 'and zoneid in (' + self.sql_value_str(input_dict['zone_list']) + ')'
        return where_clause