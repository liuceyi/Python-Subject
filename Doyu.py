#!/usr/bin/env python3
# coding=utf-8
# author:sakuyo
#----------------------------------
import re
import socket
import signal
import multiprocessing
import time

#创建类
class DoYu_Barrage():
    def __init__(self,roomId):#初始化
        self.roomId = roomId
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 8602  # 端口8601、8602、12601、12602这几个端口号都是
        self.host = socket.gethostbyname('openbarrage.douyutv.com')
        self.client.connect((host, port))
        self.bulletscreen = re.compile(b'txt@=(.+?)/')
        self.user_id = re.compile(b'nn@=(.+?)/')
        self.id_msg_list = []
    def get_bulletscreen(self,roomid):#获取弹幕方法
        loginMsg = 'type@=loginreq/roomid@={}/\0'.format(self.roomId)  # 登录请求消息,最后面的'\0',是协议规定在数据部分结尾必须是'\0'
        send_request_msg(loginMsg)
        JoinRoomMsg = 'type@=joingroup/rid@={}/gid@=-9999/\0'.format(self.roomId)  # 加入房间分组消息
        send_request_msg(JoinRoomMsg)
        while True:
            data = self.client.recv(1024) # 获取服务器响应
            bulletscreen_username = re.findall(self.user_id, data)
            bulletscreen_content = re.findall(self.bulletscreen, data)
            # print(data)
 
            if not data:
                break
            else:
                for i in range(0, len(bulletscreen_username)):
 
                    try:
                        print('[{}]:{}'.format(bulletscreen_username[i].decode('utf-8'), bulletscreen_content[i].decode('utf-8')))
                        # 返回的数据是bytes型，所以要用decode方法来解码
                        self.id_msg_list.append(bulletscreen_username[i].decode('utf-8'))
                        self.id_msg_list.append(bulletscreen_content[i].decode('utf-8'))
 
                    except:
                        continue
    def send_request_msg(self,msgstr):
        msg = msgstr.encode('utf-8')  # 协议规定所有协议内容均为 UTF-8 编码

        data_lenth = len(msg) + 8 # data_lenth表示整个协议头的长度（消息长度），包括数据部分和头部，len(msg)就是数据部分，8就是头部的长度
 
        code = 689 # 根据协议消息类型字段用689
 
        msghead = int.to_bytes(data_lenth, 4, 'little') + int.to_bytes(data_lenth, 4, 'little') + int.to_bytes(code, 4, 'little')
        # msghead是按照斗鱼第三方协议构造的协议头，前2段表示的是消息长度，最后一个是消息类型
 
        self.client.send(msghead)  # 发送协议头
        self.client.send(msg)  # 发送消息请求
    
    def login(self):#登入
        self.p1 = multiprocessing.Process(target=self.get_bulletscreen, args=(self.roomid,))
        self.p2 = multiprocessing.Process(target=keeplive)
        self.p1.start()
        self.p2.start()

    def keeplive(self):#心跳控制
        while True:
            live_msg = 'type@=keeplive/tick@=' + str(int(time.time())) + '/\0'
            self.send_request_msg(live_msg)
            time.sleep(15)

    
    def logout(self):#登出
        self.p1.terminate()  # 结束进程
        self.p2.terminate()  # 结束进程
        out_msg = 'type@=logout/'
        self.send_request_msg(out_msg)
        print('已退出服务器！')
        
    
    def signal_handler(self,signal, frame):#信号收集
        # 捕捉退出信号，即signal.SIGINT
        self.logout()
    
    def save(self,danmus):#存入txt
        with open('hcf.txt','a+',encoding='utf-8')as f:
            f.write(danmus+'\n')

#main方法---------执行层
if __name__ == '__main__':
    roomId = 9220456  # 房间号,主播开播才能获取到信息
    DoYuCatcher = DoYu_Barrage(roomId)
    DoYuCatcher.login()
    
 





