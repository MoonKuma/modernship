#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : ItemCost.py
# @Author: MoonKuma
# @Date  : 2019/3/5
# @Desc  : item cost


type_list = [6,10,13,9,16,2]
vip_tuple_list = ['(0)','(1,2,3,4,5,6,7)','(8,9,10,11,12)','(13,14,15,16)','(17)','(18)','(19)']
vip_tuple_name = ['0','1~7','8~12','13~16','17','18','19']
op = 'mysql -uroot -pr00tr00t -h10.66.179.61 test -e \"'
sql1 = 'select item_id,0 as trans,max(quality),sum(diamond_round) as diamond,sum(times),sum(users) from ItemDiamondCostSum where type=#typeName# group by item_id order by diamond desc'
sql2 = 'select vip, sum(case quality when 0 then diamond_round else 0 end) as q0, sum(case quality when 1 then diamond_round else 0 end) as q1, sum(case quality when 2 then diamond_round else 0 end) as q2, sum(case quality when 3 then diamond_round else 0 end) as q3, sum(case quality when 4 then diamond_round else 0 end) as q4, sum(case quality when 5 then diamond_round else 0 end) as q5, sum(case quality when 6 then diamond_round else 0 end) as q6, sum(case quality when 7 then diamond_round else 0 end) as q7  from ItemDiamondCostSum where type=#typeName# group by vip'
sql3 = 'select vip,item_id,max(quality), sum(diamond_round) as diamond,sum(times),sum(users) from ItemDiamondCostSum where type=#typeName# and quality in (select max(quality) from ItemDiamondCostSum where type=#typeName#) group by vip,item_id;'
sql4 = 'select #vipname# as vip_kind, type,(case quality when 0 then diamond_round else 0 end) as q0, sum(case quality when 1 then diamond_round else 0 end) as q1, sum(case quality when 2 then diamond_round else 0 end) as q2, sum(case quality when 3 then diamond_round else 0 end) as q3, sum(case quality when 4 then diamond_round else 0 end) as q4, sum(case quality when 5 then diamond_round else 0 end) as q5, sum(case quality when 6 then diamond_round else 0 end) as q6, sum(case quality when 7 then diamond_round else 0 end) as q7, sum(diamond_round) from ItemDiamondCostSum where type in (6,10,13,9,16,2) and vip in #vip_set# group by type;'
sql_type = [sql1,sql2,sql3]
sql_vip = [sql4]
sql_name = ['type1','type2','type3','vip1']

ed = '\" > /data/tmpStatistic/item_cost/result_#filename#.txt'


def search_type():
    for type_name in type_list:
        type_name_str = str(type_name)
        for sql in sql_type:
            file_name = sql_name[sql_type.index(sql)] + '_' + type_name_str
            sql_read = op + sql.replace('#typeName#', type_name_str) + ed.replace('#filename#', file_name)
            print(sql_read)


def search_vip():
    for vip_range in vip_tuple_list:
        vip_name = vip_tuple_name[vip_tuple_list.index(vip_range)]
        sql = sql4.replace('#vip_set#', vip_range).replace('#vipname#', '\''+vip_name+'\'')
        print sql


search_type()