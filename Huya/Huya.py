#!/usr/bin/env python3
# coding=utf-8
# author:sakuyo
#----------------------------------

import csv,time,sys,signal
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Huya(object):
    def __init__(self):
        #初始化cookies
        self.cookies = {
            'udb_accdata':'13302912858',
            'udb_biztoken':'AQBx5bA_J3Zh_UkWXzIpdEOxkoRwO2MFIMu5x3fczKoJxoY0V14JJMx-pIuZ2ChHW0WUbbuqtlykhSFGIK6XGK1kWZs11AU4h3yTA58LjI5RtFYLG6B5F7SnJyNPOaoRSp5icFmOzBMAV5qCjMk_SK_boIn1Ll00tUeKuNJw2JRkW8UVOUX3oZLtuh79g41YHXLJXAj-HZ5pE5SgiujRdhtMo7mMpa8hkj_7fFybkhP3ygaTebLvCVddzsoE_mwGe40o7pWVXeI2cV04LpI13ogtvukEdUKjYtnU6N4toZjfpK1sM4iEHcdsx5qIFxqUJPKbkfO-Wb2lvAcCXhgHvP9Q',
            'udb_passdata':3,
            'udb_passport':'sakuyo',
            'udb_status':1,
            'udb_uid':'1199553642488'
            }
        #初始化请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
            }

    def SaveToCSV(self,fileName,headers,contents):
        #titles = ['ShowTime','Mode','FontSize','FontColor','CommentTime','BarragePool','UserID','RowID','Content']
        titles = headers
        #data = self.barrageList
        data = contents
        #csv用utf-8-sig来保存
        with open(fileName+'.csv','a',newline='',encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f,fieldnames=titles)
            writer.writeheader()
            writer.writerows(data)
            print('写入完成！')

class HuyaLive(Huya):

    def __init__(self,target):#初始化 输入值target为直播间ID
        #父类初始化
        Huya.__init__(self)
        self.target = target
        self.barrageList = {}
    
    def Connect(self):#连接直播间
        chrome_options = Options()
        # 使用headless无界面浏览器模式
        #chrome_options.add_argument('--headless') #增加无界面选项
        chrome_options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=chrome_options)
        url  ='https://www.huya.com/'+self.target
        driver.get(url)
        time.sleep(5)
        #loginA = driver.find_element_by_class_name("J_hdLg").click()
        #driver.switch_to.frame("UDBSdkLgn_iframe")
        #switchMode = driver.find_element_by_class_name("input-login").click()
        #driver.find_element_by_class_name("udb-input-account").send_keys('13302912858')
        #driver.find_element_by_class_name("udb-input-pw").send_keys('lcyabc123')
        #driver.find_element_by_id("login-btn").click()
        
        ##返回到主页面
        #driver.switch_to.default_content()
        while True: #无限循环，伪监听
            time.sleep(1) #等待1秒加载
            chatRoomList = driver.find_element_by_id("chat-room__list")
            chatMsgs = chatRoomList.find_elements_by_class_name("J_msg")
            #定位弹幕div，逐条解析
            for chatMsg in chatMsgs:
                try:
                    dataId = chatMsg.get_attribute('data-id') #每条弹幕都有独立data-id
                    content = {} #初始化弹幕内容字典
                    #尝试是否为礼物弹幕
                    try:
                        hSend = chatMsg.find_element_by_class_name("tit-h-send")
                        content['username'] = hSend.find_elements_by_class_name("cont-item")[0].text
                        content['gift'] = hSend.find_element_by_class_name("send-gift").find_element_by_tag_name("img").get_attribute("alt")
                        content['num'] = hSend.find_elements_by_class_name("cont-item")[3].text
                    except:
                        pass
                    #尝试是否为消息弹幕
                    try:
                        mSend = chatMsg.find_element_by_class_name("msg-normal")
                        content["username"] = mSend.find_element_by_class_name("J_userMenu").text
                        content["msg"] = mSend.find_element_by_class_name("msg").text
                    except:
                        pass
                    #存入弹幕列表
                    self.SaveToBarrageList(dataId,content)
                    
                except:
                    continue

    def SaveToBarrageList(self,dataId,content):#弹幕列表存储
        if dataId in self.barrageList or not content: #去重、去空
            pass
        else:
            content['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
            self.barrageList[dataId] = content
            print(dataId,content)







def QuitAndSave(signum, frame):#监听退出信号
    print ('catched singal: %d' % signum)
    hyObj.SaveToCSV('test',['username','time','msg','gift','num'],hyObj.barrageList.values())
    sys.exit(0)


if __name__ == '__main__':#执行层
    #信号监听
    signal.signal(signal.SIGTERM, QuitAndSave)
    signal.signal(signal.SIGINT, QuitAndSave)

    hyObj = HuyaLive('tongcan')
    hyObj.Connect()