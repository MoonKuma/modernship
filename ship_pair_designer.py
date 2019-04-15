#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : ShipCorrelation.py
# @Author: MoonKuma
# @Date  : 2018/10/30
# @Desc  : Check ship correlation from log
# cmd : grep -h -s ',GroupInfo,' ModernShipStat_2018-10-30*|awk -F ',' '{last[$3]=$16} END {OFS=",";for(i in last)print i,last[i]}'


from util.LogQuery import LogQuery
import conf.ConfParameters as ConfParameters
import sys

class ShipCorrelation(LogQuery):

    def __init__(self, start_date, end_date):
        super(ShipCorrelation, self).__init__(start_date, end_date)
        pass

    def analyse_log(self, log_data):
        ship_dict = dict()
        for line in log_data:
            line = line.strip()
            array = line.split(',')
            if len(array) == 2:
                ship_list = array[1].split('|')
                ship_list = self.__clean_ship_list(ship_list)
                self.__pair_up(ship_list, ship_dict)
        return ship_dict

    def report_ship_table(self, ship_dict, file_name):
        file_open = open(file_name, 'w')
        try:
            for ship_out in ship_dict.keys():
                for ship_in in ship_dict[ship_out].keys():
                    str_wri = ship_out + ',' + ship_in + ',' + str(ship_dict[ship_out][ship_in]) + '\n'
                    file_open.write(str_wri)
        finally:
            file_open.close()
        return

    @staticmethod
    def execute(start_date, end_date, file_name):
        ship_corr = ShipCorrelation(start_date, end_date)
        log_file = ship_corr.log_file_str()
        cmd = 'grep -h -s \',GroupInfo,\' ' + log_file + '|awk -F \',\' \'{last[$3]=$16} END {OFS=\",\";for(i in last)print i,last[i]}\''
        val = ship_corr.cmd_compute(cmd)
        ship_dict = ship_corr.analyse_log(val)
        ship_corr.report_ship_table(ship_dict, file_name)
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

# main
if __name__ == '__main__':
    start_date = sys.argv[1]
    end_date = sys.argv[2]
    file_name = ConfParameters.ConfParameters().save_path + 'Ship_Correlation_' + start_date + '_' + end_date + '.txt'
    ShipCorrelation.execute(start_date, end_date, file_name)