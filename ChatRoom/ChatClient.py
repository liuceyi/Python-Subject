#!/usr/bin/env python3
# coding=utf-8
# author:sakuyo
#----------------------------------
import socket
import time
import json
import struct

class Client(object):
    def __init__(self):
        self.serverADDR = ('127.0.0.1',8888)
        self.username = socket.gethostname()
        self.header = {'user':self.username,'tag':'','key':''}
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #TCP

    def Launch(self):
        self.client.connect(self.serverADDR) #连接服务器
        print('Connected successfully.')

    def Register(self):
        self.username = input('Username:')
        self.password = input('Password:')

    def Login(self):
        self.username = input('Username:')
        self.password = input('Password:')
        

    def SendHeader(self,tag):
        header = self.header
        header['tag'] = tag
        headerBytes = bytes(json.dumps(header),encoding='utf-8')
        headerLenBytes=struct.pack('i',len(headerBytes))
        self.client.send(headerLenBytes)
        self.client.send(headerBytes)

        resMsg = self.client.recv(1024).decode('utf-8')
        if resMsg == 'success':
            return True
        else:
            return False

    def SendMsg(self):
        while True:
            newMsg = input('>>')
            if not newMsg:
                continue
            newMsg = ('[%s][%s] %s' % (self.username,time.ctime(),newMsg)).encode("utf-8")
            try:
                self.SendHeader('msg')
                self.client.send(newMsg)

            except:
                print('Server disconnected.')
                break

            resMsg = self.client.recv(1024).decode('utf-8')
            print(resMsg)
    


    def Quit(self):
        self.client.close()


if __name__ == '__main__':#执行层
    client = Client()
    client.Launch()
    client.SendMsg()