#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : LogCrew.py
# @Author: MoonKuma
# @Date  : 2018/9/11
# @Desc  : Check crew related logs
# grep -h -s 'DceGuide' ../Log_?????/ModernShipStat_2018-09-2[5-6]*|awk -F ',' '{if($1>="2018-09-25 12:00:00")max[$3]=$15} END {OFS=",";for(i in max)print i,max[i]}'|awk -F ',' '{sum[$2]=sum[$2]+1} END {OFS=",";for(k in sum)print k,sum[k]}'|sort -t ',' -k 1|more

