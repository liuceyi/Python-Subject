import requests,json,time

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
            msg = res['sms']
            return msg
        elif res['code'] == 401:
            self.Login()
        return False

    def GetPhone(self, sid):
        url = 'http://www.liuxing985.com:81/sms/api/getPhone?token={}&sid={}'.format(self.token, sid)
        res_raw = requests.get(url)
        print(res_raw.text)
        res = json.loads(res_raw.text)
        if res['code'] == 0:
            msg = res['phone']
            return msg
        elif res['code'] == 401:
            self.Login()
        return False


if __name__ == '__main__':# Run here
    hcObj = HuyaCaptcha('api-sk53ln8H', '102056')
    time.sleep(1)
    phone = hcObj.GetPhone('325')
    print(hcObj.GetMessage('325', phone))
