#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : LogChipRaise.py
# @Author: MoonKuma
# @Date  : 2018/11/28
# @Desc  :
# SQL : select date,vip,count(uid), sum(diamond) from (select date,uid,(select max(vip_level) from user_active where date=a.date and uid=a.uid) as vip,sum(cash+diamond) as diamond from diamond_detail as a where moneytype=97 and keyword='CostDiamond' group by date,uid)c group by date,vip limit 200;
# 抽奖：2018-11-28 14:40:56,10001,72382022982635377,CostDiamond,85,10171045201803261813422269697,1,2018-03-28 11:13:08,82053,10001,2,16,42953967927303,1045,97,3000,0,25860,,,,,
# 升星：2018-11-28 14:41:34,10001,72382022982635377,ChipUpStar,85,10171045201803261813422269697,1,2018-03-28 11:13:08,82053,10001,2,16,42953967927303,1045,42953971590153,163101,0,1,1,,,,
# 进化：2018-11-28 14:42:47,10001,72382022982635377,ChipEvolve,85,10171045201803261813422269697,1,2018-03-28 11:13:08,81053,10001,2,16,42953967927303,1045,42953971590151,165302,0,1,,,,,
# cmd : grep -h -s -E ',ChipEvolve,|,ChipUpStar,' ../Log_?????/ModernShipStat_2018-11-2*|awk -F ',' '{OFS=",";print $3,$4,$12,$15,$16,$18}'|awk -F ',' '{max_vip[$1","$4","$5]=$3;if($2=="ChipEvolve"){max_ev[$1","$4","$5]=$6};if($2=="ChipUpStar"){max_star[$1","$4","$5]=$6}} END {OFS=",";for(i in max_vip)print i,max_vip[i],(max_ev[i]==""?0:max_ev[i]),(max_star[i]==""?0:max_star[i])}' > /data/tmpStatistic/log_chip_ev_us_1128.txt

import sys

bad_chip = ['163103', '163102', '163101', '164303', '164202', '164101']
r6_chip = ['166302', '166301', '166202', '166201', '166102', '166101']
r5_chip = ['165302', '165301', '165202', '164201', '165102', '165101']

def dissect_files(file_read, file_write):
    global bad_chip
    global r6_chip
    global r5_chip
    result_dict = dict()
    with open(file_read, 'r') as fh:
        for line in fh.readlines():
            line = line.strip()
            array = line.split(',')
            if len(array) < 6:
                continue
            uid = array[0]
            chip_uid = array[1]
            chip_id = array[2]
            if chip_id not in r6_chip:
                continue
            vip = array[3]
            ev_lv = array[4]
            start_lv = array[5]
            if uid not in result_dict.keys():
                result_dict[uid] = dict()
            if result_dict[uid].setdefault('max_star',0) <= int(start_lv):
                result_dict[uid]['max_star'] = int(start_lv)
                result_dict[uid]['max_star_ev'] = ev_lv
                result_dict[uid]['chip_id'] = chip_id
                result_dict[uid]['chip_uid'] = chip_uid
            if result_dict[uid].setdefault('vip', 0) <= int(vip):
                result_dict[uid]['vip'] = int(vip)
    with open(file_write, 'w') as fh_write:
        for uid in result_dict:
            str_writ = uid + ',' + str(result_dict[uid]['vip']) + ',' + result_dict[uid]['chip_id'] + ',' + result_dict[uid]['chip_uid'] + ',' + str(result_dict[uid]['max_star']) + ',' + result_dict[uid]['max_star_ev']
            str_writ += '\n'
            fh_write.write(str_writ)


file1 = sys.argv[1]
file2 = sys.argv[2]
dissect_files(file1, file2)

