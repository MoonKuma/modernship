#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : ShipCorrelation.py
# @Author: MoonKuma
# @Date  : 2018/10/30
# @Desc  : Check ship correlation from log
# cmd : grep -h -s ',GroupInfo,' ModernShipStat_2018-10-30*|awk -F ',' '{last[$3]=$16} END {OFS=",";for(i in last)print i,last[i]}'


from util.LogQuery import LogQuery
import conf.ConfParameters as ConfParameters
from collections import OrderedDict
import copy
import sys

class ShipCorrelation(LogQuery):

    def __init__(self, start_date, end_date):
        super(ShipCorrelation, self).__init__(start_date, end_date)
        self.ship_dict = dict()
        self.patten_dict = dict()
        pass

    def analyse_log(self, log_data):
        self.ship_dict = dict()
        for line in log_data:
            line = line.strip()
            array = line.split(',')
            if len(array) == 2:
                ship_list = array[1].split('|')
                ship_list = self.__clean_ship_list(ship_list)
                self.__pair_up(ship_list, self.ship_dict)
        return self.ship_dict

    def analyse_log_full_compare(self, log_data):
        self.ship_dict = dict()
        for line in log_data:
            line = line.strip()
            array = line.split(',')
            if len(array) == 2:
                ship_list = array[1].split('|')
                ship_list = self.__clean_ship_list(ship_list)
                self.__pair_up_full(ship_list)
        return self.ship_dict

    def analyse_single_compare(self, log_data):
        self.ship_dict = dict()
        self.patten_dict = dict()
        for line in log_data:
            line = line.strip()
            array = line.split(',')
            if len(array) == 2:
                ship_list = array[1].split('|')
                if '' in ship_list:
                    ship_list.remove('')
                if len(ship_list) == 7:
                    ship_list_cp = ','.join(sorted(ship_list))
                    self.ship_dict[ship_list_cp] = self.ship_dict.setdefault(ship_list_cp, 0) + 1
                    self.patten_dict[ship_list_cp] = ','.join(ship_list)
        return self.ship_dict, self.patten_dict

    def report_ship_table(self, ship_dict, file_name):
        ord_dict = OrderedDict(sorted(ship_dict.items(), key=lambda t: -1 * t[1]))
        with open(file_name, 'w') as file_open:
            for key in ord_dict.keys():
                msg = key + ',' + str(ord_dict[key]) + '\n'
                file_open.write(msg)
        return

    def report_ship_table_single(self, ship_dict, patten_dict, file_name):
        ord_dict = OrderedDict(sorted(ship_dict.items(), key=lambda t: -1 * t[1]))
        with open(file_name, 'w') as file_open:
            for key in ord_dict.keys():
                msg = key + '|' + str(ord_dict[key]) + '|' + str(patten_dict[key]) + '\n'
                file_open.write(msg)
        return

    @staticmethod
    def execute(start_date, end_date, file_name):
        ship_corr = ShipCorrelation(start_date, end_date)
        log_file = ship_corr.log_file_str()
        cmd = 'grep -h -s \',GroupInfo,\' ' + log_file + '|awk -F \',\' \'{last[$3]=$16} END {OFS=\",\";for(i in last)print i,last[i]}\''
        val = ship_corr.cmd_compute(cmd)
        # ship_dict = ship_corr.analyse_log_full_compare(val)
        # ship_corr.report_ship_table(ship_dict, file_name)
        ship_dict, patten_dict = ship_corr.analyse_single_compare(val)
        ship_corr.report_ship_table_single(ship_dict, patten_dict, file_name)

        return

    # Private methods
    def __clean_ship_list(self, ship_list):
        if '' in ship_list:
            ship_list.remove('')
        ship_list = sorted(ship_list)
        return ship_list  # must return ?

    def __pair_up(self, clean_ship_list, ship_dict):
        if len(clean_ship_list) < 2:
            return
        length = len(clean_ship_list)
        for i in range(0, length):
            for j in range(0, length):
                ship_out = clean_ship_list[i]
                ship_in = clean_ship_list[j]
                if ship_out not in ship_dict.keys():
                    ship_dict[ship_out] = dict()
                ship_dict[ship_out][ship_in] = ship_dict[ship_out].setdefault(ship_in, 0) + 1
        pass

    def __pair_up_full(self, clean_ship_list):
        copy_list_big = copy.copy(clean_ship_list)
        if len(clean_ship_list) < 2:
            return
        for ship in clean_ship_list:
            copy_list_big.remove(ship)
            copy_list = copy.copy(copy_list_big)
            self.__recursive_pair(ship, copy_list)

    def __adding_dict(self, key_pair):
        self.ship_dict[key_pair] = self.ship_dict.setdefault(key_pair,0) +1

    def __recursive_pair(self, current_key, list_remain):
        copy_list_big = copy.copy(list_remain)
        if len(list_remain) == 0:
            return
        for list_item in list_remain:
            new_key = str(current_key) + '-' + str(list_item)
            self.__adding_dict(new_key)
            copy_list_big.remove(list_item)
            copy_list = copy.copy(copy_list_big)
            self.__recursive_pair(new_key, copy_list)

    def test_pair(self):
        self.ship_dict = dict()
        test_list1 = [1, 2, 3, 4, 5, 6, 7]
        test_list2 = [8, 2, 3, 4, 5, 6, 7]
        test_list3 = [8, 9, 3, 4, 5, 6, 7]
        test_list = [test_list1, test_list2, test_list3]
        for test in test_list:
            clean_list = self.__clean_ship_list(test)
            self.__pair_up_full(clean_list)
        ord_dict = OrderedDict(sorted(self.ship_dict.items(), key=lambda t: -1*t[1]))
        for item in ord_dict.items():
            print(item)


# main
if __name__ == '__main__':
    # obj = ShipCorrelation('2018-10-30', '2018-10-30')
    # obj.test_pair()
    start_date = sys.argv[1]
    end_date = sys.argv[2]
    file_name = ConfParameters.ConfParameters().save_path + 'Ship_Correlation_single' + start_date + '_' + end_date + '.txt'
    ShipCorrelation.execute(start_date, end_date, file_name)