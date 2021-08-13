#!/usr/bin/env python3
# coding=utf-8
# author:sakuyo
#----------------------------------

import csv,time,sys,signal,os
from tkinter import * 
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Huya(object):
    def __init__(self):
        #初始化cookies
        self.cookies = {
            'udb_accdata':'13302912858',
            'udb_biztoken':'AQCECPx-7jxEk5dY6Yo1vF9OzbMRh6SSNTes-XM1vgUHRQKebnh83VScatCGRrukDw_dSqQNNV41bClvs_hifyNl7VAIoPm7dZGXjOu-ohd8-mgLFGv8IWbVGVECaFbITx_NH4VH56ZcpYeQ25-JtOem4-ImYJivmoVXOfIUYZ4alSmdz_xKQiW2z76-gaggM_IEvla61e3K12AzloYX8sM6f9mzxhsuhgTFR5puyHq2Y6pTekz7C46ssYtWaIb4CgufdBAbkbnNdFnOwo3LuAktqR07Itk-UTZjgIsoXjy3dLOZQG5JCFEdxzFpL2NJqGNLqvhwgrh_I3HijXKwrHN-',
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

        
        chrome_options = Options()
        # 设置无图模式
        #prefs = {"profile.managed_default_content_settings.images": 2}  
        #chrome_options.add_experimental_option("prefs", prefs)
        #chrome_options.add_argument("--mute-audio") # 静音
        ## 使用headless无界面浏览器模式
        #chrome_options.add_argument('--headless') # 增加无界面选项
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument('log-level=3')
        chrome_driver_path = r"./chromedriver.exe"
        self.driver = webdriver.Chrome(options = chrome_options, executable_path = chrome_driver_path)

    def Connect(self, username, psw):#连接直播间
        #登录
        while True:
            self.driver.switch_to.frame("UDBSdkLgn_iframe")
        
            self.driver.find_element_by_class_name("input-login").click()

            self.driver.find_element_by_xpath("//input[contains(@class, 'udb-input-account')]").send_keys(username)
            self.driver.find_element_by_xpath("//input[contains(@class, 'udb-input-pw')]").send_keys(psw)
            self.driver.find_element_by_id("login-btn").click()
            #返回到主页面
            self.driver.switch_to.default_content()
            time.sleep(3)
            userHd = self.driver.find_element_by_xpath("//*[@id='J_duyaHeaderRight']/div/div[2]/a")
            userHd_href = userHd.get_attribute('href')
            if '#' in userHd_href:
                print('密码错误')
                return False
            else:
                print('登录成功')
                return True
                break
            
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

class HuyaMsg(Huya):
    def __init__(self):
        Huya.__init__(self)
        url = 'https://i.huya.com/index.php?m=Msg&do=listMsg'
        self.driver.get(url)
        

    def Search(self, target):
        try:
            self.driver.switch_to.frame('msgIframe')
        except:
            pass
        chat_root = self.driver.find_element_by_id('root')
        search_div = chat_root.find_element_by_class_name("search")
        search_input = search_div.find_element_by_tag_name("input").send_keys(target)
        time.sleep(3)
        search_list = self.driver.find_elements_by_class_name('search-list')
        for item in search_list:
            nickname = item.find_element_by_class_name('search-list-nick').text
            if nickname == target:
                print('已找到主播')
                item.click()
                #time.sleep(0.5)
                self.driver.find_element_by_class_name('person-send').click()
                return True
                break
        return False
    
    def SendMsg(self, msg):
        self.driver.find_element_by_class_name('input-content').send_keys(msg)
        self.driver.find_element_by_class_name('send-btn').click()

class HuyaUI(object):
    def __init__(self):
        self.hyObj = HuyaMsg()
        root = Tk()                     # 创建窗口对象的背景色
        root.geometry("500x300+750+200")
        root.title("Barrage Script")
        frame_search = Frame(root)
        frame_login = Frame(root)
        frame_msg = Frame(root)
        # Connect Frame
        Label(frame_search, text="主播名称").grid(row = 0, sticky = E)
        target_input = Entry(frame_search, bd = 5)
        target_input.grid(row = 0, column = 1, padx = 10, pady = 10)
        connectBtn = Button(frame_search, text="连接", command = lambda: Connect(target_input.get()))
        connectBtn.grid(row = 0, column = 2)
        # Login Frame
        Label(frame_login, text="用户名").grid(row = 0, sticky = E)
        user_input = Entry(frame_login, bd = 5)
        user_input.grid(row = 0, column = 1, padx = 10, pady = 10)
        Label(frame_login, text="密码").grid(row = 1, sticky = E)
        psw_input = Entry(frame_login, bd = 5, show="*")
        psw_input.grid(row = 1, column = 1, padx = 10, pady = 10)
        loginBtn = Button(frame_login, text="登录", width = 8, command = lambda: Login(user_input.get(), psw_input.get()))
        loginBtn.grid(row = 2, columnspan = 3)
        # Barrage Frame
        barrage_input = Entry(frame_msg, bd = 5)
        barrage_input.grid(row = 0, column = 0)
        sendBtn = Button(frame_msg, text="发送", command = lambda: SendBarrage(barrage_input.get()))
        sendBtn.grid(row = 0, column = 1)
        def Connect(input):
            res = self.hyObj.Search(input)
            if res == True:
                frame_msg.pack()
            else:
                messagebox.showerror('错误','主播不存在')

        def Login(user, psw):
            res = self.hyObj.Connect(user, psw)
            if res == True:
                frame_search.pack()
                frame_login.pack_forget()
            else:
                messagebox.showerror('错误','密码错误')

        def SendBarrage(msg):
            barrage_input.delete(0, END)
            res = self.hyObj.SendBarrage(msg)
            if res == True:
                pass
            else:
                messagebox.showerror('错误','弹幕发送失败')

        frame_login.pack(padx=1,pady=1)
        # loginBtn.pack()
        root.mainloop() # 进入消息循环





def QuitAndSave(signum, frame):#监听退出信号
    print('catched singal: %d' % signum)
    hyObj.SaveToCSV(hyObj.target, ['username','time','msg','gift','num'], hyObj.barrageList.values())
    sys.exit(0)


if __name__ == '__main__':#执行层
    #信号监听
    signal.signal(signal.SIGTERM, QuitAndSave)
    signal.signal(signal.SIGINT, QuitAndSave)
    
    hyObj = HuyaUI()