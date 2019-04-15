#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Bug_190124.py
# @Author: MoonKuma
# @Date  : 2019/1/24
# @Desc  : bug on 2019/01/24, check log and compute repayment


import math

# about how many each user received
# grep -h -s -E ',AddMail,|,MailCache,' /data/stat/Log_?????/ModernShipStat_2019-01-2[3-4]*|awk -F ',' '{if($1<="2019-01-24 15:02:00" && (($4=="AddMail" && $16==67)||($3=="MailCache" && $6==67)))print $0}'|awk -F ',' '{OFS=",";if($4=="AddMail") print $2,$3,$15; if($3=="MailCache")print $2,$4,$5}'|sort|uniq|awk -F ',' '{sum[$1","$2]=sum[$1","$2]+1} END {OFS=",";for(i in sum)print i,sum[i]}' > /data/tmpStatistic/bug__0124/zone_user_times_0124_mail.txt
# grep -h -s -E ',AddProp,' /data/stat/Log_?????/ModernShipStat_2019-01-2[3-4]*|awk -F ',' '{if($1<="2019-01-24 15:02:00" && ($4=="AddProp" && $15==151 && $16==20146))print $2","$3}'|awk -F '|' '{sum[$1]=sum[$1]+1} END {OFS=",";for(i in sum)print i,sum[i]}' > /data/tmpStatistic/bug__0124/zone_user_times_0124_prop.txt



# about the whole uid list
# grep -h -s -E ',AddProp,' /data/stat/Log_?????/ModernShipStat_2019-01-2[3-4]*|awk -F ',' '{if($1<="2019-01-24 15:02:00" && $15==139 )print $3}'|sort|uniq > /data/tmpStatistic/bug__0124/all_users_0124.txt


reward_str = '20149;1;1;20146;1;3;10001;1;30000;20149;1;2;20146;1;5;10001;1;50000;20148;1;1;20146;1;10;10001;1;100000'
world_dict = dict()

# world game
with open('conf/world_game.txt', 'r') as world_conf:
    for line in world_conf.readlines():
        if line.startswith('#'):
            continue
        line = line.strip()
        array = line.split('\t')
        from_z = int(array[0])
        to_z = int(array[1])
        world = array[2]
        if world not in world_dict.keys():
            world_dict[world] = dict()
            world_dict[world]['range'] = list()
        world_dict[world]['range'].append([from_z, to_z])



# world round finished
with open('conf/world_round.txt', 'r') as world_round:
    for line in world_round.readlines():
        if line.startswith('#'):
            continue
        line = line.strip()
        array = line.split('\t')
        world = array[0]
        round_n = int(array[1]) - 1
        world_dict[world]['round'] = round_n

print(world_dict)

# get uid received
user_received = dict()
received_user = set()
with open('conf/zone_user_times_0124.txt', 'r') as all_users:
    for line in all_users.readlines():
        line = line.strip()
        array = line.split(',')
        uid = array[1]
        received_user.add(uid)
        received = int(array[2])
        user_received[uid] = received
print('len(user_received.keys)', len(user_received.keys()))


# how many one zoneid should receive
def should_receive(zoneid):
    zone  = int(zoneid)
    for world in world_dict.keys():
        range_list = world_dict[world]['range']
        for zone_range in range_list:
            if zone_range[0] <= zone <= zone_range[1]:
                return world_dict[world].setdefault('round',0)
    print('Zone range not found,zoneid:',zoneid)
    raise RuntimeError


# get uid reward
reward_dict = dict()
all_users = set()
with open('conf/all_users_0124.txt', 'r') as user_receive:
    for line in user_receive.readlines():
        line = line.strip()
        array = line.split(',')
        zoneid = int(array[0])
        uid = array[1]
        all_users.add(uid)
        received = user_received.setdefault(uid, 0)
        should_rec = should_receive(zoneid)
        now_receive = received/3.0
        if now_receive >= should_rec:
            continue
        payback = should_rec - math.floor(now_receive)
        if payback != 0:
            reward_dict[uid] = int(payback)

print('len(all_users)', len(all_users))
print('len(reward_dict.keys())', len(reward_dict.keys()))

with open('result/bug_result_0124.txt', 'w') as result:
    for uid in reward_dict.keys():
        reward_times = reward_dict[uid]
        reward_list = list()
        for i in range(0, reward_times):
            reward_list.append(reward_str)
        str_wrt = uid + ',' + ';'.join(reward_list) + '\n'
        result.write(str_wrt)



print('uid who receive no reward in the past')
times = 0
for uid in all_users:
    if uid not in received_user:
        print(uid)
        times += 1
    if times > 10:
        break


print('uid who receive no reward in the future')
times = 0
for uid in all_users:
    if uid not in reward_dict.keys():
        print(uid)
        times += 1
    if times > 10:
        break





