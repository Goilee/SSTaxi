from TCP import TCP


class ServerSocket(TCP):
    def __init__(self, port):
        super().__init__()
        self.targsock.bind((self.ipServer, port))
        self.targsock.listen(5)
        print("connection started")
    def waitCon(self, wlcMsg):
        while True:
            (self.targsock, address) = self.targsock.accept()
            msg = self.waitSTR()
            print(msg)
            if msg == wlcMsg:
                self.sendSTR("Hi")

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

