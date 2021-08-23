from .TCP import TCP
from socket import SHUT_RDWR
class ClientSocket(TCP):
    def __init__(self,port, wlcMsg, ip):
        super().__init__()
        self.targsock = self.sock
        self.targsock.connect((ip, port))
        self.sendSTR(wlcMsg)
        msg = self.waitSTR()
        if msg != "nihao":
            print("trouble")
        print("connected")

    def sendCross(self, float, int):
        self.sendFloat(float)
        self.sendINT(int)
    def sendPos(self, list):
        self.waitSTR()
        self.sendList(list)
    def sendWay(self, list):
        self.sendList(list)
    def waitStopSign(self):
        self.waitSTR()


