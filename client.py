import socket
import time

from common import *
from bench import BenchCollection
import csv


class ClientApp:
    def __init__(self, url, ab_c, ab_n, app_args, times):
        """
        客户端处理程序
        :param app_args: 远程启动对方程序时，所携带的参数
        :param times: benchmark执行次数
        """
        self.args = app_args
        self.times = times
        self.cur_time = 0
        self.url = url
        self.ab_c = ab_c
        self.ab_n = ab_n
        self.results = []
        self.is_closed = False

    def init(self, conn):
        # 启动服务端程序
        self.cur_time = 0
        self.results = []
        self.is_closed = False
        conn.send(Client.args(Server.restart, self.args).encode('utf-8'))

    def is_closed(self):
        return self.is_closed

    def deal_results(self):
        print(self.results)
        ExcelUtil.save_result("bench.csv", self.results)

    def start_bench(self, conn):
        # 执行指定次数的测试
        while self.cur_time < self.times:
            bench = BenchCollection().bench(self.url, self.ab_c, self.ab_n)
            if len(bench):
                self.results.append(bench)
                self.cur_time += 1
        # 处理结果
        self.deal_results()
        # 关闭客户端连接
        conn.send(Client.close.encode('utf-8'))
        self.is_closed = True
        conn.close()


class ClientDeals:
    def __init__(self, deals, default_deal=CommandDeal("*", lambda m, c, a: print("无法处理的消息:" + m))):
        self.deal_map = {}
        self.default_deal = default_deal
        for d in deals:
            self.deal_map[d.command] = d

    def deal(self, msg, client, app):
        if msg in self.deal_map:
            self.deal_map[msg].deal(msg, client, app)
        else:
            self.default_deal.deal(msg, client, app)


class ClientSocket:
    def __init__(self, deals: ClientDeals, app, host=Server.host, port=Server.port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.deals = deals
        self.app = app

    def run(self):
        msg = Client.init
        while True:
            self.deals.deal(msg, self.client, self.app)
            if self.app.is_closed:
                return
            msg = self.client.recv(1024).decode('utf-8')
            print('收到消息:', msg)


class ExcelUtil:
    @staticmethod
    def save_result(filename, results):
        with open(filename, 'a', newline='') as file:
            fieldnames = ['uri', 'concurrency', 'requests', 'qps', 'tpr', 't_90']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(results)


client_deals = [
    # init 启动服务端，等待服务端启动完毕
    CommandDeal(Client.init, lambda m, c, a: a.init(c)),
    # started 服务已启动，开始benchmark测试, 完成后关闭client连接
    CommandDeal(Server.started, lambda m, c, a: a.start_bench(c)),
]

bench_counts = [1,
                # 10, 50, 100, 200, 500
                ]

if __name__ == '__main__':
    args_pattern = "--paramUrls={0} --pathUrls={0} --{1}"
    urls_pattern = [
        "http://{host}:{port}/param/{i}?param={opt}",
        "http://{host}:{port}/path/{opt}/{i}"
    ]
    for opt in ["no-optimize", "optimize"]:
        for url_pattern in urls_pattern:
            for i in bench_counts:
                args = args_pattern.format(i, opt)
                url = url_pattern.format(host=Server.host, port=Server.app_port, i=i, opt=opt)
                app = ClientApp(url, 100, 3000, args, 10)
                deals = ClientDeals(client_deals)
                client = ClientSocket(deals, app)
                client.run()
                print("完成一次benchmark")
                time.sleep(1)
