#!/usr/bin/env python
# -*- coding: utf-8 -*-

import conf.ConfParameters as ConfParameters
import util.DateList as DateList
import util.EasyXls as EasyXls
import os
import MySQLdb
import xlwt
import sys
import calendar
import datetime
import sys   #reload()之前必须要引入模块
import re

reload(sys)
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)



class NewFuncgf_nov25():
    def __init__(self):
        self.channel = ''
        self.viplist=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
        # initial mysql-db
        mysqlStatInfo = {'host': '10.66.127.43', 'port': 3306, 'user': 'root', 'passwd': 'r00tr00t'}
        self.db = MySQLdb.connect(host=mysqlStatInfo['host'], port=mysqlStatInfo['port'], user=mysqlStatInfo['user'],
                             passwd=mysqlStatInfo['passwd'], db='modernship_gf_stat_base', charset='utf8')
        self.cursor = self.db.cursor()
        # initial xls writer
        self.wbk = xlwt.Workbook()
        self.style = xlwt.XFStyle()
        self.borders = xlwt.Borders()
        self.borders.left = 1
        self.borders.right = 1
        self.borders.top = 1
        self.borders.bottom = 1
        self.style.borders = self.borders
        self.sheet = ''

        self.itembuyratio = dict()
        self.itemavgtimes = dict()
        self.itembuypeople = dict()
        self.activepeople = dict()

        #missionbox
        self.box1 = dict()
        self.box2 = dict()
        self.box3 = dict()
        self.box4 = dict()
        self.totaleve = dict()

        self.zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')

    def formalchannel(self):
        self.channel = ''

