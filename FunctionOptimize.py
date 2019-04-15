
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
        # self.channel_notin = (1099, 109902, 109903, 1105, 1098, 109802, 1100, 1104, 1101)
        #olduser
        # self.totaldict = dict()
        # self.peopledict = dict()
        # self.paydict = dict()
        # self.moneydict = dict()
        #
        # self.stayratio = dict()
        # self.payratio = dict()
        # #newuser
        # self.newnumdict=dict()
        # self.new_firstdaydict=dict()
        # self.new_sevendaydict = dict()

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
        #shipbuilt
        self.starlist=[1,2,3,4,5,6,7]
        self.ship1102dict = dict()
        self.ship4030dict = dict()
        self.ship4031dict = dict()
        self.ship5025dict= dict()
        self.shiptotaldict = dict()
        #
        #vipgift
        self.vipgiftlist = [168,288,388,888,1288,1688,1988,2688,3288,3888]
        self.totalvip = dict()
        self.buyvipratio = dict()
        self.buyvipnum = dict()
        self.buyvipavgtimes = dict()
        self.buyvipcash = dict()

        #missionbox
        self.box1 = dict()
        self.box2 = dict()
        self.box3 = dict()
        self.box4 = dict()
        self.totaleve = dict()

        #missonship
        self.missonship=dict()

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
        file_name =ConfParameters.ConfParameters().save_path+ 'functionoptimize' + self.channel[0:20] + '.xls'
        self.db.close()
        self.wbk.save(file_name)

    def runformalold(self):
        self.formalchannel()
        self.shipbuild('2018-08-23','2018-10-18')
        self.sheetadd('shipbuild')
        self.xls_writetwo_dict(self.sheet, '1102',self.starlist, self.viplist,self.ship1102dict)
        self.xls_writetwo_dict(self.sheet, '4030', self.starlist, self.viplist,self.ship4030dict,13,0)
        self.xls_writetwo_dict(self.sheet, '4031', self.starlist, self.viplist, self.ship4031dict,26,0)
        self.xls_writetwo_dict(self.sheet, '5025', self.starlist, self.viplist, self.ship5025dict,39,0)
        self.xls_writetwo_dict(self.sheet, 'peoplenum', self.starlist, self.viplist, self.shiptotaldict, 52, 0)
        self.vipgiftbuy('2018-08-01','2018-08-08')
        self.sheetadd('vipgiftbuy')
        self.xls_writetwo_dict(self.sheet, 'buyvipratio',self.vipgiftlist, self.viplist,self.buyvipratio)
        self.xls_writetwo_dict(self.sheet, 'buyvipnum', self.vipgiftlist, self.viplist,self.buyvipnum,13,0)
        self.xls_writetwo_dict(self.sheet, 'buyvipavgtimes', self.vipgiftlist, self.viplist, self.buyvipavgtimes,26,0)
        self.xls_writetwo_dict(self.sheet, 'buyvipcash', self.vipgiftlist, self.viplist, self.buyvipcash,39,0)
        self.xls_writetwo_dict(self.sheet, 'totalvip', self.vipgiftlist, self.viplist, self.totalvip, 52, 0)
        self.vipgiftbuy('2018-09-24', '2018-09-30')
        self.xls_writetwo_dict(self.sheet, 'buyvipratio',self.vipgiftlist, self.viplist,self.buyvipratio,0,25)
        self.xls_writetwo_dict(self.sheet, 'buyvipnum', self.vipgiftlist, self.viplist,self.buyvipnum,13,25)
        self.xls_writetwo_dict(self.sheet, 'buyvipavgtimes', self.vipgiftlist, self.viplist, self.buyvipavgtimes,26,25)
        self.xls_writetwo_dict(self.sheet, 'buyvipcash', self.vipgiftlist, self.viplist, self.buyvipcash,39,25)
        self.xls_writetwo_dict(self.sheet, 'totalvip', self.vipgiftlist, self.viplist, self.totalvip, 52, 25)

        self.missionbox('2018-09-25')
        self.sheetadd('missionbox')
        self.xls_writetwo_dict(self.sheet, 'box1', self.viplist, self.datelist, self.box1)
        self.xls_writetwo_dict(self.sheet, 'box2', self.viplist, self.datelist, self.box2,23)
        self.xls_writetwo_dict(self.sheet, 'box3', self.viplist, self.datelist, self.box3, 46)
        self.xls_writetwo_dict(self.sheet, 'box4', self.viplist, self.datelist, self.box4, 69)
        self.xls_writetwo_dict(self.sheet, 'total', self.viplist, self.datelist, self.totaleve, 92)

        self.missionship18('2018-08-30')
        self.sheetadd('missionship')
        self.xls_writeone_list(self.sheet, 'missionship', self.viplist, self.missonship)
        self.end_all()



    def vipgiftbuy(self,itembegindate,itemenddate):
        for i in self.viplist:
            self.totalvip[i] = dict()
            self.buyvipratio[i] = dict()
            self.buyvipnum[i] = dict()
            self.buyvipavgtimes[i] = dict()
            self.buyvipcash[i] = dict()
        sqlstr='select *,peoplenum/totalnums as buyratio,times/peoplenum as avgtimes from (select mvip,count(uid) as totalnums from (select uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date between \"'+itembegindate+'\" and \"'+ itemenddate +'\" '+self.channel+' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as c group by mvip) as d left join (select mvip,tcost,count(distinct(a.uid)) as peoplenum,count(a.uid) as times,sum(cash) as cash,sum(diamond) as dia from (select *,cash+diamond as tcost from modernship_stat_busi.vipbuy where cash+diamond<=8888 and date between \"'+itembegindate+'\" and \"'+ itemenddate +'\" '+self.channel+' and uid not in (select uid from modernship_stat_busi.uid_block_list)) as a inner join (select uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date between \"'+itembegindate+'\" and \"'+ itemenddate +'\" '+self.channel+' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as b on a.uid=b.uid group by mvip,tcost) as e on d.mvip=e.mvip;'

        # | mvip | totalnums | mvip | tcost | peoplenum | times | cash | dia | buyratio |avgtimes
        # +------+-----------+------+-------+-----------+-------+--------+--------+----------+
        # | 0 | 49233 | 0 | 888 | 1 | 1 | 888 | 0 | 0.0000 |1
        # | 1 | 2810 | 1 | 168 | 1584 | 1596 | 31550 | 236578 | 0.5637 |1.0000

        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        if alldata:
            for rec in alldata:
                self.totalvip[rec[0]][rec[3]] = rec[1]
                self.buyvipratio[rec[0]][rec[3]] = rec[8]
                self.buyvipnum[rec[0]][rec[3]] = rec[4]
                self.buyvipavgtimes[rec[0]][rec[3]] = rec[9]
                self.buyvipcash[rec[0]][rec[3]] = rec[6]



