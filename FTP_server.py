'''
ftp 文件服务器
并发网络功能训练
'''
from socket import *
from threading import Thread
import sys,os
import time

#全局变量
HOST = '0.0.0.0'
PORT = 7373
ADDR = (HOST,PORT)
FTP = '/home/tarena/yydaima/month02/'    #文件库路径


#将客户端请求功能封装为类
class FtpServer:
    def __init__(self,c,path):
        self.c = c
        self.path = path

    def do_cat(self):
        #获取文件列表
        files = os.listdir(self.path)
        if not files: #如果文件列表为空
            self.c.send('该文件类别为空'.encode())
            return
        else:
            self.c.send(b'ok')
            time.sleep(0.1)  #延时发送解决粘包

        #过滤隐藏文件（os可以把隐藏文件也找出来）
        fs = ''
        for file in files:
            #不是隐藏文件 并且 是普通文件
            if file[0] != '.' and os.path.isfile(self.path+file):
                fs += file +'\n' #字符串拼接，一次发送解决粘包问题
        self.c.send(fs.encode())

    def do_get(self,filename):
        try:
            fd = open(self.path+filename,'rb')
        except Exception:
            self.c.send('not exist'.encode())
            return
        else:
            self.c.send(b'ok')
            time.sleep(0.1)   #注意粘包
        #发送文件内容
        while True:
            data = fd.read(1024)
            if not data:
                time.sleep(0.1)  #注意粘包
                self.c.send(b'##')
                break
            self.c.send(data)

    def do_put(self,filename):
        if os.path.exists(self.path+filename):
            self.c.send('exist'.encode())
            return
        self.c.send(b'ok')
        fd = open(self.path+filename,'wb')
        #接收文件内容
        while True:
            data = self.c.recv(1024)
            if data == b'##':
                break
            fd.write(data)
        fd.close()


#客户端请求处理函数
def handle(c):
    #选择文件夹
    cls = c.recv(1024).decode()
    path = FTP + cls + '/' #拼接路径，最后以/结束
    ftp = FtpServer(c,path)  #函数就是少什么就得传进去
    while True:
        #接收客户端请求
        data = c.recv(1024).decode()
        # 客户端异常结束或退出时
        if not data or data[0] == 'Q':
            return  #handle结束，对应的线程结束了
        elif data[0] == 'C':
            ftp.do_cat()
        elif data[0] == 'G':
            filename = data.split(' ')[-1]
            ftp.do_get(filename)
        elif data[0] == 'P':
            filename = data.split(' ')[-1]
            ftp.do_put(filename)

#网络搭建
def main():
    s = socket(AF_INET, SOCK_STREAM)  #套接字创建在这里
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(3)
    while True:
        try:
            c,addr = s.accept()
        except KeyboardInterrupt:
            sys.exit('server exit')
        except Exception as e:
            print(e)
            continue
        print('Connect from:', addr)
        client = Thread(target = handle,args = (c,))
        client.setDaemon(True)
        client.start()


if __name__ == '__main__':
    main()































