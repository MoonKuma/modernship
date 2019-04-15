
import conf.ConfParameters as ConfParameters
import util.DateList as DateList
import util.EasyXls as EasyXls
import os
import MySQLdb
import xlwt
import sys
import calendar
import datetime




class NewOldSituation():
    def __init__(self):
        self.channel = ''
        self.viplist=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
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
        return

    def formalchannel(self):
        self.channel = 'and channel not in (1099, 109902, 109903, 1105, 1098, 109802, 1100, 1104, 1101,1099,1098,1100,1101,12003,109802,1102,1103,1104,1104,1104,1104,1104,1104,1104,1104,1104,109902,109903,1104,1104,1105,109902,109906,109913,109907,109911,109910,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,1098,109914,1100)'
        self.zoneid = '$2<50000 &&'

    def yiyouchannel(self):
        self.channel = 'and channel in (1099, 109902, 109903, 1098, 109802,1099,1098,109802,109902,109903,109902,109906,109913,109907,109911,109910,1098,109914)'
        self.zoneid = '($2>50000 && $2<55000) &&'

    def jinyouchannel(self):
        self.channel = 'and channel in (1100,1104,1101,1200,1105)'
        self.zoneid = '$2>55000 &&'


#####write xlwt
    def xls_writeone_list(self,sheet,name,somekeys, somedict, indexi=0, indexj=0):
        # xls_writer = EasyXls.EasyXls()
        defaultencoding = 'utf-8'
        if sys.getdefaultencoding() != defaultencoding:
            reload(sys)
            sys.setdefaultencoding(defaultencoding)

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
        defaultencoding = 'utf-8'
        if sys.getdefaultencoding() != defaultencoding:
            reload(sys)
            sys.setdefaultencoding(defaultencoding)

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
        file_name ='/data/tmpStatistic/project_modern_ship/result/newfunction' + self.channel[0:20] + '.xls'
        self.db.close()
        self.wbk.save(file_name)

    def runformalold(self):
        self.formalchannel()
        self.runwrite()

    def runjinyou(self):
        self.jinyouchannel()
        self.runwrite()

    def runyiyou(self):
        self.yiyouchannel()
        self.runwrite()


    def runwrite(self):
        self.naval_ports_buy('2018-09-25','2018-10-24')
        self.sheetadd('naval_ports_buy')
        self.xls_writetwo_dict(self.sheet,'itembuyratio0925-1024',self.itemlist,self.viplist,self.itembuyratio)
        self.xls_writetwo_dict(self.sheet, 'itemavg0925-1024', self.itemlist, self.viplist, self.itemavgtimes,15,0)
        self.xls_writetwo_dict(self.sheet, 'itembuypeople0925-1024', self.itemlist, self.viplist, self.itembuypeople, 30, 0)
        self.xls_writetwo_dict(self.sheet, 'activepeople0925-1024', self.itemlist, self.viplist, self.activepeople,45, 0)

        self.horn_buy('2018-09-25','2018-10-24')
        self.sheetadd('horn_buy')
        self.xls_writetwo_dict(self.sheet,'itembuyratio0925-1024',self.itemlist,self.viplist,self.itembuyratio)
        self.xls_writetwo_dict(self.sheet, 'itemavg0925-1024', self.itemlist, self.viplist, self.itemavgtimes,5,0)
        self.xls_writetwo_dict(self.sheet, 'itembuypeople0925-1024', self.itemlist, self.viplist, self.itembuypeople, 10, 0)
        self.xls_writetwo_dict(self.sheet, 'activepeople0925-1024', self.itemlist, self.viplist, self.activepeople,15, 0)

        self.arena_battle('2018-09-15','2018-10-24')
        self.sheetadd('arena_battle')
        self.xls_writetwo_dict(self.sheet, 'joinratio', self.viplist, self.datelist, self.joinratio)
        self.xls_writetwo_dict(self.sheet, 'joinavgtimes', self.viplist, self.datelist, self.joinavgtimes,23)
        self.xls_writetwo_dict(self.sheet, 'joinpeople', self.viplist, self.datelist, self.joinpeople, 46)
        self.xls_writetwo_dict(self.sheet, 'activepeople', self.viplist, self.datelist, self.activepeople, 69)

        self.champion_battle('2018-09-15','2018-10-24')
        self.sheetadd('champion_battle')
        self.xls_writetwo_dict(self.sheet, 'joinratio', self.viplist, self.datelist, self.joinratio)
        self.xls_writetwo_dict(self.sheet, 'joinavgtimes', self.viplist, self.datelist, self.joinavgtimes,23)
        self.xls_writetwo_dict(self.sheet, 'joinpeople', self.viplist, self.datelist, self.joinpeople, 46)
        self.xls_writetwo_dict(self.sheet, 'activepeople', self.viplist, self.datelist, self.activepeople, 69)

        self.Militaryrankcollect('2018-10-01','2018-10-31')
        self.sheetadd('Militaryrankcollectold')
        self.xls_writetwo_dict(self.sheet, 'militaryrankcollectoldratio', self.viplist, self.datelist,self.militaryrankcollectoldratio)
        self.xls_writetwo_dict(self.sheet, 'militaryrankcollectoldtotalnums', self.viplist, self.datelist, self.militaryrankcollectoldtotalnums, 23)
        self.xls_writetwo_dict(self.sheet, 'militaryrankcollectoldavgtimes', self.viplist, self.datelist, self.militaryrankcollectoldavgtimes, 46)
        self.sheetadd('Militaryrankcollectnew')
        self.xls_writetwo_dict(self.sheet, 'militaryrankcollectnewratio', self.viplist, self.datelist,self.militaryrankcollectnewratio)
        self.xls_writetwo_dict(self.sheet, 'militaryrankcollectnewtotalnums', self.viplist, self.datelist, self.militaryrankcollectnewtotalnums, 23)
        self.xls_writetwo_dict(self.sheet, 'militaryrankcollectnewavgtimes', self.viplist, self.datelist, self.militaryrankcollectnewavgtimes, 46)

        self.MilitaryRankSalary('2018-10-01','2018-10-31')
        self.sheetadd('Militaryranksalary')
        self.xls_writetwo_dict(self.sheet, 'militaryranksalaryratio', self.viplist, self.datelist,self.militaryranksalaryratio)
        self.xls_writetwo_dict(self.sheet, 'militaryranksalarytotalnums', self.viplist, self.datelist, self.militaryranksalarytotalnums, 23)

        self.MilitaryRankGacha('2018-10-01','2018-10-31')
        self.sheetadd('MilitaryrankGacha')
        self.xls_writetwo_dict(self.sheet, 'militaryrankGacharatio', self.viplist, self.datelist,self.militaryrankGacharatio)
        self.xls_writetwo_dict(self.sheet, 'militaryrankGachatotalnums', self.viplist, self.datelist, self.militaryrankGachatotalnums, 23)

        self.MilitaryRankGift('2018-10-01','2018-10-31')
        self.sheetadd('MilitaryrankGift')
        self.xls_writetwo_dict(self.sheet, 'militaryrankGiftratio', self.viplist, self.datelist,self.militaryrankGiftratio)
        self.xls_writetwo_dict(self.sheet, 'militaryrankGifttotalnums', self.viplist, self.datelist, self.militaryrankGifttotalnums, 23)

        self.MilitaryPorts('2018-10-01','2018-10-31')
        self.sheetadd('MilitaryrankPorts')
        self.xls_writetwo_dict(self.sheet, 'militaryrankPortsratio', self.viplist, self.datelist,self.militaryrankPortsratio)
        self.xls_writetwo_dict(self.sheet, 'militaryrankPortstotalnums', self.viplist, self.datelist, self.militaryrankPortstotalnums, 23)

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
        sqlstr = 'select *,peoplenum/totalnums,times/peoplenum as buyratio from (select mvip,count(uid) as totalnums from (select uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as c group by mvip) as d left join (select mvip,itemid,count(distinct(uid)) as peoplenum,sum(times) as times from (select a.*,b.mvip from (select uid,itemid,sum(times) as times from modernship_stat_busi.shopexchange where shopid=12 group by uid,itemid) as a inner join (select uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' and uid not in (select uid from modernship_stat_busi.uid_block_list)  group by uid) as b on a.uid=b.uid) as c group by mvip,itemid) as e on d.mvip=e.mvip;'
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

    def titleactive(self,enddate):
        self.titlelist = []
        self.itembuyratio = dict()
        self.itemavgtimes = dict()
        self.itembuypeople = dict()
        self.activepeople = dict()



    def Militaryrankcollect(self,itembegindate,itemenddate):
        #10.1 everyday join vip
        self.datelist = []
        self.militaryrankcollectoldratio = dict()
        self.militaryrankcollectoldtotalnums =dict()
        self.militaryrankcollectoldavgtimes = dict()
        self.militaryrankcollectnewratio = dict()
        self.militaryrankcollectnewtotalnums =dict()
        self.militaryrankcollectnewavgtimes = dict()
        sqlstr='select d.date,mvip,totalnums,peoplenum,times,peoplenum/totalnums,times/peoplenum from (select date,mvip,count(uid) as totalnums from (select date,uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where regdate<="2018-09-25" and  date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by date,uid) as c group by date,mvip) as d left join (select date,count(distinct(uid)) as peoplenum,viplevel,sum(times) as times from modernship_stat_busi.military_template where regdate<="2018-09-25" and keyword="MilitaryRankCollect" '+ self.channel +' group by date,viplevel) as a on a.viplevel=d.mvip and a.date=d.date;'
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
        sqlstr = 'select d.date,mvip,totalnums,peoplenum,times,peoplenum/totalnums,times/peoplenum from (select date,mvip,count(uid) as totalnums from (select date,uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where regdate>="2018-09-25" and  date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by date,uid) as c group by date,mvip) as d left join (select date,count(distinct(uid)) as peoplenum,viplevel,sum(times) as times from modernship_stat_busi.military_template where regdate>="2018-09-25" and keyword="MilitaryRankCollect" ' + self.channel + ' group by date,viplevel) as a on a.viplevel=d.mvip and a.date=d.date;'
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
        sqlstr = 'select d.date,mvip,totalnums,peoplenum,times,peoplenum/totalnums,times/peoplenum from (select date,mvip,count(uid) as totalnums from (select date,uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by date,uid) as c group by date,mvip) as d left join (select date,count(distinct(uid)) as peoplenum,viplevel,sum(times) as times from modernship_stat_busi.military_template where keyword="MilitaryRankSalary" ' + self.channel + ' group by date,viplevel) as a on a.viplevel=d.mvip and a.date=d.date;'
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
        sqlstr = 'select d.date,mvip,totalnums,peoplenum,times,peoplenum/totalnums,times/peoplenum from (select date,mvip,count(uid) as totalnums from (select date,uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by date,uid) as c group by date,mvip) as d left join (select date,count(distinct(uid)) as peoplenum,viplevel,sum(times) as times from modernship_stat_busi.military_template where keyword="MilitaryRankGacha" ' + self.channel + ' group by date,viplevel) as a on a.viplevel=d.mvip and a.date=d.date;'
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
        sqlstr = 'select d.date,mvip,totalnums,peoplenum,times,peoplenum/totalnums,times/peoplenum from (select date,mvip,count(uid) as totalnums from (select date,uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date between \"' + itembegindate + '\" and \"' + itemenddate + '\" ' + self.channel + ' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by date,uid) as c group by date,mvip) as d left join (select date,count(distinct(uid)) as peoplenum,viplevel,sum(times) as times from modernship_stat_busi.military_template where keyword="MilitaryRankGift" ' + self.channel + ' group by date,viplevel) as a on a.viplevel=d.mvip and a.date=d.date;'
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





    def runformalold(self):
        self.formalchannel()
        self.runwrite()



if __name__ == '__main__':
    NewOldSituation().runformalold()
    NewOldSituation().runjinyou()
    NewOldSituation().runyiyou()