#####write xlwt
    def xls_writeone_list(self,sheet,name,somekeys, somedict, indexi=0, indexj=0):
        # xls_writer = EasyXls.EasyXls()

        sheet.write(indexi, indexj, unicode(name))
        indexi += 1
        for i in range(len(somekeys)):
            sheet.write(indexi + i, 0, somekeys[i])
            try:
                dictlist = somedict[somekeys[i]].split(",")
            except:
                dictlist = ["None"]
            for j in range(len(dictlist)):
                try:
                    sheet.write(i + indexi, j + indexj + 1, eval(dictlist[j]),self.style)
                except:
                    sheet.write(i + indexi, j + 1+indexj,'',self.style)

    def sheetadd(self,strsheet):
        # strsheet is a string
        self.sheet = self.wbk.add_sheet(strsheet, cell_overwrite_ok=True)

    def xls_writetwo_dict(self,sheet,name,somekeyy,somekeyx,somedict,indexi=0, indexj=0):
        #sheet is func sheetadd's return
        #name is what you want to write
        #somekey is the index you want to write
        #some dict is the content you wang to write

        sheet.write(indexi, indexj, unicode(name))
        indexi += 2
        for i in range(len(somekeyy)):
            sheet.write(i + indexi, indexj, somekeyy[i],self.style)
        for j in range(len(somekeyx)):
            sheet.write(indexi-1, j + 1+indexj, somekeyx[j],self.style)
            for i in range(len(somekeyy)):
                try:
                    sheet.write(i + indexi, j + 1+indexj, somedict[somekeyx[j]].setdefault(somekeyy[i],''),self.style)
                except:
                    sheet.write(i + indexi, j + 1+indexj,'',self.style)

    def end_all(self):
        file_name ='/data/tmpStatistic/project_modern_ship/result/'+self.__class__.__name__+'.xls'
        self.db.close()
        self.wbk.save(file_name)


    def runwrite(self):

        self.Onlinegift('2018-11-22')
        self.sheetadd(unicode('在线时长礼包领取'))
        self.xls_writetwo_dict(self.sheet, 'box1', self.viplist, self.datelist, self.box1)
        self.xls_writetwo_dict(self.sheet, 'box2', self.viplist, self.datelist, self.box2,25)
        self.xls_writetwo_dict(self.sheet, 'box3', self.viplist, self.datelist, self.box3,50)
        self.xls_writetwo_dict(self.sheet, 'total', self.viplist, self.datelist, self.totaleve,75)

        self.onlinetime('2018-11-01')
        self.sheetadd(unicode('在线时长非当天注册'))
        self.xls_writetwo_dict(self.sheet, unicode('老玩家人均在线时长'), self.viplist, self.datelist,self.onlinetimeoldtime)
        self.xls_writetwo_dict(self.sheet, unicode('老玩家人数'), self.viplist, self.datelist, self.onlinetimeoldpeople, 25)
        self.sheetadd(unicode('在线时长new'))
        self.xls_writetwo_dict(self.sheet, unicode('新玩家人均在线时长'), self.viplist, self.datelist,self.onlinetimenewtime)
        self.xls_writetwo_dict(self.sheet, unicode('新玩家人数'), self.viplist, self.datelist, self.onlinetimenewpeople, 25)

        self.BlocBossBattle('2018-11-01')
        self.sheetadd(unicode('军团世界boss参与(20级以上)'))
        self.xls_writetwo_dict(self.sheet, unicode('20级以上玩家参与度'), self.viplist, self.datelist, self.blocbossratio)
        self.xls_writetwo_dict(self.sheet, unicode('20级以上每日活跃人数'), self.viplist, self.datelist, self.blocbosspeople, 25)

        self.AISystem("2018-11-22")
        self.sheetadd(unicode('AI抽取情况（耗钻）'))
        self.xls_writetwo_dict(self.sheet, unicode('抽取人数'), self.viplist, self.datelist, self.aipeople)
        self.xls_writetwo_dict(self.sheet, unicode('人均每日抽取次数'), self.viplist, self.datelist, self.aiavgtimes, 25)
        self.xls_writetwo_dict(self.sheet, unicode('抽取人数占比'), self.viplist, self.datelist, self.airatio, 50)

        self.Chip_evolve()
        self.sheetadd(unicode('芯片进化情况'))
        self.xls_writetwo_dict(self.sheet, unicode('抽取人数1122-1211'), self.chiplist, self.starlist, self.chippeople)

        self.TechInfo('2018-12-11')
        self.sheetadd(unicode('科技情况'))
        self.xls_writetwo_dict(self.sheet, unicode('科技人数1211'), self.translist, self.viplist, self.techdict)
        self.xls_writetwo_dict(self.sheet, unicode('科技人均等级1211'), self.translist, self.viplist, self.techleveldict, 50)

        self.Tech_Gacha("2018-11-01")
        self.sheetadd(unicode('科技抽取情况（耗钻）'))
        self.xls_writetwo_dict(self.sheet, unicode('抽取人数'), self.viplist, self.datelist, self.techpeople)
        self.xls_writetwo_dict(self.sheet, unicode('人均每日抽取次数'), self.viplist, self.datelist, self.techavgtimes, 25)
        self.xls_writetwo_dict(self.sheet, unicode('抽取人数占比'), self.viplist, self.datelist, self.techratio, 50)


        print(datetime.datetime.now())


        self.end_all()


    def naval_ports_buy(self, itembegindate, itemenddate):
        #naval ports
        self.itemlist=[20143,20141,134600,20002,134200,134100,134500,40067,134400,134300,40066,50045,10001]
        self.itembuyratio = dict()
        self.itemavgtimes = dict()
        self.itembuypeople = dict()
        self.activepeople = dict()
        for i in self.viplist:
            self.itembuyratio[i] = dict()
            self.itemavgtimes[i] = dict()
            self.itembuypeople[i] = dict()
            self.activepeople[i] = dict()
        sqlstr = 'select *,peoplenum/totalnums,times/peoplenum as buyratio from (select mvip,count(uid) as totalnums from (select uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date between \"'+itembegindate+'\" and \"'+ itemenddate +'\" '+self.channel+' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as c group by mvip) as d left join (select mvip,itemid,count(distinct(uid)) as peoplenum,sum(times) as times from (select a.*,b.mvip from (select uid,itemid,sum(times) as times from modernship_stat_busi.shopexchange where shopid=11 group by uid,itemid) as a inner join (select uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date between \"'+itembegindate+'\" and \"'+ itemenddate +'\" '+self.channel+' and uid not in (select uid from modernship_stat_busi.uid_block_list)  group by uid) as b on a.uid=b.uid) as c group by mvip,itemid) as e on d.mvip=e.mvip;'

        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        # | mvip | totalnums | mvip | itemid | peoplenum | times | buyratio |times/peoplenum
        # +------+-----------+------+--------+-----------+-------+----------+
        # | 0 | 62310 | 0 | 20002 | 57 | 215 | 0.0009 |1.002
        # | 0 | 62310 | 0 | 134200 | 55 | 85 | 0.0009 |
        # | 0 | 62310 | 0 | 20141 | 55 | 115 | 0.0009 |
        if alldata:
            for rec in alldata:
                self.itembuyratio[rec[0]][rec[3]] = rec[6]
                self.itemavgtimes[rec[0]][rec[3]] = rec[7]
                self.itembuypeople[rec[0]][rec[3]] = rec[4]
                self.activepeople[rec[0]][rec[3]] = rec[1]
        print(self.itembuyratio)

    def horn_buy(self, itembegindate, itemenddate):
        for i in self.viplist:
            self.itembuyratio[i] = dict()
            self.itemavgtimes[i] = dict()
            self.itembuypeople[i] = dict()
            self.activepeople[i] = dict()
        sqlstr = 'select *,peoplenum/totalnums,times/peoplenum as buyratio from (select mvip,count(uid) as totalnums from (select uid,max(vip_level) as mvip from modernship_korea_stat_base.user_active_extend where date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' group by uid) as c group by mvip) as d left join (select mvip,itemid,count(distinct(uid)) as peoplenum,sum(times) as times from (select a.*,b.mvip from (select uid,itemid,sum(times) as times from modernship_korea_stat_base.shopexchange where shopid=12 group by uid,itemid) as a inner join (select uid,max(vip_level) as mvip from modernship_korea_stat_base.user_active_extend where date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' group by uid) as b on a.uid=b.uid) as c group by mvip,itemid) as e on d.mvip=e.mvip;'
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        if alldata:
            for rec in alldata:
                self.itembuyratio[rec[0]][rec[3]] = rec[6]
                self.itemavgtimes[rec[0]][rec[3]] = rec[7]
                self.itembuypeople[rec[0]][rec[3]] = rec[4]
                self.activepeople[rec[0]][rec[3]] = rec[1]
        self.itemlist=[20038,20039]

#new
    def arena_battle(self,itembegindate, itemenddate):
        #arena_battle
        self.datelist = []
        self.joinratio = dict()
        self.joinavgtimes = dict()
        self.joinpeople = dict()
        self.activepeople = dict()
        sqlstr='select d.date,mvip,totalnums,peoplenum,times,times/peoplenum,peoplenum/totalnums from  (select date,mvip,count(uid) as totalnums from  (select date,uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where level>=16 and date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + '  and uid not in (select uid from modernship_stat_busi.uid_block_list) group by date,uid) as c group by date,mvip) as d left join  (select date,sum(peoplenum) as peoplenum,viplevel,sum(times) as times from modernship_stat_busi.behavior_template where keyword="ArenaBattle"' + self.channel +' group by date,viplevel) as a on a.viplevel=d.mvip and a.date=d.date;'
# | date       | mvip | totalnums | peoplenum | times |avgtimes|joinratio
# +------------+------+-----------+-----------+-------+
# | 2018-09-25 |    0 |      4911 |      1408 |  5373 |
# | 2018-09-25 |    1 |      1335 |       588 |  2379 |
# | 2018-09-25 |    2 |       316 |       116 |   497 |
# | 2018-09-25 |    3 |       411 |       175 |   611 |
# | 2018-09-25 |    4 |       475 |       185 |   640 |
# | 2018-09-25 |    5 |       309 |       144 |   476 |
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        if alldata:
            for rec in alldata:
                self.datelist.append(str(rec[0]))
            self.datelist = sorted(list(set(self.datelist)))
            for date in self.datelist:
                self.joinratio[date] = dict()
                self.joinavgtimes[date] = dict()
                self.joinpeople[date] = dict()
                self.activepeople[date] = dict()
            for rec in alldata:
                self.joinratio[str(rec[0])][rec[1]] = rec[6]
                self.joinavgtimes[str(rec[0])][rec[1]] = rec[5]
                self.joinpeople[str(rec[0])][rec[1]] = rec[3]
                self.activepeople[str(rec[0])][rec[1]] = rec[2]


    def champion_battle(self,itembegindate, itemenddate):
        self.datelist = []
        self.joinratio = dict()
        self.joinavgtimes = dict()
        self.joinpeople = dict()
        self.activepeople = dict()
        sqlstr='select d.date,mvip,totalnums,peoplenum,times,times/peoplenum,peoplenum/totalnums from  (select date,mvip,count(uid) as totalnums from  (select date,uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where level>=36 and date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + '  and uid not in (select uid from modernship_stat_busi.uid_block_list) group by date,uid) as c group by date,mvip) as d left join  (select date,sum(peoplenum) as peoplenum,viplevel,sum(times) as times from modernship_stat_busi.behavior_template where keyword="ChampionBattle"' + self.channel +' group by date,viplevel) as a on a.viplevel=d.mvip and a.date=d.date;'
