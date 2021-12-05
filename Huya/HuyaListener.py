import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class HuyaListener(object):
  def __init__(self) -> None:
    self.barrageList = {}
    self.target = ''
    self.is_listen = False
    self.dmc = None
    chrome_options = Options()
    # 设置无图模式
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
    # chrome_options.add_argument("--proxy-server=" + ip)
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
    # url = 'https://www.huya.com/'
    # self.driver.get(url)

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

  def listen(self):
    while True: 
      time.sleep(1)
      chatRoomList = self.driver.find_element_by_id("chat-room__list")
      chatMsgs = chatRoomList.find_elements_by_xpath("//div[@data-cmid]")

      #定位弹幕div，逐条解析
      for chatMsg in chatMsgs:
        try:
          dataId = chatMsg.get_attribute('data-cmid') #每条弹幕都有独立data-cmid
          content = {} #初始化弹幕内容字典

          #尝试是否为消息弹幕
          try:
            content["username"] = chatMsg.find_element_by_class_name("J_userMenu").text
            content["msg"] = chatMsg.find_element_by_class_name("msg").text
            if not content["username"] or not content["msg"]:
              content = {}
          except:
            content = {}
          #存入弹幕列表
          if content != {} and dataId not in self.barrageList.keys():
            print(content)
            self.barrageList[dataId] = content
        except:
          continue


hyl = HuyaListener()
hyl.SetTarget('587520')
hyl.listen()