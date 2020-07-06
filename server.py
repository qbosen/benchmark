import socket
import time
from common import *
import os
import subprocess
import urllib.request


class JavaApplication:
    def stop_app(self):
        if os.path.exists(Server.pid_file):
            pid = open(Server.pid_file).readline()
            os.kill(int(pid), 15)
            print("停止程序...")
            time.sleep(0.5)

    def start_app(self, args):
        subprocess.Popen(f'nohup java -jar {Server.program} {args}', shell=True)

    def wait_app_start(self):
        i = 0
        url = f'http://{Server.host}:{Server.app_port}{Server.test_uri}'
        time.sleep(1)
        while True:
            try:
                if urllib.request.urlopen(url).getcode() == 200:
                    print("启动成功...")
                    return
            except urllib.request.URLError as e:
                pass
            i += 1
            print("等待程序启动...", i)
            time.sleep(1)

    def restart(self, conn, msg):
        self.stop_app()
        self.start_app(msg.split(":")[1])
        self.wait_app_start()
        conn.send(Server.started.encode('utf-8'))

    def close(self, conn):
        print("关闭客户端连接")
        conn.close()


class ServerDeals:
    def __init__(self, deals, default_deal=CommandDeal("*", lambda m, c, s, a: print("无法处理的消息:" + m))):
        self.deal_map = {}
        self.default_deal = default_deal
        for d in deals:
            self.deal_map[d.command] = d

    def deal(self, msg, conn, server, app):
        """
        服务端处理消息
        :param msg: 消息以header:body的形式，body的参数处理交给具体的方法
        :param conn: 当前客户度连接
        :param server: server socket
        :param app: 协助消息处理程序
        :return: 由具体处理消息的处理器决定
        """
        header = msg.split(':')[0]
        if header in self.deal_map:
            self.deal_map[header].deal(msg, conn, server, app)
        else:
            self.default_deal.deal(msg, conn, server, app)


class ServerSocket:
    def __init__(self, dealer: ServerDeals, app, host=Server.host, port=Server.port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(1)
        self.dealer = dealer
        self.app = app

    def run(self):
        try:
            while True:
                conn, addr = self.server.accept()
                print("接受连接", addr)
                command = conn.recv(1024).decode('utf-8')
                print('收到消息:', command)
                self.dealer.deal(command, conn, self.server, self.app)
        except KeyboardInterrupt:
            self.app.stop_app()
            print("关闭程序...")
            self.server.close()
            print("关闭socket...")


server_deals = [
    # 收到客户端发来的启动消息,app启动完成后发送started回执
    CommandDeal(Server.restart, lambda m, c, s, a: a.restart(c, m)),
    # 收到客户端 断开连接消息，关闭客户端连接
    CommandDeal(Client.close, lambda m, c, s, a: a.close(c)),
]
if __name__ == '__main__':
    app = JavaApplication()
    deals = ServerDeals(server_deals)
    server = ServerSocket(deals, app)
    server.run()
