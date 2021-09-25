#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhangslob
@file: longzhu_websocket.py 
@time: 2018/11/17
@desc: simple websocket client to connect longzhu
"""

from requests.api import head
import websocket
import requests
try:
    import thread
except ImportError:
    import _thread as thread
import time
import json


msgs = []
def on_message(ws, msg_raw):
    
    try:
        msg_json = json.loads(msg_raw)
        msg = {
            'user':msg_json['msg']['user']['username'],
            'msg':msg_json['msg']['content'],
            'time':msg_json['msg']['time']
        }
        msgs.append(msg)
        print(msg)
    except:
        pass


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    pass
    # def run(*args):
    #     for i in range(3):
    #         time.sleep(1)
    #         ws.send("Hello %d" % i)
    #     time.sleep(1)
    #     ws.close()
    #     print("thread terminating...")
    # thread.start_new_thread(run, ())


headers = {
    'Pragma': 'no-cache',
    'Origin': 'http://m.longzhu.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    # 'Sec-WebSocket-Key': 'n72+EfLt2iSrQ0EswTZ+2A==',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Mobile Safari/537.36',
    'Upgrade': 'websocket',
    'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
    'Cache-Control': 'no-cache',
    'Connection': 'Upgrade',
    'Sec-WebSocket-Version': '13',
}



def sendMsg(roomId, msg):
    url = 'http://mbgo.longzhu.com/chatroom/sendmsg'
    data = {'group':roomId,'content':msg, 'color':'0xffffff', 'style':1, 'platform':'h5', 'device':'android'}
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36',
        'Cookie' : '__mtmc=2.1502187051.1629723252; _ma=OREN.2.1293049666.1629723252; __mtmb=2.326159127.1629723252; pluguest=F7B7C679CECC079BBC5F8996670A57CE2C664D9A513C384A918D02B0F18A116D1BDB841524125A650056E5E20ADAB8C518E948D5299003DD; c=H0fmLYBJ-1629723739200-fced6938f9d2e1475983117; token=18faf2e8-32bb-4232-95c8-088373373909; hm_guid=a64043ba-c4ec-456d-b7ac-375762fd675d; _fmdata=vsnkFLXvyrjWviEwjUiz9oSiFNxg7hbU94dH4eo%2Buvmsd%2FwsKouJy%2BdOcOjoGhppK00rj%2Fbs55AZpYVSDjCY10YVIlA2N%2B2KV2Tijx7RJg0%3D; _xid=KEovCnJ%2BGUJHTBCLEiiQcOCSI2ZNXt9rr3O%2FyPEBUOgBbiMsHRcJFBv%2BAEe4siwObwlW8MEiHNoxxxEPqtWsww%3D%3D; _snzwt=THHh1t17b731ac502c63kdc09; _df_ud=8d4b76da-5291-4d34-b131-86c9a534b941; iar_sncd=0; iar_low=0; p1u_id=961ec440e0e89f5dc7498840771716c5a2c5519ce87f95a6bb253148d4634d17a8c267a7f87d959b48d16f070308ff66e9963d851d383d2e; UM_distinctid=17b73470b6d1d8-022ada2b91529e-4343363-240000-17b73470b6e1658'
    }
    res = requests.get(url, params=data, headers=headers)
    res_json = json.loads(res.text)
    print(res_json)

if __name__ == "__main__":
    # websocket.enableTrace(True)
    # ws = websocket.WebSocketApp("wss://idc-cn-xs.longzhu.com:8806/?room_id=483072",
    #     on_message=on_message,
    #     on_error=on_error,
    #     on_close=on_close,
    #     header=headers
    # )
    # ws.on_open = on_open
    # ws.run_forever()
    sendMsg('483072', '6')