from .TCP import TCP


class ServerSocket(TCP):
    def __init__(self, port, ip):
        super().__init__()
        self.sock.bind((ip, port))
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
    def getCrossList(self):
        float = self.waitFloat()
        int = self.waitINT()
        return [float,int]
    def getCrossId(self):
        int = self.waitINT()
        return int
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
