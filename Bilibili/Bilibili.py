#!/usr/bin/env python3
# coding=utf-8
# author:sakuyo
#----------------------------------
import requests,time,csv
from datetime import datetime
from dateutil.relativedelta import relativedelta
import xml.dom.minidom
from xml.dom.minidom import parseString


class BiliBili(object):
    def __init__(self):
        #初始化cookies
        self.cookies = {
            'SESSDATA':'4cd739a0%2C1614857849%2Cc6c2f*91'
            }
        #初始化请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
            }

    def login(self,username,password):#登录方法
        self.username = username
        self.password = password

class BiliBiliAchive(BiliBili):

    def __init__(self,target):#初始化
        #BiliBili初始化
        BiliBili.__init__(self)
        self.target = target #target可为bvid，可为avid（aid）
        self.session = requests.Session() #启动弹幕读取session
        self.GetIdType()

    def GetIdType(self):#判断是bv号还是av号
        if self.target.isdigit():#通过是否全部为数字判断（待改进）
            self.GetAllId(aid = self.target)
        else:
            self.GetAllId(bvid = self.target)

    def GetAllId(self,bvid='',aid=''):#调用api获取bvid，avid和cid（cid即为oid）
        dataDict = {}
        url = 'https://api.bilibili.com/x/web-interface/view'
        
        if bvid != '':dataDict['bvid'] = bvid
        if aid != '':dataDict['aid'] = aid
        res = self.session.get(url,params=dataDict)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        data = res.json()
        #提取视频信息
        self.aid = data['data']['aid'] #av号
        self.bvid = data['data']['bvid'] #bv号
        self.cid = data['data']['cid']
        self.oid = self.cid #cid和oid相同
        self.pubDate = data['data']['pubdate'] #视频发布日期

class ReplyCatcher(BiliBiliAchive):
    
    def GetReply(self):
        url = 'https://api.bilibili.com/x/v2/reply'
        headers = self.headers
        #这里的oid不是cid是aid
        dataDict = {
            'type':1,
            'oid':self.aid,
            'jsonp':'jsonp'
            }
        cookies = self.cookies
        res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        data = res.json()
        print(data)

