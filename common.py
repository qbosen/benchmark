class Client:
    # 客户端关闭
    close = "close"
    init = "init"
    concurrent = 500
    requests = 30000
    repeat_times = 10
    mapping_counts = [1, 10, 50, 100, 200, 500]

    @staticmethod
    def args(header, args):
        return header + ":" + args


class Server:
    host = "192.168.6.167"
    port = 7805
    app_port = 7801
    started = "started"
    restart = "restart"
    test_uri = "/param/1?param=test"
    pid_file = "application.pid"
    program = "measure-rest-0.0.1-SNAPSHOT.jar"


class CommandDeal:

    def __init__(self, command, func):
        """
        处理一个命令
        :param command: 接收到的命令
        :param func: 处理函数
        """
        self.command = command
        self.func = func

    def deal(self, msg, *args):
        self.func(msg, *args)
