import requests,json,time
from bs4 import BeautifulSoup
from threading import Thread
class IPPool(object):
    def __init__(self):
        self.urls = [
            # 'https://www.kuaidaili.com/free/inha/', 
            "https://proxy.ip3366.net/free/?action=china&page="
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Connection':'close'
        }
        self.LoadProxies()
        
    
    def Connect(self, url, page='1'):
        url = url + str(page)
        requests.adapters.DEFAULT_RETRIES = 5
        s = requests.session()
        s.keep_alive = False
        req = requests.get(url, headers=self.headers, verify=False)
        soup = BeautifulSoup(req.text)
        ips_html = soup.find_all('td',{'data-title':'IP'})
        ips = []
        for ip_html in ips_html:
            ip = ip_html.text
            ips.append(ip)
        ports_html = soup.find_all('td',{'data-title':'PORT'})
        ports = []
        for port_html in ports_html:
            port = port_html.text
            ports.append(port)
        temps = []
        for i in range(0,len(ips)):
            temp = Thread(target=self.CheckProxy, args=(ips[i], ports[i]))
            temps.append(temp)

        for temp in temps:
            temp.start()
        
        for temp in temps:
            temp.join()

    def CheckProxy(self, ip, port, exist=False):
        print('ip:{}, port:{}'.format(ip, port))
        proxies = {}
        proxy_url = 'https://{}:{}'.format(ip, port)
        url = 'http://www.baidu.com/'
        proxy_dict = {
            'http' : 'http://{}:{}'.format(ip, port),
            'https': 'https://{}:{}'.format(ip, port)
        }
        try:
            start_time = time.time()
            response = requests.get(url, proxies=proxy_dict, timeout=5)
            if response.status_code == 200:
                end_time = time.time()
                print('代理可用：' + proxy_url)
                print('耗时:' + str(end_time - start_time))
                if exist == True:
                    return True
                for proxy in self.proxies:
                    if proxy['ip'] == ip:
                        print('重复ip，已跳过')
                        return True
                    else:
                        pass
                proxies['ip'] = ip
                proxies['port'] = port
                self.proxies.append(proxies)
                # proxiesJson = json.dumps(self.proxies)
                with open('proxies.json', 'w') as f:
                    json.dump(self.proxies, f)
                print("已写入：%s" % proxy_url)
                return True
            else:
                print('代理超时')
                return False
        except Exception as e:
            print('代理不可用--->'+str(e))
            return False

    def LoadProxies(self):
        with open('proxies.json', 'r') as f:
            try:
                self.proxies = json.load(f)
            except Exception as e:
                print(e)
                self.proxies = []
            print(self.proxies)

    def GetProxy(self):
        return self.proxies

    def CheckExistProxies(self):
        for proxy in self.proxies:
            if self.CheckProxy(proxy['ip'], proxy['port'], True) == True:
                pass
            else:
                self.proxies.remove(proxy)
        # proxiesJson = json.dumps(self.proxies)
        with open('proxies.json', 'w') as f:
            json.dump(self.proxies, f)


if __name__ == '__main__':#执行层
    ipPool = IPPool()
    ipPool.CheckExistProxies()
    i = 1
    while len(ipPool.proxies) < 2:
        for url in ipPool.urls:
            temp = Thread(target=ipPool.Connect, args=(url, i))
            temp.start()
            temp.join()
        i = i + 1