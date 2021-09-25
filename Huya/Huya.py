#!/usr/bin/env python3
# coding=utf-8
# author:sakuyo
#----------------------------------

import csv,time,datetime,time,json,requests,base64,re,uuid
import asyncio
import danmaku
from bs4 import BeautifulSoup
import pandas as pd
import threading
import webbrowser
from PIL import Image as PILImage
from tkinter import * 
from tkinter import messagebox, ttk
from tkinter.simpledialog import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains


# Huya Console
class Huya(object):
    def __init__(self):
        self.headers = {
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            # 'Accept': '*/*',
            # 'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2'
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

# Captcha Console
class HuyaCaptcha(object):
    def __init__(self, username, psw):
        self.apiUser = username
        self.psw = psw
        self.token = 'B3F8A7D497B1B6E04B3C3989B657'
        # self.Login()


    def Login(self):
        url = 'http://api.liuxing985.com:8888/sms/api/login?username={}&password={}'.format(self.apiUser, self.psw)
        res_raw = requests.get(url)
        print(res_raw.text)
        res = json.loads(res_raw.text)
        if res['code'] == 0:
            self.token = res['token']
            print('已登录，token：{}'.format(self.token))

    def GetMessage(self, sid, phone):
        url = 'http://www.liuxing985.com:81/sms/api/getMessage?token={}&sid={}&phone={}'.format(self.token, sid, phone)
        res_raw = requests.get(url)
        print(res_raw.text)
        res = json.loads(res_raw.text)
        if res['code'] == 0:
            msg_raw = res['sms']
            msg = re.findall(r"：(\d+)", msg_raw)[0]
            return msg
        elif res['code'] == 401:
            self.Login()
        elif res['code'] == -1 or res['code'] == -4:
            time.sleep(5)
            return self.GetMessage(sid, phone)
        return False

    def GetPhone(self, sid, phone=''):
        url = 'http://www.liuxing985.com:81/sms/api/getPhone?token={}&sid={}&phone={}'.format(self.token, sid, phone)
        res_raw = requests.get(url)
        print(res_raw.text)
        res = json.loads(res_raw.text)
        if res['code'] == 0:
            msg = res['phone']
            return msg
        elif res['code'] == 401:
            self.Login()
        return False

# Live Console
class HuyaLive(Huya):

    def __init__(self, is_manual = False, ip=''):# 初始化 输入值target为直播间ID
        # 父类初始化
        Huya.__init__(self)
        self.captchaObj = HuyaCaptcha('api-sk53ln8H', '102056')
        self.barrageList = []
        self.target = ''
        self.is_listen = False
        self.dmc = None
        chrome_options = Options()
        # 设置无图模式
        if is_manual == True:
            pass
        else:
            prefs = {
                # "profile.managed_default_content_settings.images": 2,
                "webrtc.ip_handling_policy": "disable_non_proxied_udp",

                "webrtc.multiple_routes_enabled": False,
                "webrtc.nonproxied_udp_enabled": False
            }  
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_argument("--mute-audio") # 静音
            # 使用headless无界面浏览器模式
            chrome_options.add_argument('--headless') # 增加无界面选项
        # 切换代理IP
        if ip =='':
            pass
        else:
            chrome_options.add_argument("--proxy-server=" + ip)
        chrome_options.add_experimental_option("excludeSwitches",["enable-logging"])
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument('log-level=3')
        chrome_driver_path = r"./chromedriver.exe"
        self.driver = webdriver.Chrome(options = chrome_options, executable_path = chrome_driver_path)
        self.driver.maximize_window()
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


    def Register(self, phoneNum, psw):
        try:
            WebDriverWait(self.driver,10,0.5).until(EC.presence_of_element_located((By.XPATH,"//*[@id='J_duyaHeaderRight']/div/div[2]/a")))
            self.driver.find_element_by_xpath("//*[@id='J_duyaHeaderRight']/div/div[2]/a").click()
            WebDriverWait(self.driver,10,0.5).until(EC.presence_of_element_located((By.XPATH,"//*[@id='UDBSdkLgn_iframe']")))
            lgn_frame = self.driver.find_element_by_xpath("//*[@id='UDBSdkLgn_iframe']")
            self.driver.switch_to.frame(lgn_frame)
        except Exception as e:
            print(str(e))

        WebDriverWait(self.driver,10,0.5).until(EC.presence_of_element_located((By.XPATH,"//*[@id='quick-login-section']/div[4]/i")))
        self.driver.find_element_by_class_name("input-login").click()
        self.driver.find_element_by_class_name("go-register").click()
        
        WebDriverWait(self.driver,10,0.5).until(EC.presence_of_element_located((By.XPATH,"//*[@id='register-form']/div[1]/input")))
        self.driver.find_element_by_xpath("//*[@id='register-form']/div[1]/input").send_keys(phoneNum)
        self.driver.find_element_by_xpath("//*[@id='register-form']/div[3]/input").send_keys(psw)

        self.driver.find_element_by_xpath("//*[@id='register-form']/div[2]/span").click()
        
        def DealVerify():
            try:
                WebDriverWait(self.driver,10,0.5).until(EC.presence_of_element_located((By.XPATH,"//iframe[contains(@id,'layui-layer-iframe')]")))
                register_frame = self.driver.find_element_by_xpath("//iframe[contains(@id,'layui-layer-iframe')]")
    
                while self.driver.find_element_by_xpath("//iframe[contains(@id,'layui-layer-iframe')]"):
                    register_frame.screenshot('./captcha.png') 
                    self.driver.switch_to.frame(register_frame)
                    
                    try:
                        WebDriverWait(self.driver,10,0.5).until(EC.presence_of_element_located((By.XPATH,"//*[@id='pic-code']")))
                        captchaImg = self.driver.find_element_by_xpath("//*[@id='pic-code']")
                        mode = 0
                        src = self.driver.find_element_by_xpath("//*[@id='pic-code']").get_attribute('src').replace('data:image/png;base64,', '')
                        
                        captcha = self.DealCaptcha(mode=mode, src=src)
                        self.driver.find_element_by_xpath("/html/body/div/div[2]/div[1]/input").send_keys(captcha)
                        time.sleep(0.5)
                        self.driver.find_element_by_xpath("/html/body/div/div[2]/div[2]").click()
                        time.sleep(1)
                    except:
                        WebDriverWait(self.driver,10,0.5).until(EC.presence_of_element_located((By.XPATH,"//*[@id='bgImg']")))
                        captchaImg = self.driver.find_element_by_xpath("//*[@id='bgImg']")
                        mode = 1
                        location = captchaImg.location  # 获取验证码x,y轴坐标
                        size = captchaImg.size  # 获取验证码的长宽
                        x = int(location['x'])
                        y = int(location['y'])
                        rangle = (x, y, int(x + size['width']), int(y + size['height']))  # 写成我们需要截取的位置坐标
                        i = PILImage.open("./captcha.png")  # 打开截图
                        frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
                        frame4.save('./save.png') # 保存我们接下来的验证码图片 进行打码
                        xDis = self.DealCaptcha(mode=mode)
                        print('distance:{}'.format(xDis))
                        self.MoveToGap(int(xDis), self.driver.find_element_by_xpath("/html/body/div/div[2]/div[2]/span"))

                    time.sleep(1)
                    self.driver.switch_to.parent_frame()
            except Exception as e:
                print(str(e))
        
        DealVerify()
        code = self.captchaObj.GetMessage('325', phone=phoneNum)
        try:
            lgn_frame = self.driver.find_element_by_xpath("//*[@id='UDBSdkLgn_iframe']")
            self.driver.switch_to.frame(lgn_frame)
        except:
            pass
        self.driver.find_element_by_xpath("//*[@id='register-form']/div[2]/input").send_keys(code)
        self.driver.find_element_by_xpath("//*[@id='register-form']/div[6]/label/input").click()
        self.driver.find_element_by_id("reg-btn").click()

        try:
            DealVerify()
        except Exception as e:
            print(str(e))

    def DealCaptcha(self, mode, src=''):
        if mode == 0:
            typeId = 1003
            b64 = src
        elif mode == 1:
            typeId = 33
            img = "./save.png"
            with open(img, 'rb') as f:
                base64_data = base64.b64encode(f.read())
                b64 = base64_data.decode()
        data = {"username": "13377235802", "password": "as971014", "typeid": typeId, "image": b64}
        result = json.loads(requests.post("http://api.ttshitu.com/predict", json=data).text)
        if result['message'] == 'success':
            return result["data"]["result"]
        else:
            print(result["message"])
            return False
        
    def MoveToGap(self, distance, slider):
        # 移动轨迹
        tracks = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 2
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            tracks.append(round(move))



        ActionChains(self.driver).click_and_hold(slider).perform()
        for x in tracks:
            ActionChains(self.driver).move_by_offset(xoffset = x, yoffset = 0).perform()
        time.sleep(0.3)
        ActionChains(self.driver).release().perform()

    def Login(self, username, psw):#连接直播间
        #登录
        try:
            self.driver.find_element_by_xpath("//*[@id='J_duyaHeaderRight']/div/div[2]/a").click()
            time.sleep(1)
            self.driver.switch_to.frame("UDBSdkLgn_iframe")
        except:
            pass
        
        self.driver.find_element_by_class_name("input-login").click()

        self.driver.find_element_by_xpath("//input[contains(@class, 'udb-input-account')]").send_keys(username)
        self.driver.find_element_by_xpath("//input[contains(@class, 'udb-input-pw')]").send_keys(psw)
        self.driver.find_element_by_id("login-btn").click()
        #返回到主页面
        self.driver.switch_to.default_content()
        time.sleep(2)
        if self.CheckLogin() == True:
            cookies = self.driver.get_cookies()
            cookieStr = json.dumps(cookies)

            return (True, cookieStr)
        else:
            return (False, None)

    def CheckLogin(self):
        WebDriverWait(self.driver,20,0.5).until(EC.presence_of_element_located((By.XPATH,"//*[@id='J_duyaHeaderRight']/div/div[2]/a")))
        userHd = self.driver.find_element_by_xpath("//*[@id='J_duyaHeaderRight']/div/div[2]/a")
        userHd_href = userHd.get_attribute('href')
        if '#' in userHd_href:
            # print('登录失败')
            return False
        else:
            # print('登录成功')
            
            return True
        
    def GetUsername(self, cookieStr = ''):
        url = "https://i.huya.com/"
        
        if cookieStr == '':
            for cookie in self.cookies:
                cookieStr += '{}={}; '.format(cookie['name'], cookie['value'])
        else:
            pass

        headers = self.headers
        headers['Cookie'] = cookieStr
        # headers['Content-Type'] = 'application/json'
        # data = json.dumps({"appId":"5002","version":"1.0","data":{"uid":uid}})
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text)
            nickname_html = soup.find('h2',{'class':'uesr_n'})
            nickname = nickname_html.text
            self.username = nickname
            return True
        except Exception as e:
            print('获取昵称失败:'+str(e))
            return False

    def LoadCookie(self, cookieStr):
        if cookieStr == '':
            return False

        try:
            cookies = json.loads(cookieStr)
        except:
            cookies_raw = cookieStr.split(';')
            cookies = []
            
            for cookie_raw in cookies_raw:
                cookie_obj = {}
                cookie_arr = cookie_raw.split('=')
                cookie_obj['name'] = cookie_arr[0].strip()
                cookie_obj['value'] = cookie_arr[1].strip()
                cookie_obj['domain'] = '.huya.com'
                cookies.append(cookie_obj)

        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except:
                continue
        
        try:
            self.driver.refresh()
            self.cookies = cookies
            return self.CheckLogin()
        except:
            print('cookie读取出错：' + str(cookies))
            return False

    def GetCookie(self):
        cookies = self.driver.get_cookies()
        cookieStr = json.dumps(cookies)
        return cookieStr

    def SendBarrage(self, msg):
        try:
            self.is_listen = True
            #listen_thread = threading.Thread(target=self.ListenBarrage)
            #listen_thread.start()
            self.ListenBarrage()
            WebDriverWait(self.driver,20,0.5).until(EC.presence_of_element_located((By.XPATH,"//*[@id='tipsOrchat']/div/div[9]/div[3]")))
            chatSpeaker = self.driver.find_element_by_class_name("chat-room__input")
            chatSpeaker.find_element_by_id("pub_msg_input").send_keys(msg)
            chatSpeaker.find_element_by_id("msg_send_bt").click()
            print('弹幕已发送')
            start_time = datetime.datetime.now()
            end_time = start_time + datetime.timedelta(seconds=10)
            while end_time > datetime.datetime.now():
                (res, status) = self.CheckSend(msg)
                if res == True:
                    return status
                
            print(self.barrageList)
            self.is_listen = False
            return status
        except Exception as e:
            print('弹幕发送出错')
            print(str(e))
    
    def CheckSend(self, msg):
        for barrage in self.barrageList:
            if (barrage['username'] == self.username and barrage['msg'] == msg):
                print('消息一致')

                return (True, '发送成功')

        try:
            warning_text = self.driver.find_element_by_xpath("//*[@id='pubNoticMe']/p").text
            # print(warning_text)
            if '禁言' in warning_text:
                return (False, '全平台禁言')
        except Exception as e:
            print(str(e))
            return (False, '发送失败')

        return (False, '发送失败')
                    
    # def ListenBarrage(self):
        while self.is_listen == True: #无限循环，伪监听
            time.sleep(1) #等待1秒加载
            chatRoomList = self.driver.find_element_by_id("chat-room__list")
            chatMsgs = chatRoomList.find_elements_by_class_name("J_msg")
            #定位弹幕div，逐条解析
            for chatMsg in chatMsgs:
                try:
                    dataId = chatMsg.get_attribute('data-id') #每条弹幕都有独立data-id
                    content = {} #初始化弹幕内容字典

                    #尝试是否为消息弹幕
                    try:
                        content["username"] = chatMsg.find_element_by_class_name("J_userMenu").text
                        content["msg"] = chatMsg.find_element_by_class_name("msg").text
                    except:
                        content = {}
                    #存入弹幕列表
                    if content != {}:
                        self.SaveToBarrageList(dataId, content)
                except:
                    continue
       
    # def SaveToBarrageList(self,dataId,content):#弹幕列表存储
        if dataId in self.barrageList or not content or content['msg'] == '': #去重、去空
            pass
        else:
            content['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            content['detected'] = False
            # print(content)
            self.barrageList[dataId] = content
    

    def ListenBarrage(self):
        if self.dmc != None:
            pass
        else:
            async def printer(q):
                while self.is_listen == True:
                    m = await q.get()
                    if m['msg_type'] == 'danmaku':
                        content = {}
                        content['username'] = m["name"]
                        content['msg'] = m["content"]
                        content['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        self.barrageList.append(content)
                print('停止监听')
                await self.dmc.stop()

            async def main(url):
                q = asyncio.Queue()
                self.dmc = danmaku.DanmakuClient(url, q)
                asyncio.create_task(printer(q))
                await self.dmc.start()
                print('开始监听')

            a = 'https://www.huya.com/' + self.target
            asyncio.run(main(a))

# Controller Console
class HuyaLiveController(object):
    data_origin = None
    def __init__(self):
        self.time_diff = 20
        self.readyToSend = False
        self.UI = HuyaUI(self)
        self.preset_msg = '666'
        self.preset_time = 5
        self.Verify()

    def Start(self):
        self.data_origin = pd.read_excel("data.xlsx", sheet_name = 0)
        self.data = self.data_origin.copy(deep=True)
        self.data.fillna('', inplace=True)
        self.data['房间'] = ''
        self.data['话术'] = self.preset_msg
        self.data['状态'] = '准备登录'
        self.data['obj'] = None
        self.cate_dict = self.GetCategory()
        self.UI.MainUI()

    def BindUI(self, UI):
        self.UI = UI

    def ManualCookie(self):
        def ThreadManual():
            obj = HuyaLive(True)
            while True:
                try:
                    if obj.CheckLogin():
                        cookie = obj.GetCookie()
                        break
                    else:
                        pass
                except:
                    pass

            obj.driver.quit()
            self.UI.CopyUI(cookie)
            
        manual_thread = threading.Thread(target=ThreadManual)
        manual_thread.start()

    def ReadyToSend(self):
        self.readyToSend = True
        self.SendBarrage()
        def CheckReSend():
            start_time = datetime.datetime.now()
            end_time = start_time + datetime.timedelta(seconds=float(self.time_diff))
            while end_time > datetime.datetime.now():
                if self.readyToSend == False:
                    return
            self.ReadyToSend()
        
        re_send_thread = threading.Thread(target=CheckReSend)
        re_send_thread.start()

    def StopSend(self):
        self.readyToSend = False

        print('停止发送弹幕')
        # StopSendBarrage()
    
    def SendBarrage(self):
        print('准备发送弹幕')
        def ThreadSend():
            def Send(obj, msg, index):
                self.data['状态'][index] = "弹幕已发送，检测是否成功..."
                self.UI.UpdateTree(self.data)
                status = obj.SendBarrage(msg)
                if status == None:
                    pass
                else:
                    self.data['状态'][index] = status
                self.UI.UpdateTree(self.data)

            accounts = []
            for i in range(len(self.data)):
                obj = self.data['obj'][i]
                msg = self.data['话术'][i]
                time_next = self.data['发送间隔'][i]
                if time_next == '':
                    time_next = 5
                account = threading.Thread(target=Send, args=(obj, msg, i))
                # accounts.append(account)
                account.start()
                time.sleep(float(time_next))


        # ThreadSend()
        send_thread = threading.Thread(target=ThreadSend)
        send_thread.start()

    def EditData(self, column_name, index, new_val):
        self.data[column_name][index] = new_val
        self.UI.UpdateTree(self.data)
        if column_name == 'cookie':
            self.Login(index)

    def Login(self, index):   
        def ThreadLogin():
            while True:
                try:
                    obj = HuyaLive()
                    # obj = HuyaLive(ip=GetProxy())
                    break
                except:
                    continue
            
            cookie = str(self.data['cookie'][index])
            cookieLogin = obj.LoadCookie(cookie)
            if cookieLogin == True:
                status = "登录成功"
                obj.GetUsername()
                response = True
                self.data['obj'][index] = obj
                self.data['状态'][index] = status
                self.data['cookie'][index] = cookie
                self.UI.UpdateTree(self.data)
                self.data_origin['cookie'][index] = cookie
                self.data_origin.to_excel('data.xlsx', index=False, header=True)
                return response

            obj.driver.quit()
            status = "登录失败"
            self.data['状态'][index] = status
            self.UI.UpdateTree(self.data)
            response = False
            return response
        login_thread = threading.Thread(target=ThreadLogin)
        login_thread.start()
        # ThreadLogin()

    def LoadAccount(self):
        for i in range(len(self.data)): # 写入数据
            self.Login(i)


    def AddAccount(self, cookie):
        new_account = pd.Series({'cookie':cookie, '发送间隔':self.preset_time, '状态':'准备登录', '房间':'', '话术':self.preset_msg})
        self.data = self.data.append(new_account, ignore_index=True)
        self.data_origin = self.data_origin.append(pd.Series({'cookie':cookie, '发送间隔':self.preset_time}), ignore_index=True)
        self.data_origin.to_excel('data.xlsx', index=False, header=True)
        self.UI.UpdateTree(self.data)
        self.Login(len(self.data)-1)

    def Connect(self, input):
        def ThreadConnect():
            for i in range(len(self.data['obj'])):
                res = self.data['obj'][i].SetTarget(input)
                if res == True:
                    status = "加入房间成功"
                else:
                    status = "加入房间失败"
                self.data['状态'][i] = status
                self.UI.UpdateTree(self.data)
        connect_thread = threading.Thread(target=ThreadConnect)
        connect_thread.start()

    def SetBarrage(self, msg):
        self.preset_msg = msg
        self.data['话术'] = ''
        for i in range(len(self.data)):
            self.data['话术'][i] = msg
        self.UI.UpdateTree(self.data)
        return True

    def SetTime(self, new_time):
        self.time_diff = new_time

    def OpenLink(self, index):
        target = self.data['obj'][index].target
        if target == '':
            return False
        link = 'https://www.huya.com/' + target
        webbrowser.open(link)

    def ChooseCate(self, input):
        url = self.cate_dict[input]
        room_list = self.GetCateRoom(url)
        room_url = room_list[0].replace('https://www.huya.com/', '')
        self.Connect(room_url)

    def GetCategory(self):
        res = requests.get('https://www.huya.com/g')
        soup = BeautifulSoup(res.text)
        titles_html = soup.find_all('li',{'class':'g-gameCard-item'})
        titles = {}
        for title_html in titles_html:
            title_href_html = title_html.find('a')
            title_href = title_href_html.get('href')
            title_name = title_html.text.replace('\n', '')
            titles[title_name] = title_href

        return titles

    def GetCateRoom(self, url):
        res = requests.get(url)
        soup = BeautifulSoup(res.text)
        titles_html = soup.find_all('li',{'class':'game-live-item'})
        titles = []
        for title_html in titles_html:
            title_href_html = title_html.find('a')
            title_href = title_href_html.get('href')
            titles.append(title_href)

        return titles

    def GetMac(self):
        mac = uuid.UUID(int = uuid.getnode()).hex[-12:]
        return mac
    
    def CheckActive(self):
        headers = {
            'Content-Type': 'application/json'
        }
        mac = uuid.UUID(int = uuid.getnode()).hex[-12:]
        data = {'flag':'check-user', 'mac':mac}
        data_json = json.dumps(data)
        res = requests.post('https://www.sakuyo.cn/backend/huya/user.php', data = data_json, headers=headers)
        content = json.loads(res.text)
        if content['code'] == 200:
            return content['msg']

    def Verify(self):
        if self.CheckActive() == True:
            self.Start()
        else:
            self.UI.VerifyUI()


# UI Console
class HuyaUI(object):
    def __init__(self, controller):
        self.controller = controller
        self.width = 150
        self.height = 18
        self.btnWidth = 20

    def FormatWindow(self, obj, w=1500, h=1200):
        sw = obj.winfo_screenwidth()
        sh = obj.winfo_screenheight()
        x = (sw - w) / 2
        y = (sh - h) / 2
        obj.geometry("%dx%d+%d+%d" % (w, h, x, y))

    def selectItem(self, row, col):
        curItem = self.tree.item(row)
        print ('curItem = ', curItem)

        if col == '#0':
            cell_value = curItem['text']
        elif col == '#1':
            cell_value = curItem['values'][0]
        elif col == '#2':
            cell_value = curItem['values'][1]
        elif col == '#3':
            cell_value = curItem['values'][2]
        print ('cell_value = ', cell_value)
        return cell_value

    def CopyUI(self, content):
        def copy():
            self.root.clipboard_clear() 
            self.root.clipboard_append(l1.get()) 

        newWindow = Toplevel(self.root)
        l1 = Entry(newWindow, width=100, bd=5)
        l1.insert(0, content)
        l2 = Button(newWindow, text='复制', command=copy)
        l1.pack()
        l2.pack()

    def UpdateTree(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i in range(len(data)):
            self.tree.insert('', i, values=tuple(data.drop('obj', axis=1).iloc[i,:]))
        self.tree.update()
        self.newBtn.place(x = self.width * 2 - 0.5 * self.btnWidth, y = (len(data) - 1) * (self.height + 2) + 45)
        self.newBtn.update()

    def MainUI(self): 
        def SetCell(event): # 双击进入编辑状态
            column = self.tree.identify_column(event.x)  # 列
            row = self.tree.identify_row(event.y)  # 行
            cn = int(str(column).replace('#',''))
            column_name = columns[cn - 1]
            rn = self.tree.index(row)
            entryedit = Text(self.root, width = 18, height = 1)
            entryedit.place(x=(cn - 1) * self.width + 1, y = 6 + (rn + 1) * (self.height + 2))
            def saveedit(event):
                new_val = entryedit.get(0.0, "end")
                if new_val == '':
                    return
                if column_name == '房间':
                    self.controller.EditData('房间', rn - 1, new_val)
                elif column_name == '话术':
                    self.controller.EditData('话术', rn - 1, new_val)
                elif column_name == '发送间隔':
                    self.controller.EditData('发送间隔', rn - 1, new_val)
                elif column_name == '状态':
                    pass
                elif column_name == 'cookie':
                    self.controller.EditData('cookie', rn - 1, new_val)
                
                entryedit.destroy()
            entryedit.bind('<Return>', saveedit)

        def NewAccount():
            cookie = askstring(title="登录新账号", prompt="请粘贴完整cookie")
            if cookie == '' or cookie == None:
                return
            self.controller.AddAccount(cookie)
            
        def SetBarrage(msg):
            if self.controller.SetBarrage(msg) == True:
                messagebox.showinfo('成功','话术设置成功')

        def SetTime(new_time):
            if self.controller.SetTime(new_time) == True:
                messagebox.showinfo('成功','时间间隔设置成功')

        def OpenLink(event):
            item = self.tree.selection()[0]
            index = self.tree.index(item)
            self.controller.OpenLink(index)

        self.root = Tk()                     # 创建窗口对象的背景色
        self.FormatWindow(self.root, 1500, 1000)
        self.root.title("Barrage Script")
        frame_connect = Frame(self.root)
        frame_barrage = Frame(self.root)
        frame_time = Frame(self.root)
        frame_manual = Frame(self.root)
        # Connect Frame
        # Category Frame
        Label(frame_connect, text="分类").grid(row = 0, sticky = E)
        # cate_link = StringVar()
        cate_dict = self.controller.GetCategory()
        cate_input = ttk.Combobox(frame_connect, values=tuple(cate_dict.keys()))
        # cate_input.bind('<<ComboboxSelected>>', ChooseCate)
        cate_input.grid(row = 0, column = 1, padx = 10, pady = 10)
        cateBtn = Button(frame_connect, text="设定", command = lambda: self.controller.ChooseCate(cate_input.get()))
        cateBtn.grid(row = 0, column = 2)

        Label(frame_connect, text="房间号").grid(row = 1, sticky = E)
        target_input = Entry(frame_connect, bd = 5)
        target_input.grid(row = 1, column = 1, padx = 10, pady = 10)
        connectBtn = Button(frame_connect, text="连接", command = lambda: self.controller.Connect(target_input.get()))
        connectBtn.grid(row = 1, column = 2)
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

        # Manual Frame
        timeBtn = Button(frame_manual, text="手动获取Cookie", command = self.controller.ManualCookie)
        timeBtn.grid(row = 0, column = 0)
        
        def IsReadyToSend():
            ck['text'] = v.get()
            if ck['text'] == 'ON':
                self.controller.ReadyToSend()
            else:
                self.controller.StopSend()

        v = StringVar()
        v.set('1')
        ck = ttk.Checkbutton(self.root, variable=v, text='OFF', onvalue='ON', offvalue='OFF', command=IsReadyToSend)
    
        # Tree
        columns = ('账号', '密码', 'cookie', '发送间隔', '房间', '话术', '状态')
        self.tree = ttk.Treeview(self.root, height=self.height, show="headings", columns=columns)

        for column in columns:
            self.tree.column(column, width=self.width, anchor='center')
            self.tree.heading(column, text=column)

        self.tree.pack(side=LEFT, fill=BOTH)
        self.newBtn = ttk.Button(self.root, text='登录新账号', width=self.btnWidth, command=NewAccount)
        self.UpdateTree(self.controller.data)

        for i in range(len(self.controller.data)):
            self.controller.Login(i)

        # Display
        frame_connect.pack(padx=1,pady=1)
        frame_time.pack(padx=1, pady=1)
        frame_barrage.pack(padx=1,pady=1)
        ck.pack()
        frame_manual.pack(padx=1,pady=1)
        
        self.tree.bind('<ButtonRelease-3>', OpenLink)
        self.tree.bind('<Double-1>', SetCell)
        self.root.mainloop()                 # 进入消息循环

    def VerifyUI(self):
        def copy():
            verify.clipboard_clear() 
            verify.clipboard_append(l1.get()) 
        def refresh():
            if self.controller.CheckActive() == True:
                verify.destroy()
                self.controller.Start()
        mac = self.controller.GetMac()
        verify = Tk()
        verify.title('请将编码复制给管理员激活')
        self.FormatWindow(verify, 400, 80)
        l1 = Entry(verify, width=30, bd=5)
        l1.insert(0, mac)
        btnFrame = Frame(verify)
        b1 = Button(btnFrame, text='复制', command=copy)
        b2 = Button(btnFrame, text='刷新', command=refresh)
        l1.pack()
        btnFrame.pack()
        verify.mainloop()


def GetProxy():
    url = 'http://http.tiqu.letecs.com:81/getip3?num=1&type=2&pro=0&city=0&yys=100017&port=11&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=2&regions=440000&gm=4'
    res = requests.get(url)
    res_json = json.loads(res.text)
    if res_json['success'] == True:
        ip = res_json['data'][0]['ip']
        port = res_json['data'][0]['port']
        proxy_url = '{}:{}'.format(ip, port)

    return proxy_url


if __name__ == '__main__':#执行层
    hyController = HuyaLiveController()
    # obj = HuyaLive()
    # phoneNum = obj.captchaObj.GetPhone('325')
    # obj.Register(phoneNum, 'qwe123456')