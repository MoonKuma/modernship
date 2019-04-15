#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : VipActivePayChannel.py
# @Author: MoonKuma
# @Date  : 2018/10/19
# @Desc  : Vip payment and active
# This is used to compare different quality of old users from channels

# mysql(big_data):
# #YIYOU# select date,vip_level,count(uid),ceil(sum(pay_money/100)) from user_active_extend where date>'2018-09-01' and channel in ('1099','109902','109903','109906','1105','109907','109905') group by date,vip_level order by date,vip_level limit 200;
# #XIONGMAOWAN# select date,vip_level,count(uid),ceil(sum(pay_money/100)) from user_active_extend where date>'2018-09-01' and channel in ('1100','1104') group by date,vip_level order by date,vip_level limit 200;
# select date,channel,ceil(sum(pay_money/100)),count(uid) from user_active_extend where date>='2018-09-01' and channel in ('1099','109902','109903','109906','1105','109907','109905') group by date,channel order by date;
# select date,channel,ceil(sum(pay_money/100)),count(uid) from user_active_extend where date>='2018-09-01' and channel in ('1099','109902','109903','109906','1105','109907','109905') and date=regdate group by date,channel order by date limit 10;
# select date,channel,format(ceil(sum(pay_money/100))/count(uid),2) from user_active_extend where date>='2018-09-01' and channel in ('1099','109902','109903','109906','1105','109907','109905') and date=regdate group by date,channel order by date;

