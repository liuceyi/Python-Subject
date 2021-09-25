from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

chrome_options = Options()
# 设置无图模式

prefs = {
    "profile.managed_default_content_settings.images": 2,
    "webrtc.ip_handling_policy": "disable_non_proxied_udp",
    "webrtc.multiple_routes_enabled": False,
    "webrtc.nonproxied_udp_enabled": False
}  
chrome_options.add_experimental_option("prefs", prefs)
    # chrome_options.add_argument("--mute-audio") # 静音
    # 使用headless无界面浏览器模式
    # chrome_options.add_argument('--headless') # 增加无界面选项
# 切换代理IP

chrome_options.add_argument("--proxy-server=140.249.72.21:8351")

chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument('log-level=3')
chrome_driver_path = r"./chromedriver.exe"
driver = webdriver.Chrome(options = chrome_options, executable_path = chrome_driver_path)
driver.maximize_window()
url = 'https://huya.com/'
driver.get(url)