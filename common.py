# 客户端发送，服务端接收
class Client:
    # 客户端关闭
    close = "close"
    init = "init"

    @staticmethod
    def args(header, args):
        return header + ":" + args


# 服务端发送，客户端接收
class Server:
    host = "192.168.6.167"
    port = 7805
    app_port = 7801
    started = "app started"
    restart = "restart"
    test_uri = "/param/1?param=test"


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
