import socket
import time
from common import *
import os
import subprocess
import urllib.request

pid_file = "application.pid"
program = "measure-rest-0.0.1-SNAPSHOT.jar"


class JavaApplication:
    def __stop_app(self):
        if os.path.exists(pid_file):
            pid = open(pid_file).readline()
            os.kill(int(pid), 15)
            print("停止程序...")
            time.sleep(0.5)

    def __start_app(self, args):
        subprocess.Popen(['nohup', 'java', '-jar', program, args],
                         stdout=subprocess.PIPE,
                         universal_newlines=True)

    def __check_app(self):
        i = 0
        url = f'http://{Server.host}:{Server.app_port}{Server.test_uri}'
        while True:
            with urllib.request.urlopen(url) as response:
                if response.ok():
                    print("启动成功...")
                    return
                else:
                    print("等待程序启动...")
            time.sleep(0.1)

    def restart(self, conn, msg):
        self.__stop_app()
        self.__start_app(msg.split(":")[1])
        self.__check_app()
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
        while True:
            conn, addr = self.server.accept()
            print("接受连接", addr)
            command = conn.recv(1024).decode('utf-8')
            print('收到消息:', command)
            self.dealer.deal(command, conn, self.server, self.app)


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