#shipbuild maxstar contrast
    def shipbuild(self,itembegindate,itemenddate):

        for i in self.viplist:
            self.ship1102dict[i]=dict()
            self.ship4030dict[i] = dict()
            self.ship4031dict[i] = dict()
            self.ship5025dict[i] = dict()
            self.shiptotaldict[i]=dict()
        sqlstr='select e.*,d.id,d.mstar,d.num,d.num/e.totalusers as ratio from (select mvip,count(uid) as totalusers from (select uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date between \"'+itembegindate+'\" and \"'+ itemenddate +'\" '+self.channel+' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as c group by mvip) as e left join (select mvip,id,mstar,count(a.uid) as num from ((select uid,id,max(star) as mstar from modernship_stat_busi.smtc where date between\"'+itembegindate+'\" and \"'+ itemenddate +'\" '+self.channel+' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid,id) as a inner join(select uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date between \"'+itembegindate+'\" and \"'+ itemenddate +'\" '+self.channel+' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as b on a.uid=b.uid) group by mvip,id,mstar) as d on d.mvip=e.mvip;'
        # | mvip | totalusers | id | mstar | num | ratio |
        # +------+------------+------+-------+------+--------+
        # | 0 | 124307 | 1102 | 1 | 211 | 0.0017 |
        # | 0 | 124307 | 1102 | 2 | 1605 | 0.0129 |
        # | 0 | 124307 | 1102 | 3 | 294 | 0.0024 |
        # | 0 | 124307 | 1102 | 4 | 43 | 0.0003 |
        # | 0 | 124307 | 1102 | 5 | 4 | 0.0000 |
        # | 0 | 124307 | 4030 | 3 | 18 | 0.0001 |
        # | 0 | 124307 | 4031 | 3 | 129 | 0.0010 |
        # | 0 | 124307 | 4031 | 4 | 2 | 0.0000 |
        # | 0 | 124307 | 5025 | 2 | 349 | 0.0028 |
        # | 0 | 124307 | 5025 | 3 | 16 | 0.0001 |
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        if alldata:
            for rec in alldata:
                if str(rec[2])=='1102':
                    self.ship1102dict[rec[0]][rec[3]]=rec[5]
                    self.shiptotaldict[rec[0]][rec[3]]=rec[1]
                elif str(rec[2]) == '4030':
                    self.ship4030dict[rec[0]][rec[3]] = rec[5]
                elif str(rec[2]) == '4031':
                    self.ship4031dict[rec[0]][rec[3]] = rec[5]
                else:
                    self.ship5025dict[rec[0]][rec[3]] = rec[5]

    def missionbox(self,boxbegindate):

        self.datelist = []
        sqlstr='select *,boxpeople/totalnums  from (select date,vip_level,count(distinct(uid)) as totalnums from modernship_gf_stat_base.user_active_extend where date>=\"'+boxbegindate+'\"'+self.channel+' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by date,vip_level) as c left join (select b.date,b.mvip,maxboxid,count(distinct(b.uid)) as boxpeople from (select * from modernship_stat_busi.missionbox where uid not in (select uid from modernship_stat_busi.uid_block_list) '+self.channel+') as a  inner join (select date,uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date>=\"'+boxbegindate+'\" '+self.channel+' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by date,uid) as b on a.uid=b.uid and a.date=b.date group by b.date,b.mvip,maxboxid) as d on c.date=d.date and c.vip_level=d.mvip;'
        # | date | vip_level | count(distinct(uid)) | date | mvip | maxboxid | count(distinct(b.uid)) |/
        # +------------+-----------+----------------------+------------+------+----------+------------------------+
        # | 2018 - 09 - 25 | 0 | 4911 | 2018 - 09 - 25 | 0 | 1 | 811 |811/4911
        # | 2018 - 09 - 25 | 0 | 4911 | 2018 - 09 - 25 | 0 | 2 | 1113 |1113/4911

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
                if str(rec[5]) == '1':
                    self.box1[str(rec[0])][rec[1]]=rec[7]
                elif str(rec[5]) == '2':
                    self.box2[str(rec[0])][rec[1]]= rec[7]
                elif str(rec[5]) == '3':
                    self.box3[str(rec[0])][rec[1]] = rec[7]
                else:
                    self.box4[str(rec[0])][rec[1]] = rec[7]
                self.totaleve[str(rec[0])][rec[1]] = rec[2]


        # print(self.box1)
        # print(self.datelist)

    def missionship18(self,shipbegindate):
        #830-1024
        # | mvip | totalnums | mvip | people | times |
        # +------+-----------+------+--------+-------+
        # | 0 | 115744 | 0 | 761 | 765 |765/115744
        # | 1 | 5450 | 1 | 571 | 576 |
        sqlstr='select *,people/totalnums from (select mvip,count(uid) as totalnums from (select uid,max(vip_level) as mvip from modernship_gf_stat_base.user_active_extend where date>=\"'+shipbegindate+'\"'+self.channel+' and uid not in (select uid from modernship_stat_busi.uid_block_list) group by uid) as c group by mvip) as d left join (select mvip,count(uid) as people,sum(times) as times from(select uid,max(viplevel) as mvip,count(uid) as times from modernship_stat_busi.missionship where uid not in (select uid from modernship_stat_busi.uid_block_list) '+self.channel+'group by uid) as a group by mvip) as b on d.mvip=b.mvip;'
        self.cursor.execute(sqlstr)
        alldata = self.cursor.fetchall()
        if alldata:
            for rec in alldata:
                self.missonship[rec[0]]=str(rec[1])+","+str(rec[3])+","+str(rec[4])+","+str(rec[5])


if __name__ == '__main__':
    NewOldSituation().runformalold()