# | date       | mvip | totalnums | peoplenum | times |avgtimes|joinratio
# +------------+------+-----------+-----------+-------+
# | 2018-09-25 |    0 |      4911 |      1408 |  5373 |
# | 2018-09-25 |    1 |      1335 |       588 |  2379 |
# | 2018-09-25 |    2 |       316 |       116 |   497 |
# | 2018-09-25 |    3 |       411 |       175 |   611 |
# | 2018-09-25 |    4 |       475 |       185 |   640 |
# | 2018-09-25 |    5 |       309 |       144 |   476 |
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        if alldata:
            for rec in alldata:
                self.datelist.append(str(rec[0]))
            self.datelist = sorted(list(set(self.datelist)))

            for date in self.datelist:
                self.joinratio[date] = dict()
                self.joinavgtimes[date] = dict()
                self.joinpeople[date] = dict()
                self.activepeople[date] = dict()

            for rec in alldata:
                self.joinratio[str(rec[0])][rec[1]] = rec[6]
                self.joinavgtimes[str(rec[0])][rec[1]] = rec[5]
                self.joinpeople[str(rec[0])][rec[1]] = rec[3]
                self.activepeople[str(rec[0])][rec[1]] = rec[2]


    def equipmentstrong(self):
        pass

    def skillup(self):
        pass

    def groupset(self):
        pass

    def Militaryrankcollect(self,itembegindate,itemenddate):
        #10.1 everyday join vip
        self.datelist = []
        self.militaryrankcollectoldratio = dict()
        self.militaryrankcollectoldtotalnums =dict()
        self.militaryrankcollectoldavgtimes = dict()
        self.militaryrankcollectnewratio = dict()
        self.militaryrankcollectnewtotalnums =dict()
        self.militaryrankcollectnewavgtimes = dict()
        sqlstr='select d.date,mvip,totalnums,peoplenum,times,peoplenum/totalnums,times/peoplenum from (select date,mvip,count(uid) as totalnums from (select date,uid,max(vip_level) as mvip from modernship_korea_stat_base.user_active_extend where regdate<="2018-11-14" and  date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' group by date,uid) as c group by date,mvip) as d left join (select date,count(distinct(uid)) as peoplenum,viplevel,sum(times) as times from modernship_korea_stat_base.military_template where regdate<="2018-11-14" and keyword="MilitaryRankCollect" '+ self.channel +' group by date,viplevel) as a on a.viplevel=d.mvip and a.date=d.date;'
        # | 2018 - 10 - 04 | 0 | 3017 | 1915 | 8197 |
        # | 2018 - 10 - 04 | 1 | 1206 | 903 | 5103 |
        # | 2018 - 10 - 04 | 2 | 259 | 193 | 1290 |
        # | 2018 - 10 - 04 | 3 | 384 | 297 | 1800 |
        # | 2018 - 10 - 04 | 4 | 453 | 365 | 2414 |
        # | 2018 - 10 - 04 | 5 | 277 | 236 | 1543 |
        # | 2018 - 10 - 04 | 6 | 382 | 324 | 2478 |
        # | 2018 - 10 - 04 | 7 | 189 | 171 | 1318 |
        # | 2018 - 10 - 04 | 8 | 173 | 147 | 1418 |
        # | 2018 - 10 - 04 | 9 | 177 | 157 | 1498 |
        # | 2018 - 10 - 04 | 10 | 108 | 93 | 831 |
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        if alldata:
            for rec in alldata:
                self.datelist.append(str(rec[0]))
            self.datelist = sorted(list(set(self.datelist)))
            for date in self.datelist:
                self.militaryrankcollectoldratio[date] = dict()
                self.militaryrankcollectoldtotalnums[date] = dict()
                self.militaryrankcollectoldavgtimes[date] = dict()
            for rec in alldata:
                self.militaryrankcollectoldratio[str(rec[0])][rec[1]] = rec[5]
                self.militaryrankcollectoldtotalnums[str(rec[0])][rec[1]] = rec[2]
                self.militaryrankcollectoldavgtimes[str(rec[0])][rec[1]] = rec[6]

        #new
        sqlstr = 'select d.date,mvip,totalnums,peoplenum,times,peoplenum/totalnums,times/peoplenum from (select date,mvip,count(uid) as totalnums from (select date,uid,max(vip_level) as mvip from modernship_korea_stat_base.user_active_extend where regdate>"2018-11-14" and  date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' group by date,uid) as c group by date,mvip) as d left join (select date,count(distinct(uid)) as peoplenum,viplevel,sum(times) as times from modernship_korea_stat_base.military_template where regdate>"2018-11-14" and keyword="MilitaryRankCollect" ' + self.channel + ' group by date,viplevel) as a on a.viplevel=d.mvip and a.date=d.date;'
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        if alldata:
            for date in self.datelist:
                self.militaryrankcollectnewratio[date] = dict()
                self.militaryrankcollectnewtotalnums[date] = dict()
                self.militaryrankcollectnewavgtimes[date] = dict()
            for rec in alldata:
                self.militaryrankcollectnewratio[str(rec[0])][rec[1]] = rec[5]
                self.militaryrankcollectnewtotalnums[str(rec[0])][rec[1]] = rec[2]
                self.militaryrankcollectnewavgtimes[str(rec[0])][rec[1]] = rec[6]

        pass

    def MilitaryRankSalary(self,itembegindate,itemenddate):
        self.datelist = []
        self.militaryranksalaryratio = dict()
        self.militaryranksalarytotalnums = dict()
        sqlstr = 'select d.date,mvip,totalnums,peoplenum,times,peoplenum/totalnums,times/peoplenum from (select date,mvip,count(uid) as totalnums from (select date,uid,max(vip_level) as mvip from modernship_korea_stat_base.user_active_extend where date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' group by date,uid) as c group by date,mvip) as d left join (select date,count(distinct(uid)) as peoplenum,viplevel,sum(times) as times from modernship_korea_stat_base.military_template where keyword="MilitaryRankSalary" ' + self.channel + ' group by date,viplevel) as a on a.viplevel=d.mvip and a.date=d.date;'
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        # | date | mvip | totalnums | peoplenum | times |
        # +------------+------+-----------+-----------+-------+
        # | 2018 - 10 - 01 | 0 | 5445 | 1839 | 1882 |
        # | 2018 - 10 - 01 | 1 | 1394 | 959 | 977 |
        # | 2018 - 10 - 01 | 2 | 320 | 257 | 263 |
        # | 2018 - 10 - 01 | 3 | 424 | 358 | 367 |
        # | 2018 - 10 - 01 | 4 | 490 | 420 | 431 |
        if alldata:
            for rec in alldata:
                self.datelist.append(str(rec[0]))
            self.datelist = sorted(list(set(self.datelist)))
            for date in self.datelist:
                self.militaryranksalaryratio[date] = dict()
                self.militaryranksalarytotalnums[date] = dict()
            for rec in alldata:
                self.militaryranksalaryratio[str(rec[0])][rec[1]] = rec[5]
                self.militaryranksalarytotalnums[str(rec[0])][rec[1]] = rec[2]

    def MilitaryRankGacha(self,itembegindate,itemenddate):
        self.datelist = []
        self.militaryrankGacharatio = dict()
        self.militaryrankGachatotalnums = dict()
        sqlstr = 'select d.date,mvip,totalnums,peoplenum,times,peoplenum/totalnums,times/peoplenum from (select date,mvip,count(uid) as totalnums from (select date,uid,max(vip_level) as mvip from modernship_korea_stat_base.user_active_extend where date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' group by date,uid) as c group by date,mvip) as d left join (select date,count(distinct(uid)) as peoplenum,viplevel,sum(times) as times from modernship_korea_stat_base.military_template where keyword="MilitaryRankGacha" ' + self.channel + ' group by date,viplevel) as a on a.viplevel=d.mvip and a.date=d.date;'
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        # | date | mvip | totalnums | peoplenum | times |
        # +------------+------+-----------+-----------+-------+
        # | 2018 - 10 - 01 | 0 | 5445 | 1839 | 1882 |
        # | 2018 - 10 - 01 | 1 | 1394 | 959 | 977 |
        # | 2018 - 10 - 01 | 2 | 320 | 257 | 263 |
        # | 2018 - 10 - 01 | 3 | 424 | 358 | 367 |
        # | 2018 - 10 - 01 | 4 | 490 | 420 | 431 |
        if alldata:
            for rec in alldata:
                self.datelist.append(str(rec[0]))
            self.datelist = sorted(list(set(self.datelist)))
            for date in self.datelist:
                self.militaryrankGacharatio[date] = dict()
                self.militaryrankGachatotalnums[date] = dict()
            for rec in alldata:
                self.militaryrankGacharatio[str(rec[0])][rec[1]] = rec[5]
                self.militaryrankGachatotalnums[str(rec[0])][rec[1]] = rec[2]

    def MilitaryRankGift(self,itembegindate,itemenddate):
        self.datelist = []
        self.militaryrankGiftratio = dict()
        self.militaryrankGifttotalnums = dict()
        sqlstr = 'select d.date,mvip,totalnums,peoplenum,times,peoplenum/totalnums,times/peoplenum from (select date,mvip,count(uid) as totalnums from (select date,uid,max(vip_level) as mvip from modernship_korea_stat_base.user_active_extend where date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' group by date,uid) as c group by date,mvip) as d left join (select date,count(distinct(uid)) as peoplenum,viplevel,sum(times) as times from modernship_korea_stat_base.military_template where keyword="MilitaryRankGift" ' + self.channel + ' group by date,viplevel) as a on a.viplevel=d.mvip and a.date=d.date;'
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        # | date | mvip | totalnums | peoplenum | times |
        # +------------+------+-----------+-----------+-------+
        # | 2018 - 10 - 01 | 0 | 5445 | 1839 | 1882 |
        # | 2018 - 10 - 01 | 1 | 1394 | 959 | 977 |
        # | 2018 - 10 - 01 | 2 | 320 | 257 | 263 |
        # | 2018 - 10 - 01 | 3 | 424 | 358 | 367 |
        # | 2018 - 10 - 01 | 4 | 490 | 420 | 431 |
        if alldata:
            for rec in alldata:
                self.datelist.append(str(rec[0]))
            self.datelist = sorted(list(set(self.datelist)))
            for date in self.datelist:
                self.militaryrankGiftratio[date] = dict()
                self.militaryrankGifttotalnums[date] = dict()
            for rec in alldata:
                self.militaryrankGiftratio[str(rec[0])][rec[1]] = rec[5]
                self.militaryrankGifttotalnums[str(rec[0])][rec[1]] = rec[2]

    def MilitaryPorts(self,itembegindate,itemenddate):
        self.datelist = []
        self.militaryrankPortsratio = dict()
        self.militaryrankPortstotalnums = dict()
        sqlstr = 'select d.date,mvip,totalnums,peoplenum,times,peoplenum/totalnums,times/peoplenum from (select date,mvip,count(uid) as totalnums from (select date,uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where level>=40 and date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by date,uid) as c group by date,mvip) as d left join (select date,sum(peoplenum) as peoplenum,viplevel,sum(times) as times from modernship_stat_busi.military_join where viplevel<=30 ' + self.channel + ' group by date,viplevel) as a on a.viplevel=d.mvip and a.date=d.date;'
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        # | date | mvip | totalnums | peoplenum | times |
        # +------------+------+-----------+-----------+-------+
        # | 2018 - 10 - 06 | 0 | 2193 | 200 | 4199 |
        # | 2018 - 10 - 06 | 1 | 1125 | 112 | 2822 |
        # | 2018 - 10 - 06 | 2 | 261 | 25 | 639 |
        # | 2018 - 10 - 06 | 3 | 375 | 57 | 1828 |
        # | 2018 - 10 - 06 | 4 | 451 | 71 | 1795 |
        # | 2018 - 10 - 06 | 5 | 293 | 66 | 2082 |

        if alldata:
            for rec in alldata:
                self.datelist.append(str(rec[0]))
            self.datelist = sorted(list(set(self.datelist)))
            for date in self.datelist:
                self.militaryrankPortsratio[date] = dict()
                self.militaryrankPortstotalnums[date] = dict()
            for rec in alldata:
                self.militaryrankPortsratio[str(rec[0])][rec[1]] = rec[5]
                self.militaryrankPortstotalnums[str(rec[0])][rec[1]] = rec[2]

    def Onlinegift(self,begindate):
        #log:2018-12-05 10:39:49,20001,72424972655534394,OnlineGift,40,10171007201802062146175099337,0,2018-03-28 11:10:12,7152,20001,1,8,0,1007,1,,,,,,,,
        self.datelist = []
        sqlstr= 'select a.*,b.maxboxid,b.giftnum,b.giftnum/a.totalnum from (select date,vip_level,count(uid) as totalnum from user_active_extend where date>=\"'+begindate+'\" and uid not in (select uid from modernship_stat_busi.uid_block_list) group by date,vip_level) as a left join (select date,viplevel,maxboxid,count(uid) as giftnum from onlinebox id  group by date,viplevel,maxboxid) as b on a.date=b.date and a.vip_level=b.viplevel;'
        # | date | vip_level | totalnum | maxboxid | giftnum |
        # +------------+-----------+----------+----------+---------+
        # | 2018 - 11 - 22 | 0 | 4039 | 1 | 764 |
        # | 2018 - 11 - 22 | 0 | 4039 | 2 | 568 |
        # | 2018 - 11 - 22 | 0 | 4039 | 3 | 334 |
        # | 2018 - 11 - 22 | 1 | 2793 | 1 | 552 |
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        # print(alldata)
        if alldata:
            for rec in alldata:
                self.datelist.append(str(rec[0]))
            self.datelist = sorted(list(set(self.datelist)))

        for date in self.datelist:
            self.box1[date] = dict()
            self.box2[date] = dict()
            self.box3[date] = dict()
            self.box4[date] = dict()
            self.totaleve[date] = dict()

        for rec in alldata:
            if str(rec[3]) == '1':
                self.box1[str(rec[0])][rec[1]] = rec[5]
            elif str(rec[3]) == '2':
                self.box2[str(rec[0])][rec[1]] = rec[5]
            elif str(rec[3]) == '3':
                self.box3[str(rec[0])][rec[1]] = rec[5]
            self.totaleve[str(rec[0])][rec[1]] = rec[2]

    def onlinetime(self,begindate):
        self.datelist = []
        #select date,vip_level,count(uid),sum(online_time)/count(uid)/60 from user_active_extend where datediff(date,regdate)>0 group by date,vip_level
        # | date | vip_level | count(uid) | sum(online_time) / count(uid) / 60 |
        # +------------+-----------+------------+--------------------------------+
        # | 2018 - 10 - 23 | 0 | 1922 | 120.40574055 |
        # | 2018 - 10 - 23 | 1 | 292 | 196.49874429 |
        # | 2018 - 10 - 23 | 2 | 66 | 254.36489899 |
        # | 2018 - 10 - 23 | 3 | 48 | 318.63090278 |
        # | 2018 - 10 - 23 | 4 | 70 | 345.48547619 |
        # | 2018 - 10 - 23 | 5 | 29 | 315.11379310 |
        self.onlinetimeoldpeople=dict()
        self.onlinetimeoldtime = dict()
        self.onlinetimenewpeople=dict()
        self.onlinetimenewtime = dict()

        sqlstr='select date,vip_level,count(uid),sum(online_time)/count(uid)/60 from user_active_extend where datediff(date,regdate)>0 and uid not in (select uid from modernship_stat_busi.uid_block_list) and date>=\"'+begindate+'\" group by date,vip_level;'
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        # print(alldata)
        if alldata:
            for rec in alldata:
                self.datelist.append(str(rec[0]))
            self.datelist = sorted(list(set(self.datelist)))
        for date in self.datelist:

            self.onlinetimeoldpeople[date] = dict()
            self.onlinetimeoldtime[date] = dict()


        for rec in alldata:
            self.onlinetimeoldpeople[str(rec[0])][rec[1]] = rec[2]
            self.onlinetimeoldtime[str(rec[0])][rec[1]] = rec[3]

        sqlstr='select date,vip_level,count(uid),sum(online_time)/count(uid)/60 from user_active_extend where datediff(date,regdate)=0 and uid not in (select uid from modernship_stat_busi.uid_block_list) and date>=\"'+begindate+'\" group by date,vip_level;'
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        if alldata:
            for rec in alldata:
                self.datelist.append(str(rec[0]))
            self.datelist = sorted(list(set(self.datelist)))

        for date in self.datelist:
            self.onlinetimenewpeople[date] = dict()
            self.onlinetimenewtime[date] = dict()

        for rec in alldata:
            self.onlinetimenewpeople[str(rec[0])][rec[1]] = rec[2]
            self.onlinetimenewtime[str(rec[0])][rec[1]] = rec[3]

    def BlocBossBattle(self,begindate):
        #select date,viplevel,sum(peoplenum),sum(times) from blocbossbattle group by date,viplevel limit 10;
        self.datelist = []
        self.blocbossratio=dict()
        self.blocbosspeople = dict()
        sqlstr='select a.*,b.peoplenum,b.peoplenum/a.totalnum from (select date,vip_level,count(uid) as totalnum from user_active_extend where level>=20 and uid not in (select uid from modernship_stat_busi.uid_block_list) and date>=\"'+begindate+'\" group by date,vip_level) as a left join (select date,viplevel,sum(peoplenum) as peoplenum from blocbossbattle group by date,viplevel)as b on a.date=b.date and a.vip_level=b.viplevel;'
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        # | date | vip_level | totalnum | peoplenum |
        # | 2018 - 10 - 26 | 0 | 3910 | 17 |
        # | 2018 - 10 - 26 | 1 | 1055 | 10 |
        if alldata:
            for rec in alldata:
                self.datelist.append(str(rec[0]))
            self.datelist = sorted(list(set(self.datelist)))

        for date in self.datelist:
            self.blocbossratio[date] = dict()
            self.blocbosspeople[date] = dict()

        for rec in alldata:
            self.blocbossratio[str(rec[0])][rec[1]] = rec[4]
            self.blocbosspeople[str(rec[0])][rec[1]] = rec[2]

    def AISystem(self,begindate):
        self.datelist = []
        self.airatio=dict()
        self.aipeople = dict()
        self.aiavgtimes = dict()
        sqlstr='select a.*,b.peoplenum,b.peoplenum/a.totalnum,b.avgtimes from (select date,vip_level,count(uid) as totalnum from user_active_extend where date>=\"'+begindate+'\" and uid not in (select uid from modernship_stat_busi.uid_block_list) group by date,vip_level) as a left join (select date,viplevel,sum(peoplenum) as peoplenum,sum(Cash+diamond),sum(Cash+diamond)/300/sum(peoplenum) as avgtimes from DiamondCost_Hour where moneytype=97 group by date,viplevel) as b on a.date=b.date and a.vip_level=b.viplevel;'
        # | date | vip_level | totalnum | peoplenum | b.peoplenum / a.totalnum | avgtimes |
        # +------------+-----------+----------+-----------+------------------------+----------+
        # | 2018 - 03 - 28 | 0 | 46555 | NULL | NULL | NULL |
        # | 2018 - 03 - 28 | 1 | 6042 | NULL | NULL | NULL |
        # | 2018 - 03 - 28 | 2 | 471 | NULL | NULL | NULL |
        # | 2018 - 03 - 28 | 3 | 149 | NULL | NULL | NULL |
        # | 2018 - 03 - 28 | 4 | 251 | NULL | NULL | NULL |
        # | 2018 - 03 - 28 | 5 | 56 | NULL | NULL | NULL |
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        if alldata:
            for rec in alldata:
                self.datelist.append(str(rec[0]))
            self.datelist = sorted(list(set(self.datelist)))

        for date in self.datelist:
            self.airatio[date] = dict()
            self.aipeople[date] = dict()
            self.aiavgtimes[date] = dict()

        for rec in alldata:
            self.airatio[str(rec[0])][rec[1]] = rec[4]
            self.aipeople[str(rec[0])][rec[1]] = rec[3]
            self.aiavgtimes[str(rec[0])][rec[1]] = rec[5]

    # def aiamplifibuy(self):
    #     self.datelist = []
    #     self.aiamplifiratio=dict()
    #     self.aiamplifipeople = dict()
    #     self.aiamplifiavgtimes = dict()
    #     pass


    def Chip_evolve(self):
        self.chiplist = [167101,167102,167103,167201,167202,167203,167301,167302,167303,166101,166102,166201,166202,166301,166302,165101,165102,165201,165202,165301,165302]
        self.starlist = []
        self.chippeople = dict()
        sqlstr = 'select mstar,id,count(uid) from(select uid,id,max(star) as mstar from smtc where flag=5 group by uid) as a group by mstar,id;'
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        if alldata:
            for rec in alldata:
                self.starlist.append(str(rec[0]))
            self.starlist = sorted(list(set(self.starlist)))

        for star in self.starlist:
            self.chippeople[star] = dict()

        for rec in alldata:
            self.chippeople[str(rec[0])][rec[1]] = rec[2]

    def TechInfo(self,begindate):
        self.techlist = [1010,1020,1030,1040,1050,1060,1070,1080,1090,1100,'高速突防技术','隐身突防技术','低空突防技术','超高频雷达技术','双波段雷达技术','合成孔径雷达技术','一体化核动力技术','电力推进技术','燃料电池技术','智能数据链技术','综合通信桅杆技术','蓝绿激光通信技术','超高速跳频技术','全频谱对抗技术','有源主动对消技术','超地平线防空技术','舰队指挥中枢技术','激光防御系统技术','战区空天防御技术','复合声纳系统技术','复合制导鱼雷技术','低频降噪技术','泵喷推进技术','舰队中枢技术','隐形舰载机技术','先进起降技术','综合电力技术','联合指挥中心技术','极高频通讯卫星技术','全球卫星定位技术','海洋监视卫星技术','海底声纳阵列技术','预警飞艇技术','空天飞机技术','亚轨道飞行器技术','超长时无人机技术','天基飞船技术']

        self.translist=[]
        for i in self.techlist:
            if(self.zh_pattern.search(unicode(str(i)))):
                self.translist.append(unicode(i))
            else:
                self.translist.append(i)
        # print(self.translist)

        self.techdict=dict()
        self.techleveldict=dict()

        sqlstr = 'select viplevel,techid,sum(peoplenum),sum(techlevel*peoplenum)/sum(peoplenum) from TechInfoNew where date=\"'+begindate+'\"' + self.channel + ' and techlevel>0 group by viplevel,techid;'
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()

        # for i in range(len(self.techlist)):
        #     self.techdict[self.translist[i]] = dict()
        #     self.techleveldict[self.translist[i]]  = dict()
        for i in self.viplist:
            self.techdict[i] = dict()
            self.techleveldict[i] = dict()
        if alldata:
            for rec in alldata:
                # self.techdict[self.translist[int(rec[0])]][rec[1]] = rec[2]
                # self.techleveldict[self.translist[int(rec[0])]][rec[1]] = rec[3]
                self.techdict[rec[0]][self.translist[int(rec[1])]]= rec[2]
                self.techleveldict[rec[0]][self.translist[int(rec[1])]] = rec[3]

    def Tech_Gacha(self,begindate):

        self.datelist = []
        self.techratio = dict()
        self.techpeople = dict()
        self.techavgtimes = dict()
        sqlstr = 'select a.*,b.peoplenum,b.times,peoplenum/total,b.times/b.peoplenum from (select date,vip_level,count(distinct(uid)) as total from user_active_extend where date>=\"'+begindate+'\" and level>=25 and uid not in (select uid from modernship_stat_busi.uid_block_list) group by date,vip_level) as a inner join (select date,viplevel,sum(count) as peoplenum,sum(number*times) as times from ResearchCenter where pay>0 group by date,viplevel)as b on a.vip_level=b.viplevel and a.date=b.date;'

        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        if alldata:
            for rec in alldata:
                self.datelist.append(str(rec[0]))
            self.datelist = sorted(list(set(self.datelist)))

        for date in self.datelist:
            self.techratio[date] = dict()
            self.techpeople[date] = dict()
            self.techavgtimes[date] = dict()

        for rec in alldata:
            self.techratio[str(rec[0])][rec[1]] = rec[5]
            self.techpeople[str(rec[0])][rec[1]] = rec[3]
            self.techavgtimes[str(rec[0])][rec[1]] = rec[6]



    def runformalold(self):
        self.formalchannel()
        self.runwrite()


if __name__ == '__main__':
    NewFuncgf_nov25().runformalold()