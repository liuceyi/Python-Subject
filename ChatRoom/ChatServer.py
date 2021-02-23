#!/usr/bin/env python3
# coding=utf-8
# author:sakuyo
#----------------------------------
import socket
import threading
import struct
import json
class Server(object):
    def __init__(self):
        serverADDR = ('127.0.0.1',8888)
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #TCP
        self.server.bind(serverADDR) #绑定
        self.server.listen(5) #5为挂起的最大连接数
        print('Server starts running.')
        self.users = [] #在线用户列表
        

    def Launch(self): #启动并等待连接
        self.acceptMode = True
        while self.acceptMode:
            conn,addr=self.server.accept() #等待连接……
            connectThread = threading.Thread(target=self.Connect,args=(conn,addr)) #将单个连接接入线程
            connectThread.start()
            #print(conn)
            print('Client %s connected.' % str(addr))

    def Connect(self,conn,addr): #连接单个客户端
        try:
            while True:
                self.CheckHeader(conn)

                clientMsg = conn.recv(1024)
                #中途断开
                if not clientMsg:
                    print('Client %s disconnected.' % str(addr))
                    raise Exception('disconnected')

                clientMsg = clientMsg.decode('utf-8')
                print('>> %s' %clientMsg)

                resMsg = 'Sent successfully.'.encode('utf-8')
                conn.send(resMsg) #发消息

        except HeaderError as e:
            print(e)
            conn.close()
        except Exception as e:
            print('Client %s disconnected.[%s]' % (str(addr),str(e)))
            conn.close()

    def CheckHeader(self,conn):
        try:
            headerLenBytes = conn.recv(4) #收消息
            headerLen = struct.unpack('i',headerLenBytes)[0]
            headerBytes = conn.recv(headerLen)       
            header = json.loads(headerBytes)
            user[header['user']] = header['key']
            resMsg = 'success'.encode('utf-8')
            conn.send(resMsg) #发消息
        except:
            raise HeaderError('Invalid Client')

    def Stop(self):
        self.acceptMode = False

    def Shutdown(self):
        self.server.close()
    
class HeaderError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

if __name__ == '__main__':#执行层
    server = Server()
    server.Launch()



