from TCP import TCP

class ClientSocket(TCP):
    def __init__(self,port, wlcMsg):
        super().__init__()
        self.targsock = self.sock
        self.targsock.connect((self.ipServer, port))
        self.sendMSG(wlcMsg)
        msg = self.waitMSG()
        if msg != "hi":
            print("trouble")
        print("connected")

    def sendCross(self, int):
        self.sendMSG(str(int))


