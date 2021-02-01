#!/usr/bin/env python3
# coding=utf-8
# author:sakuyo
#----------------------------------
import requests,csv,re

class Weibo(object):
    def __init__(self):
        #初始化cookies
        self.cookies = {
            }
        #初始化请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
            }
        self.session = requests.Session() #启动弹幕读取session

    def SaveToFile(self,fileName,headers,contents):
        titles = headers
        data = contents
        #csv用utf-8-sig来保存
        with open(fileName+'.csv','a',newline='',encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f,fieldnames=titles,dialect='excel')
            writer.writeheader()
            writer.writerows(data)
            print('写入完成！')

    def GetSearch(self,keyword,pageMax = 10):
        msgList = []
        for pageNum in range(1,pageMax):
            data = self.GetSearchData(keyword,pageNum)
            msgList.extend(self.DealSearchData(data))
        self.SaveToFile('keyword',headers = ['userId','user','mobile','content'],contents = msgList)

    
    def GetSearchData(self,keyword,pageNum):
        url = 'https://m.weibo.cn/api/container/getIndex'
        dataDict = {
            'containerid':'100103type%3D1%26t%3D10%26q%3D'+keyword,
            'page':pageNum
            }
        headers = self.headers
        cookies = self.cookies
        res = self.session.get(url,params=dataDict,headers=headers,cookies=cookies)
        res.raise_for_status()
        res.encoding = 'utf-8'
        data = res.json()
        return data

    def DealSearchData(self,data):
        try:
            cardList = data['data']['cards']
            msgList = []
            for i in range(len(cardList)):
                try:
                    weiboList = data["data"]["cards"][i]
                    
                    if 'card_group' in weiboList.keys():
                        sector = weiboList["card_group"][0]["mblog"]
                        weibo={}
                        weibo['content'] = re.sub(r"</?(.+?)>", "", sector["text"]) # 去除标签
                        weibo['user'] = sector["user"]["screen_name"]
                        weibo['userId'] = sector["user"]["id"]
                        weibo['mobile'] = sector["source"]
                        msgList.append(weibo)

                    else:
                        sector = weiboList["mblog"]
                        weibo={}
                        weibo['content'] = re.sub(r"</?(.+?)>", "", sector["text"]) # 去除标签
                        weibo['user'] = sector["user"]["screen_name"]
                        weibo['userId'] = sector["user"]["id"]
                        weibo['mobile'] = sector["source"]
                        msgList.append(weibo)
  
                    
                except Exception as err:
                    print(err)
            return msgList
        except Exception as err:
            raise err

if __name__ == '__main__':#执行层
    weibo = Weibo()
    weibo.GetSearch('难听')




