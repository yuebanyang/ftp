from socket import *
import sys
import time

#具体功能
class FtpClient:
    # def __init__(self):
    #     self.s = socket()
    def __init__(self,s):
        self.s = s

    def do_cat(self):
        self.s.send(b'C')  #发送请求 类似聊天室，协议商定请求类型
        #等待回复
        data = self.s.recv(128).decode()
        #OK表示请求成功
        if data == 'ok':
            #接收文件列表
            data = self.s.recv(4096)
            print(data.decode())
        else:
            print(data)

    def do_quit(self):
        self.s.send(b'Q')
        self.s.close()
        sys.exit('tks,bye')

    def do_get(self,filename):
        self.s.send(('G '+filename).encode())
        data = self.s.recv(128).decode()
        if data == 'ok':#注意粘包，发送的时候要sleep一下
            fd = open(filename,'wb')
            #接收内容写入文件
            while True:
                data = self.s.recv(1024)
                if data == b'##':
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)

    def do_put(self,filename):
        try:
            f = open(filename,'rb')
        except Exception:
            print('not exist')
            return

        #发送请求
        filename = filename.split('/')[-1] #以防带路径的文件名
        # print(filename)
        self.s.send(('P ' + filename).encode())
        #等待回复
        data = self.s.recv(128).decode()
        if data == 'ok':  # 注意粘包，发送的时候要sleep一下
            while True:
                data = f.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.s.send(b'##')
                    break
                self.s.send(data)
            f.close()
        else:
            print(data)


#发起请求
def request(s):
    ftp = FtpClient(s)
    while True:
        print('\n~~~~~~~~~~~~~~~命令选项~~~~~~~~~~~~~')
        print('~~~~~~~~~~~~~~~~cat~~~~~~~~~~~~~~~~')
        print('~~~~~~~~~~~~~~get file~~~~~~~~~~~~~')
        print('~~~~~~~~~~~~~~put file~~~~~~~~~~~~~')
        print('~~~~~~~~~~~~~~~~quit~~~~~~~~~~~~~~~')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        cmd = input('命令：')
        if cmd.strip() == 'cat':
            ftp.do_cat()
        elif cmd.strip() == 'quit':
            ftp.do_quit()
        elif cmd[:3] == 'get':
            filename = cmd.split(' ')[-1] #切割文件名，取后面的
            ftp.do_get(filename)
        elif cmd[:3] == 'put':
            filename = cmd.split(' ')[-1] #切割文件名，取后面的
            ftp.do_put(filename)
        #在控制台输入data文件夹（相当于选择上传到哪个文件夹
        # 客户端所在文件夹里有seek.py(相对路径）
        # 绝对路径就可以不用和客户端在同一个文件夹下
        # put后，传入到data



#网络链接
def main():
    ADDR = ('127.0.0.1',7373)
    s = socket()
    try:
        s.connect(ADDR)
    except Exception as e:
        print('链接失败')
        return
    else:
        print('''
********************************
   data pythonNet concurrent
********************************
        ''')
        cls = input('文件种类')
        if cls not in ['data', 'pythonNet', 'concurrent']:
            print('input error')
            return
        else:
            s.send(cls.encode())
            request(s)

if __name__ == '__main__':
    main()