class BarrageCatcher(BiliBiliAchive):
    
    def IsValidDate(self, date):#日期格式验证
        try:
            time.strptime(date, "%Y-%m-%d")
            return True
        except:
            return False 

    def GetMonthDiff(self,startDate,endDate):#获取日期差值(必须为datetime格式)
        startMon = startDate
        endMon = endDate
        diffNum = (endMon.year - startMon.year) *12 +(endMon.month - startMon.month)
        return diffNum

    def GetBarrageRecordByMonth(self,month):#获取当月弹幕
        url = 'https://api.bilibili.com/x/v2/dm/history/index'
        headers = self.headers
        dataDict = {
            'type':1,
            'oid':self.oid,
            'month':month
            }
        cookies = self.cookies
        res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        data = res.json()
        dateList = data['data']
        for unitDate in dateList:
            self.GetHistory(unitDate)

    def GetBarrageRecord(self):#获取产生弹幕的日期（按月遍历）
        startTime = datetime.fromtimestamp(self.pubDate) #时间戳转datetime @发布日期
        monthDiff = self.GetMonthDiff(startTime,datetime.now()) #从发布至今几个月
        for i in range(monthDiff+1):
            targetMonth = startTime + relativedelta(months=i) #日期前推i个月（从0开始）
            targetMonth = targetMonth.strftime('%Y-%m')  #格式转为00-00（年-月）
            self.GetBarrageRecordByMonth(targetMonth) #调用api获取当月弹幕日期 

    def GetHistory(self,date):#根据日期获取弹幕
        #验证日期输入
        if self.IsValidDate(date):
            pass
        else:
            raise ValueError('时间格式错误')

        oid = self.oid
        url = 'https://api.bilibili.com/x/v2/dm/history'
        headers = self.headers
        dataDict = {
            'type':1,
            'oid':oid,
            'date':date
            }
        #此处仅需SESSDATA（登录态）
        cookies = self.cookies
        
        res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        rawContent = res.text
        barrage = self.GetBarrageXML(rawContent) # 处理xml，提取弹幕
        return barrage

    def GetBarrageXML(self,rawStr):#解析XML内容
        self.barrageList = [] #定义空数组装载弹幕
        DOMTree=parseString(rawStr)
        docList=DOMTree.documentElement
        barrageList = docList.getElementsByTagName('d') #将d标签全部读取
        for unit in barrageList:
            barrage = {} #每条弹幕数据
            barrageAttr = unit.getAttribute('p') #p标签存储了弹幕信息
            attrList=barrageAttr.split(',')
            barrage['ShowTime'] = attrList[0]
            barrage['Mode'] = attrList[1]
            barrage['FontSize'] = attrList[2]
            barrage['FontColor'] = attrList[3]
            barrage['CommentTime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(attrList[4])))
            barrage['BarragePool'] = attrList[5]
            barrage['UserID'] = attrList[6]
            barrage['RowID'] = attrList[7]
            barrage['Content'] = unit.childNodes[0].data #读取弹幕正文
            #barrageText = unit.childNodes[0].data
            print(barrage)
            self.barrageList.append(barrage)
        print('共读取%d条'% (len(self.barrageList)))

    def SaveToCSV(self,fileName):
        titles = ['ShowTime','Mode','FontSize','FontColor','CommentTime','BarragePool','UserID','RowID','Content']
        data = self.barrageList
        #csv用utf-8-sig来保存
        with open(fileName+'.csv','a',newline='',encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f,fieldnames=titles)
            writer.writeheader()
            writer.writerows(data)
            print('写入完成！')

class UserCatcher(BiliBili):     

    def GetUserFollowerList(self,mid):#获取用户粉丝列表
        url = 'https://api.bilibili.com/x/relation/followers'
        headers = self.headers
        cookies = self.cookies
        dataDict = {
            'vmid':mid,
            'order':'desc',
            'jsonp':'jsonp'
            }
        res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        data = res.json()
        return data

    def GetUserFollowingList(self,mid):#获取用户关注列表
        url = 'https://api.bilibili.com/x/relation/followings'
        headers = self.headers
        cookies = self.cookies
        dataDict = {
            'vmid':mid,
            'order':'desc',
            'jsonp':'jsonp'
            }
        res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        data = res.json()
        return data

    def GetUserInfoByInfo(self,mid):#获取用户信息API ①
        #该API包含生日、等级、姓名、性别、硬币数、签名等
        url = 'https://api.bilibili.com/x/space/acc/info'
        headers = self.headers
        cookies = self.cookies
        dataDict = {
            'mid':mid,
            'jsonp':'jsonp'
            }
        res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        data = res.json()
        return data

    def GetUserInfoByStat(self,mid):#获取用户信息API ②
        #该API包含关注、粉丝数等
        url = 'https://api.bilibili.com/x/relation/stat'
        headers = self.headers
        cookies = self.cookies
        dataDict = {
            'vmid':mid,
            'jsonp':'jsonp'
            }
        res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        data = res.json()
        return data

    def GetUserInfoByUpStat(self,mid):#获取用户信息API ③
        #该API包含UP主视频播放量、文章阅读量、获赞数等
        url = 'https://api.bilibili.com/x/space/upstat'
        headers = self.headers
        cookies = self.cookies
        dataDict = {
            'mid':mid,
            'jsonp':'jsonp'
            }
        res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        data = res.json()
        return data

    def GetUserInfoByTagList(self,mid):#获取用户信息API ④
        #该API包含用户订阅标签
        url = 'https://api.bilibili.com/x/space/tag/sub/list'
        headers = self.headers
        cookies = self.cookies
        dataDict = {
            'vmid':mid,
            'jsonp':'jsonp'
            }
        res = self.session.get(url,headers=headers,params=dataDict,cookies=cookies)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        data = res.json()
        return data

    def GetUserInfo(self,mid):#提取用户信息（调用api）
        user = {}
        user['mid'] = mid
        #调用API
        infoData = self.GetUserInfoByInfo(mid)
        statData = self.GetUserInfoByStat(mid)
        upStatData = self.GetUserInfoByUpStat(mid)
        tagListData = self.GetUserInfoByTagList(mid)
        #提取用户信息
        user['birthday'] = infoData['data']['birthday']
        user['level'] = infoData['data']['level']
        user['name'] = infoData['data']['name']
        user['sex'] = infoData['data']['sex']
        user['coins'] = infoData['data']['coins']
        user['sign'] = infoData['data']['sign']
        user['official'] = infoData['data']['official']

        user['follower'] = statData['data']['follower']
        user['following'] = statData['data']['following']
        
        user['archive-view'] = upStatData['data']['archive']['view']
        user['article-view'] = upStatData['data']['article']['view']
        user['likes'] = upStatData['data']['likes']

        user['tag-list'] = tagListData['data']['tags']
        return user



if __name__ == '__main__':#执行层
    targetBv = 'BV1Ch411y75c'
    #bcObj = BarrageCatcher(target = targetBv)
    #bcObj.GetBarrageRecord()
    #bcObj.SaveToCSV(targetBv)
    #ucObj = UserCatcher()
    #user = ucObj.GetUserInfo(mid='1727142')
    #user = ucObj.GetUserFollowerList(mid='1727142')
    #print(user)
    rpObj = ReplyCatcher(target = targetBv)
    rpObj.GetReply()