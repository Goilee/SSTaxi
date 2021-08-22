from .TCP import TCP


class ServerSocket(TCP):
    def __init__(self, port):
        super().__init__()
        self.sock.bind((self.ipServer, port))
        self.sock.listen(5)
        print("connection started")
    def waitCon(self, wlcMsg):
        while True:
            (self.targsock, address) = self.sock.accept()
            msg = self.waitSTR()
            print(msg)
            if msg == wlcMsg:
                self.sendSTR("nihao")

                print("connected")
            else:
                raise RuntimeError("wrong answer")
                continue
            break
    def getCrossId(self):
        id = self.waitINT()
        return id
    def getWay(self):
        msg = self.waitList()
        return msg
    def sendStopSign(self):
        self.sendSTR("Done")
        print("done sended")
    def sendDirection(self, direction):
        self.sendSTR(direction)
        print("direction is " + direction)
    def getInitialPos(self):
        self.sendSTR("pos")
        list = self.waitList()
        return list
