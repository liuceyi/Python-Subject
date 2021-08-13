#!/usr/bin/env python3
# coding=utf-8
# author:sakuyo
#----------------------------------

import csv,time,sys,signal,os,time,json
import pandas as pd
import numpy as np
import threading
from tkinter import * 
from tkinter import messagebox
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

sys.setrecursionlimit(100000)

class Huya(object):
    def __init__(self):
        #初始化cookies
        #self.cookies = {
        #    'udb_accdata':'13302912858',
        #    'udb_biztoken':'AQBx5bA_J3Zh_UkWXzIpdEOxkoRwO2MFIMu5x3fczKoJxoY0V14JJMx-pIuZ2ChHW0WUbbuqtlykhSFGIK6XGK1kWZs11AU4h3yTA58LjI5RtFYLG6B5F7SnJyNPOaoRSp5icFmOzBMAV5qCjMk_SK_boIn1Ll00tUeKuNJw2JRkW8UVOUX3oZLtuh79g41YHXLJXAj-HZ5pE5SgiujRdhtMo7mMpa8hkj_7fFybkhP3ygaTebLvCVddzsoE_mwGe40o7pWVXeI2cV04LpI13ogtvukEdUKjYtnU6N4toZjfpK1sM4iEHcdsx5qIFxqUJPKbkfO-Wb2lvAcCXhgHvP9Q',
        #    'udb_passdata':3,
        #    'udb_passport':'sakuyo',
        #    'udb_status':1,
        #    'udb_uid':'1199553642488'
        #    }
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

    def __init__(self, is_manual = False):# 初始化 输入值target为直播间ID
        # 父类初始化
        Huya.__init__(self)
        self.barrageList = {}
        chrome_options = Options()
        # 设置无图模式
        if is_manual == True:
            pass
        else:
            prefs = {"profile.managed_default_content_settings.images": 2}  
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_argument("--mute-audio") # 静音
            # 使用headless无界面浏览器模式
            chrome_options.add_argument('--headless') # 增加无界面选项

        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument('log-level=3')
        chrome_driver_path = r"./chromedriver.exe"
        self.driver = webdriver.Chrome(options = chrome_options, executable_path = chrome_driver_path)
        url = 'https://www.huya.com/'
        self.driver.get(url)

    def SetTarget(self, target):
        self.target = target
        url = 'https://www.huya.com/' + self.target
        self.driver.get(url)
        try:
            s = self.driver.find_element_by_id("J_roomTitle").get_attribute('title')
            print('进入房间：' + s)
            return True
        except:
            print('找不到该房间')
            return False

    def Login(self, username, psw):#连接直播间
        #登录
        try:
            self.driver.find_element_by_xpath("//*[@id='J_duyaHeaderRight']/div/div[2]/a").click()
        except:
            pass
        try:
            self.driver.switch_to.frame("UDBSdkLgn_iframe")
        except:
            time.sleep(1)
            self.driver.switch_to.frame("UDBSdkLgn_iframe")

        self.driver.find_element_by_class_name("input-login").click()

        self.driver.find_element_by_xpath("//input[contains(@class, 'udb-input-account')]").send_keys(username)
        self.driver.find_element_by_xpath("//input[contains(@class, 'udb-input-pw')]").send_keys(psw)
        self.driver.find_element_by_id("login-btn").click()
        #返回到主页面
        self.driver.switch_to.default_content()
        time.sleep(5)
        if self.CheckLogin() == True:
            cookies = self.driver.get_cookies()
            cookieStr = json.dumps(cookies)

            return (True, cookieStr)
        else:
            return (False, None)

    def CheckLogin(self):
        userHd = self.driver.find_element_by_xpath("//*[@id='J_duyaHeaderRight']/div/div[2]/a")
        userHd_href = userHd.get_attribute('href')
        if '#' in userHd_href:
            # print('密码错误')
            return False
        else:
            # print('登录成功')
            return True
        
    def LoadCookie(self, cookieStr):
        print(cookieStr)
        if cookieStr == '':
            return False
        cookies = json.loads(cookieStr)
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        
        try:
            self.driver.refresh()
            return self.CheckLogin()
        except:
            print('cookie读取出错：'+cookies)
            return False


    def GetCookie(self):
        cookies = self.driver.get_cookies()
        cookieStr = json.dumps(cookies)
        return cookieStr

    def SendBarrage(self, msg):
        time.sleep(3)
        try:
            chatSpeaker = self.driver.find_element_by_class_name("chat-room__input")
            chatSpeaker.find_element_by_id("pub_msg_input").send_keys(msg)
            chatSpeaker.find_element_by_id("msg_send_bt").click()
            return True
        except:
            return False
        
    def ListenBarrage(self):
        while True: #无限循环，伪监听
            time.sleep(1) #等待1秒加载
            chatRoomList = self.driver.find_element_by_id("chat-room__list")
            chatMsgs = chatRoomList.find_elements_by_class_name("J_msg")
            #定位弹幕div，逐条解析
            for chatMsg in chatMsgs:
                try:
                    dataId = chatMsg.get_attribute('data-id') #每条弹幕都有独立data-id
                    content = {} #初始化弹幕内容字典
                    #尝试是否为礼物弹幕
                    try:
                        hSend = chatMsg.find_element_by_class_name("tit-h-send")
                        content['username'] = hSend.find_element_by_class_name("J_userMenu").text
                        content['gift'] = hSend.find_element_by_class_name("send-gift").find_element_by_tag_name("img").get_attribute("alt")
                        content['num'] = hSend.find_elements_by_class_name("cont-item")[3].text
                    except:
                        content = {}
                    #尝试是否为消息弹幕
                    try:
                        # mSend = chatMsg.find_element_by_class_name("msg-normal")
                        content["username"] = chatMsg.find_element_by_class_name("J_userMenu").text
                        #//*[@id="chat-room__list"]/li[35]/div/span[3]
                        content["msg"] = chatMsg.find_element_by_class_name("msg").text
                    except:
                        content = {}
                    #存入弹幕列表
                    if content != {}:
                        self.SaveToBarrageList(dataId,content)
                except:
                    continue
       

    def SaveToBarrageList(self,dataId,content):#弹幕列表存储
        if dataId in self.barrageList or not content: #去重、去空
            pass
        else:
            content['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
            self.barrageList[dataId] = content
            print(len('已记录'+self.barrageList), end='\r')

class HuyaMsg(object):
    def __init__(self):
        url = 'https://i.huya.com/index.php?m=Msg&do=listMsg'
        self.driver.get(url)

    def Search(self, target):
        self.driver.find_element_by_xpath("//*[@id='root']/div/div[1]/div[2]/div[1]/input").send_keys(target)
        search_list = self.driver.find_elements_by_class_name('search-list')
        for item in search_list:
            nickname = item.find_element_by_class_name('search-list-nick').text
            if nickname == target:
                item.click()
                break
    

class HuyaUI(object):
    def __init__(self):
        self.time_diff = 20
        self.readyToSend = False

    def Start(self):
        root = Tk()                     # 创建窗口对象的背景色
        root.geometry("1000x600")
        root.title("Barrage Script")
        frame_connect = Frame(root)
        frame_barrage = Frame(root)
        frame_time = Frame(root)
        # Connect Frame
        Label(frame_connect, text="房间号").grid(row = 0, sticky = E)
        target_input = Entry(frame_connect, bd = 5)
        target_input.grid(row = 0, column = 1, padx = 10, pady = 10)
        connectBtn = Button(frame_connect, text="连接", command = lambda: Connect(target_input.get()))
        connectBtn.grid(row = 0, column = 2)
        # Barrage Frame
        Label(frame_barrage, text="话术").grid(row = 0, sticky = E)
        barrage_input = ttk.Combobox(frame_barrage)
        barrage_input['value'] = ('666','哈哈哈哈','秀啊','主播真帅')
        barrage_input.grid(row = 0, column = 1, padx = 10, pady = 10)
        barrageBtn = Button(frame_barrage, text="设定", command = lambda: SetBarrage(barrage_input.get()))
        barrageBtn.grid(row = 0, column = 2)
        # Time Frame
        Label(frame_time, text="时间间隔").grid(row = 0, sticky = E)
        time_input = Entry(frame_time, bd = 5)
        time_input.grid(row = 0, column = 1, padx = 10, pady = 10)
        timeBtn = Button(frame_time, text="设置", command = lambda: SetTime(time_input.get()))
        timeBtn.grid(row = 0, column = 2)

        def IsReadyToSend():
            ck['text'] = v.get()
            if ck['text'] == 'ON':
                self.readyToSend = True
                print('准备发送弹幕...')
                SendBarrage()
            else:
                print('停止发送弹幕')
                self.readyToSend = False

        v = StringVar()
        v.set('1')
        ck = ttk.Checkbutton(root, variable=v, text='OFF', onvalue='ON', offvalue='OFF', command=IsReadyToSend)
        


        data = pd.read_excel("data.xlsx", sheet_name = 0)
        data_temp = data.copy(deep=True)
        data_temp.fillna('', inplace=True)
        columns = tuple(np.append(data_temp.columns.values, "状态"))
        tree = ttk.Treeview(root, height=18, show="headings", columns=columns)

        for item in data_temp.columns.values:
            tree.column(item, width=100, anchor='center')
            tree.heading(item, text=item)
        tree.column("状态", width=100, anchor='center')
        tree.heading("状态", text="状态")

        tree.pack(side=LEFT, fill=BOTH)
        data_temp['obj'] = None
        data_temp['话术'] = '666'

        def Login(obj):
            obj = HuyaLive()
            account_data = data_temp.iloc[i, :-2]
            user = str(account_data['账号'])
            psw = str(account_data['密码'])
            cookie = str(account_data['cookie'])
            cookieLogin = obj.LoadCookie(cookie)
            if cookieLogin == True:
                res = True
            else:
                (res, cookie) = obj.Login(user, psw)
            if res == True:
                status = "登录成功"
                response = True
            else:
                status = "登录失败, 点击手动登录"
                obj.driver.quit()
                response = False
            account_data = np.append(account_data, status)
            return (response, account_data, cookie)
        def ManualLogin(event):
            item = tree.selection()[0]
            index = tree.index(item)
            data_temp['obj'][index] = HuyaLive(True)
            while True:
                try:
                    if data_temp['obj'][index].CheckLogin():
                        cookie = data_temp['obj'][index].GetCookie()
                        data['cookie'][index] = cookie
                        data.to_excel('data.xlsx', index=False, header=True)
                        break
                    else:
                        pass
                except:
                    pass
            data_temp['obj'][index].driver.quit()
            Login(data_temp['obj'][index])

        for i in range(len(data_temp)): # 写入数据
            (res, account_data, cookie) = Login(data_temp['obj'][i])
            if res == True:
                data['cookie'][i] = cookie
                data.to_excel('data.xlsx', index=False, header=True)
            tree.bind('<ButtonRelease-1>', ManualLogin)
            tree.insert('', i, values=tuple(account_data))




        


        def Connect(input):
            for item in tree.get_children():
                obj = data_temp['obj'][tree.index(item)]
                res = obj.SetTarget(input)
                if res == True:
                    status = "加入房间成功"
                else:
                    status = "加入房间失败"
                tree.set(item, "状态", status)



        def SetBarrage(msg):
            data_temp['话术'] = ''
            for item in tree.get_children():
                data_temp['话术'][tree.index(item)] = msg
            messagebox.showinfo('成功','话术设置成功')

        def SendBarrage():
            if self.readyToSend == True:
                print('开始发送  '+time.asctime(time.localtime(time.time())))
            else:
                print('停止发送', self.readyToSend)
                return

            def Send(obj, msg, tree):
                while self.readyToSend == True:
                    res = obj.SendBarrage(msg)
                    if res == True:
                        status = "发送成功"
                    else:
                        status = "发送失败"

                    tree.set(item, "状态", status)
                    time.sleep(self.time_diff)
                

            accounts = []
            for item in tree.get_children():
                obj = data_temp['obj'][tree.index(item)]
                msg = data_temp['话术'][tree.index(item)]
                time_next = data_temp['发送间隔'][tree.index(item)]
                account = threading.Thread(target=Send, args=(obj, msg, tree,))
                accounts.append(account)
                account.start()
                time.sleep(time_next)
                


        def SetTime(new_time):
            self.time_diff = new_time
            messagebox.showinfo('成功','时间间隔设置成功')

        frame_connect.pack(padx=1,pady=1)
        frame_time.pack(padx=1, pady=1)
        frame_barrage.pack(padx=1,pady=1)
        ck.pack()

        root.mainloop()                 # 进入消息循环





def QuitAndSave(signum, frame):#监听退出信号
    print('catched singal: %d' % signum)
    hyObj.SaveToCSV(hyObj.target, ['username','time','msg','gift','num'], hyObj.barrageList.values())
    sys.exit(0)


if __name__ == '__main__':#执行层
    #信号监听
    signal.signal(signal.SIGTERM, QuitAndSave)
    signal.signal(signal.SIGINT, QuitAndSave)
    
    hyObj = HuyaUI()
    hyObj.Start()